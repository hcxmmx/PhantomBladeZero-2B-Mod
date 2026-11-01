import unreal as u,json,datetime,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[2];P=R/'work/ue-retarget/ProjectPBZ';O=R/'output/2B-retarget'
B=R/'work/diagnostics'/('before-0.2.14-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));B.mkdir(parents=True)
f=P/'Plugins/HuaShira/Content/Characters/Hero/Hero_Hun/SkinParts/Hun_Hair_Band.uasset';shutil.copy2(f,B/f.name);shutil.copy2(O/'blueprint-setup.json',B/'blueprint-setup.json')
m=u.load_asset('/HuaShira/Characters/Hero/Hero_Hun/SkinParts/Hun_Hair_Band');c=u.EditorAssetLibrary.load_blueprint_class('/Game/Hcx2B/ABP_2B_Wide');assert m and c
m.set_editor_property('post_process_anim_blueprint',c);u.EditorAssetLibrary.save_loaded_asset(m,only_if_is_dirty=False)
j=json.loads((O/'blueprint-setup.json').read_text(encoding='utf-8'));j.update(template='/Game/Hcx2B/ABPT_2B_Wide.ABPT_2B_Wide',blueprint='/Game/Hcx2B/ABP_2B_Wide.ABP_2B_Wide',post_process_class=c.get_path_name());(O/'blueprint-setup.json').write_text(json.dumps(j,indent=2),encoding='utf-8')
u.log('HCX_WIDTH_ACTIVE')
