"""Isolated FK leg correspondence experiment; runtime retargeter stays unchanged."""
import unreal as u
from pathlib import Path
R=Path(__file__).resolve().parents[2];D='/Game/Hcx2B/Diagnostics';O=R/'work/pose-diagnosis';O.mkdir(exist_ok=True)
tools=u.AssetToolsHelpers.get_asset_tools();original=u.load_asset('/Game/Hcx2B/RTG_2B_Adult');assert original
variant=u.load_asset(D+'/RTG_2B_LegOneToOne') or tools.duplicate_asset('RTG_2B_LegOneToOne',D,original)
c=u.IKRetargeterController.get_controller(variant);op=c.get_op_controller(2);settings=op.get_settings();chains=list(settings.get_editor_property('chains_to_retarget'))
for i,row in enumerate(chains):
 if str(row.target_chain_name) in ['Leg_l','Leg_r']:row.rotation_mode=u.FKChainRotationMode.ONE_TO_ONE;chains[i]=row
settings.set_editor_property('chains_to_retarget',chains);op.set_settings(settings);u.EditorAssetLibrary.save_loaded_asset(variant,only_if_is_dirty=False)
source=u.load_asset('/Game/Hcx2B/SK_SourceHun');target=u.load_asset('/Game/Hcx2B/SK_2B')
paths=list((R/'work/animation-preview/extract').glob('*-samples.json'))+list((O/'extract').glob('*-samples.json'))
for path in sorted(paths):
 name=path.name.removesuffix('-samples.json')
 for label,rtg in [('baseline',original),('leg-one-to-one',variant)]:
  assert u.HcxRetargetTools.bake_diagnostic_animation(source,target,rtg,str(path),D+'/PoseTests/'+label,str(O/(name+'-'+label+'.json')))
u.log('HCX_JOINT_CORRESPONDENCE_TEST_READY')
