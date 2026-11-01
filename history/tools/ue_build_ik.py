import unreal as u,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];dest='/Game/Hcx2B';tools=u.AssetToolsHelpers.get_asset_tools()
source=u.load_asset(dest+'/SK_SourceHun');target=u.load_asset(dest+'/SK_2B');assert source and target
# Source rig must use the exact game reference pose, independent of FBX axes.
ref=json.loads((R/'work/pbz/Hun_Body_Simple-reference.json').read_text());poses={b['Name'].lower():p for b,p in zip(ref['FinalRefBoneInfo'],ref['FinalRefBonePose'])}
mod=u.SkeletonModifier();assert mod.set_skeletal_mesh(source);names=list(mod.get_all_bone_names());trans=[]
for n in names:
 p=poses[str(n).lower()];q=p['Rotation'];t=u.Transform();t.translation=u.Vector(*[p['Translation'][k] for k in 'XYZ']);t.rotation=u.Quat(*[q[k] for k in 'XYZW']);t.scale3d=u.Vector(1,1,1);trans.append(t)
assert mod.set_bones_transforms(names,trans,True);assert mod.commit_skeleton_to_skeletal_mesh()
def asset(n,cls,factory):return u.load_asset(dest+'/'+n) or tools.create_asset(n,dest,cls,factory())
chains=[('Spine','spine_01','spine_05','SKEL_Spine0','SKEL_Spine3'),('Neck','neck_01','neck_02','SKEL_Neck_1','SKEL_Neck_1'),('Head','Head','Head','SKEL_Head','SKEL_Head')]
for s in ['l','r']:
 S=s.upper()
 for chain,a,b,c,d in [('Clavicle','clavicle','clavicle','Clavicle','Clavicle'),('Arm','upperarm','hand','UpperArm','Hand'),('Leg','thigh','foot','Thigh','Foot'),('Toe','ball','ball','Toe0','Toe0')]:chains.append((chain+'_'+s,a+'_'+s,b+'_'+s,'SKEL_'+S+'_'+c,'SKEL_'+S+'_'+d))
 for f,word in enumerate(['thumb','index','middle','ring','pinky']):chains.append((word+'_'+s,word+'_01_'+s,word+'_03_'+s,'SKEL_'+S+'_Finger'+str(f)+'0','SKEL_'+S+'_Finger'+str(f)+'2'))
rigs=[];report={'chains':[c[0] for c in chains],'positions':{}}
for label,mesh,root,columns in [('Source',source,'pelvis',(1,2)),('2B',target,'SKEL_Pelvis',(3,4))]:
 rig=asset('IK_'+label,u.IKRigDefinition,u.IKRigDefinitionFactory);c=u.IKRigController.get_controller(rig);assert c.set_skeletal_mesh(mesh);assert c.set_retarget_root(root)
 for old in list(c.get_retarget_chains()):c.remove_retarget_chain(old.chain_name)
 for row in chains:c.add_retarget_chain(row[0],row[columns[0]],row[columns[1]],'None')
 report['positions'][label]={str(n):str(c.get_ref_pose_transform_of_bone(n)) for n in [root,chains[2][columns[0]],chains[5][columns[1]]]};rigs.append(rig)
rtg=asset('RTG_2B_Adult',u.IKRetargeter,u.IKRetargetFactory);c=u.IKRetargeterController.get_controller(rtg);c.set_ik_rig(u.RetargetSourceOrTarget.SOURCE,rigs[0]);c.set_ik_rig(u.RetargetSourceOrTarget.TARGET,rigs[1]);c.remove_all_ops()
for typename in ['IKRetargetPelvisMotionOp','IKRetargetFKChainsOp']:
 index=c.add_retarget_op('/Script/IKRig.'+typename);assert index>=0,typename;c.run_op_initial_setup(index)
for row in chains:assert c.set_source_chain(row[0],row[0]),row[0]
c.auto_align_all_bones(u.RetargetSourceOrTarget.TARGET)
report['ops']=[str(c.get_op_name(i)) for i in range(c.get_num_retarget_ops())];report['retargeter']=rtg.get_path_name()
u.EditorAssetLibrary.save_directory(dest,only_if_is_dirty=False)
(R/'output/2B-retarget/ik-setup.json').write_text(json.dumps(report,indent=2))
u.log('HCX_IK_READY '+str(len(chains))+' chains; '+str(report['ops']))
