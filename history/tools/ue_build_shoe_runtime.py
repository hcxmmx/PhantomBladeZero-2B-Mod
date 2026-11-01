"""Build the movement-gated shoe test and activate it for game cooking."""
import unreal as u,json,shutil,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[2];P=R/'work/ue-retarget/ProjectPBZ';D='/Game/Hcx2B';tools=u.AssetToolsHelpers.get_asset_tools()
strong='-HcxStrong' in u.SystemLibrary.get_command_line();version='0.2.9' if strong else '0.2.8';suffix='ShoeStrong' if strong else 'Shoe';max_angle=18 if strong else 6
backup=R/'work/diagnostics'/('before-'+version+'-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
bandfile=P/'Plugins/HuaShira/Content/Characters/Hero/Hero_Hun/SkinParts/Hun_Hair_Band.uasset';shutil.copy2(bandfile,backup/bandfile.name)
report=R/'output/2B-retarget/blueprint-setup.json';shutil.copy2(report,backup/report.name)
assert not u.load_asset(D+'/ABPT_2B_'+suffix),'Use a clean template when rebuilding the append-only shoe graph'
bp=tools.duplicate_asset('ABPT_2B_'+suffix,D,u.load_asset(D+'/ABPT_2B_Gait'));assert bp
settings=json.loads((R/'output/gait-study/shoe-runtime-settings.json').read_text(encoding='utf-8'))
if strong:settings.update(max_correction_degrees=18,correction_gain=1.0,near_full_cm=12,near_fade_cm=28,interp_speed=20)
(R/'output/gait-study'/('shoe-settings-'+version+'.json')).write_text(json.dumps(settings,indent=2),encoding='utf-8')
result=u.HcxRetargetTools.build_shoe_graph(bp,json.dumps(settings));assert result=='OK',result
u.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
factory=u.AnimBlueprintFactory();factory.set_editor_property('parent_class',u.EditorAssetLibrary.load_blueprint_class(D+'/ABPT_2B_'+suffix));factory.set_editor_property('target_skeleton',u.load_asset(D+'/SK_2B_Skeleton'))
child=tools.create_asset('ABP_2B_'+suffix,D,u.AnimBlueprint,factory);assert child
u.BlueprintEditorLibrary.compile_blueprint(child);u.EditorAssetLibrary.save_loaded_asset(child,only_if_is_dirty=False)
# Focused state-gate exercise before saving the display reference.
source=u.load_asset(D+'/SK_SourceHun');target=u.load_asset(D+'/SK_2B');base=u.load_asset(D+'/RTG_2B_Adult');sample=R/'work/gait-study/extract/Hun_DoubleBlade_Run_Fwd_Loop-samples.json'
assert u.HcxRetargetTools.bake_diagnostic_animation(source,target,base,str(sample),D+'/Diagnostics/ShoeGate',str(R/'work/gait-study/shoe-gate-source.json'))
seq=u.load_asset(D+'/Diagnostics/ShoeGate/A_Hun_DoubleBlade_Run_Fwd_Loop_Soul');assert seq
check=json.loads(u.HcxRetargetTools.check_gait_gate(child,source,target,seq));(R/'output/gait-study'/('shoe-gate-'+version+'.json')).write_text(json.dumps(check,indent=2),encoding='utf-8')
for case in check['cases']:
 for key in ['left_shoe_roll','right_shoe_roll']:assert abs(case[key])<=max_angle+.0001,case
 if case['state']!='moving_ground':assert case['left_shoe_roll']==case['right_shoe_roll']==0,case
moving=check['cases'][0];assert max(abs(moving['left_shoe_roll']),abs(moving['right_shoe_roll']))>.01,check
if strong:
 assert max(x['rotation_delta_degrees'] for x in check['final_graph_foot_changes'])>1,check
 for foot in check['final_graph_foot_changes']:
  assert foot['position_delta_cm']<.001,foot
  assert abs(foot['rotation_delta_degrees']-abs(foot['evaluated_roll_input']))<.1,foot
mesh=u.load_asset('/HuaShira/Characters/Hero/Hero_Hun/SkinParts/Hun_Hair_Band');cls=u.EditorAssetLibrary.load_blueprint_class(D+'/ABP_2B_'+suffix);mesh.set_editor_property('post_process_anim_blueprint',cls);u.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
setup=json.loads(report.read_text(encoding='utf-8'));setup.update(template=bp.get_path_name(),blueprint=child.get_path_name(),post_process_class=cls.get_path_name());report.write_text(json.dumps(setup,indent=2),encoding='utf-8')
u.log('HCX_SHOE_RUNTIME_READY '+json.dumps(check))
