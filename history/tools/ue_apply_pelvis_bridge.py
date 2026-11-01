"""Promote the tested bridge and compare all output to the diagnostic rig."""
import unreal as u,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];D='/Game/Hcx2B';out=R/'work/pelvis-diagnosis'
rtg=u.load_asset(D+'/RTG_2B_Adult');c=u.IKRetargeterController.get_controller(rtg);assert c.get_num_retarget_ops()==3
test=u.load_asset(D+'/Diagnostics/RTG_2B_PelvisBridge');reference=u.IKRetargeterController.get_controller(test).get_op_controller(1)
i=c.add_retarget_op('/Script/IKRig.IKRetargetPinBoneOp');op=c.get_op_controller(i);op.set_settings(reference.get_settings())
op.set_bone_pair('SKEL_Pelvis','SKEL_Spine_Root')
assert op.get_all_bone_pairs()==reference.get_all_bone_pairs()
c.set_op_name('Bridge Pelvis to Spine Root',i);assert c.move_retarget_op_in_stack(i,1)
source=u.load_asset(D+'/SK_SourceHun');target=u.load_asset(D+'/SK_2B')
inputs=list(out.glob('*-samples.json'))+list((R/'work/animation-preview/extract').glob('*-samples.json'));clips=[]
for path in sorted(inputs):
 name=path.name.removesuffix('-samples.json');expected=out/(name+'-bridge.json');actual=out/(name+'-runtime023.json')
 if not expected.exists():assert u.HcxRetargetTools.bake_diagnostic_animation(source,target,test,str(path),D+'/Diagnostics/PelvisTests/bridge',str(expected))
 assert u.HcxRetargetTools.bake_diagnostic_animation(source,target,rtg,str(path),D+'/Diagnostics/Runtime023',str(actual))
 assert json.loads(actual.read_text())==json.loads(expected.read_text()),name+' differs from test'
 clips.append(name)
u.EditorAssetLibrary.save_loaded_asset(rtg,only_if_is_dirty=False)
(out/'runtime-023-verification.json').write_text(json.dumps({'runtime_matches_test_all_samples':True,'clips':clips,'ops':[str(c.get_op_name(i)) for i in range(c.get_num_retarget_ops())]},indent=2),encoding='utf-8')
u.log('HCX_RUNTIME_023_MATCHES_BRIDGE_ALL_6_TESTS')
