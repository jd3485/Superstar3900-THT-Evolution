#!/usr/bin/env python3
"""Check actual native KiCad 9 exported pins across previously ISOLATED CAD-01/02.
This PASS means only wiring; PLL stabilization, hardware, master hierarchy & PCB are NOT_RUN.
"""
import json,runpy,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
read=runpy.run_path(str(root/"03_Verifiche/V1.0/verify_kicad_netlist_v10.py"))["read_nets"]
nets=read(Path(sys.argv[1]))
req={
 "PLL_PDOUT_3STATE":{("U401","4"),("R901","1"),("J401","1"),("J901","1")},
 "PD_FILTER":{("R901","2"),("C901","1"),("U803","3")},
 "PLL_FB_18M":{("U401","1"),("U402","5")},
 "DIV2_QBAR":{("U402","2"),("U402","6")},
 "OPA_FB_A":{("U803","2"),("R803","2"),("R804","1")},
 "OPA_OUT_A":{("U803","1"),("R803","1"),("R805","1")},
 "OPA_OUT_B":{("U803","6"),("U803","7")},
 "VANA20_FILT":{("J902","1"),("U803","8"),("C803","1")},
 "+5V_PLL":{("U401","3"),("U402","14"),("J402","1")},
 "GND":{("U401","2"),("U402","7"),("U803","4"),("J901","2"),("J402","2")},
 "VTUNE_RAIL":{("R805","2"),("J903","1")},
 "LO1_CMOS_BUFFERED":{("J403","1"),("U402","3")},
 "XTAL_IN":{("U401","27"),("X401","2")},
 "XTAL_DRIVE":{("U401","26"),("X401","1")},
 "PRESCALER_RESET_N":{("U402","1"),("J404","1")},
 "PLL_LD_OBSERVE":{("U401","28"),("J406","1")}
}
for i in range(12):req[f"N_CODE_{i}"]={("U401",str(i+11 if i<=9 else i+14)),("J405",str(i+1))}
missing=[]
for net,need in req.items():
 actual=nets.get(net,set())
 if not need.issubset(actual):missing.append(f"{net} lacks {sorted(need-actual)} actual {sorted(actual)}")
for net in ("+5V_PLL","VANA20_FILT","GND","PD_FILTER","VTUNE_RAIL","PLL_PDOUT_3STATE"):
 if net not in nets:missing.append("No separate net "+net)
for net in ("PLL_FB_18M","DIV2_QBAR"):
 if len(nets.get(net,set()))!=2:missing.append(net+" has unintended pins")
if missing:raise AssertionError("V1.2 INTEGRATION FAIL:\n"+"\n".join(missing))
allpins={pin:n for n,pins in nets.items() for pin in pins}
for ref,expect in (("U401",28),("U402",14),("U803",8)):
 count=len([p for p in allpins if p[0]==ref])
 if count!=expect:raise AssertionError(f"{ref}: only {count} of {expect} pins appear in netlist")
result={"status":"PASS_NATIVE_FLAT_CAD01_CAD02_INTEGRATION_ONLY","net_count":len(nets),
        "verified_net_groups":len(req),"U401_pin4_to_R901_pin1":True,
        "pll_closed_loop":False,"master_hierarchical":False,"VCO_integrated":False,
        "hardware_rf":"NOT_RUN","pcb_DRC":"NOT_RUN","fab_authorized":False,"tx_authorized":False}
Path(sys.argv[1]).parent.joinpath("integration_pin_net_checks.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result))
