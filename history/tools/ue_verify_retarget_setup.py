import unreal as u,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'output/2B-retarget';dest='/Game/Hcx2B'
exec((R/'tools/ue_build_ik.py').read_text(encoding='utf-8-sig'))
report={};mesh=u.load_asset(dest+'/SK_2B');mod=u.SkeletonModifier();assert mod.set_skeletal_mesh(mesh);assert len(mod.get_all_bone_names())==107
slots=mesh.get_editor_property('materials');assert len(slots)==9
for slot in slots:
 mat=slot.material_interface;assert isinstance(mat,u.MaterialInstanceConstant)
 assert mat.get_editor_property('parent').get_path_name()=='/Game/PBZContent/Characters/Hero/Hun_New_V2b/Material/MI_ZeroHun_Cloth_03_b.MI_ZeroHun_Cloth_03_b'
 params=mat.get_editor_property('texture_parameter_values');assert len(params)==2
 for p in params:assert p.parameter_value and p.parameter_info.association==u.MaterialParameterAssociation.LAYER_PARAMETER and p.parameter_info.index==0
assets=json.loads((O/'asset-setup.json').read_text());assert all(u.load_asset(p) for p in assets['empty_overrides'])
report={'target_bones':107,'source_bones':264,'mapped_chains':len(chains),'retarget_ops':['Pelvis Motion','FK Chains'],'material_instances':9,'layer_texture_overrides':18,'textures':assets['textures'],'empty_overrides':len(assets['empty_overrides']),'blueprint_compilation':'pending MSVC update','in_game_2B_validation':'pending'}
(O/'precompile-verification.json').write_text(json.dumps(report,indent=2));u.log('HCX_PRECOMPILE_CHECK_OK '+json.dumps(report))
