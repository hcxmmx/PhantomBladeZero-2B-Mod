"""Match a small rear-right waist patch to the nearby tight garment skinning."""
import bpy
from pathlib import Path
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];O=R/'output/skirt-prototype/0.2.47';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'output/skirt-prototype/0.2.46/2B-skirt110.blend'))
arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');assert len(arm.data.bones)==107
points=[];triangles=[];weights=[]
for name in ['hash_0616AD58_mesh','hash_0739FE07_mesh','hash_B4D83256_mesh']:
 obj=bpy.data.objects[name];base=len(points);obj.data.calc_loop_triangles()
 for v in obj.data.vertices:
  points.append(obj.matrix_world@v.co);weights.append({obj.vertex_groups[g.group].name:g.weight for g in v.groups if obj.vertex_groups[g.group].name in arm.data.bones})
 for tri in obj.data.loop_triangles:
  ids=tuple(base+i for i in tri.vertices);p=(points[ids[0]]+points[ids[1]]+points[ids[2]])/3
  if p.x<3 and p.y>0 and 94<p.z<118:triangles.append(ids)
assert triangles
tree=BVHTree.FromPolygons(points,triangles,all_triangles=True)
obj=bpy.data.objects['hash_5677568D_mesh'];changed=0;distances=[]
for v in obj.data.vertices:
 p=obj.matrix_world@v.co
 if p.x>=-.5 or p.y<=1:continue
 e=((p.x+10)/9)**2+((p.y-9)/10)**2+((p.z-106)/7)**2
 if e>=1:continue
 q,_,face,distance=tree.find_nearest(p)
 if face is None or distance>5:continue
 ids=triangles[face];a,b,c=[points[i] for i in ids];u=b-a;w=c-a;d=q-a
 uu=u.dot(u);ww=w.dot(w);uw=u.dot(w);du=d.dot(u);dw=d.dot(w);den=uu*ww-uw*uw
 if abs(den)<1e-10:continue
 b1=(ww*du-uw*dw)/den;b2=(uu*dw-uw*du)/den;bs=[max(0,1-b1-b2),max(0,b1),max(0,b2)];s=sum(bs);bs=[x/s for x in bs]
 target={}
 for i,k in zip(ids,bs):
  for name,value in weights[i].items():target[name]=target.get(name,0)+k*value
 t=1-e;blend=t*t*(3-2*t)
 old={obj.vertex_groups[g.group].name:g.weight for g in v.groups if obj.vertex_groups[g.group].name in arm.data.bones}
 result={name:value*(1-blend) for name,value in old.items()}
 for name,value in target.items():result[name]=result.get(name,0)+value*blend
 result=dict(sorted(result.items(),key=lambda x:-x[1])[:8]);total=sum(result.values());assert total>0
 for index in [g.group for g in v.groups if obj.vertex_groups[g.group].name in arm.data.bones]:obj.vertex_groups[index].remove([v.index])
 for name,value in result.items():
  if value<=1e-6:continue
  group=obj.vertex_groups.get(name) or obj.vertex_groups.new(name=name);group.add([v.index],value/total,'REPLACE')
 assigned=[g.weight for g in v.groups if obj.vertex_groups[g.group].name in arm.data.bones];assert abs(sum(assigned)-1)<1e-4 and len(assigned)<=8
 changed+=1;distances.append(distance)
assert 50<changed<700,changed
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type in {'MESH','ARMATURE'}:o.select_set(True)
bpy.context.view_layer.objects.active=arm
bpy.ops.wm.save_as_mainfile(filepath=str(O/'2B-skirt110.blend'))
bpy.ops.export_scene.fbx(filepath=str(O/'2B-skirt110.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',path_mode='STRIP')
print('HCX_WAIST47_WEIGHTS_READY',changed,'vertices; nearest underlayer distance cm',round(min(distances),3),round(max(distances),3),'geometry unchanged')
