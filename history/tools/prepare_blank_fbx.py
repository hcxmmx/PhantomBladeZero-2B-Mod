import bpy
from pathlib import Path
from mathutils import Matrix,Vector
exec((Path(__file__).resolve().parent/'prepare_retarget_fbx.py').read_text(encoding='utf-8-sig').split('bpy.ops.wm.open_mainfile')[0])
def tiny(arm,bone):
 p=arm.matrix_world@arm.data.bones[bone].head_local;d=.0001
 data=bpy.data.meshes.new('Tiny');data.from_pydata([p,p+Vector((d,0,0)),p+Vector((0,0,d))],[],[(0,1,2)]);data.update()
 obj=bpy.data.objects.new('Tiny',data);bpy.context.scene.collection.objects.link(obj);obj.parent=arm;obj.matrix_world=Matrix.Identity(4)
 vg=obj.vertex_groups.new(name=bone);vg.add([0,1,2],1,'REPLACE');mod=obj.modifiers.new('Rig','ARMATURE');mod.object=arm
 return obj
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'work/pbz/exported/HuaShira/Characters/Hero/Hero_Hun/SkinParts/Hun_Body_Simple.glb'))
arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
for obj in list(bpy.context.scene.objects):
 if obj.type=='MESH':bpy.data.objects.remove(obj,do_unlink=True)
obj=tiny(arm,'pelvis');export_cm(OUT/'Blank-source-cm.fbx',arm,[obj])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.object.armature_add();arm=bpy.context.object;bpy.ops.object.mode_set(mode='EDIT');root=arm.data.edit_bones[0];root.name='root';root.head=(0,0,0);root.tail=(0,0,.1);bone=arm.data.edit_bones.new('pelvis');bone.head=(0,0,1);bone.tail=(0,0,1.1);bone.parent=root;bpy.ops.object.mode_set(mode='OBJECT')
obj=tiny(arm,'pelvis');export_cm(OUT/'Blank-part-cm.fbx',arm,[obj])
print('BLANK_FBX_READY')
