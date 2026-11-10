#!/usr/bin/env python3
"""Native KiCad exported netlist: 5V supply pin-level electrical assertions, NOT bench approval."""
import json,runpy,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
read=runpy.run_path(str(root/"03_Verifiche/V1.0/verify_kicad_netlist_v10.py"))["read_nets"]
nets=read(Path(sys.argv[1]))
need={
 "+13V8_PROTECTED":{("J601","1"),("U601","1"),("C600","1"),("C601","1"),("D601","1")},
 "+5V_REG":{("U601","3"),("D601","2"),("C602","1"),("C603","1"),("R611","1"),("R612","1"),("R613","1"),("J605","1")},
 "GND":{("U601","2"),("J601","2"),("J602","2"),("J603","2"),("J604","2"),("J605","2"),
        ("C600","2"),("C601","2"),("C602","2"),("C603","2"),
        ("C611","2"),("C612","2"),("C613","2"),("C614","2"),("C615","2"),("C616","2")},
 "+5V_PLL":{("R611","2"),("C611","1"),("C614","1"),("J602","1")},
 "VCC_VCO5":{("R612","2"),("C612","1"),("C615","1"),("J603","1")},
 "VCC_BUF5":{("R613","2"),("C613","1"),("C616","1"),("J604","1")},
}
if set(nets)!=set(need):raise AssertionError("Unexpected net list "+repr(sorted(set(nets)^set(need))))
for name,pins in need.items():
 actual=nets.get(name,set())
 if actual!=pins:raise AssertionError(name+" missing="+repr(sorted(pins-actual))+" excess="+repr(sorted(actual-pins)))
if any(need[x]&need[y] for x in need for y in need if x!=y):
 raise AssertionError("Pin double assigned")
# Exactly 3 regulator pins (datasheet 1 VIN, 2 GND, 3 VOUT); reverse diode K=1 to 13.8, A=2 to 5V.
allpins={p:n for n,ps in nets.items() for p in ps}
for ref,n in [("U601",3),("D601",2),("R611",2),("R612",2),("R613",2)]:
 if len([p for p in allpins if p[0]==ref])!=n:raise AssertionError("Pin count mismatch "+ref)
result={"status":"PASS_THT_NATIVE_5V_SUPPLY_NETS_ONLY","verified_nets":len(need),
"separate_5v_branches":True,"regulator_pinmap":"U601 VIN1 GND2 VOUT3","D601_orientation":"K1 13.8V / A2 5V",
"no_input_protection":True,"branch_current_qualified":False,"thermal_qualified":False,"production_pcb":False,
"RF_qualification":"NOT_RUN","fab_authorized":False,"tx_authorized":False}
Path(sys.argv[1]).parent.joinpath("v15_net_evidence.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result))
