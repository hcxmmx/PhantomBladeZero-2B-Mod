"""Calibrate feed-forward two-bone IK helpers for a single lateral trajectory offset."""
from pathlib import Path
import json,numpy as np
from scipy.spatial.transform import Rotation as Q
R=Path(__file__).resolve().parents[1];W=R/'work/gait-direct';O=R/'output/gait-width';O.mkdir(exist_ok=True);cfg={'offset_cm_per_foot':3.0};maxerr=0
for path in sorted(W.glob('*-direct-native.json')):
 j=json.loads(path.read_text(encoding='utf-8'));s,t=j['source'],j['target'];sf,tf=np.array(s['frames']),np.array(t['frames']);si={n:i for i,n in enumerate(s['bones'])};ti={n:i for i,n in enumerate(t['bones'])};ref=np.array(t['reference_global'])
 for side in ['L','R']:
  h,k,f,p,roll=[ti[n] for n in ['SKEL_'+side+'_Thigh','SKEL_'+side+'_Calf','SKEL_'+side+'_Foot','SKEL_Pelvis','RB_'+side+'_ThighRoll']]
  names={'thigh':'thigh_'+side.lower(),'calf':'calf_'+side.lower(),'foot':'foot_'+side.lower(),'pelvis':'pelvis'};indices={'thigh':h,'calf':k,'foot':f,'pelvis':p};row={}
  for name in names:
   source=Q.from_quat(sf[:,si[names[name]],3:7]);target=Q.from_quat(tf[:,indices[name],3:7]);offset=source[0].inv()*target[0];row[name+'_offset_quat']=offset.as_quat().tolist()
  row['calf_local_translation']=Q.from_quat(ref[h,3:7]).inv().apply(ref[k,:3]-ref[h,:3]).tolist();row['foot_local_translation']=Q.from_quat(ref[k,3:7]).inv().apply(ref[f,:3]-ref[k,:3]).tolist();row['roll_offset_quat']=(Q.from_quat(tf[0,h,3:7]).inv()*Q.from_quat(tf[0,roll,3:7])).as_quat().tolist()
  if side not in cfg:cfg[side]=row
  row=cfg[side]
  thigh=Q.from_quat(sf[:,si[names['thigh']],3:7])*Q.from_quat(row['thigh_offset_quat']);calf=Q.from_quat(sf[:,si[names['calf']],3:7])*Q.from_quat(row['calf_offset_quat']);predk=thigh.apply(row['calf_local_translation']);predf=predk+calf.apply(row['foot_local_translation']);maxerr=max(maxerr,float(np.linalg.norm(predf-(tf[:,f,:3]-tf[:,h,:3]),axis=1).max()))
assert maxerr<.001,maxerr
cfg['calibration_max_relative_ankle_error_cm']=maxerr
(O/'runtime-settings.json').write_text(json.dumps(cfg,indent=2),encoding='utf-8');print('WIDTH_CALIBRATION_MAX_ERROR_CM',maxerr)
