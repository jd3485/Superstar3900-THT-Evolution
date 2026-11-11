#!/usr/bin/env python3
"""V2.0 positive BOM/pinout-to-footprint coverage gate. Explicitly BLOCK fabrication.
Never claim all footprints production-fit merely because KiCad ERC is 0.
"""
import csv,re,json,sys
from pathlib import Path
repo=Path(__file__).resolve().parents[2]
sch=(repo/"04_KiCad/V2.0/POWER20_VTUNE_BOOST_LDO_V2.0.kicad_sch").read_text()
bom=list(csv.DictReader((repo/"07_Componenti/BOM_DELTA_VTUNE20_V2.0.csv").open()))
expected={"U911","U912","L920","D920","D921","D922"}|{f"R{i}" for i in range(920,928)}|{f"C{i}" for i in range(920,930)}
assert len(expected)==24
got={}
for b in re.finditer(r'\(symbol \(lib_id "THT_V20:[^"]+"\).*?\(property "Reference" "([A-Z]+\d+)" \(at .*?\(property "Footprint" "([^"]*)"',sch,re.S):
 ref,foot=b.group(1),b.group(2)
 if ref in got:raise AssertionError(f"Duplicate physical THT ref {ref}")
 if ref in expected:got[ref]=foot
if got.keys()!=expected:raise AssertionError(f"Physical BOM not exact: missing={expected-got.keys()} extra={got.keys()-expected}")
refbom={r["reference"]:r for r in bom if r["reference"]!="PWR920"}
if refbom.keys()!=expected:raise AssertionError("BOM delta references do not match native schematic components")
allowed=("Package_DIP:","Package_TO_SOT_THT:","Diode_THT:","Resistor_THT:","Capacitor_THT:")
unresolved=[]
for ref,foot in got.items():
 spec=refbom[ref]
 if ref=="L920":
  if foot!="":raise AssertionError("L920 inductor footprint added without independent mechanical qualification")
  unresolved.append(ref)
 elif not foot.startswith(allowed):
  raise AssertionError(f"Non-THT or missing footprint on {ref}: {foot}")
 elif spec["footprint_proposed"]!=foot:
  raise AssertionError(f"BOM != schematic footprint {ref}: {foot} {spec['footprint_proposed']}")
 if "SMT" in foot or "_SMD" in foot:raise AssertionError("SMD footprint violates THT-only constraint")
if unresolved!=["L920"]:raise AssertionError("Incorrect missing-footprint manifest")
assert '(property "Reference" "PWR920"' in sch
if len([r for r in bom if r["reference"]=="PWR920"])!=1:raise AssertionError("ERC marker BOM provenance missing")
report={"status":"PASS_THT_ONLY_BOM_TO_KICAD_FOOTPRINT_CONSISTENCY_BUT_FAB_BLOCKED",
"new_real_components":len(expected),"BOM_rows_including_nonphysical_ERC":len(bom),
"physical_THT_footprint_candidates":len(expected)-len(unresolved),
"missing_physical_footprints":unresolved,
"capacitor_exact_MPNs":"NOT_SELECTED",
"input_F701_D702_footprints":"STILL_UNRESOLVED_BEFORE_PRODUCTION",
"LM317_tab_to_case_insulation":"NOT_VERIFIED",
"mechanical_fit_and_clearances":"NOT_VERIFIED",
"PCB_exists":False,"fab_authorized":False,"tx_authorized":False}
out=repo/"03_Verifiche/V2.0/native_results/bom_footprint_v20.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,sort_keys=True))
