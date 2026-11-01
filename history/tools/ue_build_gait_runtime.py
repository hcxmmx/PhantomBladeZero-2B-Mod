"""Build isolated runtime gait assets. Main display mesh is changed only after verification."""
import unreal as u
from pathlib import Path
R=Path(__file__).resolve().parents[2];D='/Game/Hcx2B';tools=u.AssetToolsHelpers.get_asset_tools();base=u.load_asset(D+'/RTG_2B_Adult');variants=[]
for side in ['L','R']:
 name='RTG_2B_Gait'+side;rtg=u.load_asset(D+'/'+name) or tools.duplicate_asset(name,D,base);c=u.IKRetargeterController.get_controller(rtg);assert c.get_num_retarget_ops()==4
 i=c.add_retarget_op('/Script/IKRig.IKRetargetAlignPoleVectorOp');c.run_op_initial_setup(i);op=c.get_op_controller(i);settings=op.get_settings();rows=list(settings.chains_to_align)
 for n,row in enumerate(rows):
  row.enabled=str(row.target_chain_name)=='Leg_'+side.lower();row.align_alpha=0.;row.static_angular_offset=(-10. if side=='L' else 10.);rows[n]=row
 settings.chains_to_align=rows;op.set_settings(settings);assert c.move_retarget_op_in_stack(i,3);u.EditorAssetLibrary.save_loaded_asset(rtg,only_if_is_dirty=False);variants.append(rtg)
template=u.load_asset(D+'/ABPT_2B_Gait') or tools.duplicate_asset('ABPT_2B_Gait',D,u.load_asset(D+'/ABPT_2B_Adult'))
result=u.HcxRetargetTools.build_gait_graph(template,base,variants[0],variants[1]);assert result=='OK',result
u.EditorAssetLibrary.save_loaded_asset(template,only_if_is_dirty=False)
child=u.load_asset(D+'/ABP_2B_Gait')
if not child:
 factory=u.AnimBlueprintFactory();factory.set_editor_property('parent_class',u.EditorAssetLibrary.load_blueprint_class(D+'/ABPT_2B_Gait'));factory.set_editor_property('target_skeleton',u.load_asset(D+'/SK_2B_Skeleton'))
 child=tools.create_asset('ABP_2B_Gait',D,u.AnimBlueprint,factory)
u.BlueprintEditorLibrary.compile_blueprint(child);u.EditorAssetLibrary.save_loaded_asset(child,only_if_is_dirty=False)
u.log('HCX_GAIT_RUNTIME_BLUEPRINTS_BUILT')
