"""Calibrate source-foot vectors against native UE retarget output, without runtime feedback."""
from pathlib import Path
import json,numpy as np
R=Path(__file__).resolve().parents[1];O=R/'output/gait-study'
scope={'__file__':str(R/'tools/analyze_shoe_gait.py')};exec((R/'tools/analyze_shoe_gait.py').read_text(encoding='utf-8').split('rows=[]')[0],scope);rotation=scope['rotation'];shoes=scope['shoes'];settings={};max_error=0
for path in sorted((R/'work/gait-study').glob('*-inward0.json')):
 j=json.loads(path.read_text(encoding='utf-8'));s,t=j['source'],j['target'];sf,tf=np.array(s['frames']),np.array(t['frames']);ref=np.array(t['reference_global'])
 for side in ['L','R']:
  i=t['bones'].index('SKEL_'+side+'_Foot');src=rotation(sf[:,s['bones'].index('foot_'+side.lower()),3:7]);dst=rotation(tf[:,i,3:7]);refrot=rotation(ref[i,3:7]);offset=src[0].T@dst[0]
  lm=next(x for x in shoes['rows'] if x['side']==side)['landmarks_ue_cm'];forward=np.array(lm['front_contact'])-lm['heel_contact'];forward/=np.linalg.norm(forward)
  local=refrot.T@forward;up=refrot.T@np.array([0.,0,1])
  row={'source_forward_local':(offset@local).tolist(),'source_up_local':(offset@up).tolist(),'target_forward_local':local.tolist()}
  if side not in settings:settings[side]=row
  for key,target in [('source_forward_local',dst@local),('source_up_local',dst@up)]:max_error=max(max_error,float(np.linalg.norm(src@np.array(settings[side][key])-target,axis=1).max()))
assert max_error<1e-5,max_error
settings['calibration_max_vector_error']=max_error;settings['max_correction_degrees']=6
(O/'shoe-runtime-settings.json').write_text(json.dumps(settings,indent=2),encoding='utf-8');print('CALIBRATED_ALL_SIX_CLIPS',max_error)
