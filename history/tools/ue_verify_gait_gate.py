import unreal as u,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];D='/Game/Hcx2B';source=u.load_asset(D+'/SK_SourceHun');target=u.load_asset(D+'/SK_2B');base=u.load_asset(D+'/RTG_2B_Adult');path=R/'work/gait-study/extract/Hun_DoubleBlade_Sprint_Loop-samples.json'
assert u.HcxRetargetTools.bake_diagnostic_animation(source,target,base,str(path),D+'/Diagnostics/GaitGate',str(R/'work/gait-study/gate-source.json'))
sequence=u.load_object(None,D+'/Diagnostics/GaitGate/A_Hun_DoubleBlade_Sprint_Loop_Soul');assert sequence
result=json.loads(u.HcxRetargetTools.check_gait_gate(u.load_asset(D+'/ABP_2B_Gait'),source,target,sequence))
(R/'output/gait-study/gate-verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8');u.log('HCX_GAIT_GATE_RESULT '+json.dumps(result))
assert result['source_move_curve']>10,result
assert result['source_montage_playing'],result
moving=next(x for x in result['cases'] if x['state']=='moving_ground');assert max(moving['left_alpha'],moving['right_alpha'])>0.01,moving
for row in result['cases']:
 assert 0<=row['left_alpha']<=1 and 0<=row['right_alpha']<=1,row
 if row['state']!='moving_ground':assert row['left_alpha']==row['right_alpha']==0,row
u.log('HCX_GAIT_GATE_PASSED')
