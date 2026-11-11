#!/usr/bin/env python3
"""V2.4 limited PVT screening; a passing model is NOT a safety qualification."""
from itertools import product
import json

R_NOM = 820.0
R_TOL = 0.05
R_REF = 3300.0
R_PULL = 2200.0
V_REF = 2.5
VINS = (0.0, 9.0, 10.0, 11.0, 12.0, 13.8, 16.5, 20.0, 24.0, 36.0, 48.0)
# Diotec 1N5352B voltage window only specified at vendor test 75 mA.
VZ_ASSUMED_TEST_POINTS = (14.2, 15.0, 15.8)

def pr03_cu_derated_w(ambient_c):
    """Vishay PR03 Cu 3W P70, illustrative linear derating to 0W at 200C."""
    return 3.0 * max(0.0, min(1.0, (200.0-ambient_c)/130.0))

samples = []
for vin, rf, vd, icc, vz in product(
    VINS, (1-R_TOL, 1+R_TOL), (0.25, 0.65), (0.0005, 0.001), VZ_ASSUMED_TEST_POINTS
):
    r = R_NOM*rf
    # NOT vendor SPICE: 2.5V ideal TL431 and ideal stiff Zener at assumed Vz.
    free_vcc = max(0.0, (vin-vd+r*V_REF/R_REF-r*icc)/(1+r/R_REF))
    vcc = min(free_vcc, vz)
    ir = max(0.0, (vin-vd-vcc)/r)
    iref = max(0.0, (vcc-V_REF)/R_REF)
    ik = iref-V_REF/R_PULL
    iz = max(0.0, ir-icc-iref)
    samples.append(dict(vin=vin, vcc=vcc, ik=ik, iz=iz,
                        pr=ir*ir*r, pz=vcc*iz))

def rows(vin):
    return [s for s in samples if s["vin"]==vin]

at_nom,at_low,at_high=rows(13.8),rows(10.0),rows(48.0)
ikmin=min(s["ik"] for s in at_nom)*1000
prmax=max(s["pr"] for s in at_high)
pzmax=max(s["pz"] for s in at_high)
izmax=max(s["iz"] for s in at_high)*1000
assert len(samples)==264
assert ikmin>1.0
assert min(s["ik"] for s in at_low)<0.001
assert prmax<pr03_cu_derated_w(125.0)
assert prmax>pr03_cu_derated_w(140.0), "Expected high-ambient derating hazard must remain visible"
assert pzmax<5.0
assert 0.0<izmax<75.0, "Vz limits NOT guaranteed at these lower currents"
report={
 "gate":"PASS_V24_LIMITED_IDEALIZED_SCREEN_ONLY",
 "R1011":"Vishay PR03000208200JAC00 820R 3W Cu-lead PR03 5pct",
 "D806":"Diotec 1N5352B DO-201 15V 5W 5pct",
 "scenarios":len(samples),
 "at_13p8V_TL431_min_est_mA":round(ikmin,3),
 "at_10V_TL431_min_est_mA":round(min(s["ik"] for s in at_low)*1000,3),
 "at_48V_R_power_max_ideal_W":round(prmax,3),
 "PR03_derated_125C_W":round(pr03_cu_derated_w(125),3),
 "PR03_derated_140C_W":round(pr03_cu_derated_w(140),3),
 "at_48V_Z_power_max_ideal_W":round(pzmax,3),
 "at_48V_Z_current_max_ideal_mA":round(izmax,3),
 "zener_vz_limits_apply_only_at_75mA":True,
 "vendor_spice_model_used":False,
 "brownout_failclosed_qualified":False,
 "sustained_48V_qualified":False,
 "reverse_gate_F701_D702_qualified":False,
 "powergood_mute_hardware_present":False,
 "no_fab":True,"no_tx":True,"no_battery_or_vehicle":True
}
print(json.dumps(report,sort_keys=True))
