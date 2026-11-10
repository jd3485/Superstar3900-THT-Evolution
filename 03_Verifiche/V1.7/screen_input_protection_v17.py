#!/usr/bin/env python3
"""Vendor-rating based arithmetic screening, NOT safety/surge/fuse coordination validation."""
from pathlib import Path
import json
outdir=Path(__file__).resolve().parent
vin=[11.0,13.8,15.5]
currents=[0.05,0.1,0.25,0.4]
# Conservative simple assumptions, NOT measured at actual loads or temperature:
fuse_cold_resistance_ohms=0.302 # product data catalog nominal only
diode_vf_screening_v=0.6 # approx maximum at rated 1A for selected 1N5819 in datasheet
checks=[]
for x in vin:
 for i in currents:
  vf=diode_vf_screening_v
  f_drop=i*fuse_cold_resistance_ohms
  checks.append({"raw_v":x,"assumed_load_a":i,"estimated_protected_v":round(x-f_drop-vf,4),
   "fuse_cold_resistance_drop_v":round(f_drop,4),
   "fuse_dissipation_w_est":round(i*i*fuse_cold_resistance_ohms,5),
   "series_diode_dissipation_w_est":round(i*vf,4),
   "regulator_and_boost_load_not_accounted":True})
tvs={"mpn_candidate":"ST P6KE20CA (bidirectional, DO-15)",
 "maximum_working_standoff_v":17.1,"breakdown_min_v":19.0,"breakdown_max_v":21.0,
 "max_clamp_v_at_specified_pulse_current":27.7,
 "specified_10_1000us_power_w":600,
 "continuous_overvoltage_disconnect":False,"automotive_iso7637_load_dump":"NOT_TESTED",
 "source_energy_and_fuse_coordination":"NOT_TESTED"}
status={"status":"ARITHMETIC_AND_DATASHEET_SCREENING_ONLY",
 "fuse_candidate":"Littelfuse 0251.500MXL axial 500mA FAST; board footprint NOT SELECTED",
 "diode_candidate":"Vishay 1N5819 DO-41 1A 40V",
 "normal_input_range_v":vin,"nominal_scenarios":checks,
 "tvs":tvs,"source_short_circuit_A":"UNKNOWN","nominal_fuse_current_a":0.5,
 "dropout_and_transient_load":"NOT_MODELED","thermal_qualified":False,
 "safe_for_vehicle":False,"fab_authorized":False,"tx_authorized":False}
assert len(checks)==12
assert max(vin)<tvs["maximum_working_standoff_v"]
assert not status["safe_for_vehicle"] and not status["fab_authorized"]
(outdir/"input_protection_screen_v17.json").write_text(json.dumps(status,indent=2)+"\n")
print(json.dumps({"status":status["status"],"scenarios":len(checks),"max_vin":max(vin),
                  "tvs_vrwm":tvs["maximum_working_standoff_v"],
                  "continuous_ovp":False,"safe_for_vehicle":False}))
