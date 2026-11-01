import unreal as u,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'output/2B-retarget';tools=u.AssetToolsHelpers.get_asset_tools();dest='/Game/Hcx2B'
mapping=json.loads((O/'direct-material-map.json').read_text());base=u.load_asset('/Game/HcxEditorStubs/M_Placeholder');assert base
parents={};texture_paths=[]
for row in mapping:
 path=row['material'];folder,name=path.rsplit('/',1);mat=u.load_asset(path) or tools.create_asset(name,folder,u.MaterialInstanceConstant,u.MaterialInstanceConstantFactoryNew());assert mat
 u.MaterialEditingLibrary.set_material_instance_parent(mat,base);parents[row['diffuse']]=mat;u.EditorAssetLibrary.save_loaded_asset(mat,only_if_is_dirty=False)
 for spec in row['overrides']:
  folder,name=spec['target'].rsplit('/',1);source=(O/'neutral_ARM.png') if spec['kind']=='Mix' else (R/'output/2B-default/textures'/spec['source'])
  task=u.AssetImportTask();task.filename=str(source);task.destination_path=folder;task.destination_name=name;task.automated=True;task.replace_existing=True;task.save=True;tools.import_asset_tasks([task]);tex=u.load_asset(spec['target']);assert isinstance(tex,u.Texture2D)
  tex.set_editor_property('srgb',spec['kind'] in ['Albedo','Basecolor'])
  tex.set_editor_property('virtual_texture_streaming',True)
  if spec['kind']=='Normal':tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_NORMALMAP)
  u.EditorAssetLibrary.save_loaded_asset(tex,only_if_is_dirty=False);texture_paths.append(spec['target'])
for path in [dest+'/SK_2B','/HuaShira/Characters/Hero/Hero_Hun/SkinParts/Hun_Hair_Band']:
 mesh=u.load_asset(path);slots=mesh.get_editor_property('materials')
 for i in range(len(slots)):
  slot=slots[i];key=next(k for k in parents if str(slot.material_slot_name).startswith(k));slot.material_interface=parents[key];slots[i]=slot
 mesh.set_editor_property('materials',slots);u.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
folder='/HuaShira/Characters/Hero/Hero_Hun/SkinParts';names=['Hun_BrowLashCard','Hun_BrowLashCardMoQu']
for name in names:
 path=folder+'/'+name
 if u.EditorAssetLibrary.does_asset_exist(path):assert u.EditorAssetLibrary.delete_asset(path),'Cannot replace local working copy '+path
u.SystemLibrary.collect_garbage()
part=u.load_asset(dest+'/SK_BlankPart2');assert part
for name in names:
 blank=tools.duplicate_asset(name,folder,part);assert blank;u.EditorAssetLibrary.save_loaded_asset(blank,only_if_is_dirty=False)
setup=json.loads((O/'asset-setup.json').read_text());setup['texture_overrides']=texture_paths;setup['direct_game_materials']=[r['material'] for r in mapping];setup['empty_overrides']=list(dict.fromkeys(setup['empty_overrides']+[folder+'/'+n for n in names]));setup['exclude_cooked_stub_packages'] += [p.get_path_name() for p in parents.values()]
(O/'asset-setup.json').write_text(json.dumps(setup,indent=2))
bp=json.loads((O/'blueprint-setup.json').read_text());bp['visible_overrides']=[folder+'/Hun_Hair_Band'];(O/'blueprint-setup.json').write_text(json.dumps(bp,indent=2))
u.EditorAssetLibrary.save_directory('/HuaShira',only_if_is_dirty=False);u.EditorAssetLibrary.save_directory('/Game/PBZContent',only_if_is_dirty=False)
u.log('HCX_DIRECT_MATERIAL_FIX_READY 7 direct materials, 20 texture replacements, one animated display mesh')
