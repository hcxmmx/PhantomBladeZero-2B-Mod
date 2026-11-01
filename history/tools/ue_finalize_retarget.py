import unreal as u,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];dest='/Game/Hcx2B';tools=u.AssetToolsHelpers.get_asset_tools()
assert hasattr(u,'HcxRetargetTools'),'Build the HcxEditor editor module first'
mesh=u.load_asset(dest+'/SK_2B');rtg=u.load_asset(dest+'/RTG_2B_Adult');assert mesh and rtg
path=dest+'/ABPT_2B_Adult';template=u.load_asset(path)
if not template:
 factory=u.AnimBlueprintFactory();factory.set_editor_property('template',True);factory.set_editor_property('parent_class',u.AnimInstance)
 template=tools.create_asset('ABPT_2B_Adult',dest,u.AnimBlueprint,factory)
 assert template and u.HcxRetargetTools.build_retarget_graph(template,rtg),'Cannot create retarget graph'
u.EditorAssetLibrary.save_loaded_asset(template,only_if_is_dirty=False)
path=dest+'/ABP_2B_Adult';blueprint=u.load_asset(path)
if not blueprint:
 factory=u.AnimBlueprintFactory();factory.set_editor_property('parent_class',u.EditorAssetLibrary.load_blueprint_class(dest+'/ABPT_2B_Adult'));factory.set_editor_property('target_skeleton',mesh.skeleton)
 blueprint=tools.create_asset('ABP_2B_Adult',dest,u.AnimBlueprint,factory)
 assert blueprint,'Cannot create skeleton-specific retarget blueprint'
u.BlueprintEditorLibrary.compile_blueprint(blueprint);u.EditorAssetLibrary.save_loaded_asset(blueprint,only_if_is_dirty=False)
cls=u.EditorAssetLibrary.load_blueprint_class(path);assert cls
mesh.set_editor_property('post_process_anim_blueprint',cls)
overrides=[]
for name in ['Hun_BrowLashCard','Hun_BrowLashCardMoQu','Hun_Hair_Band']:
 folder='/HuaShira/Characters/Hero/Hero_Hun/SkinParts';target=folder+'/'+name
 copy=u.load_asset(target) or tools.duplicate_asset(name,folder,mesh);assert copy
 copy.set_editor_property('post_process_anim_blueprint',cls);u.EditorAssetLibrary.save_loaded_asset(copy,only_if_is_dirty=False);overrides.append(target)
u.EditorAssetLibrary.save_directory(dest,only_if_is_dirty=False);u.EditorAssetLibrary.save_directory('/HuaShira',only_if_is_dirty=False)
(R/'output/2B-retarget/blueprint-setup.json').write_text(json.dumps({'template':template.get_path_name(),'blueprint':blueprint.get_path_name(),'post_process_class':cls.get_path_name(),'visible_overrides':overrides},indent=2));u.log('HCX_RETARGET_BLUEPRINT_READY')
