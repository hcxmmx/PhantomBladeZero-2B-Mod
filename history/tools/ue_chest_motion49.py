import unreal as u
D='/Game/Hcx2B'
bp=u.load_asset(D+'/ABPT_2B_Adult');assert bp
result=u.HcxRetargetTools.build_chest_motion(bp);assert result=='OK',result
for name in ['ABPT_2B_Adult','ABP_2B_Adult','WBP_SkirtControls34']:
 asset=u.load_asset(D+'/'+name);assert asset
 u.BlueprintEditorLibrary.compile_blueprint(asset);u.EditorAssetLibrary.save_loaded_asset(asset,only_if_is_dirty=False)
u.log('HCX_CHEST49_READY')
