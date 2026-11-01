import unreal as u,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];D='/Game/Hcx2B/Diagnostics';O=R/'work/pose-diagnosis';tools=u.AssetToolsHelpers.get_asset_tools();original=u.load_asset('/Game/Hcx2B/RTG_2B_Adult')
variant=u.load_asset(D+'/RTG_2B_KneeNeutral') or tools.duplicate_asset('RTG_2B_KneeNeutral',D,original);c=u.IKRetargeterController.get_controller(variant)
for row in json.loads((O/'knee-neutral-correction.json').read_text()):
 for name,key in [(row['calf'],'calf_offset_xyzw'),(row['foot'],'foot_offset_xyzw')]:c.set_rotation_offset_for_retarget_pose_bone(name,u.Quat(*row[key]),u.RetargetSourceOrTarget.TARGET)
u.EditorAssetLibrary.save_loaded_asset(variant,only_if_is_dirty=False)
source=u.load_asset('/Game/Hcx2B/SK_SourceHun');target=u.load_asset('/Game/Hcx2B/SK_2B')
paths=list((R/'work/animation-preview/extract').glob('*-samples.json'))+list((O/'extract').glob('*-samples.json'))+list((R/'work/pelvis-diagnosis').glob('*-samples.json'))
for path in sorted(paths):
 name=path.name.removesuffix('-samples.json')
 for label,rtg in [('baseline',original),('knee-neutral',variant)]:
  if label=='baseline' and (O/(name+'-baseline.json')).exists():continue
  assert u.HcxRetargetTools.bake_diagnostic_animation(source,target,rtg,str(path),D+'/PoseTests/'+label,str(O/(name+'-'+label+'.json')))
u.log('HCX_KNEE_NEUTRAL_TEST_READY')
