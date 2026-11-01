"""Creates editor-only comparison assets; nothing is packaged or installed."""
import unreal as u,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];D='/Game/Hcx2B/Diagnostics';tools=u.AssetToolsHelpers.get_asset_tools()
def duplicate(name,src):
 return u.load_asset(D+'/'+name) or tools.duplicate_asset(name,D,u.load_asset(src))
target=duplicate('SK_2B_Preview','/Game/Hcx2B/SK_2B');target.set_editor_property('post_process_anim_blueprint',None)
source=duplicate('SK_Soul_Preview','/Game/Hcx2B/SK_SourceHun');source.set_editor_property('post_process_anim_blueprint',None)
gray=u.load_asset(D+'/M_Soul_Preview') or tools.create_asset('M_Soul_Preview',D,u.Material,u.MaterialFactoryNew())
e=u.MaterialEditingLibrary.create_material_expression(gray,u.MaterialExpressionConstant3Vector);e.constant=u.LinearColor(.25,.38,.45,1);u.MaterialEditingLibrary.connect_material_property(e,'',u.MaterialProperty.MP_BASE_COLOR);u.MaterialEditingLibrary.recompile_material(gray)
slots=source.get_editor_property('materials')
if not slots:slots=[u.SkeletalMaterial(material_interface=gray,material_slot_name='Gray')]
else:
 for i in range(len(slots)):
  s=slots[i];s.material_interface=gray;slots[i]=s
source.set_editor_property('materials',slots)
slots=target.get_editor_property('materials')
for i in range(len(slots)):
 s=slots[i];slot_name=str(s.material_slot_name);key=next(p.stem for p in (R/'output/2B-default/textures').glob('*diff*.png') if slot_name.startswith(p.stem));name='M_Preview_'+key
 mat=u.load_asset(D+'/'+name) or tools.create_asset(name,D,u.Material,u.MaterialFactoryNew())
 path=R/'output/2B-default/textures'/(key+'.png');assert path.exists(),path
 tex=u.load_asset(D+'/T_'+key)
 if not tex:
  task=u.AssetImportTask();task.filename=str(path);task.destination_path=D;task.destination_name='T_'+key;task.automated=True;task.save=True;tools.import_asset_tasks([task]);tex=u.load_asset(D+'/T_'+key)
 expr=u.MaterialEditingLibrary.create_material_expression(mat,u.MaterialExpressionTextureSample);expr.texture=tex
 u.MaterialEditingLibrary.connect_material_property(expr,'RGB',u.MaterialProperty.MP_BASE_COLOR)
 u.MaterialEditingLibrary.recompile_material(mat);s.material_interface=mat;slots[i]=s
target.set_editor_property('materials',slots)
for obj in [target,source,gray]:u.EditorAssetLibrary.save_loaded_asset(obj,only_if_is_dirty=False)
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
if u.EditorAssetLibrary.does_asset_exist(D+'/L_MotionComparison'):assert level.load_level(D+'/L_MotionComparison')
else:assert level.new_level(D+'/L_MotionComparison')
u.log('HCX_SCENE_NEW_LEVEL')
actors=u.get_editor_subsystem(u.EditorActorSubsystem);pairs=[]
for existing in list(actors.get_all_level_actors()):
 if isinstance(existing,(u.SkeletalMeshActor,u.DirectionalLight,u.SkyLight,u.StaticMeshActor,u.CameraActor)):actors.destroy_actor(existing)
def spawn(cls,location,rotation=u.Rotator()):
 return u.HcxRetargetTools.spawn_preview_actor(cls,u.Transform(location=location,rotation=rotation))
for label,mesh,x in [('Soul source',source,-150),('2B baseline',target,0),('2B thigh follow test',target,150)]:
 a=spawn(u.SkeletalMeshActor,u.Vector(x,0,0));assert a;a.set_actor_label(label)
 u.log('HCX_SCENE_ACTOR_SPAWNED '+label)
 component=a.get_editor_property('skeletal_mesh_component');component.set_skeletal_mesh_asset(mesh);component.set_animation_mode(u.AnimationMode.ANIMATION_SINGLE_NODE);pairs.append(a)
 u.log('HCX_SCENE_ACTOR '+label)
light=spawn(u.DirectionalLight,u.Vector(0,0,300),u.Rotator(-45,-60,0));light.light_component.set_editor_property('intensity',3.0)
ambient=spawn(u.SkyLight,u.Vector(0,0,300));ambient.light_component.set_editor_property('intensity',1.0)
floor=spawn(u.StaticMeshActor,u.Vector(0,0,-5));floor.static_mesh_component.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cube'));floor.set_actor_scale3d(u.Vector(9,6,.1))
camera_location=u.Vector(0,600,150);camera=spawn(u.CameraActor,camera_location,u.MathLibrary.find_look_at_rotation(camera_location,u.Vector(0,0,100)));camera.set_actor_label('Comparison Camera');camera.camera_component.set_editor_property('field_of_view',50.0)
seq=u.load_asset(D+'/LS_MotionComparison') or tools.create_asset('LS_MotionComparison',D,u.LevelSequence,u.LevelSequenceFactoryNew())
u.log('HCX_SCENE_SEQUENCE_CREATED')
for binding in list(seq.get_bindings()):binding.remove()
for old in list(seq.get_tracks()):seq.remove_track(old)
seq.set_display_rate(u.FrameRate(30,1));seq.set_playback_start(0)
segments=json.loads((R/'output/animation-preview/preview-segments.json').read_text())
seq.set_playback_end(segments[-1]['end']+1)
for i,a in enumerate(pairs):
 binding=seq.add_possessable(a);track=binding.add_track(u.MovieSceneSkeletalAnimationTrack)
 for segment in segments:
  prefix=D+('/ThighFollow' if i==2 else '')+'/A_'+segment['clip'];suffix='_Soul' if i==0 else '_2B_Baseline'
  anim=u.load_asset(prefix+suffix);assert anim,prefix+suffix
  section=track.add_section();section.set_range(segment['start'],segment['end']+1)
  params=section.get_editor_property('params');params.animation=anim;section.set_editor_property('params',params)
binding=seq.add_possessable(camera);cuts=seq.add_track(u.MovieSceneCameraCutTrack);cut=cuts.add_section();cut.set_range(0,segments[-1]['end']+1)
camera_id=u.MovieSceneObjectBindingID();camera_id.set_editor_property('guid',binding.get_id());cut.set_camera_binding_id(camera_id)
u.EditorAssetLibrary.save_directory(D,only_if_is_dirty=False);assert level.save_current_level()
u.log('HCX_PREVIEW_SCENE_READY '+seq.get_path_name())
