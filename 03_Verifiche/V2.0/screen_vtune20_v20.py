#!/usr/bin/env python3
"""MC34063/LM317 analytical topology screen, NOT vendor electrical simulation.
Never use model output as real verified 20V, phase-noise, stability, EMI or approval.
"""
import json,itertools,math
from pathlib import Path
VIN=[10.2,10.5,13.2,15.1]
LOAD=[.0143,.020,.030,.050] # includes base LM317 min-load approx; NOT verified RF load
FBBOOST=1.25*(1+47000/2200)
LM317=1.25*(1+3570/240)+50e-6*3570
Iprog=1.25/240
Ibleed=LM317/2200
Imin=Iprog+Ibleed
assert abs(FBBOOST-27.954545)<.001
assert abs(LM317-20.02225)<.001
assert Imin>.01,"Candidate minimum programming+bleeder budget must exceed 10mA target"
cases=[]
for vin,iout in itertools.product(VIN,LOAD):
 vf=.6;vsat=1.;fsw=40000.;L=680e-6
 ratio=(FBBOOST+vf-vin)/(vin-vsat)
 duty=ratio/(1+ratio)
 ton=duty/fsw
 dI=(vin-vsat)*ton/L
 ipeak_ideal=2*iout*(ratio+1) # upper estimate for continuous? idealized datasheet expression, not guarantee
 iclim_nom=.30/1. # comparator limit can vary, use 0.30 typical only, not worst case
 efficiency=.70 # explicit design assumption only
 pboost=FBBOOST*iout
 pin=pboost/efficiency
 iin=pin/vin
 cases.append({"Vin_protected_v":vin,"boost_load_a_assumed":iout,
   "duty_est":round(duty,5),"ton_us_est":round(ton*1e6,4),
   "inductor_current_ramp_a_est":round(dI,5),
   "datasheet_ideal_Ipeak_required_a":round(ipeak_ideal,5),
   "Rsc_typ_current_limit_a":round(iclim_nom,3),
   "input_A_at_assumed_70pct_eff":round(iin,5),
   "L920_DCR_1p6ohm_loss_at_est_input_W":round(iin*iin*1.6,4),
   "LM317_nominal_20V_Vout_with_Iadj_50uA":round(LM317,4),
   "LM317_28V_input_diff_v":round(FBBOOST-LM317,3),
   "nominal_reg_loss_W_if_load_assumed":round((FBBOOST-LM317)*iout,4),
   "real_hardware_qualified":False})
assert len(cases)==16
assert max(c["duty_est"] for c in cases)<.8
safe_window=[c for c in cases if c["boost_load_a_assumed"]<=.03]
assert max(c["datasheet_ideal_Ipeak_required_a"] for c in safe_window)<.3
# 50mA cases MAY EXCEED nominal .3A; do not claim these as supported.
limit_cases=[c for c in cases if c["datasheet_ideal_Ipeak_required_a"]>=.3]
assert limit_cases,"Must explicitly report too-high loads"
corners=[]
for vrefb,t_high,t_low,vref317,Iadj in itertools.product([1.225,1.275],[.99,1.01],[.99,1.01],[1.20,1.30],[0,.0001]):
 boost=vrefb*(1+47000*t_high/(2200*t_low))
 ldo=vref317*(1+(3570*t_high)/(240*t_low))+Iadj*3570*t_high
 corners.append({"boost":boost,"ldo":ldo,"headroom":boost-ldo})
out={"status":"PASS_ONLY_MC34063_LM317_ARITHMETIC_ENVELOPE_NO_VENDOR_MODEL",
 "BOOST28_divider_v_nom":round(FBBOOST,4),"LM317_20V_nom_with_50uA_Iadj":round(LM317,4),
 "R927_load_program_min_nom_a":round(Imin,6),
 "worst_case_from_UNVERIFIED_component_assumptions":{
  "boost_min_v":round(min(x["boost"] for x in corners),3),
  "boost_max_v":round(max(x["boost"] for x in corners),3),
  "ldo_min_v":round(min(x["ldo"] for x in corners),3),
  "ldo_max_v":round(max(x["ldo"] for x in corners),3),
  "headroom_min_v":round(min(x["headroom"] for x in corners),3)},
 "MC34063_design_max_duty_spec":.8,"Rsc_1ohm_limit_nominal_a":.30,
 "L920":"Bourns RLB0914-681KL 680uH 1.6ohm DCRmax 0.49A Irms typ 0.9A Isat typ",
 "L920_footprint":"NOT_SELECTED","assumed_f_switch_Hz":40000,
 "assumed_inductor_H":.00068,"scenarios":cases,"limited_scenarios":len(limit_cases),
 "unknowns":["actual MC34063 switch timing and internal saturation","startup 28V cap charge and current limit",
 "LM317 minimum load and dropout over temperature", "maximum transient Vboost and 50V cap stress",
 "D920 1N5819 40V reverse transient margin", "output rail short/reverse discharge diode stress",
 "switched-source F701 500mA fuse I2t coordination", "L920 unshielded RF coupling; 40kHz harmonics into mixer",
 "RF phase noise and VTUNE control loop stability","heat and mechanical isolation LM317 OUT metal tab"],
 "device_vendor_models_run":False,"EMI_RF_TESTS":False,
 "PCB_DRC":False,"hardware_qual":False,"fab_authorized":False,"tx_authorized":False}
p=Path(__file__).resolve().parent/"screen_v20.json"
p.write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps({"status":out["status"],"VIN_scenarios":len(cases),"nominal_v":out["LM317_20V_nom_with_50uA_Iadj"],
 "worst_case_assumed":out["worst_case_from_UNVERIFIED_component_assumptions"],
 "Ipeak_over_assumed_limit":len(limit_cases),"no_hardware_pass":True}))
