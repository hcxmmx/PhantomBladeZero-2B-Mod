import unreal as u,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];D='/Game/Hcx2B';O=R/'output/scale-study/115/motion';O.mkdir(parents=True,exist_ok=True)
source=u.load_asset(D+'/SK_SourceHun');target=u.load_asset(D+'/SK_2B');rtg=u.load_asset(D+'/RTG_2B_Adult')
paths=list((R/'work/pelvis-diagnosis').glob('*-samples.json'))+list((R/'work/animation-preview/extract').glob('*-samples.json'))
for path in sorted(paths):
 name=path.name.removesuffix('-samples.json')
 assert u.HcxRetargetTools.bake_diagnostic_animation(source,target,rtg,str(path),D+'/Diagnostics/Scaled115',str(O/(name+'-scaled115.json')))
u.log('HCX_115_ALL_SIX_MOTION_OUTPUTS_READY')
