"""Obvious loading/route probe. Compile, save, activate; no diagnostic captures."""
import unreal as u,json,datetime,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[2];P=R/'work/ue-retarget/ProjectPBZ';O=R/'output/2B-retarget';D='/Game/Hcx2B'
B=R/'work/diagnostics'/('before-0.2.15-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));B.mkdir(parents=True)
for file in [P/'Content/Hcx2B/ABPT_2B_Adult.uasset',P/'Content/Hcx2B/ABP_2B_Adult.uasset',P/'Plugins/HuaShira/Content/Characters/Hero/Hero_Hun/SkinParts/Hun_Hair_Band.uasset',O/'blueprint-setup.json']:shutil.copy2(file,B/file.name)
bp=u.load_asset(D+'/ABPT_2B_Adult');base=u.load_asset(D+'/RTG_2B_Adult');direct=u.load_asset(D+'/RTG_2B_DirectLegs')
assert u.HcxRetargetTools.build_movement_leg_graph(bp,base,direct)=='OK'
settings=json.loads((R/'output/gait-width/runtime-settings.json').read_text(encoding='utf-8'));settings.update(offset_cm_per_foot=10.0,force_visible_probe=True)
result=u.HcxRetargetTools.build_width_graph(bp,json.dumps(settings));assert result=='OK',result
u.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
child=u.load_asset(D+'/ABP_2B_Adult');u.BlueprintEditorLibrary.compile_blueprint(child);u.EditorAssetLibrary.save_loaded_asset(child,only_if_is_dirty=False)
cls=u.EditorAssetLibrary.load_blueprint_class(D+'/ABP_2B_Adult');mesh=u.load_asset('/HuaShira/Characters/Hero/Hero_Hun/SkinParts/Hun_Hair_Band');mesh.set_editor_property('post_process_anim_blueprint',cls);u.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
j=json.loads((O/'blueprint-setup.json').read_text(encoding='utf-8'));j.update(template=bp.get_path_name(),blueprint=child.get_path_name(),post_process_class=cls.get_path_name());(O/'blueprint-setup.json').write_text(json.dumps(j,indent=2),encoding='utf-8')
u.log('HCX_VISIBLE_PROBE_ACTIVE')
