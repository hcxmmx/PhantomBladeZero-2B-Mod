"""Remove the moving skirt's inward sheet; preserve the outer shell and its UVs."""
import bpy,bmesh
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'output/skirt-prototype/0.2.44';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'output/skirt-prototype/0.2.37/2B-skirt110.blend'))
obj=bpy.data.objects['hash_5677568D_mesh'];bm=bmesh.new();bm.from_mesh(obj.data);bm.normal_update();inner=[]
for f in bm.faces:
 p=f.calc_center_median();rad=p.copy();rad.z=0
 if p.z<111 and rad.length>5 and f.normal.dot(rad.normalized())<-.02:inner.append(f)
assert 4000<len(inner)<6500,len(inner)
removed=len(inner);bmesh.ops.delete(bm,geom=inner,context='FACES_ONLY')
loose=[v for v in bm.verts if not v.link_faces]
if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
bm.to_mesh(obj.data);bm.free();obj.data.update()
arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');assert len(arm.data.bones)==107
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type in {'MESH','ARMATURE'}:o.select_set(True)
bpy.context.view_layer.objects.active=arm
bpy.ops.wm.save_as_mainfile(filepath=str(O/'2B-skirt110.blend'))
bpy.ops.export_scene.fbx(filepath=str(O/'2B-skirt110.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',path_mode='STRIP')
print('HCX_SINGLE44_READY inward faces removed',removed,'dress faces remaining',len(obj.data.polygons),'bones',len(arm.data.bones))
