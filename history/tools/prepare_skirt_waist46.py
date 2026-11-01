"""A small radial clearance at the character's right posterior skirt waist."""
import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'output/skirt-prototype/0.2.46';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'output/skirt-prototype/0.2.36/2B-skirt110.blend'))
obj=bpy.data.objects['hash_5677568D_mesh'];inv=obj.matrix_world.inverted();changed=0;largest=0
for v in obj.data.vertices:
 p=obj.matrix_world@v.co
 if p.x>=-.5 or p.y<=1:continue
 e=((p.x+8)/10)**2+((p.y-9)/10)**2+((p.z-106)/9)**2
 if e>=1:continue
 t=1-e;amount=.6*t*t*(3-2*t)
 radial=p.copy();radial.z=0
 if radial.length<1:continue
 p+=radial.normalized()*amount;v.co=inv@p;changed+=1;largest=max(largest,amount)
assert 30<changed<2000,(changed,largest)
obj.data.update();arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');assert len(arm.data.bones)==107
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type in {'MESH','ARMATURE'}:o.select_set(True)
bpy.context.view_layer.objects.active=arm
bpy.ops.wm.save_as_mainfile(filepath=str(O/'2B-skirt110.blend'))
bpy.ops.export_scene.fbx(filepath=str(O/'2B-skirt110.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',path_mode='STRIP')
print('HCX_WAIST46_READY',changed,'vertices; max offset cm',round(largest,4),'bones',len(arm.data.bones))
