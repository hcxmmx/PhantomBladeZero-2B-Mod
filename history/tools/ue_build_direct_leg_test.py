"""Single-variable trial: leg FK rotation sampling, movement-only and no extra offsets."""
import unreal as u,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'work/gait-direct';O.mkdir(exist_ok=True);D='/Game/Hcx2B';tools=u.AssetToolsHelpers.get_asset_tools();base=u.load_asset(D+'/RTG_2B_Adult')
rtg=u.load_asset(D+'/RTG_2B_DirectLegs') or tools.duplicate_asset('RTG_2B_DirectLegs',D,base);c=u.IKRetargeterController.get_controller(rtg);assert c.get_num_retarget_ops()==4
op=c.get_op_controller(2);settings=op.get_settings();chains=list(settings.chains_to_retarget);changed=[]
for i,row in enumerate(chains):
 if str(row.target_chain_name) in ['Leg_l','Leg_r']:
  changed.append(str(row.target_chain_name));row.rotation_mode=u.FKChainRotationMode.ONE_TO_ONE;chains[i]=row
settings.chains_to_retarget=chains;op.set_settings(settings);assert sorted(changed)==['Leg_l','Leg_r'];u.EditorAssetLibrary.save_loaded_asset(rtg,only_if_is_dirty=False)
bp=u.load_asset(D+'/ABPT_2B_DirectLegs')
if not bp:
 bp=tools.duplicate_asset('ABPT_2B_DirectLegs',D,u.load_asset(D+'/ABPT_2B_Adult'));assert bp
 result=u.HcxRetargetTools.build_movement_leg_graph(bp,base,rtg);assert result=='OK',result
 u.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
child=u.load_asset(D+'/ABP_2B_DirectLegs')
if not child:
 factory=u.AnimBlueprintFactory();factory.set_editor_property('parent_class',u.EditorAssetLibrary.load_blueprint_class(D+'/ABPT_2B_DirectLegs'));factory.set_editor_property('target_skeleton',u.load_asset(D+'/SK_2B_Skeleton'));child=tools.create_asset('ABP_2B_DirectLegs',D,u.AnimBlueprint,factory)
u.BlueprintEditorLibrary.compile_blueprint(child);u.EditorAssetLibrary.save_loaded_asset(child,only_if_is_dirty=False)
source=u.load_asset(D+'/SK_SourceHun');target=u.load_asset(D+'/SK_2B');baseline=u.load_asset(D+'/ABP_2B_Adult');last=None
for path in sorted((R/'work/gait-diagnosis/extract-v2').rglob('*-samples.json')):
 name=path.name.removesuffix('-samples.json');package=D+'/Diagnostics/DirectLegs/'+name
 assert u.HcxRetargetTools.bake_diagnostic_animation(source,target,rtg,str(path),package,str(O/(name+'-direct-native.json')))
 seq=u.load_asset(package+'/A_'+name+'_Soul');assert seq;last=seq
 assert u.HcxRetargetTools.capture_gait_cycle(source,target,seq,baseline,child,str(O/(name+'-cycle.json')))
 u.log('HCX_DIRECT_LEG_CYCLE '+name)
check=json.loads(u.HcxRetargetTools.check_gait_gate(child,source,target,last))
for row in check['cases']:
 if row['state']=='moving_ground':assert row['left_alpha']>.99 and row['right_alpha']>.99,row
 else:assert row['left_alpha']==row['right_alpha']==0,row
(O/'movement-gate.json').write_text(json.dumps(check,indent=2),encoding='utf-8')
(O/'retarget-change.json').write_text(json.dumps({'base':base.get_path_name(),'candidate':rtg.get_path_name(),'changed_chains':changed,'sole_setting_change':'FK rotation_mode Interpolated -> OneToOne','foot_width_offset_cm':0,'fk_settings':settings.export_text()},indent=2),encoding='utf-8')
u.log('HCX_DIRECT_LEG_TEST_READY')
