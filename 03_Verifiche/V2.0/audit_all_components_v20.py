#!/usr/bin/env python3
"""Independently parse entire KiCad9 exported netlist for component/footprint coverage.
Pass means honest coverage report, not release of an incomplete radio or PCB.
"""
from pathlib import Path
import json,runpy,sys
root=Path(__file__).resolve().parents[2]
helper=runpy.run_path(str(root/"03_Verifiche/V1.0/verify_kicad_netlist_v10.py"))
source=Path(sys.argv[1]).read_text()
tokens=helper["PAT"].findall(source)
ast,end=helper["parse_expr"](tokens)
assert end==len(tokens) and ast[0]=="export"
components=helper["child"](ast,"components")
child=helper["child"];optional=helper["optional_child"]
results={}
for c in components[1:]:
 if not isinstance(c,list) or not c or c[0]!="comp":continue
 ref=str(child(c,"ref")[1])
 fp=optional(c,"footprint")
 footprint=str(fp[1]) if fp and len(fp)>1 else ""
 assert ref not in results,"Duplicate designator in KiCad BOM: "+ref
 results[ref]=footprint
for name,footprint in {
 "F701":"THT_V20:Fuse_Littelfuse_PICOII_0251_500MXL_P12.70mm",
 "D702":"THT_V20:TVS_ST_P6KE20CA_DO15_P12.70mm"
}.items():
 assert results.get(name)==footprint,(name,results.get(name))
 if not (root/"04_KiCad/V2.0/THT_V20.pretty"/(footprint.split(":")[1]+".kicad_mod")).exists():
  raise AssertionError(f"No real custom KiCad footprint for {name}")
explicit_smd={ref:fp for ref,fp in results.items() if any(z in fp for z in ("_SMD", "Package_DFN", "Package_QFN", "Package_SO", "BGA", "LGA"))}
assert not explicit_smd,"THT-only project accidentally assigned surface-mount footprint: "+repr(explicit_smd)
missing=sorted(ref for ref,fp in results.items() if not fp)
resolved=sum(bool(fp) for fp in results.values())
report={"status":"PASS_HONEST_NATIVE_BOM_FOOTPRINT_COVERAGE_AUDIT",
 "partially_implemented_6_sheet_RX_only":True,
 "non_board_power_flags_excluded_by_KiCad":True,
 "real_components_exported":len(results),
 "components_with_explicit_footprint":resolved,
 "components_missing_footprint":len(missing),
 "missing_references":missing,
 "F701_and_D702_now_resolved":True,
 "THT_mandate_no_explicit_SMD_footprints":True,
 "manufacturer_mounting_pitch_12p70_approval":False,
 "full_radio_component_set":"INCOMPLETE",
 "PCB_layout":"DOES_NOT_EXIST",
 "pcb_drc":"NOT_RUN",
 "fab_authorized":False,"tx_authorized":False}
dst=Path(sys.argv[1]).parent/"v20_component_footprint_coverage.json"
dst.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({k:v for k,v in report.items() if k!="missing_references"},sort_keys=True))
