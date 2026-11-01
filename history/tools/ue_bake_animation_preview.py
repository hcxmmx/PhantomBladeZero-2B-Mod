import unreal as u
from pathlib import Path
R=Path(__file__).resolve().parents[2]; folder=R/'work/animation-preview'; out=R/'output/animation-preview';out.mkdir(exist_ok=True)
source=u.load_asset('/Game/Hcx2B/SK_SourceHun');target=u.load_asset('/Game/Hcx2B/SK_2B');rtg=u.load_asset('/Game/Hcx2B/RTG_2B_Adult')
for path in sorted((folder/'extract').glob('*-samples.json')):
    name=path.name.removesuffix('-samples.json')
    assert u.HcxRetargetTools.bake_diagnostic_animation(source,target,rtg,str(path),'/Game/Hcx2B/Diagnostics',str(out/(name+'-baseline.json'))),name
    for suffix in ['_Soul','_2B_Baseline']:
        obj=u.load_object(None,'/Game/Hcx2B/Diagnostics/A_'+name+suffix)
        assert obj
        u.EditorAssetLibrary.save_loaded_asset(obj,only_if_is_dirty=False)
    u.log('HCX_ANIMATION_PREVIEW_READY '+name)
