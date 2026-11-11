#!/usr/bin/env python3
"""V2.5 mathematical UVLO screen only; no vendor model or hardware safety rating."""
from itertools import product
import json
vrefs=(2.45,2.50,2.55)
rtop=(36000*.99,36000*1.01)
rbot=(10000*.99,10000*1.01)
thresholds=[ref*(1+t/b) for ref,t,b in product(vrefs,rtop,rbot)]
assert 11.0<min(thresholds)<11.25
assert 11.75<max(thresholds)<12.0
assert min(thresholds)<11.5<max(thresholds)
# Secondary LM393 open-collector B sinks CMP_OUT when IN+ < IN-.
# Comparator A sinks same CMP_OUT during OVP: logical wired-AND only.
def tl431_est(vin,vref,r,vd,icc,rref):
    vcc=max(0.,(vin-vd+r*vref/rref-r*icc)/(1+r/rref))
    return ((vcc-vref)/rref-vref/2200)*1000,vcc
def scan(vin):
    return [tl431_est(vin,ref,r,vd,icc,rr) for ref,r,vd,icc,rr in product(
        vrefs,(820*.95,820*1.05),(.25,.65),(.0005,.001),(1800*.95,1800*1.05))]
ik11=min(v[0] for v in scan(11.0))
ik138=min(v[0] for v in scan(13.8))
assert ik11>1.0,ik11
assert ik138>2.0,ik138
report={"gate":"PASS_V25_IDEAL_UVLO_WINDOW_MATH_ONLY",
"R1001":"Vishay PR01000101801JR500 1k8 1W 5pct",
"R1012":"Yageo MFR-25FBF52-36K 36k 1pct",
"R1013":"Yageo MFR-25FBF52-10K 10k 1pct",
"uvlo_nominal_v":11.5,
"uvlo_min_assumed_v":round(min(thresholds),3),
"uvlo_max_assumed_v":round(max(thresholds),3),
"tl431_at_11v_ika_min_mA_ideal":round(ik11,3),
"tl431_at_13p8v_ika_min_mA_ideal":round(ik138,3),
"wired_AND_only":True,"hysteresis_present":False,
"TL431_fault_qualified":False,"startup_qualified":False,"gate_fault_qualified":False,
"no_vendor_spice":True,"48v_qualified":False,"no_fab":True,"no_tx":True}
print(json.dumps(report,sort_keys=True))
