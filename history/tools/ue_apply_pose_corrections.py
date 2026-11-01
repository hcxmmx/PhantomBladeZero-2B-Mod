import unreal as u,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];D='/Game/Hcx2B';O=R/'work/pose-diagnosis';reference=u.IKRetargeterController.get_controller(u.load_asset(D+'/Diagnostics/RTG_2B_LocalBridge'))
rtg=u.load_asset(D+'/RTG_2B_Adult');c=u.IKRetargeterController.get_controller(rtg);assert c.get_num_retarget_ops()==4
c.get_op_controller(1).set_settings(reference.get_op_controller(1).get_settings())
for side in ['L','R']:
 for part in ['Calf','Foot']:
  bone='SKEL_'+side+'_'+part;c.set_rotation_offset_for_retarget_pose_bone(bone,reference.get_rotation_offset_for_retarget_pose_bone(bone,u.RetargetSourceOrTarget.TARGET),u.RetargetSourceOrTarget.TARGET)
source=u.load_asset(D+'/SK_SourceHun');target=u.load_asset(D+'/SK_2B')
paths=list((R/'work/animation-preview/extract').glob('*-samples.json'))+list((O/'extract').glob('*-samples.json'))+list((R/'work/pelvis-diagnosis').glob('*-samples.json'));names=[]
for path in sorted(paths):
 name=path.name.removesuffix('-samples.json');output=O/(name+'-runtime025.json')
 assert u.HcxRetargetTools.bake_diagnostic_animation(source,target,rtg,str(path),D+'/Diagnostics/Runtime025',str(output))
 assert json.loads(output.read_text())==json.loads((O/(name+'-local-bridge.json')).read_text()),name
 names.append(name)
assert len(names)==11
u.EditorAssetLibrary.save_loaded_asset(rtg,only_if_is_dirty=False)
(O/'runtime-025-verification.json').write_text(json.dumps({'passed':True,'all_samples_match_diagnostic':True,'clips':names},indent=2),encoding='utf-8')
u.log('HCX_RUNTIME_025_MATCHES_ALL_11_TESTS')
