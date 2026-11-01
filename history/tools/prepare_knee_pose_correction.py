"""Calibrate knee neutral bend to the source anatomical reference, compensating foot rotation."""
from pathlib import Path
import json,math,numpy as np
R=Path(__file__).resolve().parents[1];j=json.loads((R/'output/scale-study/115/motion/Pelvis_Z-scaled115.json').read_text());props=json.loads((R/'work/retarget-readback-0.2.4/RTG_2B_Adult.json').read_text())[0]['Properties'];offsets={r['Key']:np.array([r['Value'][k] for k in 'XYZW']) for r in props['TargetRetargetPoses'][0]['Value']['BoneRotationOffsets']}
def mul(a,b):
 x,y,z,w=a;X,Y,Z,W=b;return np.array([w*X+x*W+y*Z-z*Y,w*Y-x*Z+y*W+z*X,w*Z+x*Y-y*X+z*W,w*W-x*X-y*Y-z*Z])
def inv(q):return np.array([-q[0],-q[1],-q[2],q[3]])/np.dot(q,q)
def rotate(q,v):return mul(mul(q,[*v,0]),inv(q))[:3]
def knee(a,b,c):
 u=b-a;v=c-b;angle=math.acos(np.clip(np.dot(u,v)/np.linalg.norm(u)/np.linalg.norm(v),-1,1));axis=np.cross(u,v);axis/=np.linalg.norm(axis);return angle,axis
corrections=[]
for side in ['L','R']:
 s=j['source'];t=j['target'];si={n:i for i,n in enumerate(s['bones'])};ti={n:i for i,n in enumerate(t['bones'])};sf=s['frames'][0];tf=t['frames'][0]
 wanted,_=knee(*[np.array(sf[si[n+'_'+side.lower()]][:3]) for n in ['thigh','calf','foot']]);actual,axis=knee(*[np.array(tf[ti['SKEL_'+side+'_'+n]][:3]) for n in ['Thigh','Calf','Foot']])
 delta=wanted-actual;calf='SKEL_'+side+'_Calf';foot='SKEL_'+side+'_Foot';q=np.array(tf[ti[calf]][3:7]);local_axis=rotate(inv(q),axis);local_delta=np.r_[local_axis*math.sin(delta/2),math.cos(delta/2)]
 old=offsets.get(calf,np.array([0.,0.,0.,1.]));new=mul(old,local_delta);new/=np.linalg.norm(new)
 # The calf edit would pitch the foot. Cancel that edit in the child's local frame.
 global_delta=np.r_[axis*math.sin(delta/2),math.cos(delta/2)];qfoot=np.array(tf[ti[foot]][3:7]);foot_cancel=mul(mul(inv(qfoot),inv(global_delta)),qfoot);foot_new=mul(offsets.get(foot,np.array([0.,0.,0.,1.])),foot_cancel);foot_new/=np.linalg.norm(foot_new)
 corrections.append({'side':side,'source_reference_bend_deg':math.degrees(wanted),'prior_reference_bend_deg':math.degrees(actual),'bend_correction_deg':math.degrees(delta),'calf':calf,'calf_offset_xyzw':new.tolist(),'foot':foot,'foot_offset_xyzw':foot_new.tolist()})
out=R/'work/pose-diagnosis/knee-neutral-correction.json';out.write_text(json.dumps(corrections,indent=2),encoding='utf-8');print(json.dumps(corrections,indent=2))
