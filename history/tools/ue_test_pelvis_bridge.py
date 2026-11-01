"""Test the GTA sibling pelvis/spine roots without touching the installed mod."""
import unreal as u,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];D='/Game/Hcx2B/Diagnostics';O=R/'work/pelvis-diagnosis';tools=u.AssetToolsHelpers.get_asset_tools()
original=u.load_asset('/Game/Hcx2B/RTG_2B_Adult');assert original
rig=u.load_asset(D+'/RTG_2B_PelvisBridge') or tools.duplicate_asset('RTG_2B_PelvisBridge',D,original)
c=u.IKRetargeterController.get_controller(rig)
assert c.get_num_retarget_ops()==3
i=c.add_retarget_op('/Script/IKRig.IKRetargetPinBoneOp');op=c.get_op_controller(i);s=op.get_settings()
for name,value in [('skeleton_to_copy_from',u.RetargetSourceOrTarget.TARGET),('copy_translation',True),('copy_rotation',True),('copy_scale',False),('propagate_to_children',True),('translation_mode',u.PinBoneTranslationMode.COPY_GLOBAL_POSITION_AND_MAINTAIN_OFFSET),('rotation_mode',u.PinBoneRotationMode.MAINTAIN_OFFSET_FROM_BONE_TO_COPY_FROM)]:s.set_editor_property(name,value)
op.set_settings(s);op.set_bone_pair('SKEL_Pelvis','SKEL_Spine_Root');c.set_op_name('Bridge Pelvis to Spine Root',i);assert c.move_retarget_op_in_stack(i,1)
assert str(c.get_op_name(1))=='Bridge Pelvis to Spine Root'
u.EditorAssetLibrary.save_loaded_asset(rig,only_if_is_dirty=False)
source=u.load_asset('/Game/Hcx2B/SK_SourceHun');target=u.load_asset('/Game/Hcx2B/SK_2B')
for label,rtg in [('baseline',original),('bridge',rig)]:
 for path in sorted(O.glob('*-samples.json')):
  name=path.name.removesuffix('-samples.json')
  assert u.HcxRetargetTools.bake_diagnostic_animation(source,target,rtg,str(path),D+'/PelvisTests/'+label,str(O/(name+'-'+label+'.json')))
u.log('HCX_PELVIS_BRIDGE_STRESS_TEST_READY')
