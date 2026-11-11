#!/usr/bin/env python3
"""V2.6 candidate UVLO hysteresis algebra only; no KiCad or vendor validation."""
from itertools import product
import json

def vin_trip(vref, vout, rt=36000., rb=10000., rf=470000.):
    return vref * (1 + rt/rb + rt/rf) - rt*vout/rf

rising = vin_trip(2.5, 0.25)
falling = vin_trip(2.5, 2.5)
assert 11.65 < rising < 11.70
assert abs(falling - 11.5) < 0.001
pairs = [(
    vin_trip(v, lo, rt, rb, rf), vin_trip(v, hi, rt, rb, rf)
) for v,lo,hi,rt,rb,rf in product(
    (2.45, 2.50, 2.55), (0.1,0.25,0.5), (2.1,2.35,2.5),
    (35640.,36360.),(9900.,10100.),(446500.,493500.)
)]
assert len(pairs) == 216
assert all(up > down for up,down in pairs)
print(json.dumps({
    "gate":"PASS_V26_IDEAL_UVLO_HYSTERESIS_STUDY_ONLY",
    "rising_nominal_v":round(rising,4),
    "falling_nominal_v":round(falling,4),
    "hysteresis_nominal_v":round(rising-falling,4),
    "illustrative_cases":len(pairs),
    "minimum_assumed_hysteresis_v":round(min(a-b for a,b in pairs),4),
    "hardware_or_vendor_qualified":False,
    "kicad_v26_completed":False,
    "D807_low_level_and_leakage_qualified":False,
    "NO_FAB":True,"NO_TX":True
},sort_keys=True))
