"""Confine breast bones to the chest before adding limited secondary motion."""
import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'output/chest-prototype/0.2.48';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'output/skirt-prototype/0.2.47/2B-skirt110.blend'))
arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');assert len(arm.data.bones)==107
chest={'SPR_L_Breast','SPR_R_Breast'};assert chest.issubset(arm.data.bones.keys())
foreign=local=0
for obj in bpy.context.scene.objects:
 if obj.type!='MESH':continue
 for v in obj.data.vertices:
  old={obj.vertex_groups[g.group].name:g.weight for g in v.groups if obj.vertex_groups[g.group].name in arm.data.bones}
  cw={n:w for n,w in old.items() if n in chest and w>1e-6}
  if not cw:continue
  p=obj.matrix_world@v.co
  valid=obj.name in {'hash_0739FE07_mesh','hash_B4D83256_mesh'} and 130<p.z<154 and p.y<-6 and abs(p.x)<22
  other={n:w for n,w in old.items() if n not in chest};total=sum(cw.values())
  if valid:
   newtotal=min(.75,total*1.8);remaining=sum(other.values())
   if remaining<1e-6:other={'SKEL_Spine3':1};remaining=1
   result={n:w*(1-newtotal)/remaining for n,w in other.items()}
   for n,w in cw.items():result[n]=newtotal*w/total
   local+=1
  else:
   target='SKEL_Head' if p.z>=155 else max(other,key=other.get) if other else 'SKEL_Spine3' if p.z>=130 else 'SKEL_Pelvis'
   result=other;result[target]=result.get(target,0)+total;foreign+=1
  for index in [g.group for g in v.groups if obj.vertex_groups[g.group].name in arm.data.bones]:obj.vertex_groups[index].remove([v.index])
  result=dict(sorted(result.items(),key=lambda item:-item[1])[:8]);s=sum(result.values());assert s>0
  for n,w in result.items():
   if w<1e-6:continue
   group=obj.vertex_groups.get(n) or obj.vertex_groups.new(name=n);group.add([v.index],w/s,'REPLACE')
  assert abs(sum(g.weight for g in v.groups if obj.vertex_groups[g.group].name in arm.data.bones)-1)<1e-4
assert foreign>1000 and local>200,(foreign,local)
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.context.scene.objects:
 if obj.type in {'MESH','ARMATURE'}:obj.select_set(True)
bpy.context.view_layer.objects.active=arm
bpy.ops.wm.save_as_mainfile(filepath=str(O/'2B-chest110.blend'))
bpy.ops.export_scene.fbx(filepath=str(O/'2B-chest110.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',path_mode='STRIP')
print('HCX_CHEST48_WEIGHTS_READY foreign cleaned',foreign,'chest weighted',local,'bones',len(arm.data.bones))
