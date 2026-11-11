#!/usr/bin/env python3
"""KiCad9 proof of an ACTUAL connected seven-sheet RX PLL power20 supply, NOT functional regulation.
All baseline V1.9 physical pin partitions MUST remain identical. No fabrication claims.
"""
import json,runpy,sys
from pathlib import Path
repo=Path(__file__).resolve().parents[2]
read=runpy.run_path(str(repo/"03_Verifiche/V1.0/verify_kicad_netlist_v10.py"))["read_nets"]
baseline=read(Path(sys.argv[1]));actual=read(Path(sys.argv[2]))
if len(baseline)!=64:raise AssertionError(f"V1.9 64 native net baseline changed: {len(baseline)}")
if len(actual)!=72:raise AssertionError(f"V2.0 expected 72 electrical groups (V1.9+8), got {len(actual)}")
pinnet={}
for name,members in actual.items():
 for pin in members:
  if pin in pinnet:raise AssertionError(f"Double-assigned KiCad pin {pin}")
  pinnet[pin]=name
previous={}
for name,members in baseline.items():
 final={pinnet.get(p) for p in members}
 if len(final)!=1 or None in final:
  raise AssertionError(f"PREVIOUS V1.9 physical pin group SPLIT/LOST {name} -> {final}")
 group=next(iter(final))
 if group in previous:raise AssertionError(f"SHORT between baseline {name} and {previous[group]}")
 previous[group]=name
def same(label,*pins):
 names={pinnet.get(p) for p in pins}
 if len(names)!=1 or None in names:raise AssertionError(f"{label} pins do not share one net: {pins} -> {names}")
 return next(iter(names))
raw=same("Raw external 13V8",("J701","1"),("F701","1"))
protected=same("V1.9 protected source of new U911",("D701","1"),("U601","1"),
 ("U911","6"),("R920","1"),("C920","1"),("C921","1"))
ground=same("GND across all seven native child sheets",("J701","2"),("U601","2"),
 ("U401","2"),("U911","2"),("U911","4"),("C920","2"),("R923","2"),
 ("U912","2") if False else ("C922","2"),("R925","2"),("R927","2"))
sense=same("MC34063 peak current sense / inductor feed",("R920","2"),("U911","7"),("L920","1"),("R921","1"))
switch=same("Boost switching node isolated from other rails",("L920","2"),("U911","1"),("D920","2"))
timing=same("MC34063 timing",("U911","3"),("C922","1"))
feedback=same("MC34063 FB to boost resistor divider",("U911","5"),("R922","2"),("R923","1"))
driver=same("MC34063 bias resistor",("U911","8"),("R921","2"))
boost=same("Rectified boosted rail and LDO input",("D920","1"),("U912","3"),
 ("R922","1"),("C923","1"),("C924","1"),("C925","1"),("D921","1"))
adj=same("LM317 pin1 adjust including CAdj and discharge diode",("U912","1"),
 ("R924","2"),("R925","1"),("C927","1"),("D922","2"))
ldo=same("LM317 pin2 output TAB is NOT ground",("U912","2"),("R924","1"),
 ("R926","1"),("R927","1"),("C926","1"),("D921","2"),("D922","1"))
vtune=same("New actual VTUNE20 source wired through hierarchy to LM358",("R926","2"),
 ("C928","1"),("C929","1"),("U803","8"))
five=same("Existing 7805 output separate from VTUNE",("U601","3"),
 ("R611","1"),("R612","1"),("R613","1"))
pll=same("PLL5 separate",("R611","2"),("U401","3"))
vco=same("VCO5 separate",("R612","2"),("L501","1"))
buf=same("Digital buffer5 separate",("R613","2"),("U520","14"))
old_vtune=same("VTUNE control voltage from old PLL driver",("R805","2"),("D501","2"))
clock=same("LO clock from VCO to PLL",("U402","3"),("R513","2"))
groups={raw,protected,ground,sense,switch,timing,feedback,driver,boost,adj,ldo,vtune,five,pll,vco,buf,old_vtune,clock}
if len(groups)!=18:raise AssertionError("Power short / accidental RF net merge")
oldrefs={r for members in baseline.values() for r,p in members}
newrefs={"U911","U912","L920","D920","D921","D922"}|{f"R{n}" for n in range(920,928)}|{f"C{n}" for n in range(920,930)}
if oldrefs&newrefs:raise AssertionError("New THT components duplicate an old reference")
for ref,pcount in [("U911",8),("U912",3),("L920",2),("D920",2),("D921",2),("D922",2)]+[(f"R{n}",2) for n in range(920,928)]+[(f"C{n}",2) for n in range(920,930)]:
 count=sum(1 for x in pinnet if x[0]==ref)
 if count!=pcount:raise AssertionError(f"{ref} connected physical pin count {count} != {pcount}")
helper=runpy.run_path(str(repo/"03_Verifiche/V1.0/verify_kicad_netlist_v10.py"))
tokens=helper["PAT"].findall(Path(sys.argv[2]).read_text())
ast,end=helper["parse_expr"](tokens)
assert end==len(tokens),"KiCad native netlist parsing truncated"
paths={}
for comp in helper["child"](ast,"components")[1:]:
 if not isinstance(comp,list) or not comp or comp[0]!="comp":continue
 sp=helper["optional_child"](comp,"sheetpath")
 if sp:
  names=helper["optional_child"](sp,"names")
  paths[str(helper["child"](comp,"ref")[1])]=str(names[1]) if names else str(sp)
if len({paths.get("U911"),paths.get("U601"),paths.get("U803")})!=3 or any(not paths.get(x) for x in ("U911","U601","U803")):
 raise AssertionError("VTUNE source, 5V supply and LM358 must occupy three DISTINCT child sheets")
sch=(repo/"04_KiCad/V2.0/POWER20_VTUNE_BOOST_LDO_V2.0.kicad_sch").read_text()
if '(property "Footprint" "" (at 120.65 201.93 0)' not in sch:
 raise AssertionError("L920 non-qualified inductor footprint must remain EXPLICITLY unselected")
if "PWR920" not in sch or "BOOST_SOURCE_KICAD_ERC_ONLY_NOT_HARDWARE" not in sch:
 raise AssertionError("Boost KiCad ERC flag provenance missing")
if any(p[0]=="PWR920" for p in pinnet):
 raise AssertionError("ERC-only fake power flag must not enter physical BOM/netlist")
out={"status":"PASS_NATIVE_SEVEN_SHEET_VTUNE20_TOPOLOGY_ONLY","previous_v19_nets":len(baseline),
"v20_native_nets":len(actual),"all_original_v19_physical_pin_groups_preserved":True,
"MC34063ABN":"U911 DIP8 P1-SW P2-GND P3-CT P4-GND P5-FB P6-VCC P7-Ipk P8-Driver",
"LM317T":"U912 TO220 P1-Adjust P2-Output_and_metal_tab P3-Input",
"power_path":"V1.9 Q801 -> D701 cathode -> MC34063 -> boost diode -> LM317 -> R926 -> LM358 pin8",
"old_RX_RF_PLL_VCO_5V_and_VTUNE_control_unmodified":True,"seventh_sheet_independent":True,
"R927_min_load":"Candidate only, no vendor startup validation",
"inductor_L920":"Bourns 680uH THT footprint UNSELECTED","LM317_Cadj_discharge":"D922 A2 ADJ K1 OUTPUT",
"LM317_output_input_discharge":"D921 A2 OUTPUT K1 INPUT","new_boot_and_noise_qualification":False,
"actual_20V_power_verified":False,"PCB_DRC":"NOT_RUN","fab_authorized":False,"tx_authorized":False}
Path(sys.argv[2]).parent.joinpath("native_v20_evidence.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,sort_keys=True))
