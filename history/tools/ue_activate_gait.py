"""Activate the isolated gait child on the single displayed body, preserving rollback files."""
import unreal as u
import json, shutil, datetime
from pathlib import Path
R=Path(__file__).resolve().parents[2];P=R/'work/ue-retarget/ProjectPBZ'
backup=R/'work/diagnostics'/('before-0.2.7-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True)
relative='Plugins/HuaShira/Content/Characters/Hero/Hero_Hun/SkinParts/Hun_Hair_Band.uasset'
shutil.copy2(P/relative,backup/'Hun_Hair_Band.uasset')
report=R/'output/2B-retarget/blueprint-setup.json';shutil.copy2(report,backup/report.name)
mesh=u.load_asset('/HuaShira/Characters/Hero/Hero_Hun/SkinParts/Hun_Hair_Band')
cls=u.EditorAssetLibrary.load_blueprint_class('/Game/Hcx2B/ABP_2B_Gait');assert mesh and cls
mesh.set_editor_property('post_process_anim_blueprint',cls)
u.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
setup=json.loads(report.read_text(encoding='utf-8'))
setup.update(template='/Game/Hcx2B/ABPT_2B_Gait.ABPT_2B_Gait',blueprint='/Game/Hcx2B/ABP_2B_Gait.ABP_2B_Gait',post_process_class=cls.get_path_name())
report.write_text(json.dumps(setup,indent=2),encoding='utf-8')
u.log('HCX_GAIT_ACTIVATED '+cls.get_path_name())
