"""Deployable clean hip-only candidate: original retarget plus reduced axial thigh twist."""
import unreal as u,json,math,shutil,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[2];P=R/'work/ue-retarget/ProjectPBZ';D='/Game/Hcx2B';tools=u.AssetToolsHelpers.get_asset_tools();version='0.2.11'
backup=R/'work/diagnostics'/('before-'+version+'-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
bandfile=P/'Plugins/HuaShira/Content/Characters/Hero/Hero_Hun/SkinParts/Hun_Hair_Band.uasset';shutil.copy2(bandfile,backup/bandfile.name)
report=R/'output/2B-retarget/blueprint-setup.json';shutil.copy2(report,backup/report.name)
settings=json.loads((R/'output/gait-study/hip-twist-settings.json').read_text(encoding='utf-8'));base=u.load_asset(D+'/RTG_2B_Adult')
bp=u.load_asset(D+'/ABPT_2B_Hip')
if not bp:
 bp=tools.duplicate_asset('ABPT_2B_Hip',D,u.load_asset(D+'/ABPT_2B_Adult'));assert bp
 # Reuse the established state gate, but all three inputs use the same original RTG.
 # Therefore the old inward-pole candidate does not affect this version.
 assert u.HcxRetargetTools.build_gait_graph(bp,base,base,base)=='OK'
 result=u.HcxRetargetTools.build_hip_graph(bp,json.dumps(settings));assert result=='OK',result
 u.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
child=u.load_asset(D+'/ABP_2B_Hip')
if not child:
 factory=u.AnimBlueprintFactory();factory.set_editor_property('parent_class',u.EditorAssetLibrary.load_blueprint_class(D+'/ABPT_2B_Hip'));factory.set_editor_property('target_skeleton',u.load_asset(D+'/SK_2B_Skeleton'));child=tools.create_asset('ABP_2B_Hip',D,u.AnimBlueprint,factory);assert child
u.BlueprintEditorLibrary.compile_blueprint(child);u.EditorAssetLibrary.save_loaded_asset(child,only_if_is_dirty=False)
source=u.load_asset(D+'/SK_SourceHun');target=u.load_asset(D+'/SK_2B');sample=R/'work/gait-study/extract/Hun_DoubleBlade_Sprint_Loop-samples.json'
assert u.HcxRetargetTools.bake_diagnostic_animation(source,target,base,str(sample),D+'/Diagnostics/HipGate',str(R/'work/gait-study/hip-gate-source.json'))
seq=u.load_asset(D+'/Diagnostics/HipGate/A_Hun_DoubleBlade_Sprint_Loop_Soul');assert seq
check=json.loads(u.HcxRetargetTools.check_gait_gate(child,source,target,seq));out=R/'output/gait-study/hip-runtime-verification.json';out.write_text(json.dumps(check,indent=2),encoding='utf-8')
for case in check['cases']:
 assert 0<=case['hip_weight']<=1,case
 if case['state']!='moving_ground':assert case['hip_weight']==0,case
for hip in check['final_graph_hips']:
 assert abs(hip['correction_degrees'])<=30.0001,hip
 assert hip['hip_position_delta_cm']<.001,hip
 assert hip['desired_rotation_error_degrees']<.1,hip
 a,b=hip['roll_offset_quat'],settings[hip['side']]['roll_offset_quat'];dot=abs(sum(x*y for x,y in zip(a,b)))/math.sqrt(sum(x*x for x in a)*sum(x*x for x in b));hip['roll_follow_error_degrees']=math.degrees(2*math.acos(min(1,dot)));assert hip['roll_follow_error_degrees']<.1,hip
assert len(check['final_graph_hips'])==2,check
assert max(abs(h['correction_degrees']) for h in check['final_graph_hips'])>3,check
for knee in check['final_graph_knees']:assert knee['knee_position_delta_cm']<.001,knee
out.write_text(json.dumps(check,indent=2),encoding='utf-8')
mesh=u.load_asset('/HuaShira/Characters/Hero/Hero_Hun/SkinParts/Hun_Hair_Band');cls=u.EditorAssetLibrary.load_blueprint_class(D+'/ABP_2B_Hip');mesh.set_editor_property('post_process_anim_blueprint',cls);u.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
setup=json.loads(report.read_text(encoding='utf-8'));setup.update(template=bp.get_path_name(),blueprint=child.get_path_name(),post_process_class=cls.get_path_name());report.write_text(json.dumps(setup,indent=2),encoding='utf-8')
u.log('HCX_HIP_RUNTIME_READY '+json.dumps(check))
