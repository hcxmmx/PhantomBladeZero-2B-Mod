import unreal as u
D='/Game/Hcx2B'
widget=u.load_asset(D+'/WBP_SkirtControls34');assert widget
for name,value in [('AmountSlider',.6),('SpringSlider',145.)]:
 slider=u.find_object(widget,'WidgetTree.'+name)
 assert slider,(name,'template slider not found')
 slider.set_value(value)
 u.log('SKIRT_DEFAULT '+slider.get_path_name()+' = '+str(value))
for name,text in [('AmountValue','0.6'),('SpringValue','145')]:
 label=u.find_object(widget,'WidgetTree.'+name);assert label
 label.set_text(u.Text(text))
u.BlueprintEditorLibrary.compile_blueprint(widget)
u.EditorAssetLibrary.save_loaded_asset(widget,only_if_is_dirty=False)
u.log('HCX_SKIRT35_DEFAULTS_READY')
