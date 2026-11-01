import unreal as u,json
from pathlib import Path
D='/Game/Hcx2B/Diagnostics';level=u.get_editor_subsystem(u.LevelEditorSubsystem)
assert level.load_level(D+'/L_MotionComparison')
seq=u.load_asset(D+'/LS_MotionComparison');assert seq
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors();skeletal=[a for a in actors if isinstance(a,u.SkeletalMeshActor)]
assert len(skeletal)==3,len(skeletal)
assert len(seq.get_bindings())==4
sections=[]
for binding in seq.get_bindings():
 for track in binding.get_tracks():
  if isinstance(track,u.MovieSceneSkeletalAnimationTrack):
   for section in track.get_sections():
    params=section.get_editor_property('params');assert params.animation
    sections.append(params.animation.get_path_name())
assert len(sections)==9,sections
assert any(isinstance(t,u.MovieSceneCameraCutTrack) for t in seq.get_tracks())
for path in ['SK_2B_Preview','SK_Soul_Preview']:
 mesh=u.load_asset(D+'/'+path);assert mesh;assert mesh.get_editor_property('post_process_anim_blueprint') is None
result={'fresh_editor_reload':True,'skeletal_actors':3,'bindings':4,'animation_sections':9,'camera_cut_track':True,'animation_assets':sections}
(Path(__file__).resolve().parents[2]/'output/animation-preview/ue-scene-verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
u.log('HCX_MOTION_LAB_RELOAD_OK')
