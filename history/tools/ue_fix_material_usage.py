import unreal as u,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
rows=[]
for path in u.EditorAssetLibrary.list_assets('/Game/Hcxmmx2B/Materials',recursive=True):
 mat=u.load_asset(path)
 u.MaterialEditingLibrary.set_material_usage(mat,u.MaterialUsage.MATUSAGE_SKELETAL_MESH)
 u.MaterialEditingLibrary.recompile_material(mat)
 u.EditorAssetLibrary.save_loaded_asset(mat,only_if_is_dirty=False)
 rows.append({'material':path,'skeletal_usage':u.MaterialEditingLibrary.has_material_usage(mat,u.MaterialUsage.MATUSAGE_SKELETAL_MESH)})
(ROOT/'output/2B-prototype/material-usage.json').write_text(json.dumps(rows,indent=2))
u.log('MATERIAL_USAGE_OK '+str(len(rows)))
