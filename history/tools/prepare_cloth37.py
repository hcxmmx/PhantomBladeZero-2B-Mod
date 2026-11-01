import bpy,bmesh
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'output/skirt-prototype/0.2.37';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'output/skirt-prototype/0.2.36/2B-skirt110.blend'))
obj=bpy.data.objects['hash_5677568D_mesh'];bm=bmesh.new();bm.from_mesh(obj.data)
before=(len(bm.verts),len(bm.faces));bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.001);bmesh.ops.triangulate(bm,faces=list(bm.faces))
bad=[f for f in bm.faces if f.calc_area()<.001]
if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
bm.to_mesh(obj.data);bm.free();obj.data.update()
arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');assert len(arm.data.bones)==107
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type in {'MESH','ARMATURE'}:o.select_set(True)
bpy.context.view_layer.objects.active=arm
bpy.ops.wm.save_as_mainfile(filepath=str(O/'2B-skirt110.blend'))
bpy.ops.export_scene.fbx(filepath=str(O/'2B-skirt110.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',path_mode='STRIP')
print('HCX_CLOTH37_MESH_READY',before,'to',len(obj.data.vertices),len(obj.data.polygons),'tiny_faces_removed',len(bad))
