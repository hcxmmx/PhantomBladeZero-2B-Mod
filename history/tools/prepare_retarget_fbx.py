import bpy,json
from pathlib import Path
from mathutils import Matrix
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/2B-retarget';OUT.mkdir(exist_ok=True)
def export_cm(path,arm,meshes,normalize_floor=False):
 bpy.ops.object.select_all(action='DESELECT')
 worlds={obj:obj.matrix_world.copy() for obj in [arm]+meshes}
 floor=min((worlds[obj]@v.co).z for obj in meshes for v in obj.data.vertices) if normalize_floor else 0.0
 lift=Matrix.Translation((0,0,-100*floor))
 for obj in [arm]+meshes:
  obj.data=obj.data.copy()
  obj.select_set(True); obj.matrix_world=lift@Matrix.Scale(100,4)@worlds[obj]
 bpy.context.view_layer.objects.active=arm
 bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 arm.name='Armature'
 bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=0.01
 bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',path_mode='STRIP')
 report={'floor_lift_cm':-100*floor,'bones':{b.name:{'parent':b.parent.name if b.parent else None,'head':list(b.head_local),'matrix':[list(r) for r in b.matrix_local]} for b in arm.data.bones},'armature_world':[list(r) for r in arm.matrix_world]}
 path.with_suffix('.json').write_text(json.dumps(report))
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'output/2B-default/2B-conversion.blend'))
arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE'); meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
export_cm(OUT/'2B-original-rig-cm.fbx',arm,meshes,normalize_floor=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'2B-original-rig-cm.blend'))
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'work/pbz/exported/HuaShira/Characters/Hero/Hero_Hun/SkinParts/Hun_Body_Simple.glb'))
arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
export_cm(OUT/'Hun-source-cm.fbx',arm,meshes)
print('RETARGET_FBX_READY')
