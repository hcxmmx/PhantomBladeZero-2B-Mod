"""Reimport uniformly scaled geometry, preserve runtime paths and restore exact scaled poses."""
import unreal as u,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[2];D='/Game/Hcx2B';O=R/'output/scale-study/105';tools=u.AssetToolsHelpers.get_asset_tools()
original=json.loads((R/'work/retarget-readback-0.2.3/Hun_Hair_Band-reference.json').read_text(encoding='utf-8'))
poses={b['Name']:p for b,p in zip(original['FinalRefBoneInfo'],original['FinalRefBonePose'])}
skeleton=u.load_asset(D+'/SK_2B_Skeleton');assert skeleton
u.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
paths=[D+'/SK_2B','/HuaShira/Characters/Hero/Hero_Hun/SkinParts/Hun_Hair_Band'];report=[]
for path in paths:
 old=u.load_asset(path);assert old
 materials=[(str(s.material_slot_name),s.material_interface) for s in old.get_editor_property('materials')]
 post=old.get_editor_property('post_process_anim_blueprint')
 ui=u.FbxImportUI();ui.import_as_skeletal=True;ui.mesh_type_to_import=u.FBXImportType.FBXIT_SKELETAL_MESH;ui.automated_import_should_detect_type=False;ui.skeleton=skeleton
 ui.import_materials=False;ui.import_textures=False;ui.import_animations=False;ui.create_physics_asset=False
 ui.skeletal_mesh_import_data.set_editor_property('convert_scene',True);ui.skeletal_mesh_import_data.set_editor_property('convert_scene_unit',True)
 task=u.AssetImportTask();task.filename=str(O/'2B-original-rig-cm-105.fbx');task.destination_path=path.rsplit('/',1)[0];task.destination_name=path.rsplit('/',1)[1];task.automated=True;task.replace_existing=True;task.save=False;task.options=ui
 tools.import_asset_tasks([task]);mesh=u.load_asset(path);assert mesh.skeleton==skeleton
 mod=u.SkeletonModifier();assert mod.set_skeletal_mesh(mesh);names=list(mod.get_all_bone_names());assert len(names)==107
 transforms=[]
 for name in names:
  p=poses[str(name)];q=p['Rotation'];t=u.Transform();t.translation=u.Vector(*[p['Translation'][k]*1.05 for k in 'XYZ']);t.rotation=u.Quat(*[q[k] for k in 'XYZW']);t.scale3d=u.Vector(*[p['Scale3D'][k] for k in 'XYZ']);transforms.append(t)
 assert mod.set_bones_transforms(names,transforms,True)
 # An exact FBX import may already contain the requested pose; commit reports
 # "No modification needed" in that case. Validate the actual mesh below.
 mod.commit_skeleton_to_skeletal_mesh()
 slots=mesh.get_editor_property('materials');assert len(slots)==len(materials)==9
 for i in range(len(slots)):
  slot=slots[i];name=str(slot.material_slot_name);matches=[m for n,m in materials if n==name];assert len(matches)==1,(name,materials)
  slot.material_interface=matches[0];slots[i]=slot
 mesh.set_editor_property('materials',slots);mesh.set_editor_property('post_process_anim_blueprint',post)
 check=u.SkeletonModifier();assert check.set_skeletal_mesh(mesh)
 for name in names:
  p=poses[str(name)];t=check.get_bone_transform(name,False)
  assert max(abs(getattr(t.translation,k.lower())-p['Translation'][k]*1.05) for k in 'XYZ')<0.0001,name
  assert max(abs(getattr(t.scale3d,k.lower())-p['Scale3D'][k]) for k in 'XYZ')<0.0001,name
 u.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
 report.append({'mesh':path,'bones':len(names),'material_slots':len(slots),'postprocess':post.get_path_name() if post else None})
target=u.load_asset(D+'/SK_2B');u.HcxRetargetTools.sync_reference_pose(target);u.EditorAssetLibrary.save_loaded_asset(skeleton,only_if_is_dirty=False)
rig=u.load_asset(D+'/IK_2B');assert u.IKRigController.get_controller(rig).set_skeletal_mesh(target);u.EditorAssetLibrary.save_loaded_asset(rig,only_if_is_dirty=False)
bp=u.load_asset(D+'/ABPT_2B_Adult');result=u.HcxRetargetTools.scale_gait_reference_vectors(bp,105.0/110.0);assert result=='OK',result
u.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
for name in ['RTG_2B_Adult','RTG_2B_DirectLegs']:
 asset=u.load_asset(D+'/'+name);u.EditorAssetLibrary.save_loaded_asset(asset,only_if_is_dirty=False)
rtg=u.load_asset(D+'/RTG_2B_Adult');controller=u.IKRetargeterController.get_controller(rtg);assert controller.get_num_retarget_ops()==4
for name in ['ABPT_2B_Adult','ABP_2B_Adult']:
 bp=u.load_asset(D+'/'+name);u.BlueprintEditorLibrary.compile_blueprint(bp);u.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
(O/'ue-import.json').write_text(json.dumps({'uniform_scale':1.05,'meshes':report,'retarget_ops':[str(controller.get_op_name(i)) for i in range(4)]},indent=2),encoding='utf-8')
u.log('HCX_105_IMPORT_READY 0.2.33')
