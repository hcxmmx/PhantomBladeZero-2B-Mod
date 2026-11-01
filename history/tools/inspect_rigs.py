import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'output/2B-default/2B-conversion.blend'))
src=bpy.data.objects['2B']; source=[o for o in bpy.context.scene.objects if o.type=='MESH']
bpy.ops.import_scene.gltf(filepath=str(ROOT/'work/pbz/exported/HuaShira/Characters/Hero/Hero_Hun/SkinParts/Hun_Body_Simple.glb'))
tgt=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE' and o!=src)
def row(a):
 return {'name':a.name,'world':[list(r) for r in a.matrix_world],'bones':{b.name:{'head':list(a.matrix_world@b.head_local),'tail':list(a.matrix_world@b.tail_local),'parent':b.parent.name if b.parent else None} for b in a.data.bones}}
report={'source':row(src),'target':row(tgt),'weights':sorted({g.name for o in source for g in o.vertex_groups if any(vg.group==g.index and vg.weight>0 for v in o.data.vertices for vg in v.groups)})}
(ROOT/'work/rig-comparison.json').write_text(json.dumps(report,indent=2))
for a,names in [(src,['SKEL_ROOT','SKEL_Pelvis','SKEL_Head','SKEL_L_UpperArm','SKEL_L_Forearm','SKEL_L_Hand','SKEL_L_Thigh','SKEL_L_Foot']),(tgt,['root','pelvis','head','upperarm_l','lowerarm_l','hand_l','thigh_l','foot_l'])]:
 print(a.name,[(n,[round(v,4) for v in a.matrix_world@a.data.bones[n].head_local]) for n in names])
print('WEIGHTED_BONES',report['weights'])
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'work/rig-comparison.blend'))
