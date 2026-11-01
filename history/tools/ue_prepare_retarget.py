import unreal as u,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'output/2B-retarget';dest='/Game/Hcx2B'
u.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
tools=u.AssetToolsHelpers.get_asset_tools()
def asset(n,cls,factory,folder=dest):
 return u.load_asset(folder+'/'+n) or tools.create_asset(n,folder,cls,factory())
def import_fbx(file,name):
 existing=u.load_asset(dest+'/'+name)
 if existing and not (O/'force-reimport.txt').exists():return existing
 ui=u.FbxImportUI();ui.import_as_skeletal=True;ui.mesh_type_to_import=u.FBXImportType.FBXIT_SKELETAL_MESH;ui.automated_import_should_detect_type=False;ui.import_materials=False;ui.import_textures=False;ui.import_animations=False;ui.create_physics_asset=False
 ui.skeletal_mesh_import_data.convert_scene=True;ui.skeletal_mesh_import_data.convert_scene_unit=True
 task=u.AssetImportTask();task.filename=str(file);task.destination_path=dest;task.destination_name=name;task.automated=True;task.replace_existing=True;task.save=True;task.options=ui
 tools.import_asset_tasks([task]);return next(u.load_asset(p) for p in task.imported_object_paths if isinstance(u.load_asset(p),u.SkeletalMesh))
target=import_fbx(O/'2B-original-rig-cm.fbx','SK_2B');source=import_fbx(O/'Hun-source-cm.fbx','SK_SourceHun')
report={}
for label,mesh in [('target',target),('source',source)]:
 mod=u.SkeletonModifier();assert mod.set_skeletal_mesh(mesh);names=list(mod.get_all_bone_names())
 report[label]={'mesh':mesh.get_path_name(),'skeleton':mesh.skeleton.get_path_name(),'bones':len(names),'names':[str(n) for n in names],'transforms':{str(n):str(mod.get_bone_transform(n,False)) for n in names[:12]}}
(O/'ue-rigs.json').write_text(json.dumps(report,indent=2))
for name in ['IKRigController','IKRetargeterController','IKRigDefinitionFactory','IKRetargetFactory','ChaosClothAssetFactory','IKRetargetFKChainsController','IKRetargetPelvisMotionController']:
 cls=getattr(u,name,None);u.log('HCX_API '+name+' '+str(cls))
 if cls:u.log('HCX_METHODS '+str([n for n in dir(cls) if n.startswith(('get_','set_','add_','auto_'))]))
u.EditorAssetLibrary.save_directory(dest,only_if_is_dirty=False)
u.log('HCX_RETARGET_IMPORT_READY '+json.dumps(report))
