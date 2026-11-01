import unreal as u
D='/Game/Hcx2B'
for path in [D+'/SK_2B','/HuaShira/Characters/Hero/Hero_Hun/SkinParts/Hun_Hair_Band']:
 mesh=u.load_asset(path);assert mesh
 result=u.HcxRetargetTools.refine_skirt_cloth(mesh);assert result.startswith('OK '),(path,result)
 u.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
 u.log('HCX_CLOTH42_CLEARANCE '+path+' '+result)
physics=u.load_asset(D+'/PA_2B_Cloth37');assert physics;u.EditorAssetLibrary.save_loaded_asset(physics,only_if_is_dirty=False)
widget=u.load_asset(D+'/WBP_SkirtControls34');assert widget
u.find_object(widget,'WidgetTree.Title').set_text(u.Text('2B Cloth 0.2.42 / F9'))
u.BlueprintEditorLibrary.compile_blueprint(widget);u.EditorAssetLibrary.save_loaded_asset(widget,only_if_is_dirty=False)
u.log('HCX_CLOTH42_CLEARANCE_READY')
