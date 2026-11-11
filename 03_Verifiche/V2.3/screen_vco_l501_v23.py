#!/usr/bin/env python3
"""Pure 1/sqrt(L) screening of nominal VCO L variation, C intentionally held fixed.
Cannot replace nonlinear varactor vendor model or VCO loop measurements.
"""
import math,json
L0=166.
cases=[]
for L in (137.,150.,165.,166.,180.,193.):
  scale=math.sqrt(L0/L)
  cases.append({"L_nH":L,"frequency_ratio_vs_166nH":round(scale,7),
                "at_37MHz_ideal_MHz":round(37.*scale,4)})
assert abs(math.sqrt(166/165)-1)<0.004
assert 137<=166<=193
print(json.dumps({"MPN":"Coilcraft 150-05J08L","source":"https://www.coilcraft.com/getmedia/aaa9fcd2-5ef1-4ee2-b9b8-0ec1aa8c8db0/uni7.pdf",
 "nominal_tunable_L_nH":165,"adjustment_min_nH":137,"adjustment_max_nH":193,
 "Qmin_at_50MHz":114,"SRF_min_MHz":650,
 "model":"first-order ideal LC fixed-C only, not nonlinear varactor or calibrated VCO",
 "scenarios":cases,"hardware_qualified":False,"PLL_lock_verified":False,"RF_phase_noise_measured":False,"NO_FAB":True,"NO_TX":True},indent=2))
