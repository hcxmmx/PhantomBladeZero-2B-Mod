import unreal as u,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];DEST='/Game/Hcxmmx2B'
u.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
tools=u.AssetToolsHelpers.get_asset_tools()
options=u.FbxImportUI()
options.set_editor_property('import_as_skeletal',True)
options.set_editor_property('mesh_type_to_import',u.FBXImportType.FBXIT_SKELETAL_MESH)
options.set_editor_property('automated_import_should_detect_type',False)
options.set_editor_property('import_materials',False)
options.set_editor_property('import_textures',False)
options.set_editor_property('import_animations',False)
options.set_editor_property('create_physics_asset',False)
options.skeletal_mesh_import_data.set_editor_property('import_morph_targets',False)
options.skeletal_mesh_import_data.set_editor_property('convert_scene',True)
options.skeletal_mesh_import_data.set_editor_property('convert_scene_unit',True)
options.skeletal_mesh_import_data.set_editor_property('normal_import_method',u.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
reference_dir='/HuaShira/Characters/Hero/Hero_Hun'
existing_skeleton=u.load_asset(reference_dir+'/Hun_Skin_Skeleton')
if existing_skeleton:options.set_editor_property('skeleton',existing_skeleton)
task=u.AssetImportTask();task.filename=str(ROOT/'output/2B-prototype/SK_2B_Hun.fbx');task.destination_path=reference_dir;task.destination_name='Hun_Skin';task.automated=True;task.replace_existing=True;task.save=True;task.options=options
tools.import_asset_tasks([task])
u.log('IMPORTED_PATHS '+str(task.imported_object_paths))
mesh=next((u.load_asset(p) for p in task.imported_object_paths if isinstance(u.load_asset(p),u.SkeletalMesh)),None)
if not mesh:raise RuntimeError('No imported SkeletalMesh')
skeleton=mesh.get_editor_property('skeleton')
target='/HuaShira/Characters/Hero/Hero_Hun/Hun_Skin_Skeleton'
if skeleton.get_path_name().split('.')[0]!=target:raise RuntimeError('Unexpected skeleton path: '+skeleton.get_path_name())
package_name,asset_name=tools.create_unique_asset_name(DEST+'/SK_2B_Prototype','')
mesh=tools.duplicate_asset(asset_name,DEST,mesh)
if not mesh:raise RuntimeError('Cannot duplicate imported mesh')
textures={}
for png in (ROOT/'output/2B-default/textures').glob('*diff*.png'):
 t=u.AssetImportTask();t.filename=str(png);t.destination_path=DEST+'/Textures';t.destination_name='T_'+png.stem;t.automated=True;t.replace_existing=True;t.save=True
 tools.import_asset_tasks([t]);textures[png.stem]=u.load_asset(t.imported_object_paths[0])
slots=mesh.get_editor_property('materials');slot_report=[]
for index in range(len(slots)):
 slot=slots[index]
 name=str(slot.material_slot_name)
 key=next((k for k in sorted(textures,key=len,reverse=True) if name.startswith(k)),None)
 mat=tools.create_asset('M_'+name.replace('.','_'),DEST+'/Materials',u.Material,u.MaterialFactoryNew())
 if not mat:mat=u.load_asset(DEST+'/Materials/M_'+name.replace('.','_'))
 mat.set_editor_property('blend_mode',u.BlendMode.BLEND_MASKED);mat.set_editor_property('two_sided',True)
 u.MaterialEditingLibrary.set_material_usage(mat,u.MaterialUsage.MATUSAGE_SKELETAL_MESH)
 if key:
  sample=u.MaterialEditingLibrary.create_material_expression(mat,u.MaterialExpressionTextureSample,-400,0)
  sample.set_editor_property('texture',textures[key]);sample.set_editor_property('sampler_type',u.MaterialSamplerType.SAMPLERTYPE_COLOR)
  u.MaterialEditingLibrary.connect_material_property(sample,'RGB',u.MaterialProperty.MP_BASE_COLOR)
  u.MaterialEditingLibrary.connect_material_property(sample,'A',u.MaterialProperty.MP_OPACITY_MASK)
 rough=u.MaterialEditingLibrary.create_material_expression(mat,u.MaterialExpressionConstant,-400,250);rough.set_editor_property('r',0.65)
 u.MaterialEditingLibrary.connect_material_property(rough,'',u.MaterialProperty.MP_ROUGHNESS)
 u.MaterialEditingLibrary.recompile_material(mat)
 slot.material_interface=mat;slots[index]=slot;slot_report.append({'slot':name,'texture':key})
mesh.set_editor_property('materials',slots)
mesh.set_editor_property('positive_bounds_extension',u.Vector(50,50,50));mesh.set_editor_property('negative_bounds_extension',u.Vector(50,50,50))
u.EditorAssetLibrary.save_directory(DEST,only_if_is_dirty=False,recursive=True)
u.EditorAssetLibrary.save_directory('/HuaShira',only_if_is_dirty=False,recursive=True)
report={'mesh':mesh.get_path_name(),'skeleton':skeleton.get_path_name(),'slots':slot_report,'source':'SK_2B_Hun.fbx'}
(ROOT/'output/2B-prototype/ue-import-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.log('HCXMMX_IMPORT_OK '+json.dumps(report))
