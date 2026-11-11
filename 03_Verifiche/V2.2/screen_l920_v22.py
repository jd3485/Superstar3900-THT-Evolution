#!/usr/bin/env python3
"""Bourns RLB0914-681KL DC loss/energy screening from datasheet ratings, NOT a vendor SPICE model."""
import json
L=680e-6; dcr_max=1.60; irms_typ=0.49; isat_typ=0.90
rows=[]
for amps in (0.20,0.35,0.49,0.70,0.90):
    rows.append({"I_A":amps,"Pdc_W_using_RdcMax":round(amps**2*dcr_max,4),
    "L_energy_J_using_680uH_no_saturation":round(0.5*L*amps**2,8),
    "above_typical_Irms":amps>irms_typ,"at_or_above_typical_Isat":amps>=isat_typ})
assert abs(rows[2]["Pdc_W_using_RdcMax"]-0.38416)<0.0001
assert abs(rows[-1]["L_energy_J_using_680uH_no_saturation"]-0.0002754)<1e-7
print(json.dumps({"MPN":"Bourns RLB0914-681KL","ratings_source":"https://www.bourns.com/docs/product-datasheets/rlb.pdf",
"SRF_min_MHz":1.6,"DCR_max_ohm":1.6,"Irms_typ_A":0.49,"Isat_typ_A":0.90,
"assumptions":"I values hypothetical; L nominal constant (invalid near saturation); DCR max constant (no temp coefficient); no switching waveform",
"scenarios":rows,"gate":"PASS_ARITHMETIC_ONLY_NOT_ELECTRICAL_QUALIFICATION",
"bench_test":False,"vendor_SPICE_simulation":False,"rf_EMI_test":False,"NO_FAB":True,"NO_TX":True},indent=2))
