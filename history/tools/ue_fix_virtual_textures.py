import unreal as u,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'output/2B-retarget';tools=u.AssetToolsHelpers.get_asset_tools();mapping=json.loads((O/'direct-material-map.json').read_text())
for row in mapping:
 for spec in row['overrides']:
  if spec['kind']=='Mix':
   folder,name=spec['target'].rsplit('/',1);t=u.AssetImportTask();t.filename=str(O/'neutral_ARM.png');t.destination_path=folder;t.destination_name=name;t.automated=True;t.replace_existing=True;t.save=True;tools.import_asset_tasks([t])
  tex=u.load_asset(spec['target']);assert isinstance(tex,u.Texture2D)
  tex.set_editor_property('virtual_texture_streaming',True)
  tex.set_editor_property('srgb',spec['kind'] in ['Albedo','Basecolor'])
  if spec['kind']=='Normal':tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_NORMALMAP)
  u.EditorAssetLibrary.save_loaded_asset(tex,only_if_is_dirty=False)
u.log('HCX_VIRTUAL_TEXTURES_READY 20 game-path texture replacements')
