"""Activate movement-only knee hinge reconstruction, without separate shoe leveling."""
import unreal as u,json,math,shutil,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[2];P=R/'work/ue-retarget/ProjectPBZ';D='/Game/Hcx2B';tools=u.AssetToolsHelpers.get_asset_tools();version='0.2.10'
backup=R/'work/diagnostics'/('before-'+version+'-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
bandfile=P/'Plugins/HuaShira/Content/Characters/Hero/Hero_Hun/SkinParts/Hun_Hair_Band.uasset';shutil.copy2(bandfile,backup/bandfile.name)
report=R/'output/2B-retarget/blueprint-setup.json';shutil.copy2(report,backup/report.name)
settings=json.loads((R/'output/gait-study/knee-hinge-settings.json').read_text(encoding='utf-8'))
bp=u.load_asset(D+'/ABPT_2B_Hinge')
if not bp:
 bp=tools.duplicate_asset('ABPT_2B_Hinge',D,u.load_asset(D+'/ABPT_2B_Gait'));assert bp
 result=u.HcxRetargetTools.build_hinge_graph(bp,json.dumps(settings));assert result=='OK',result
 u.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
child=u.load_asset(D+'/ABP_2B_Hinge')
if not child:
 factory=u.AnimBlueprintFactory();factory.set_editor_property('parent_class',u.EditorAssetLibrary.load_blueprint_class(D+'/ABPT_2B_Hinge'));factory.set_editor_property('target_skeleton',u.load_asset(D+'/SK_2B_Skeleton'));child=tools.create_asset('ABP_2B_Hinge',D,u.AnimBlueprint,factory);assert child
u.BlueprintEditorLibrary.compile_blueprint(child);u.EditorAssetLibrary.save_loaded_asset(child,only_if_is_dirty=False)
source=u.load_asset(D+'/SK_SourceHun');target=u.load_asset(D+'/SK_2B');base=u.load_asset(D+'/RTG_2B_Adult');sample=R/'work/gait-study/extract/Hun_DoubleBlade_Run_Fwd_Loop-samples.json'
assert u.HcxRetargetTools.bake_diagnostic_animation(source,target,base,str(sample),D+'/Diagnostics/HingeGate',str(R/'work/gait-study/hinge-gate-source.json'))
seq=u.load_asset(D+'/Diagnostics/HingeGate/A_Hun_DoubleBlade_Run_Fwd_Loop_Soul');assert seq
check=json.loads(u.HcxRetargetTools.check_gait_gate(child,source,target,seq))
(R/'output/gait-study/hinge-runtime-verification.json').write_text(json.dumps(check,indent=2),encoding='utf-8')
def multiply(a,b):
 x,y,z,w=a;X,Y,Z,W=b
 return [w*X+x*W+y*Z-z*Y,w*Y-x*Z+y*W+z*X,w*Z+x*Y-y*X+z*W,w*W-x*X-y*Y-z*Z]
for row in check['final_graph_knees']:
 p=settings[row['side']];angle=math.radians(row['source_knee_angle_degrees'])/2
 delta=[x*math.sin(angle) for x in p['target_hinge_axis']]+[math.cos(angle)];wanted=multiply(p['target_neutral_quat'],delta);actual=row['local_quat'];dot=abs(sum(x*y for x,y in zip(wanted,actual)))/math.sqrt(sum(x*x for x in wanted)*sum(x*x for x in actual));error=math.degrees(2*math.acos(min(1,dot)));row['reconstructed_rotation_error_deg']=error
 assert error<.1,row
 assert row['knee_position_delta_cm']<.001,row
 assert row['hinge_weight']>.99,row
for row in check['cases']:
 if row['state']!='moving_ground':assert row['hinge_weight']==0,row
assert max(row['rotation_delta_degrees'] for row in check['final_graph_foot_changes'])>1,check
(R/'output/gait-study/hinge-runtime-verification.json').write_text(json.dumps(check,indent=2),encoding='utf-8')
mesh=u.load_asset('/HuaShira/Characters/Hero/Hero_Hun/SkinParts/Hun_Hair_Band');cls=u.EditorAssetLibrary.load_blueprint_class(D+'/ABP_2B_Hinge');mesh.set_editor_property('post_process_anim_blueprint',cls);u.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
setup=json.loads(report.read_text(encoding='utf-8'));setup.update(template=bp.get_path_name(),blueprint=child.get_path_name(),post_process_class=cls.get_path_name());report.write_text(json.dumps(setup,indent=2),encoding='utf-8')
u.log('HCX_KNEE_HINGE_READY '+json.dumps(check))
