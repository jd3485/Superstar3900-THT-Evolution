#!/usr/bin/env python3
"""Conservative analytical screening only (NOT a thermal validation, no measurements)."""
import json
from pathlib import Path
# ST L7800 Rev13 TO220 RthJA=50C/W unheatsinked, quiescent max unqualified: 6mA taken as typical.
vins=[11.0,13.8,15.5]
loads=[0.03,0.09,0.15,0.25]
theta=50.0
ambient=50.0
iq_typ=0.006
rows=[]
for vin in vins:
 for load in loads:
  pd=(vin-5.0)*load+vin*iq_typ
  tj=ambient+pd*theta
  rows.append({"vin_v":vin,"load_a":load,"reg_dissipation_w_screening":round(pd,3),
   "estimated_junction_c_no_heatsink":round(tj,1),"risk_at_125c_screener":tj>=125.0})
branch=[{"i_ma":i,"r_ohm":1.0,"v_drop_mv":i,"power_mw":i*i/1000} for i in (10,30,60,120)]
res={"status":"ANALYTICAL_SCREENING_ONLY","st_rthja_to220_c_per_w":theta,"ambient_c":ambient,
     "assumed_iq_typical_ma":iq_typ*1000,"scenarios":rows,"branch_drops":branch,
     "actual_loads":"UNKNOWN","heat_sink":"UNSELECTED","ripple":"NOT_SIMULATED",
     "powergood_mute":"NOT_DESIGNED","regulator_vendor_macromodel":"NOT_USED",
     "fab_authorized":False,"tx_authorized":False}
assert any(x["risk_at_125c_screener"] for x in rows),"must not conceal worst-case heating risk"
output=Path(__file__).resolve().parent/"v15_power_budget.json"
output.write_text(json.dumps(res,indent=2)+"\n")
print(json.dumps({"scenarios":len(rows),"at_risk":sum(r["risk_at_125c_screener"] for r in rows),
"validated":False,"output":str(output)}))
