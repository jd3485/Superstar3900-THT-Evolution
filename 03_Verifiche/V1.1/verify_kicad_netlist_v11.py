#!/usr/bin/env python3
"""Native KiCad netlist assertions for unqualified RX PLL core, never a lock or RF lab claim."""
import runpy,sys,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
read=runpy.run_path(str(root/"03_Verifiche/V1.0/verify_kicad_netlist_v10.py"))["read_nets"]
nets=read(Path(sys.argv[1]))
req={
"PLL_FB_18M":{("U401","1"),("U402","5")},
"DIV2_QBAR":{("U402","2"),("U402","6")},
"PLL_PDOUT_3STATE":{("U401","4"),("J401","1")},
"XTAL_IN":{("U401","27"),("X401","2"),("C403","1")},
"XTAL_DRIVE":{("U401","26"),("X401","1"),("C404","1")},
"+5V_PLL":{("U401","3"),("U401","5"),("U401","7"),("U401","21"),("U402","4"),("U402","10"),("U402","14"),("J402","1")},
"GND":{("U401","2"),("U401","6"),("U401","22"),("U401","23"),("U402","7"),("U402","11"),("U402","12"),("U402","13"),("J402","2")},
"LO1_CMOS_BUFFERED":{("U402","3"),("J403","1")},
"PRESCALER_RESET_N":{("U402","1"),("J404","1"),("R403","2"),("C406","1")},
"PLL_LD_OBSERVE":{("U401","28"),("J406","1")}}
for i in range(12):req[f"N_CODE_{i}"]={("U401",str(i+11 if i<=9 else i+14)),("J405",str(i+1))}
err=[]
for name,expected in req.items():
 found=nets.get(name,set())
 if not expected.issubset(found):err.append(f"{name}: {sorted(expected-found)} missing; actual={sorted(found)}")
for name in ("PLL_FB_18M","DIV2_QBAR"):
 if len(nets.get(name,set()))!=2:err.append(name+" must have exactly two pins")
if err:raise AssertionError("\n".join(err))
result={"status":"PASS_NETLIST_RX_CORE_ONLY","verified_nets":len(req),"full_PLL":False,"pcb_DRC":"NOT_RUN","RF_lab":"NOT_RUN","fab_authorized":False,"tx_authorized":False}
Path(sys.argv[1]).parent.joinpath("cad02_netlist_evidence.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result))
