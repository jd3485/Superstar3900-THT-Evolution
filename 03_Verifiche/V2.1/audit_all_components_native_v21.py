#!/usr/bin/env python3
"""Independent native KiCad9 BOM->footprint coverage for ALL seven sheets.
A passing audit is only a truthful statement of residual gaps, never fab approval.
"""
from pathlib import Path
import json,runpy,sys
repo=Path(__file__).resolve().parents[2]
h=runpy.run_path(str(repo/"03_Verifiche/V1.0/verify_kicad_netlist_v10.py"))
tokens=h["PAT"].findall(Path(sys.argv[1]).read_text())
ast,end=h["parse_expr"](tokens)
assert end==len(tokens) and ast[0]=="export"
seen={}
for c in h["child"](ast,"components")[1:]:
 if not isinstance(c,list) or not c or c[0]!="comp":continue
 ref=str(h["child"](c,"ref")[1]); fp=h["optional_child"](c,"footprint")
 assert ref not in seen,("Duplicated ref",ref)
 seen[ref]=str(fp[1]) if fp and len(fp)>1 else ""
for ref,name in [("F701","Fuse_Littelfuse_PICOII_0251_500MXL_P12.70mm"),
                 ("D702","TVS_ST_P6KE20CA_DO15_P12.70mm")]:
 assert seen.get(ref)=="THT_V21:"+name,(ref,seen.get(ref))
 assert (repo/"04_KiCad/V2.1/THT_V21.pretty"/(name+".kicad_mod")).exists()
for mandatory in ("L501","L920","U911","U912","U601","U401","Q801","U801"):
 assert mandatory in seen,("lost seven-sheet CAD physical component",mandatory)
missing=sorted(ref for ref,fp in seen.items() if not fp)
# Neither inductor's pitch is known/approved: do not hide lack of a physical package.
assert "L501" in missing and "L920" in missing,("review expected unresolved RF/boost inductors",missing)
explicit_smd={ref:fp for ref,fp in seen.items() if any(marker in fp for marker in ("_SMD","Package_QFN","Package_DFN","Package_BGA","Package_SOIC","Package_SOT-23"))}
assert not explicit_smd,"THT-only violated: "+repr(explicit_smd)
report={"status":"PASS_V21_HONEST_SEVEN_SHEET_COMPONENT_FOOTPRINT_AUDIT",
 "real_references":len(seen),"references_with_footprint":sum(bool(x) for x in seen.values()),
 "references_missing_footprint":missing,"missing_count":len(missing),
 "must_select_and_qualify_L501_vco_and_L920_boost_before_PCB":True,
 "F701_and_D702_assigned":True,"no_explicit_SMD_footprints":True,
 "complete_RX_RF_IF_audio_controller":"NOT_DESIGNED",
 "PCB_radio_layout":"NOT_STARTED","PCB_DRC":"NOT_RUN",
 "fuse_TVS_automotive_qualification":False,"fab_authorized":False,"tx_authorized":False}
dst=Path(sys.argv[1]).parent/"v21_component_footprint_audit.json"
dst.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,sort_keys=True))
