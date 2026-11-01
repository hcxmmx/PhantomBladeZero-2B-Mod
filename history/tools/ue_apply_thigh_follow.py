"""Promote the previewed two-bone correction to the runtime retargeter only."""
import unreal as u,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];dest='/Game/Hcx2B';rtg=u.load_asset(dest+'/RTG_2B_Adult');assert rtg
c=u.IKRetargeterController.get_controller(rtg);assert c.get_num_retarget_ops()==2,'Expected unchanged 0.2.1 runtime retargeter'
i=c.add_retarget_op('/Script/IKRig.IKRetargetPinBoneOp');assert i==2
op=c.get_op_controller(i);settings=op.get_settings()
for name,value in [('skeleton_to_copy_from',u.RetargetSourceOrTarget.TARGET),('copy_translation',False),('copy_scale',False),('copy_rotation',True),('rotation_mode',u.PinBoneRotationMode.MAINTAIN_OFFSET_FROM_BONE_TO_COPY_FROM)]:settings.set_editor_property(name,value)
op.set_settings(settings)
for s in ['L','R']:op.set_bone_pair('SKEL_'+s+'_Thigh','RB_'+s+'_ThighRoll')
reference=u.IKRetargeterController.get_controller(u.load_asset(dest+'/Diagnostics/RTG_2B_ThighFollow')).get_op_controller(2)
for name in ['skeleton_to_copy_from','copy_translation','copy_rotation','copy_scale','rotation_mode','translation_mode','propagate_to_children','global_offset','local_offset']:
 assert op.get_settings().get_editor_property(name)==reference.get_settings().get_editor_property(name),name
assert op.get_all_bone_pairs()==reference.get_all_bone_pairs()
u.EditorAssetLibrary.save_loaded_asset(rtg,only_if_is_dirty=False)
# Compare all three real clips to the exact preview output before cooking.
source=u.load_asset(dest+'/SK_SourceHun');target=u.load_asset(dest+'/SK_2B');out=R/'work/retarget-0.2.2-motion';out.mkdir(exist_ok=True)
for path in sorted((R/'work/animation-preview/extract').glob('*-samples.json')):
 name=path.name.removesuffix('-samples.json');result=out/(name+'.json')
 assert u.HcxRetargetTools.bake_diagnostic_animation(source,target,rtg,str(path),dest+'/Diagnostics/Runtime022',str(result))
 expected=json.loads((R/'output/animation-preview'/(name+'-thigh-follow.json')).read_text());actual=json.loads(result.read_text())
 assert actual==expected,name+' differs from preview'
u.log('HCX_RUNTIME_022_MATCHES_PREVIEW_ALL_3_CLIPS')
