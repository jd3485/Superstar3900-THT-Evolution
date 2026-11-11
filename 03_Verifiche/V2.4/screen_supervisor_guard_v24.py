#!/usr/bin/env python3
"""Screen ONLY: resistor/zener nominal PVT and TL431 UVLO risk. NOT safety qualification."""
import json,math
Rnom=680.; Vznom=15.; Vref=2.5; Rref=3300.; Rpull=2200.
samples=[]
for vin in (0.,9.,10.,11.,12.,13.8,16.5,20.,24.,36.,48.):
 for rf in (.95,1.05):
  for vd in (.25,.65):
   for icc in (.0005,.001):
    R=Rnom*rf
    vr=(vin-vd+R*Vref/Rref-R*icc)/(1+R/Rref)
    vr=max(0.,vr)
    # 15V+-5% approximate vendor Vz at 17mA. At other currents, Vz is not a guaranteed clamp.
    vz=Vznom
    if vr>vz:vr=vz
    total=max(0.,(vin-vd-vr)/R)
    iref=max(0.,(vr-Vref)/Rref)
    cathode=iref-Vref/Rpull
    iz=max(0.,total-icc-iref)
    pr=total**2*R;pz=vr*iz
    samples.append({"vin":vin,"vcc":round(vr,3),"v_sense":round(vin*10000./66200.,3),"i_tl431_net_mA":round(cathode*1000,3),"p_r_w":round(pr,3),"p_z_w":round(pz,3)})
assert max(q["vcc"] for q in samples)<=15.001
at_nom=[q for q in samples if q["vin"]==13.8]
assert min(q["i_tl431_net_mA"] for q in at_nom)>1.,at_nom
at_low=[q for q in samples if q["vin"]==10.]
assert min(q["i_tl431_net_mA"] for q in at_low)<1.
at_high=[q for q in samples if q["vin"]==48.]
assert max(q["p_r_w"] for q in at_high)<2.0
report={"gate":"PASS_V24_ANALYTIC_SCREEN_ONLY","MPN_R1011":"Vishay PR02000206800JR500 680R 2W 5pct","MPN_D806":"onsemi 1N4744A 15V 1W 5pct","lab_voltage_min_qualified":False,"sustained_48V_qualified":False,"zener_dynamic_and_thermal_qualified":False,"TL431_brownout_10V_known_risk":True,"reverse_fault_qualified":False,"gate_qualified":False,"datasheet_limits":{"LM393N_Vcc_max_V":36,"IRF9540N_Vgs_abs_V":20,"Zener_1N4744A_power_TL50C_W":1},"ranges":{"at_13p8V_TL431_net_min_mA":min(q["i_tl431_net_mA"] for q in at_nom),"at_48V_R_power_max_analytic_W":max(q["p_r_w"] for q in at_high),"at_48V_zener_power_max_analytic_W":max(q["p_z_w"] for q in at_high)},"scenarios":len(samples),"no_fab":True,"no_tx":True}
print(json.dumps(report,sort_keys=True))
