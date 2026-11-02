import unreal as u
from pathlib import Path
import json

root = Path(__file__).resolve().parents[2]
(root / 'output/2B-retarget').mkdir(parents=True, exist_ok=True)
bp = u.load_asset('/Game/Hcx2B/ABPT_2B_Adult')
assert bp
result = u.HcxRetargetTools.make_player_build(bp)
assert result.startswith('OK:'), result
for name in ['ABPT_2B_Adult', 'ABP_2B_Adult']:
    asset = u.load_asset('/Game/Hcx2B/' + name)
    u.BlueprintEditorLibrary.compile_blueprint(asset)
    u.EditorAssetLibrary.save_loaded_asset(asset, only_if_is_dirty=False)
cdo = u.get_default_object(bp.generated_class())
names = ['HcxFootRequestedL', 'HcxFootRequestedR', 'HcxWidthCm', 'HcxKneeCm',
         'HcxBlendSeconds', 'HcxIdleWidthCm', 'HcxIdleKneeCm', 'HcxSkirtWeight',
         'HcxSkirtSpring', 'HcxChestAmount', 'HcxChestSpring', 'HcxFootPreview']
defaults = {name: cdo.get_editor_property(name) for name in names}
(root / 'output/2B-retarget/player52-setup.json').write_text(
    json.dumps({'graph': result, 'defaults': defaults}, indent=2), encoding='utf-8')
u.log('HCX_PLAYER52_READY ' + result)
