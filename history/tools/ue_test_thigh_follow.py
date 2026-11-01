"""Isolated A/B test: standard UE Pin Bones op. No game asset or installed mod changes."""
import unreal as u
from pathlib import Path
R=Path(__file__).resolve().parents[2];D='/Game/Hcx2B/Diagnostics';tools=u.AssetToolsHelpers.get_asset_tools()
rtg=u.load_asset(D+'/RTG_2B_ThighFollow') or tools.duplicate_asset('RTG_2B_ThighFollow',D,u.load_asset('/Game/Hcx2B/RTG_2B_Adult'))
c=u.IKRetargeterController.get_controller(rtg)
while c.get_num_retarget_ops()>2:c.remove_retarget_op(c.get_num_retarget_ops()-1)
i=c.add_retarget_op('/Script/IKRig.IKRetargetPinBoneOp');assert i>=0
op=c.get_op_controller(i);settings=op.get_settings()
settings.set_editor_property('skeleton_to_copy_from',u.RetargetSourceOrTarget.TARGET)
settings.set_editor_property('copy_translation',False)
settings.set_editor_property('copy_scale',False)
settings.set_editor_property('copy_rotation',True)
settings.set_editor_property('rotation_mode',u.PinBoneRotationMode.MAINTAIN_OFFSET_FROM_BONE_TO_COPY_FROM)
op.set_settings(settings)
for s in ['L','R']:op.set_bone_pair('SKEL_'+s+'_Thigh','RB_'+s+'_ThighRoll')
u.EditorAssetLibrary.save_loaded_asset(rtg,only_if_is_dirty=False)
source=u.load_asset('/Game/Hcx2B/SK_SourceHun');target=u.load_asset('/Game/Hcx2B/SK_2B')
for path in sorted((R/'work/animation-preview/extract').glob('*-samples.json')):
 name=path.name.removesuffix('-samples.json')
 assert u.HcxRetargetTools.bake_diagnostic_animation(source,target,rtg,str(path),D+'/ThighFollow',str(R/'output/animation-preview'/(name+'-thigh-follow.json'))),name
 for suffix in ['_Soul','_2B_Baseline']:
  obj=u.load_object(None,D+'/ThighFollow/A_'+name+suffix);u.EditorAssetLibrary.save_loaded_asset(obj,only_if_is_dirty=False)
 u.log('HCX_THIGH_FOLLOW_TEST '+name)
