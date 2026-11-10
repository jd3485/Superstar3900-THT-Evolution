#!/usr/bin/env python3
"""KiCad9 native 6-sheet pin-net continuity and 13V8 input protection topology gate.
Only CAD connectivity is asserted; no surge immunity, fuse coordination, RF or fab approval.
"""
import json, runpy, sys
from pathlib import Path
repo=Path(__file__).resolve().parents[2]
read=runpy.run_path(str(repo/"03_Verifiche/V1.0/verify_kicad_netlist_v10.py"))["read_nets"]
before=read(Path(sys.argv[1]));after=read(Path(sys.argv[2]))
if len(before)!=52:raise AssertionError(f"Expected V1.6 native 52 groups, got {len(before)}")
if len(after)!=54:raise AssertionError(f"Expected V1.7 native 54 groups, got {len(after)}")
pins={}
for net, members in after.items():
 for p in members:
  if p in pins:raise AssertionError(f"Pin on two nets {p}")
  pins[p]=net
if any(p[0]=="J601" for p in pins):raise AssertionError("Legacy J601 bypass input must be physically removed")
mapped={}
for net, members in before.items():
 included={p for p in members if p[0]!="J601"}
 if not included:raise AssertionError("Removing J601 unexpectedly deleted a whole legacy net")
 destinations={pins.get(p) for p in included}
 if len(destinations)!=1 or None in destinations:
  raise AssertionError(f"Original V1.6 pin group broken: {net} {destinations}")
 dest=next(iter(destinations))
 if dest in mapped:raise AssertionError(f"Two formerly distinct V1.6 nets SHORTED: {mapped[dest]} and {net}")
 mapped[dest]=net
def group(label,*expected):
 dests={pins.get(p) for p in expected}
 if len(dests)!=1 or None in dests:raise AssertionError(f"{label} disconnected: {expected}: {dests}")
 return next(iter(dests))
raw=group("raw external supply",("J701","1"),("F701","1"))
fused=group("fuse output and TVS clamp",("F701","2"),("D701","2"),("D702","1"))
protected=group("Schottky cathode to 7805 input",("D701","1"),("U601","1"),("C600","1"),("C601","1"))
ground=group("same physical ground",("J701","2"),("D702","2"),("U601","2"),("U401","2"),("U520","7"))
five=group("regulated 5V still distinct",("U601","3"),("R611","1"),("R612","1"),("R613","1"))
pll=group("separate PLL 5V",("R611","2"),("U401","3"))
vco=group("separate VCO 5V",("R612","2"),("L501","1"))
buf=group("separate LO buffer 5V",("R613","2"),("U520","14"))
if len({raw,fused,protected,ground,five,pll,vco,buf})!=8:
 raise AssertionError("Unexpected protective input, GND or 5V rail SHORT")
group("VTUNE preserved",("D501","2"),("R805","2"))
group("LO buffer feedback preserved",("U402","3"),("R513","2"))
for ref,number in [("J701",2),("F701",2),("D701",2),("D702",2),("U601",3)]:
 if len([p for p in pins if p[0]==ref])!=number:raise AssertionError(f"{ref} pin count wrong")
helper=runpy.run_path(str(repo/"03_Verifiche/V1.0/verify_kicad_netlist_v10.py"))
tokens=helper["PAT"].findall(Path(sys.argv[2]).read_text())
ast,end=helper["parse_expr"](tokens)
if end!=len(tokens):raise AssertionError("Trailing KiCad netlist parse")
sp={}
for comp in helper["child"](ast,"components")[1:]:
 if not isinstance(comp,list) or not comp or comp[0]!="comp":continue
 sheet=helper["optional_child"](comp,"sheetpath")
 if sheet:
  names=helper["optional_child"](sheet,"names")
  sp[str(helper["child"](comp,"ref")[1])]=str(names[1]) if names else str(sheet)
if not sp.get("F701") or not sp.get("U601") or sp["F701"]==sp["U601"]:
 raise AssertionError("F701 and U601 not in distinct native child sheets")
protection=(repo/"04_KiCad/V1.7/INPUT_FUSE_REVERSE_TVS_V1.7.kicad_sch").read_text()
power=(repo/"04_KiCad/V1.7/POWER5_DISTRIBUTION_V1.7.kicad_sch").read_text()
if '(property "Reference" "J601"' in power or '(property "Reference" "PWR601"' in power:
 raise AssertionError("Upstream power test bypass J601 or obsolete power flag remains")
if protection.count('(property "Footprint" ""')<2:
 raise AssertionError("Missing explicit unselected safety footprints")
out={"status":"PASS_NATIVE_6_SHEET_13V8_PROTECTION_TOPOLOGY_ONLY",
     "baseline_v16_nets":len(before),"integrated_v17_nets":len(after),
     "all_existing_component_pin_net_partitions_preserved_except_removed_J601":True,
     "legacy_bypass_J601":"REMOVED","fuse_F701_series":True,"D701":"ANODE2_FUSED_CATHODE1_PROTECTED",
     "TVS_D702":"BIDIRECTIONAL_ACROSS_FUSED_RAW_AND_GND",
     "regulator_plus_5V_rails_isolated":True,"child_sheetpaths_distinct":True,
     "continuous_overvoltage_disconnect":"NOT_DESIGNED","source_fault_current":"UNKNOWN",
     "fuse_DC_I2t_coordination":"NOT_RUN","surge_reverse_battery_qualification":"NOT_RUN",
     "fuse_and_TVS_footprint":"UNSELECTED","thermal_hardware":"NOT_RUN",
     "RF_PLL_lock":"NOT_RUN","PCB_DRC":"NOT_RUN","fab_authorized":False,"tx_authorized":False}
Path(sys.argv[2]).parent.joinpath("native_v17_evidence.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,sort_keys=True))
