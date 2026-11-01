"""Activate the verified movement-only leg correspondence trial, preserving rollback."""
import unreal as u,json,datetime,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[2];P=R/'work/ue-retarget/ProjectPBZ';O=R/'output/2B-retarget';assert (R/'output/gait-direct/verification.json').is_file()
backup=R/'work/diagnostics'/('before-0.2.13-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
bandfile=P/'Plugins/HuaShira/Content/Characters/Hero/Hero_Hun/SkinParts/Hun_Hair_Band.uasset';shutil.copy2(bandfile,backup/bandfile.name);shutil.copy2(O/'blueprint-setup.json',backup/'blueprint-setup.json')
mesh=u.load_asset('/HuaShira/Characters/Hero/Hero_Hun/SkinParts/Hun_Hair_Band');cls=u.EditorAssetLibrary.load_blueprint_class('/Game/Hcx2B/ABP_2B_DirectLegs');assert mesh and cls
mesh.set_editor_property('post_process_anim_blueprint',cls);u.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
setup=json.loads((O/'blueprint-setup.json').read_text(encoding='utf-8'));setup.update(template='/Game/Hcx2B/ABPT_2B_DirectLegs.ABPT_2B_DirectLegs',blueprint='/Game/Hcx2B/ABP_2B_DirectLegs.ABP_2B_DirectLegs',post_process_class=cls.get_path_name());(O/'blueprint-setup.json').write_text(json.dumps(setup,indent=2),encoding='utf-8')
u.log('HCX_DIRECT_LEG_ACTIVE '+cls.get_path_name())
