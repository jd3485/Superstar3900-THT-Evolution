#!/usr/bin/env python3
"""V1.8 algebraic only: resistor/ref/comparator-offset corners, NOT vendor SPICE or lab OVP approval.
Schottky/fuse/TVS, TL431 startup/transient, IRF9540 SOA, LM393 speed not modeled.
"""
import itertools,json
from pathlib import Path
VREF=2.495
RHI=56_200
RLO=10_000
RPOS=100_000
RHYST=1_000_000
def point(vref,hi,lo,rp,rh,vos=0.,out_hi=2.5,out_lo=0.2):
 # With open collector high clamped by BASE load, realistic high may be 2.3V, not 2.5.
 vplus_hi=(vref/rp+out_hi/rh)/(1/rp+1/rh)
 vplus_lo=(vref/rp+out_lo/rh)/(1/rp+1/rh)
 fac=(hi+lo)/lo
 return {"trip_rising_v":(vplus_hi+vos)*fac,"reclose_falling_v":(vplus_lo+vos)*fac}
nominal=point(VREF,RHI,RLO,RPOS,RHYST,out_hi=2.335,out_lo=0.2)
corner=[]
for ref,hi,lo,rp,rh,vos in itertools.product(
 [VREF*.995,VREF*1.005],[RHI*.99,RHI*1.01],[RLO*.99,RLO*1.01],
 [RPOS*.99,RPOS*1.01],[RHYST*.99,RHYST*1.01],[-.005,.005]):
 for high in [2.2,2.5]:
  q=point(ref,hi,lo,rp,rh,vos,out_hi=high,out_lo=0.05)
  corner.append(q)
ranges={k:{"min":round(min(q[k] for q in corner),4),
           "max":round(max(q[k] for q in corner),4)} for k in nominal}
assert len(corner)==128
assert ranges["trip_rising_v"]["min"]>15.5
# NOTE bounds are 25°C reference accuracy + assumed LM393 offset and resistor tolerances, not thermal or dynamic.
ref_current_11v=(11-VREF)/3300
pullup_low_current=(VREF-.2)/2200
ref_remainder=ref_current_11v-pullup_low_current
assert ref_remainder>0
loads=[.05,.1,.25,.5]
budget=[{"load_a":i,"IRF9540_RDSmax_0p117ohm_drop_v":round(i*.117,4),
         "IRF9540_RDSmax_power_w":round(i*i*.117,4)} for i in loads]
screen={"status":"ALGORITHMIC_REF_RESISTOR_OFFSET_SCREEN_ONLY",
 "Vref_nominal_v":VREF,"TL431B_initial_25C_accuracy":0.005,
 "LM393_typical_offset_bound_assumed_v":0.005,"resistor_tolerance_assumed":0.01,
 "schematic_high_switch":"IRF9540N PMOS Q801; Q802 open-collector controlled",
 "nominal_comparator_approx_v":{k:round(v,4) for k,v in nominal.items()},
 "corner_count":len(corner),"corner_ranges_v":ranges,
 "min_nominal_raw_input_v":11.0,"max_nominal_raw_input_v":15.5,
 "TL431_remain_current_at_11v_output_low_a_estimate":round(ref_remainder,6),
 "IRF9540_at_10V_GATE_data_screen":budget,
 "unknowns":["TL431 current, temperature and cathode stability","LM393 input common-mode near startup","BJT gain and saturation","OVP switch transient and inrush","IRF9540 SOA and VGS clamp at low Zener current","sustained overvoltage above LM393 36V maximum","fuse I2t and TVS surge coordination","thermal RF EMI"],"continuous_overvoltage_hardware_test":False,
 "fab_authorized":False,"tx_authorized":False}
out=Path(__file__).resolve().parent/"screen_v18.json"
out.write_text(json.dumps(screen,indent=2)+"\n")
print(json.dumps({"status":screen["status"],"nominal_v":screen["nominal_comparator_approx_v"],
 "corners":len(corner),"ranges":ranges,"hardware_pass":False}))
