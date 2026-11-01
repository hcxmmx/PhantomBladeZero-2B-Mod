"""Audit hip axial rotation and prepare a clean hip-only movement candidate."""
from pathlib import Path
import json,numpy as np
from scipy.spatial.transform import Rotation as Q
R=Path(__file__).resolve().parents[1];O=R/'output/gait-study';W=R/'work/gait-study'
neutral=json.loads((R/'work/pose-diagnosis/Pelvis_Z-runtime025.json').read_text(encoding='utf-8'));settings={};rows=[];max_error=0
for side in ['L','R']:
 s,t=neutral['source'],neutral['target'];sf,tf=np.array(s['frames'][0]),np.array(t['frames'][0]);si={n:i for i,n in enumerate(s['bones'])};ti={n:i for i,n in enumerate(t['bones'])}
 sp,sh=si['pelvis'],si['thigh_'+side.lower()];tp,th,tk,tr=[ti[n] for n in ['SKEL_Pelvis','SKEL_'+side+'_Thigh','SKEL_'+side+'_Calf','RB_'+side+'_ThighRoll']]
 pelvis_offset=Q.from_quat(sf[sp,3:7]).inv()*Q.from_quat(tf[tp,3:7]);thigh_offset=Q.from_quat(sf[sh,3:7]).inv()*Q.from_quat(tf[th,3:7]);local=Q.from_quat(tf[tp,3:7]).inv()*Q.from_quat(tf[th,3:7]);axis=Q.from_quat(tf[th,3:7]).inv().apply(tf[tk,:3]-tf[th,:3]);axis/=np.linalg.norm(axis)
 settings[side]={'pelvis_offset_inverse_quat':pelvis_offset.inv().as_quat().tolist(),'thigh_offset_quat':thigh_offset.as_quat().tolist(),'neutral_local_inverse_quat':local.inv().as_quat().tolist(),'thigh_axis_local':axis.tolist(),'roll_offset_quat':(Q.from_quat(tf[th,3:7]).inv()*Q.from_quat(tf[tr,3:7])).as_quat().tolist()}
for path in sorted(W.glob('*-inward0.json')):
 j=json.loads(path.read_text(encoding='utf-8'));s,t=j['source'],j['target'];sf,tf=np.array(s['frames']),np.array(t['frames']);si={n:i for i,n in enumerate(s['bones'])};ti={n:i for i,n in enumerate(t['bones'])};row={'clip':j['name'],'sides':{}}
 for side in ['L','R']:
  p=settings[side];sp,sh=si['pelvis'],si['thigh_'+side.lower()];tp,th,tk,foot=[ti[n] for n in ['SKEL_Pelvis','SKEL_'+side+'_Thigh','SKEL_'+side+'_Calf','SKEL_'+side+'_Foot']]
  predicted=Q.from_quat(p['pelvis_offset_inverse_quat'])*Q.from_quat(sf[:,sp,3:7]).inv()*Q.from_quat(sf[:,sh,3:7])*Q.from_quat(p['thigh_offset_quat']);actual=Q.from_quat(tf[:,tp,3:7]).inv()*Q.from_quat(tf[:,th,3:7]);error=(predicted.inv()*actual).magnitude();max_error=max(max_error,float(error.max()*180/np.pi))
  delta=Q.from_quat(p['neutral_local_inverse_quat'])*predicted;q=delta.as_quat();angle=2*np.arctan2(q[:,:3]@p['thigh_axis_local'],q[:,3]);angle=(angle+np.pi)%(2*np.pi)-np.pi;correction=np.clip(-.75*angle,np.radians(-30),np.radians(30));changed=predicted*Q.from_rotvec(correction[:,None]*p['thigh_axis_local']);world=Q.from_quat(tf[:,tp,3:7])*changed;global_change=world*Q.from_quat(tf[:,th,3:7]).inv()
  knee=tf[:,th,:3]+global_change.apply(tf[:,tk,:3]-tf[:,th,:3]);end=tf[:,th,:3]+global_change.apply(tf[:,foot,:3]-tf[:,th,:3]);shift=end-tf[:,foot,:3];ball=sf[:,si['ball_'+side.lower()],2];low=ball<ball.min()+3
  assert np.linalg.norm(knee-tf[:,tk,:3],axis=1).max()<.001
  row['sides'][side]={'hip_twist_degrees_min_mean_max':np.degrees([angle.min(),angle.mean(),angle.max()]).tolist(),'correction_degrees_min_max':np.degrees([correction.min(),correction.max()]).tolist(),'ankle_shift_cm_mean_max':[float(np.linalg.norm(shift,axis=1).mean()),float(np.linalg.norm(shift,axis=1).max())],'near_ground_ankle_z_shift_cm_min_max':[float(shift[low,2].min()),float(shift[low,2].max())]}
 rows.append(row)
assert max_error<.001,max_error
settings['keep_twist_fraction']=.25;settings['max_correction_degrees']=30
(O/'hip-twist-settings.json').write_text(json.dumps(settings,indent=2),encoding='utf-8');(O/'hip-twist-candidate.json').write_text(json.dumps({'offline_only':True,'target_hip_reconstruction_error_deg_max':max_error,'clips':rows},indent=2),encoding='utf-8')
print('HIP_RECONSTRUCTION_MAX_ERROR_DEG',max_error)
for row in rows:print(row['clip'],row['sides'])
