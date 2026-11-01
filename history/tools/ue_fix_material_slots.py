import unreal as u,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
report=json.loads((ROOT/'output/2B-prototype/ue-import-report.json').read_text())
mesh=u.load_asset(report['mesh']);slots=mesh.get_editor_property('materials');result=[]
for index in range(len(slots)):
 slot=slots[index];name=str(slot.material_slot_name)
 path='/Game/Hcxmmx2B/Materials/M_'+name.replace('.','_')
 material=u.load_asset(path)
 assert material,(index,path)
 slot.material_interface=material
 slots[index]=slot
 result.append({'index':index,'slot':name,'material':path})
mesh.set_editor_property('materials',slots)
u.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
for index,slot in enumerate(mesh.get_editor_property('materials')):
 assert slot.material_interface,(index,str(slot.material_slot_name))
(ROOT/'output/2B-prototype/material-slot-repair.json').write_text(json.dumps(result,indent=2))
u.log('MATERIAL_SLOTS_FIXED '+str(len(result)))
