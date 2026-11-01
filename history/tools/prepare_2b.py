import bpy, sys, json, math
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/2B-default'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'2B-imported.blend'))
arm = bpy.data.objects['2B']
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
checks = []
for obj in meshes:
    world = obj.matrix_world.copy()
    for mod in obj.modifiers:
        if mod.type == 'ARMATURE' and mod.object != arm:
            old = mod.object
            used = {obj.vertex_groups[g.group].name for v in obj.data.vertices for g in v.groups if g.weight > 0}
            max_delta = max(abs(old.data.bones[name].matrix_local[r][c]-arm.data.bones[name].matrix_local[r][c]) for name in used for r in range(4) for c in range(4))
            checks.append({'mesh':obj.name,'old_armature':old.name,'weighted_bones':sorted(used),'max_weighted_rest_matrix_delta':max_delta})
            print('REST_DIFFERENCE', obj.name, old.name, max_delta, flush=True)
            if max_delta > 0.0001:
                for b in arm.data.bones:
                    delta=max(abs(old.data.bones[b.name].matrix_local[r][c]-b.matrix_local[r][c]) for r in range(4) for c in range(4))
                    if delta>0.0001: print('BONE_DIFFERENCE',b.name,delta,flush=True)
                raise RuntimeError('Skeleton rest matrices differ; do not merge automatically')
            mod.object = arm
    obj.name = obj.parent.name + '_mesh'
    obj.parent = arm
    obj.matrix_world = world
for obj in list(bpy.context.scene.objects):
    if obj not in meshes and obj != arm:
        bpy.data.objects.remove(obj, do_unlink=True)
texout = OUT/'textures'
texout.mkdir(exist_ok=True)
for img in bpy.data.images:
    if img.source == 'FILE' and img.size[0] > 0:
        _ = img.pixels[0]
        img.filepath_raw = str(texout/(Path(img.name).stem+'.png'))
        img.file_format = 'PNG'
        img.save()
for mat in bpy.data.materials:
    if not mat.use_nodes: continue
    n = mat.node_tree.nodes
    print('MATERIAL_INPUT',mat.name,[(x.name,x.type,getattr(getattr(x,'image',None),'name',None)) for x in n if x.type=='TEX_IMAGE'],flush=True)
    diffuse = n.get('DiffuseSampler')
    image = diffuse.image if diffuse else None
    mat.node_tree.nodes.clear()
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = 0.65
    output = n.new('ShaderNodeOutputMaterial')
    mat.node_tree.links.new(bsdf.outputs['BSDF'],output.inputs['Surface'])
    if image and image.has_data:
        tex = n.new('ShaderNodeTexImage'); tex.image = image
        mat.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color'])
        mat.node_tree.links.new(tex.outputs['Alpha'],bsdf.inputs['Alpha'])
        mat.blend_method = 'CLIP'; mat.alpha_threshold=0.4
    else:
        bsdf.inputs['Base Color'].default_value=(0.12,0.12,0.12,1)
bpy.ops.object.select_all(action='DESELECT')
for obj in meshes+[arm]: obj.select_set(True)
bpy.context.view_layer.objects.active=arm
bpy.ops.export_scene.fbx(filepath=str(OUT/'2B-gta-skeleton.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',path_mode='COPY',embed_textures=True)
(OUT/'skeleton-merge-check.json').write_text(json.dumps(checks,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'2B-conversion.blend'))
# Neutral inspection render; all imported component choices are deliberately visible.
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=800;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.world.color=(0.15,0.15,0.15)
scene.view_settings.view_transform='Standard'
scene.view_settings.look='Medium High Contrast'
for loc,power,size in [((2,-4,4),450,4),((-3,-2,2),300,3),((0,3,3),500,3)]:
    data=bpy.data.lights.new('Inspection light','AREA');data.energy=power;data.size=size
    obj=bpy.data.objects.new(data.name,data);scene.collection.objects.link(obj);obj.location=loc
    obj.rotation_euler=(Vector((0,0,0.9))-obj.location).to_track_quat('-Z','Y').to_euler()
data=bpy.data.cameras.new('Inspection camera');cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam)
scene.camera=cam;data.type='ORTHO';data.ortho_scale=2.05
corners=[obj.matrix_world@Vector(c) for obj in meshes for c in obj.bound_box]
center=Vector(tuple((min(v[i] for v in corners)+max(v[i] for v in corners))/2 for i in range(3)))
data.ortho_scale=(max(v.z for v in corners)-min(v.z for v in corners))*1.12
for label,loc in [('front',(0,-4,0.85)),('back',(0,4,0.85))]:
    cam.location=(center.x,loc[1],center.z);cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(OUT/f'preview-{label}.png');bpy.ops.render.render(write_still=True)
print('PREPARE_OK',sum(len(o.data.polygons) for o in meshes))
