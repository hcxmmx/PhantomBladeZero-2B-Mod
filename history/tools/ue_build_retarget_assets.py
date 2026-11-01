import unreal as u,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'output/2B-retarget';dest='/Game/Hcx2B';tools=u.AssetToolsHelpers.get_asset_tools()
def asset(n,cls,factory,folder=dest):return u.load_asset(folder+'/'+n) or tools.create_asset(n,folder,cls,factory())
def duplicate(source,path):
 folder,name=path.rsplit('/',1);return u.load_asset(path) or tools.duplicate_asset(name,folder,source)
def import_file(file,name,folder=dest,skeletal=False,skeleton=None):
 old=u.load_asset(folder+'/'+name)
 if old and (not skeletal or old.skeleton):return old
 t=u.AssetImportTask();t.filename=str(file);t.destination_path=folder;t.destination_name=name;t.automated=True;t.replace_existing=True;t.replace_existing_settings=True;t.save=True
 if skeletal:
  u.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0');ui=u.FbxImportUI();ui.import_as_skeletal=True;ui.mesh_type_to_import=u.FBXImportType.FBXIT_SKELETAL_MESH;ui.automated_import_should_detect_type=False;ui.import_materials=False;ui.import_textures=False;ui.import_animations=False;ui.create_physics_asset=False;ui.set_editor_property('skeleton',skeleton);t.options=ui
 tools.import_asset_tasks([t]);return next(u.load_asset(p) for p in t.imported_object_paths if isinstance(u.load_asset(p),u.SkeletalMesh if skeletal else u.Texture2D))
source=u.load_asset(dest+'/SK_SourceHun');target=u.load_asset(dest+'/SK_2B');assert target and source
shared=duplicate(source.skeleton,'/HuaShira/Characters/Hero/Hero_Hun/Hun_Skin_Skeleton');u.EditorAssetLibrary.save_loaded_asset(shared,only_if_is_dirty=False)
body=import_file(O/'Blank-source-cm.fbx','SK_BlankBody2',skeletal=True,skeleton=shared);part=import_file(O/'Blank-part-cm.fbx','SK_BlankPart2',skeletal=True,skeleton=shared)
u.EditorAssetLibrary.save_directory(dest,only_if_is_dirty=False)
reference=json.loads((R/'work/pbz/Hun_Body_Simple-reference.json').read_text());poses={b['Name'].lower():p for b,p in zip(reference['FinalRefBoneInfo'],reference['FinalRefBonePose'])}
mod=u.SkeletonModifier();assert mod.set_skeletal_mesh(body);names=list(mod.get_all_bone_names());trans=[]
for n in names:
 p=poses[str(n).lower()];t=u.Transform();t.translation=u.Vector(*[p['Translation'][k] for k in 'XYZ']);t.rotation=u.Quat(*[p['Rotation'][k] for k in 'XYZW']);t.scale3d=u.Vector(1,1,1);trans.append(t)
assert mod.set_bones_transforms(names,trans,True);assert mod.commit_skeleton_to_skeletal_mesh()
base=asset('M_Placeholder',u.Material,u.MaterialFactoryNew,folder='/Game/HcxEditorStubs')
parent=asset('MI_ZeroHun_Cloth_03_b',u.MaterialInstanceConstant,u.MaterialInstanceConstantFactoryNew,folder='/Game/PBZContent/Characters/Hero/Hun_New_V2b/Material')
u.MaterialEditingLibrary.set_material_instance_parent(parent,base)
textures={}
for p in (R/'output/2B-default/textures').glob('*.png'):
 if '_diff_' not in p.stem and '_normal_' not in p.stem:continue
 tex=import_file(p,'T_'+p.stem,dest+'/Textures')
 if '_normal_' in p.stem:tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_NORMALMAP);tex.set_editor_property('srgb',False)
 textures[p.stem]=tex
slots=target.get_editor_property('materials');materials=[]
for i in range(len(slots)):
 slot=slots[i];slotname=str(slot.material_slot_name);key=next(k for k in textures if '_diff_' in k and slotname.startswith(k));normal=key.split('_diff_')[0]+'_normal_'+key.split('_diff_')[1][:3]
 mat=asset('MI_'+slotname.replace('.','_'),u.MaterialInstanceConstant,u.MaterialInstanceConstantFactoryNew,dest+'/Materials');u.MaterialEditingLibrary.set_material_instance_parent(mat,parent)
 values=[]
 for param,tex in [('Albedo',textures[key]),('Normal',textures[normal])]:
  info=u.MaterialParameterInfo();info.set_editor_property('name',param);info.set_editor_property('association',u.MaterialParameterAssociation.LAYER_PARAMETER);info.set_editor_property('index',0)
  value=u.TextureParameterValue();value.set_editor_property('parameter_info',info);value.set_editor_property('parameter_value',tex);values.append(value)
 mat.set_editor_property('texture_parameter_values',values)
 slot.material_interface=mat;slots[i]=slot;materials.append({'slot':slotname,'albedo':key,'normal':normal,'material':mat.get_path_name()})
target.set_editor_property('materials',slots)
basepath='/HuaShira/Characters/Hero/Hero_Hun';overrides=[]
for name in ['Hun_Body_Simple']:
 path=basepath+'/SkinParts/'+name;duplicate(body,path);overrides.append(path)
for name in ['Hun_Head_New','Hun_Head','Hun_Head_New_MoQu','Hun_Hair','Hun_Scarf','Hun_Scarf_Climax']:
 path=basepath+'/SkinParts/'+name;duplicate(part,path);overrides.append(path)
for name in ['Hun_Hat_00','Hun_Hat_01']:
 path=basepath+'/Hats/'+name;duplicate(part,path);overrides.append(path)
for name in ['CA_Hun_Hair01','CA_Hun_Hair02','CA_Hun_Cape','CA_Hun_Skirt','CA_Hun_UpperCloth']:
 path=basepath+'/SkinParts/Cloth/'+name;folder,_=path.rsplit('/',1);asset(name,u.ChaosClothAsset,u.ChaosClothAssetFactory,folder);overrides.append(path)
u.EditorAssetLibrary.save_directory(dest,only_if_is_dirty=False);u.EditorAssetLibrary.save_directory('/HuaShira',only_if_is_dirty=False);u.EditorAssetLibrary.save_loaded_asset(parent,only_if_is_dirty=False);u.EditorAssetLibrary.save_loaded_asset(base,only_if_is_dirty=False)
report={'materials':materials,'textures':len(textures),'empty_overrides':overrides,'game_parent':parent.get_path_name(),'exclude_cooked_stub_packages':[shared.get_path_name(),parent.get_path_name(),base.get_path_name()]}
(O/'asset-setup.json').write_text(json.dumps(report,indent=2));u.log('HCX_RETARGET_ASSETS_READY '+str(len(overrides))+' overrides; '+str(len(materials))+' material instances')
