#!/usr/bin/env python3
"""Local Python risk screen: proposed V2.6 diode/LM393 UVLO interlock to Q802.
Illustrative resistors and diode drops only; NOT vendor SPICE or hardware qualification.
"""
from itertools import product
import json
PULLUP=2200.; RB=22000.; RG=100000.; VREF=2.5

def analyze(vol,vf):
    vcmp=vol+vf
    base_open=vcmp*RG/(RB+RG)
    sink_current_ma=1000*(max(0.,(VREF-vcmp)/PULLUP)+vcmp/(RB+RG))
    return (vcmp,base_open,sink_current_ma)

cases=[analyze(vol,vf) for vol,vf in product((.10,.25,.40),(.20,.35,.55,.70))]
assert len(cases)==12
flagged=sum(base>=.65 for _,base,_ in cases)
assert flagged==5,flagged
assert all(i<1.5 for _,_,i in cases)
report={
 "gate":"PASS_RISK_DETECTED_NOT_HARDWARE_APPROVAL",
 "cases":len(cases),"flagged_base_ge_650mV":flagged,
 "vcmp_range_v":[round(min(x[0] for x in cases),3),round(max(x[0] for x in cases),3)],
 "base_unloaded_range_v":[round(min(x[1] for x in cases),3),round(max(x[1] for x in cases),3)],
 "combined_sink_current_mA":[round(min(x[2] for x in cases),3),round(max(x[2] for x in cases),3)],
 "model":"Resistor-divider only; no transistor BE I-V, no vendor diode I-V/leakage, no temperature, no full startup or loaded comparator output.",
 "fail_closed_proved":False,"cad_not_checked_by_diode_screen":True,"NO_FAB":True,"NO_TX":True}
print(json.dumps(report,sort_keys=True))
