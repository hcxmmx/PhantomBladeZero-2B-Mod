"""One-variable wider-trajectory comparison on top of 0.2.13, not yet activated."""
import unreal as u,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'work/gait-width';O.mkdir(exist_ok=True);D='/Game/Hcx2B';tools=u.AssetToolsHelpers.get_asset_tools()
bp=u.load_asset(D+'/ABPT_2B_Wide')
if not bp:
 bp=tools.duplicate_asset('ABPT_2B_Wide',D,u.load_asset(D+'/ABPT_2B_DirectLegs'));assert bp
 result=u.HcxRetargetTools.build_width_graph(bp,(R/'output/gait-width/runtime-settings.json').read_text(encoding='utf-8'));assert result=='OK',result
 u.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
child=u.load_asset(D+'/ABP_2B_Wide')
if not child:
 factory=u.AnimBlueprintFactory();factory.set_editor_property('parent_class',u.EditorAssetLibrary.load_blueprint_class(D+'/ABPT_2B_Wide'));factory.set_editor_property('target_skeleton',u.load_asset(D+'/SK_2B_Skeleton'));child=tools.create_asset('ABP_2B_Wide',D,u.AnimBlueprint,factory)
u.BlueprintEditorLibrary.compile_blueprint(child);u.EditorAssetLibrary.save_loaded_asset(child,only_if_is_dirty=False)
source=u.load_asset(D+'/SK_SourceHun');target=u.load_asset(D+'/SK_2B');rtg=u.load_asset(D+'/RTG_2B_DirectLegs');baseline=u.load_asset(D+'/ABP_2B_DirectLegs');last=None
for path in sorted((R/'work/gait-diagnosis/extract-v2').rglob('*-samples.json')):
 name=path.name.removesuffix('-samples.json');package=D+'/Diagnostics/Width/'+name
 assert u.HcxRetargetTools.bake_diagnostic_animation(source,target,rtg,str(path),package,str(O/(name+'-native.json')))
 seq=u.load_asset(package+'/A_'+name+'_Soul');assert seq;last=seq
 assert u.HcxRetargetTools.capture_gait_cycle(source,target,seq,baseline,child,str(O/(name+'-cycle.json')))
 u.log('HCX_WIDTH_CYCLE '+name)
check=json.loads(u.HcxRetargetTools.check_gait_gate(child,source,target,last))
for row in check['cases']:
 if row['state']=='moving_ground':assert row['width_weight']>.99,row
 else:assert row['width_weight']==0,row
(O/'movement-gate.json').write_text(json.dumps(check,indent=2),encoding='utf-8')
u.log('HCX_WIDTH_TEST_READY')
