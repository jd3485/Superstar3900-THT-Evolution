#!/usr/bin/env python3
"""Screen V1.9 D804/D805 and R1001 using only basic worst-case arithmetic and
public vendor nominal/maximum ratings. No device physics or vehicle safety verdict.
"""
import json
from pathlib import Path
VREF=2.495
R=3300.0
R_TOL=0.05 # Vishay PR01000103301JR500 5% part
R_POWER_W=1.0 # 1 W only at qualifying temperature/assembly conditions
cases=[]
for raw in [11,13.8,15.5,17,24,36,48]:
 for vf in [.25,.45,.6]:
  vc=max(0.,raw-vf)
  nominal=((max(vc-VREF,0))**2)/R
  max_power=((max(vc-VREF+.0125,0))**2)/(R*(1-R_TOL))
  cases.append({"raw_v":raw,"assumed_D804_forward_drop_v":vf,"control_supply_est_v":round(vc,3),
   "R1001_nominal_W":round(nominal,5),"R1001_5pct_low_R_high_REF_assumed_W":round(max_power,5),
   "nominal_1W_fraction":round(nominal/R_POWER_W,3),
   "LM393_VCC_above36V_not_allowed":vc>36,
   "no_derating_assumed":False})
v36=[c for c in cases if c["raw_v"]==36]
v48=[c for c in cases if c["raw_v"]==48]
assert all(c["R1001_nominal_W"]<.36 for c in v36)
assert all(c["R1001_nominal_W"]<.65 for c in v48)
v18_trip_min,v18_trip_max=15.9553,16.9133
v18_release_min,v18_release_max=14.6598,15.4407
screen={"status":"PASS_ONLY_DC_RESISTOR_1W_AND_DIODE_APPROXIMATE_SCREEN",
 "R1001_MPN":"Vishay PR01000103301JR500 3k3 1W 5pct axial THT",
 "R1001_1W_power_rating_not_same_as_ambient_derating":True,
 "R1001_36V_nominal_W_range":[min(c["R1001_nominal_W"] for c in v36),
                                   max(c["R1001_nominal_W"] for c in v36)],
 "R1001_48V_nominal_W_range":[min(c["R1001_nominal_W"] for c in v48),
                                   max(c["R1001_nominal_W"] for c in v48)],
 "D804":"Vishay 1N5819 DO-41 1A/40V; min/typ/max forward drop not guaranteed at assumed 0.25/0.45/0.60",
 "D805":"Shunt to ground clamps negative control rail only approximately; 1N5819 reverse leakage can be high at temperature",
 "nominal_input_range_v":[11,15.5],"cases":cases,
 "trip_rising_raw_v_est_range_including_D804_drop":[round(v18_trip_min+.25,4),round(v18_trip_max+.6,4)],
 "reclose_raw_v_est_range_including_D804_drop":[round(v18_release_min+.25,4),round(v18_release_max+.6,4)],
 "LM393_supply_absolute_max_v":36,
 "reverse_fault_polarity":"NOT_QUALIFIED",
 "high_temperature_and_fault_currents":"NOT_QUALIFIED",
 "automotive_transients":"NOT_TESTED",
 "fuse_F701_D702":"STILL_NOT_COORDINATED_OR_FOOTPRINT_SELECTED",
 "board_and_RF":"NOT_TESTED","fab_authorized":False,"tx_authorized":False}
assert len(cases)==21
dest=Path(__file__).resolve().parent/"v19_stress_screen.json"
dest.write_text(json.dumps(screen,indent=2)+"\n")
print(json.dumps({"status":screen["status"],"scenarios":len(cases),
 "R1001_36V_power_W_range":screen["R1001_36V_nominal_W_range"],
 "raw_trip_est_v":screen["trip_rising_raw_v_est_range_including_D804_drop"],
 "safe_for_automotive":False}))
