"""Reweight only the outer dress below its waist, preserving the 110% rig."""
import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'output/skirt-prototype/110';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'output/scale-study/110/2B-original-rig-cm-110.blend'))
arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
assert len(arm.data.bones)==107
obj=bpy.data.objects['hash_5677568D_mesh']
targets=['SM_L_FrontSkirtRoll','SM_R_FrontSkirtRoll','SM_L_BackSkirtRoll','SM_R_BackSkirtRoll']
groups=[obj.vertex_groups.get(n) or obj.vertex_groups.new(name=n) for n in targets]
deform={g.index:g for g in obj.vertex_groups if g.name in arm.data.bones}
changed=0
for v in obj.data.vertices:
 p=obj.matrix_world@v.co;t=max(0,min(1,(110-p.z)/18));a=t*t*(3-2*t)
 if a<=0:continue
 old={g.group:g.weight for g in v.groups if g.group in deform}
 left=max(0,min(1,.5+p.x/20));front=max(0,min(1,.5-p.y/16))
 values={i:w*(1-a) for i,w in old.items()}
 for g,w in zip(groups,[left*front,(1-left)*front,left*(1-front),(1-left)*(1-front)]):values[g.index]=values.get(g.index,0)+w*a
 for g in deform.values():g.remove([v.index])
 values=dict(sorted(values.items(),key=lambda kv:-kv[1])[:8]);s=sum(values.values());assert s>0
 for i,w in values.items():
  if w>1e-6:obj.vertex_groups[i].add([v.index],w/s,'REPLACE')
 changed+=1
assert changed>1000
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type in {'MESH','ARMATURE'}:o.select_set(True)
bpy.context.view_layer.objects.active=arm
bpy.ops.wm.save_as_mainfile(filepath=str(O/'2B-skirt110.blend'))
bpy.ops.export_scene.fbx(filepath=str(O/'2B-skirt110.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',path_mode='STRIP')
print('HCX_SKIRT_WEIGHTS_READY',changed,'vertices; bones',len(arm.data.bones))
