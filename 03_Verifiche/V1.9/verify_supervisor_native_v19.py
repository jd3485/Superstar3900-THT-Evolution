#!/usr/bin/env python3
"""Native KiCad9 V1.9 full pin-partition proof; the only intentional split is
three V1.8 supervisor-power/sense pins moved from FUSED_RAW to D804 cathode.
NOT a reverse-battery qualification or a claim of OVP safety.
"""
import json,runpy,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
read=runpy.run_path(str(root/"03_Verifiche/V1.0/verify_kicad_netlist_v10.py"))["read_nets"]
old=read(Path(sys.argv[1]));new=read(Path(sys.argv[2]))
assert len(old)==63,f"V1.8 baseline changed: {len(old)}"
assert len(new)==64,f"V1.9 expected 64 net groups (63+1 control rail): {len(new)}"
where={}
for name,members in new.items():
 for p in members:
  if p in where:raise AssertionError(f"Duplicate pin {p}")
  where[p]=name
migrated={("U801","8"),("R1001","1"),("R1002","1")}
def net(name,*pins):
 matches={where.get(p) for p in pins}
 if len(matches)!=1 or None in matches:raise AssertionError(f"{name}: {pins} => {matches}")
 return next(iter(matches))
previous={}
old_refs={p[0] for members in old.values() for p in members}
for label,members in old.items():
 keep=members-migrated
 if not keep:raise AssertionError(f"Lost old net {label}")
 newnet={where.get(p) for p in keep}
 if len(newnet)!=1 or None in newnet:raise AssertionError(f"Old net split: {label} -> {newnet}")
 n=next(iter(newnet))
 if n in previous:raise AssertionError(f"Short merged prior nets: {label} with {previous[n]}")
 previous[n]=label
 for p in members:
  if p not in where:raise AssertionError(f"Legacy component pin lost {p}")
expected_new_refs={"D804","D805","PWR802"}
assert not old_refs&expected_new_refs,"New references collide with prior design"
raw=net("Raw supply",("J701","1"),("F701","1"))
fused=net("Fused raw domain",("F701","2"),("D702","1"),("Q801","3"),("D803","1"),
 ("R1008","1"),("PWR801","1"),("D804","2"))
ctrl=net("Reverse-isolated control supply",("D804","1"),("D805","1"),
 ("U801","8"),("R1001","1"),("R1002","1"),("PWR802","1"))
gnd=net("Shared GND",("D805","2"),("D702","2"),("U601","2"),("U801","4"),
 ("J701","2"),("U401","2"))
ovp=net("PMOS downstream path",("Q801","2"),("D701","2"))
protected=net("5V regulator protected input",("D701","1"),("U601","1"))
vref=net("TL431 reference unchanged",("U802","1"),("U802","3"),("R1001","2"),
 ("R1004","1"),("R1006","1"))
sense=net("Now protected raw-sensing divider",("R1002","2"),("R1003","1"),("U801","2"))
gate=net("PMOS gate",("Q801","1"),("R1008","2"),("D803","2"),("R1009","1"))
five=net("7805 output",("U601","3"),("R611","1"),("R612","1"),("R613","1"))
pll=net("PLL 5V branch",("R611","2"),("U401","3"))
vco=net("VCO 5V branch",("R612","2"),("L501","1"))
lo=net("LO 5V branch",("R613","2"),("U520","14"))
assert len({raw,fused,ctrl,gnd,ovp,protected,vref,sense,gate,five,pll,vco,lo})==13,"Power short"
for ref in ("D804","D805"):
 assert sum(p[0]==ref for p in where)==2,f"{ref} pin connectivity"
assert sum(p[0]=="PWR802" for p in where)==1
assert net("Original VTUNE link",("D501","2"),("R805","2"))
assert net("Original LO buffered clock",("U402","3"),("R513","2"))
no=where.get(("U801","7"))
assert no and no.startswith("unconnected-") and new[no]=={("U801","7")},"U801/7 isolated NC missing"
sch=(root/"04_KiCad/V1.9/INPUT_FUSE_REVERSE_TVS_OVP_V1.9.kicad_sch").read_text()
needle='(property "Footprint" "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" (at 254 242.57 0)'
if needle not in sch or 'VISHAY_PR01000103301JR500_3K3_1W' not in sch:
 raise AssertionError("R1001 physical 1W Vishay PR01 or footprint missing")
evidence={"status":"PASS_V19_NATIVE_KICAD_SUPERVISOR_REVERSE_RAIL_TOPOLOGY_ONLY",
"v18_original_groups":len(old),"v19_groups":len(new),"v19_new_power_net":"OVP_CTL_VCC",
"all_original_net_partitions_preserved_except_3_moved_supervisor_pins":True,
"moved_pins":sorted(map(str,migrated)),"D804":"A2_FUSED_RAW_K1_OVP_CTL_VCC",
"D805":"A2_GND_K1_OVP_CTL_VCC_REVERSE_LEAKAGE_CLAMP",
"R1001":"Vishay_PR01000103301JR500_3k3_1W_THT_footprint_selected_not_board_verified",
"old_RF_PLL_VTUNE_nets_preserved":True,"U801_7_explicit_no_connect":True,
"reverse_battery_qualification":"NOT_TESTED","actual_reverse_leakage":"NOT_MEASURED",
"control_input_max36V":"STILL_UNPROTECTED_ABOVE_LIMIT",
"fuse_TVS_source_coordination":"NOT_RUN","resistor_derating_at_temperature":"NOT_QUALIFIED",
"vendor_SPICE":"NOT_USED","PCB_DRC":"NOT_RUN","fab_authorized":False,"tx_authorized":False}
Path(sys.argv[2]).parent.joinpath("v19_native_evidence.json").write_text(json.dumps(evidence,indent=2)+"\n")
print(json.dumps(evidence,sort_keys=True))
