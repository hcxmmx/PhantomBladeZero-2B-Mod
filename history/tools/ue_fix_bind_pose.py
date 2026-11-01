import unreal as u,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
report=json.loads((ROOT/'output/2B-prototype/ue-import-report.json').read_text())
reference=json.loads((ROOT/'work/pbz/Hun_Body_Simple-reference.json').read_text())
mesh=u.load_asset(report['mesh']);modifier=u.SkeletonModifier()
assert modifier.set_skeletal_mesh(mesh)
original={b['Name'].lower():(b,p) for b,p in zip(reference['FinalRefBoneInfo'],reference['FinalRefBonePose'])}
names=list(modifier.get_all_bone_names());transforms=[]
assert len(names)==264,len(names)
for name in names:
 b,p=original[str(name).lower()]
 actual_parent=str(modifier.get_parent_name(name)).lower()
 expected_parent=reference['FinalRefBoneInfo'][b['ParentIndex']]['Name'].lower() if b['ParentIndex']>=0 else 'none'
 assert actual_parent==expected_parent,(name,actual_parent,expected_parent)
 t=u.Transform()
 t.translation=u.Vector(**{k.lower():v for k,v in p['Translation'].items()})
 q=p['Rotation'];t.rotation=u.Quat(q['X'],q['Y'],q['Z'],q['W'])
 s=p['Scale3D'];t.scale3d=u.Vector(s['X'],s['Y'],s['Z'])
 transforms.append(t)
assert modifier.set_bones_transforms(names,transforms,True)
assert modifier.commit_skeleton_to_skeletal_mesh()
u.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
u.EditorAssetLibrary.save_directory('/HuaShira',only_if_is_dirty=False,recursive=True)
(ROOT/'output/2B-prototype/bind-pose-repair.json').write_text(json.dumps({'bones':len(names),'mesh':report['mesh'],'source':'original Hun_Body_Simple reference transforms'},indent=2))
u.log('BIND_POSE_FIXED '+str(len(names)))
