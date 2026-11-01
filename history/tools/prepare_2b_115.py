"""Scale the original converted model and its native rig once, around the floor origin."""
import bpy,json
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[2];O=R/'output/scale-study/115';O.mkdir(parents=True,exist_ok=True);factor=1.15
bpy.ops.wm.open_mainfile(filepath=str(R/'output/2B-retarget/2B-original-rig-cm.blend'))
arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];objects=[arm]+meshes
weights=lambda obj:[[(g.group,round(g.weight,9)) for g in v.groups] for v in obj.data.vertices]
before={obj.name:weights(obj) for obj in meshes};positions={obj.name:[obj.matrix_world@v.co for v in obj.data.vertices] for obj in meshes}
worlds={obj:obj.matrix_world.copy() for obj in objects};bpy.ops.object.select_all(action='DESELECT')
for obj in objects:obj.data=obj.data.copy();obj.select_set(True);obj.matrix_world=Matrix.Scale(factor,4)@worlds[obj]
bpy.context.view_layer.objects.active=arm;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);bpy.context.view_layer.update()
error=0
for obj in meshes:
 assert weights(obj)==before[obj.name]
 for v,old in zip(obj.data.vertices,positions[obj.name]):error=max(error,((obj.matrix_world@v.co)-old*factor).length)
assert error<0.0001,error
assert len(arm.data.bones)==107
bpy.ops.export_scene.fbx(filepath=str(O/'2B-original-rig-cm-115.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',path_mode='STRIP')
bpy.ops.wm.save_as_mainfile(filepath=str(O/'2B-original-rig-cm-115.blend'),compress=True)
report={'uniform_scale':factor,'vertices':sum(len(o.data.vertices) for o in meshes),'bones':len(arm.data.bones),'skin_weights_identical':True,'maximum_vertex_scale_error_cm':error,'bone_reference_global':{b.name:[list(row) for row in b.matrix_local] for b in arm.data.bones}}
(O/'preparation.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('HCX_115_FBX_READY',report['vertices'],error)
