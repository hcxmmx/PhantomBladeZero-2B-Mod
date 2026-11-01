"""Pin the skirt waist to torso weights; retain the existing four-panel hem rig."""
import bpy
from mathutils.kdtree import KDTree
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'output/skirt-prototype/0.2.36';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'output/scale-study/110/2B-original-rig-cm-110.blend'))
arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');assert len(arm.data.bones)==107
body=bpy.data.objects['hash_0739FE07_mesh'];dress=bpy.data.objects['hash_5677568D_mesh']
torso={'SKEL_Pelvis','SKEL_Spine0','SKEL_Spine1','SKEL_Spine2','SKEL_Spine3'}
samples=[]
for v in body.data.vertices:
 p=body.matrix_world@v.co
 if not 96<=p.z<=123:continue
 weights={body.vertex_groups[g.group].name:g.weight for g in v.groups if body.vertex_groups[g.group].name in torso}
 total=sum(weights.values())
 if total>.5:samples.append((p,{n:w/total for n,w in weights.items()}))
assert len(samples)>30,len(samples)
tree=KDTree(len(samples))
for i,(p,w) in enumerate(samples):tree.insert(p,i)
tree.balance()
targets=['SM_L_FrontSkirtRoll','SM_R_FrontSkirtRoll','SM_L_BackSkirtRoll','SM_R_BackSkirtRoll']
for name in targets+list(torso):
 if not dress.vertex_groups.get(name):dress.vertex_groups.new(name=name)
deform={g.index:g for g in dress.vertex_groups if g.name in arm.data.bones}
def smooth(v):
 v=max(0,min(1,v));return v*v*(3-2*v)
changed=pinned=0
for v in dress.data.vertices:
 p=dress.matrix_world@v.co
 if p.z>=118:continue
 old={dress.vertex_groups[g.group].name:g.weight for g in v.groups if g.group in deform}
 sampled={};total=0
 for _,i,d in tree.find_n(p,4):
  a=1/max(.15,d)**2;total+=a
  for n,w in samples[i][1].items():sampled[n]=sampled.get(n,0)+a*w
 sampled={n:w/total for n,w in sampled.items()}
 pin=1-smooth((p.z-113)/5)
 base={n:w*(1-pin) for n,w in old.items()}
 for n,w in sampled.items():base[n]=base.get(n,0)+w*pin
 a=smooth((108-p.z)/20)
 left=max(0,min(1,.5+p.x/20));front=max(0,min(1,.5-p.y/16))
 values={n:w*(1-a) for n,w in base.items()}
 for n,w in zip(targets,[left*front,(1-left)*front,left*(1-front),(1-left)*(1-front)]):values[n]=values.get(n,0)+w*a
 for group in deform.values():group.remove([v.index])
 values=dict(sorted(values.items(),key=lambda item:-item[1])[:8]);total=sum(values.values());assert total>0
 for n,w in values.items():
  if w>1e-6:dress.vertex_groups[n].add([v.index],w/total,'REPLACE')
 # A small radial clearance, tapered out above the waist. No body geometry changes.
 clearance=.5*(1-smooth((p.z-108)/8))+1.0*smooth((106-p.z)/16)
 radial=p.copy();radial.z=0
 if radial.length>5:
  p+=radial.normalized()*clearance;v.co=dress.matrix_world.inverted()@p
 changed+=1
 if a==0 and pin>.99:pinned+=1
assert changed>1000 and pinned>20,(changed,pinned)
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.context.scene.objects:
 if obj.type in {'MESH','ARMATURE'}:obj.select_set(True)
bpy.context.view_layer.objects.active=arm
bpy.ops.wm.save_as_mainfile(filepath=str(O/'2B-skirt110.blend'))
bpy.ops.export_scene.fbx(filepath=str(O/'2B-skirt110.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',path_mode='STRIP')
print('HCX_SKIRT36_READY','torso_samples',len(samples),'dress_vertices',changed,'fully_pinned',pinned,'bones',len(arm.data.bones))
