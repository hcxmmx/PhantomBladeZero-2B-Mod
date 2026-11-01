"""Offline pole-direction candidates. Not installed and not yet movement-state gated."""
import unreal as u
from pathlib import Path
R=Path(__file__).resolve().parents[2];D='/Game/Hcx2B/Diagnostics';O=R/'work/gait-study';tools=u.AssetToolsHelpers.get_asset_tools();original=u.load_asset('/Game/Hcx2B/RTG_2B_Adult')
source=u.load_asset('/Game/Hcx2B/SK_SourceHun');target=u.load_asset('/Game/Hcx2B/SK_2B')
paths=list((O/'extract').glob('*-samples.json'))+[R/'work/animation-preview/extract/Hun_TangBlade_Walk_Fwd_Loop-samples.json',R/'work/pose-diagnosis/extract/Hun_DoubleBlade_Walk_Fwd_Loop-samples.json']
for degrees in [0,10,20]:
 rtg=original
 if degrees:
  name='RTG_2B_GaitInward'+str(degrees);rtg=u.load_asset(D+'/'+name) or tools.duplicate_asset(name,D,original);c=u.IKRetargeterController.get_controller(rtg)
  assert c.get_num_retarget_ops()==4
  i=c.add_retarget_op('/Script/IKRig.IKRetargetAlignPoleVectorOp');c.run_op_initial_setup(i);op=c.get_op_controller(i);settings=op.get_settings();rows=list(settings.get_editor_property('chains_to_align'))
  for index,row in enumerate(rows):
   name=str(row.target_chain_name);row.enabled=name in ['Leg_l','Leg_r'];row.align_alpha=0.;row.static_angular_offset=(-degrees if name=='Leg_l' else degrees if name=='Leg_r' else 0.);rows[index]=row
  settings.set_editor_property('chains_to_align',rows);op.set_settings(settings);assert c.move_retarget_op_in_stack(i,3);u.EditorAssetLibrary.save_loaded_asset(rtg,only_if_is_dirty=False)
 for path in paths:
  name=path.name.removesuffix('-samples.json');assert u.HcxRetargetTools.bake_diagnostic_animation(source,target,rtg,str(path),D+'/GaitTests/inward'+str(degrees),str(O/(name+'-inward'+str(degrees)+'.json')))
u.log('HCX_GAIT_POLE_CANDIDATES_READY')
