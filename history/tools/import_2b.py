"""Run with portable Blender 3.6 --background --factory-startup --python this-file."""
import sys, json, os, shutil
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
os.environ['BLENDER_USER_CONFIG'] = str(ROOT / 'work/blender-config')
Path(os.environ['BLENDER_USER_CONFIG']).mkdir(parents=True, exist_ok=True)
import addon_utils
addon_utils.enable('Sollumz', default_set=True, persistent=False)
from Sollumz.sollumz_preferences import get_import_settings
from Sollumz.ydd.yddimport import import_ydd
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
settings = get_import_settings()
settings.import_ext_skeleton = True
settings.split_by_group = False
texture_dir = ROOT / 'work/2B-default-xml/2B'
texture_dir.mkdir(exist_ok=True)
for dds in (ROOT / 'work/2B-default-xml').glob('*.dds'):
    shutil.copy2(dds, texture_dir / dds.name)
root = import_ydd(str(ROOT / 'work/2B-default-xml/2B.ydd.xml'))
out = ROOT / 'output/2B-default'
out.mkdir(parents=True, exist_ok=True)
report = {'blender': bpy.app.version_string, 'objects': [], 'images': []}
for obj in bpy.context.scene.objects:
    row = {'name': obj.name, 'type': obj.type, 'parent': obj.parent.name if obj.parent else None, 'sollum_type':getattr(obj,'sollum_type',''), 'dimensions':list(obj.dimensions)}
    if obj.type == 'ARMATURE':
        row['bones'] = [{'name': b.name, 'parent': b.parent.name if b.parent else None} for b in obj.data.bones]
    if obj.type == 'MESH':
        mesh = obj.data
        mesh.calc_loop_triangles()
        row.update(vertices=len(mesh.vertices), triangles=len(mesh.loop_triangles), materials=[m.name if m else None for m in mesh.materials], vertex_groups=len(obj.vertex_groups), unweighted_vertices=sum(not any(g.weight > 0 for g in v.groups) for v in mesh.vertices), modifiers=[{'type':m.type,'object':getattr(getattr(m,'object',None),'name',None)} for m in obj.modifiers])
    report['objects'].append(row)
for img in bpy.data.images:
    report['images'].append({'name':img.name,'path':img.filepath,'size':list(img.size),'has_data':img.has_data})
    if img.has_data and img.source == 'FILE':
        img.pack()
(out/'import-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'2B-imported.blend'))
print('IMPORT_REPORT',json.dumps({'meshes':sum(o['type']=='MESH' for o in report['objects']), 'armatures':sum(o['type']=='ARMATURE' for o in report['objects'])}))
