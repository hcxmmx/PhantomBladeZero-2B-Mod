"""Movement-scoped 10cm foot offset plus mild inward knee guide. No extra diagnostics."""
import unreal as u,json,datetime,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[2];P=R/'work/ue-retarget/ProjectPBZ';O=R/'output/2B-retarget';D='/Game/Hcx2B'
weapon_panel='-HcxFootPanelWeapon' in u.SystemLibrary.get_command_line();grip_panel=weapon_panel or '-HcxFootPanelGrip' in u.SystemLibrary.get_command_line();idle_defaults=grip_panel or '-HcxFootPanelIdleDefaults' in u.SystemLibrary.get_command_line();idle_panel=idle_defaults or '-HcxFootPanelIdle' in u.SystemLibrary.get_command_line();gait_defaults=idle_panel or '-HcxFootPanelDefaults' in u.SystemLibrary.get_command_line();gait_panel=gait_defaults or '-HcxFootPanelGait' in u.SystemLibrary.get_command_line();panel_direct='-HcxFootPanelDirect' in u.SystemLibrary.get_command_line();panel_status='-HcxFootPanelStatus' in u.SystemLibrary.get_command_line();foot_panel='-HcxFootPanel' in u.SystemLibrary.get_command_line();foot_lock=foot_panel or '-HcxFootTwistLock' in u.SystemLibrary.get_command_line();foot_probe=not foot_lock and '-HcxFoot90' in u.SystemLibrary.get_command_line();twist_test=not foot_lock and not foot_probe and '-HcxFootUntwist' in u.SystemLibrary.get_command_line();follow_test=not foot_lock and not foot_probe and '-HcxFootFollow' in u.SystemLibrary.get_command_line();toe_test=not foot_lock and (foot_probe or twist_test or follow_test or '-HcxToeOut' in u.SystemLibrary.get_command_line());version='0.2.30' if weapon_panel else '0.2.29' if grip_panel else '0.2.28' if idle_defaults else '0.2.27' if idle_panel else '0.2.26' if gait_defaults else '0.2.25' if gait_panel else '0.2.24' if panel_direct else '0.2.23' if panel_status else '0.2.22' if foot_panel else '0.2.21' if foot_lock else '0.2.20' if foot_probe else '0.2.19' if twist_test else '0.2.18' if follow_test else '0.2.17' if toe_test else '0.2.16'
B=R/'work/diagnostics'/('before-'+version+'-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));B.mkdir(parents=True)
for file in [P/'Content/Hcx2B/ABPT_2B_Adult.uasset',P/'Content/Hcx2B/ABP_2B_Adult.uasset',P/'Plugins/HuaShira/Content/Characters/Hero/Hero_Hun/SkinParts/Hun_Hair_Band.uasset',O/'blueprint-setup.json']:shutil.copy2(file,B/file.name)
bp=u.load_asset(D+'/ABPT_2B_Adult');base=u.load_asset(D+'/RTG_2B_Adult');direct=u.load_asset(D+'/RTG_2B_DirectLegs')
assert u.HcxRetargetTools.build_movement_leg_graph(bp,base,direct)=='OK'
settings=json.loads((R/'output/gait-width/runtime-settings.json').read_text(encoding='utf-8'));settings.update(offset_cm_per_foot=10.0,force_visible_probe=False,parent_movement_gate=True,knee_pole_inward_cm=4.0)
if gait_defaults:settings.update(offset_cm_per_foot=3.0,knee_pole_inward_cm=6.0)
if toe_test:settings['toe_out_degrees']=8.0
if follow_test:settings['backswing_foot_follow_max_degrees']=12.0
if twist_test:settings['foot_inward_twist_max_degrees']=30.0
if foot_probe:settings.update(toe_out_degrees=90.0,foot_yaw_force_probe=True)
if foot_lock:settings.update(toe_out_degrees=0.0,foot_relative_twist_lock=True)
if foot_panel:
 assert u.HcxRetargetTools.create_foot_tuning_panel()=='OK'
 settings['foot_runtime_panel']=True
result=u.HcxRetargetTools.build_width_graph(bp,json.dumps(settings));assert result=='OK',result
if grip_panel:
 result=(u.HcxRetargetTools.build_weapon_follow_graph if weapon_panel else u.HcxRetargetTools.build_grip_graph)(bp,(R/'output/grip-tuning/reference-settings.json').read_text(encoding='utf-8'));assert result=='OK',result
if foot_panel:
 result=u.HcxRetargetTools.attach_foot_tuning_panel(bp);assert result=='OK',result
 for name in (['WBP_CharacterTuning30'] if weapon_panel else ['WBP_CharacterTuning29'] if grip_panel else ['WBP_GaitTuning28'] if idle_defaults else ['WBP_GaitTuning27'] if idle_panel else ['WBP_GaitTuning26'] if gait_defaults else ['WBP_GaitTuning25'] if gait_panel else ['WBP_FootTuning24'] if panel_direct else ['WBP_FootTuning23','MPC_FootTuning23'] if panel_status else ['WBP_FootTuning','MPC_FootTuning']):u.EditorAssetLibrary.save_loaded_asset(u.load_asset(D+'/'+name),only_if_is_dirty=False)
u.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
child=u.load_asset(D+'/ABP_2B_Adult');u.BlueprintEditorLibrary.compile_blueprint(child);u.EditorAssetLibrary.save_loaded_asset(child,only_if_is_dirty=False)
cls=u.EditorAssetLibrary.load_blueprint_class(D+'/ABP_2B_Adult');mesh=u.load_asset('/HuaShira/Characters/Hero/Hero_Hun/SkinParts/Hun_Hair_Band');mesh.set_editor_property('post_process_anim_blueprint',cls);u.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
j=json.loads((O/'blueprint-setup.json').read_text(encoding='utf-8'));j.update(template=bp.get_path_name(),blueprint=child.get_path_name(),post_process_class=cls.get_path_name());(O/'blueprint-setup.json').write_text(json.dumps(j,indent=2),encoding='utf-8')
u.log('HCX_MOVEMENT_INNER_ACTIVE '+version)
