import unreal as u,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];dest='/Game/Hcx2B';source=u.load_asset(dest+'/SK_SourceHun');target=u.load_asset(dest+'/SK_2B');rtg=u.load_asset(dest+'/RTG_2B_Adult')
for mesh in [source,target]:u.HcxRetargetTools.sync_reference_pose(mesh);u.EditorAssetLibrary.save_loaded_asset(mesh.skeleton,only_if_is_dirty=False)
bp=u.load_asset(dest+'/ABP_2B_Adult');u.BlueprintEditorLibrary.compile_blueprint(bp);u.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
r=json.loads(u.HcxRetargetTools.check_retarget_motion(source,target,rtg));assert r['ok'],r
(R/'output/2B-retarget/retarget-motion-verification.json').write_text(json.dumps(r,indent=2));u.log('HCX_RETARGET_MOTION_OK '+json.dumps(r))
