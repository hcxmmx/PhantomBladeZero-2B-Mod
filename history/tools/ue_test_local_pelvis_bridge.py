"""Fix rotation transfer for opposite pelvis/spine bone bases using a local offset."""
import unreal as u,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[2];D='/Game/Hcx2B/Diagnostics';O=R/'work/pose-diagnosis';tools=u.AssetToolsHelpers.get_asset_tools()
base=u.load_asset(D+'/RTG_2B_KneeNeutral');assert base
variant=u.load_asset(D+'/RTG_2B_LocalBridge') or tools.duplicate_asset('RTG_2B_LocalBridge',D,base);c=u.IKRetargeterController.get_controller(variant)
j=json.loads((R/'output/scale-study/115/motion/Pelvis_Yaw-scaled115.json').read_text());b=j['target'];ix={n:i for i,n in enumerate(b['bones'])};frame=b['frames'][0]
qfrom=frame[ix['SKEL_Pelvis']][3:7];qto=frame[ix['SKEL_Spine_Root']][3:7]
x,y,z,w=[-qfrom[0],-qfrom[1],-qfrom[2],qfrom[3]];X,Y,Z,W=qto
values=[w*X+x*W+y*Z-z*Y,w*Y-x*Z+y*W+z*X,w*Z+x*Y-y*X+z*W,w*W-x*X-y*Y-z*Z];length=math.sqrt(sum(v*v for v in values));offset=u.Quat(*[v/length for v in values])
op=c.get_op_controller(1);settings=op.get_settings();local=u.Transform();local.rotation=offset
settings.set_editor_property('rotation_mode',u.PinBoneRotationMode.COPY_GLOBAL_ROTATION);settings.set_editor_property('local_offset',local);op.set_settings(settings)
u.EditorAssetLibrary.save_loaded_asset(variant,only_if_is_dirty=False)
(O/'local-bridge-settings.json').write_text(json.dumps({'rotation_mode':'CopyGlobalRotation','local_offset_xyzw':[offset.x,offset.y,offset.z,offset.w],'derivation':'inverse(pelvis retarget reference rotation) * spine-root retarget reference rotation'},indent=2),encoding='utf-8')
source=u.load_asset('/Game/Hcx2B/SK_SourceHun');target=u.load_asset('/Game/Hcx2B/SK_2B')
paths=list((R/'work/animation-preview/extract').glob('*-samples.json'))+list((O/'extract').glob('*-samples.json'))+list((R/'work/pelvis-diagnosis').glob('*-samples.json'))
for path in sorted(paths):
 name=path.name.removesuffix('-samples.json')
 assert u.HcxRetargetTools.bake_diagnostic_animation(source,target,variant,str(path),D+'/PoseTests/local-bridge',str(O/(name+'-local-bridge.json')))
u.log('HCX_LOCAL_PELVIS_BRIDGE_TEST_READY')
