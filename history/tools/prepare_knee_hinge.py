"""Prepare a movement-only anatomical knee hinge candidate from native neutral poses."""
from pathlib import Path
import json,numpy as np
from scipy.spatial.transform import Rotation as Q
R=Path(__file__).resolve().parents[1];W=R/'work/gait-study';O=R/'output/gait-study'
neutral=json.loads((R/'work/pose-diagnosis/Pelvis_Z-runtime025.json').read_text(encoding='utf-8'));settings={};rows=[]
for side in ['L','R']:
 values={}
 for key in ['source','target']:
  d=neutral[key];f=np.array(d['frames'][0]);names=d['bones'];n=['thigh_'+side.lower(),'calf_'+side.lower(),'foot_'+side.lower()] if key=='source' else ['SKEL_'+side+'_'+p for p in ['Thigh','Calf','Foot']];h,k,c=[names.index(x) for x in n];axis=np.cross(f[k,:3]-f[h,:3],f[c,:3]-f[k,:3]);axis/=np.linalg.norm(axis);calf=Q.from_quat(f[k,3:7]);local=Q.from_quat(f[h,3:7]).inv()*calf
  values[key]=(local,calf.inv().apply(axis))
 settings[side]={'source_neutral_inverse_quat':values['source'][0].inv().as_quat().tolist(),'source_hinge_axis':values['source'][1].tolist(),'target_neutral_quat':values['target'][0].as_quat().tolist(),'target_hinge_axis':values['target'][1].tolist()}
for path in sorted(W.glob('*-inward0.json')):
 j=json.loads(path.read_text(encoding='utf-8'));s,t=j['source'],j['target'];sf,tf=np.array(s['frames']),np.array(t['frames']);row={'clip':j['name'],'sides':{}}
 for side in ['L','R']:
  p=settings[side];sh,sk=[s['bones'].index(n+'_'+side.lower()) for n in ['thigh','calf']];th,tk,tc=[t['bones'].index('SKEL_'+side+'_'+n) for n in ['Thigh','Calf','Foot']]
  delta=Q.from_quat(p['source_neutral_inverse_quat'])*Q.from_quat(sf[:,sh,3:7]).inv()*Q.from_quat(sf[:,sk,3:7]);q=delta.as_quat();angle=2*np.arctan2(q[:,:3]@p['source_hinge_axis'],q[:,3]);angle=(angle+np.pi)%(2*np.pi)-np.pi
  target_local=Q.from_quat(p['target_neutral_quat'])*Q.from_rotvec(angle[:,None]*p['target_hinge_axis']);calf=Q.from_quat(tf[:,th,3:7])*target_local;change=calf*Q.from_quat(tf[:,tk,3:7]).inv();ankle=tf[:,tk,:3]+change.apply(tf[:,tc,:3]-tf[:,tk,:3]);shift=ankle-tf[:,tc,:3];ball=sf[:,s['bones'].index('ball_'+side.lower()),2];low=ball<ball.min()+3
  swing_axis=np.cross(tf[:,tk,:3]-tf[:,th,:3],ankle-tf[:,tk,:3]);swing_axis/=np.linalg.norm(swing_axis,axis=1)[:,None];local_axis=calf.inv().apply(swing_axis);alignment=np.abs(local_axis@p['target_hinge_axis']);axis_error=np.degrees(np.arccos(np.clip(alignment,-1,1)))
  row['sides'][side]={'max_calf_correction_deg':float(change.magnitude().max()*180/np.pi),'mean_ankle_shift_cm':float(np.linalg.norm(shift,axis=1).mean()),'max_ankle_shift_cm':float(np.linalg.norm(shift,axis=1).max()),'near_ground_z_shift_cm_min_max':[float(shift[low,2].min()),float(shift[low,2].max())],'corrected_hinge_plane_error_deg_max':float(axis_error.max())}
 rows.append(row)
(O/'knee-hinge-settings.json').write_text(json.dumps(settings,indent=2),encoding='utf-8');(O/'knee-hinge-candidate.json').write_text(json.dumps({'offline_candidate':True,'clips':rows},indent=2),encoding='utf-8')
for row in rows:print(row['clip'],row['sides'])
