"""Read-only runtime graph cycle capture from corrected, case-insensitive game samples."""
import unreal as u,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'work/gait-diagnosis';O.mkdir(exist_ok=True);D='/Game/Hcx2B'
source=u.load_asset(D+'/SK_SourceHun');target=u.load_asset(D+'/SK_2B');rtg=u.load_asset(D+'/RTG_2B_Adult');base=u.load_asset(D+'/ABP_2B_Adult');current=u.load_asset(D+'/ABP_2B_Hip')
for path in sorted((O/'extract-v2').rglob('*-samples.json')):
 name=path.name.removesuffix('-samples.json');package=D+'/Diagnostics/CorrectedGait/'+name
 if not (O/(name+'-cycle.json')).exists():
  assert u.HcxRetargetTools.bake_diagnostic_animation(source,target,rtg,str(path),package,str(O/(name+'-native-v2.json')))
  sequence=u.load_asset(package+'/A_'+name+'_Soul');assert sequence
  assert u.HcxRetargetTools.capture_gait_cycle(source,target,sequence,base,current,str(O/(name+'-cycle.json')))
 u.log('HCX_GAIT_CYCLE_CAPTURED '+name)
c=u.IKRetargeterController.get_controller(rtg);report={'retargeter':rtg.get_path_name(),'ops':[],'rigs':{}}
for i in range(c.get_num_retarget_ops()):
 op=c.get_op_controller(i);settings=op.get_settings();row={'name':str(c.get_op_name(i)),'settings_text':settings.export_text()}
 report['ops'].append(row)
for name in ['IK_Source','IK_2B']:
 rig=u.load_asset(D+'/'+name);rc=u.IKRigController.get_controller(rig);report['rigs'][name]={'root':str(rc.get_retarget_root()),'chains':[{'name':str(ch.chain_name),'start':str(rc.get_retarget_chain_start_bone(ch.chain_name)),'end':str(rc.get_retarget_chain_end_bone(ch.chain_name)),'ik_goal':str(rc.get_retarget_chain_goal(ch.chain_name)),'source_chain':str(c.get_source_chain(ch.chain_name))} for ch in rc.get_retarget_chains()]}
(O/'retarget-config-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.log('HCX_GAIT_DIAGNOSIS_CAPTURE_COMPLETE')
