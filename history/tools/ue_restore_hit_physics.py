import unreal as u
from pathlib import Path
import shutil,datetime
R=Path(__file__).resolve().parents[2];P=R/'work/ue-retarget/ProjectPBZ';rel=Path('Plugins/HuaShira/Content/Characters/Hero/Hero_Hun/SkinParts/Hun_Body_Simple.uasset');backup=R/'work/diagnostics'/('before-0.2.6-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True);shutil.copy2(P/rel,backup/rel.name)
mesh=u.load_asset('/HuaShira/Characters/Hero/Hero_Hun/SkinParts/Hun_Body_Simple');path='/HuaShira/Characters/Hero/Hero_Hun/PA_Hun'
assert u.HcxRetargetTools.restore_physics_reference(mesh,path)
asset=u.load_object(None,path+'.PA_Hun');assert asset
u.EditorAssetLibrary.save_loaded_asset(asset,only_if_is_dirty=False);u.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
u.log('HCX_ORIGINAL_PA_HUN_REFERENCE_RESTORED; editor placeholder must not enter game package')
