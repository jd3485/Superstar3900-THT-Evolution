"""V0.8 candidate THT VTUNE source and driver budget (analytic, NOT device simulation).

MC34063A: boost 27 V candidate, 470 uH, Rsc 0.47 ohm, 40kHz ASSUMED.
LM317: 20 V candidate + 2.4k/0.5W bleeder for minimum-load worst case.
LM358-N PDIP-8: candidate noninverting gain 4 from PD_FILTER 0..5 V.
NO representation of actual MC34063 control/phase detector, LM317 dropout,
real LM358 voltage swing guaranteed over temperature, loop phase stability,
PCB layout, EMI, RF phase noise or hardware qualification.
"""
from __future__ import annotations
import math
from dataclasses import dataclass

VIN_LEVELS=(11.0,13.8,15.5)
BOOST_TARGET_V=27.0
BOOST_OUTPUT_CURRENT_DESIGN_A=.025
SWITCH_F_HZ_ASSUMED=40_000.
SWITCH_SAT_V_ASSUMED=1.0
DIODE_DROP_V_ASSUMED=.5
L_H_CANDIDATE=470e-6
R_SENSE_OHM_CANDIDATE=.47
SENSE_TRIP_LOW_V_DATASHEET=.250
SENSE_TRIP_TYP_V_DATASHEET=.300
SENSE_TRIP_HIGH_V_DATASHEET=.350
BOOST_FB_TOP_OHM=24700.0
BOOST_FB_BOTTOM_OHM=1200.0
BOOST_REF_V_TYP=1.25
LM317_R1_OHM=240.
LM317_R2_OHM=3570.
LM317_REF_TYP_V=1.25
LM317_IADJ_TYP_A=50e-6
BLEEDER_OHM=2400.
BLEEDER_WATT_RATING=.5
MIN_LOAD_LM317_MAX_A=.010
RC_SERIES_OHM=10.
RC_CAP_F=100e-6
LM358_R_F_OHM=30000.
LM358_R_G_OHM=10000.
LM358_GAIN_NOMINAL=1+LM358_R_F_OHM/LM358_R_G_OHM
VCO_VTUNE_LOW_V=8.0
VCO_VTUNE_HIGH_V=15.0
LM358_OUTPUT_HEADROOM_V_ASSUMED=3.0
LM317_DROPOUT_V_ASSUMED=3.0

@dataclass(frozen=True)
class BoostBudget:
    vin_v:float
    on_off_ratio:float
    duty:float
    on_time_us:float
    off_time_us:float
    inductor_current_rise_a:float
    minimum_current_limit_a:float
    current_margin_from_zero_a:float
    # This is NOT guaranteed under continuous conduction or limits of timing!
def duty_budget(vin_v):
    if vin_v<=SWITCH_SAT_V_ASSUMED or vin_v>=BOOST_TARGET_V:
        raise ValueError("invalid step-up range")
    r=(BOOST_TARGET_V+DIODE_DROP_V_ASSUMED-vin_v)/(vin_v-SWITCH_SAT_V_ASSUMED)
    d=r/(1+r)
    if d<=0 or d>=.8: raise ValueError("outside nominal MC34063 duty envelope")
    t=d/SWITCH_F_HZ_ASSUMED
    di=(vin_v-SWITCH_SAT_V_ASSUMED)*t/L_H_CANDIDATE
    limit=SENSE_TRIP_LOW_V_DATASHEET/R_SENSE_OHM_CANDIDATE
    return BoostBudget(vin_v,r,d,t*1e6,(1/SWITCH_F_HZ_ASSUMED-t)*1e6,
                       di,limit,limit-di)

def boost_divider_v(vref=BOOST_REF_V_TYP,rtop=BOOST_FB_TOP_OHM,rbottom=BOOST_FB_BOTTOM_OHM):
    if min(vref,rtop,rbottom)<=0:raise ValueError("invalid divider")
    return vref*(1+rtop/rbottom)

def boost_divider_window():
    # Manufacturer reference 1.21..1.29 over temperature may be broader
    # than this illustrative +/-2% window; these are NOT guaranteed.
    return (boost_divider_v(1.225,BOOST_FB_TOP_OHM*.99,BOOST_FB_BOTTOM_OHM*1.01),
            boost_divider_v(1.275,BOOST_FB_TOP_OHM*1.01,BOOST_FB_BOTTOM_OHM*.99))

def lm317_output(vref=LM317_REF_TYP_V,iadj=LM317_IADJ_TYP_A):
    if vref<=0 or iadj<0:raise ValueError("invalid regulator parameters")
    return vref*(1+LM317_R2_OHM/LM317_R1_OHM)+iadj*LM317_R2_OHM

def lm317_window():
    return lm317_output(1.2,0),lm317_output(1.3,100e-6)

def bleeder_min_load_amps():
    lo,_=lm317_window()
    feedback_min_a=1.2/LM317_R1_OHM
    return feedback_min_a+lo/BLEEDER_OHM

def bleeder_watts_nominal():
    return lm317_output()**2/BLEEDER_OHM

def bleeder_watts_max_assumed():
    return lm317_window()[1]**2/BLEEDER_OHM

def rc_ideal_db(hz):
    if hz<0:raise ValueError("bad frequency")
    return -10*math.log10(1+(2*math.pi*hz*RC_SERIES_OHM*RC_CAP_F)**2)

def vtune_input_for_output(vtune_v):
    if vtune_v<0:raise ValueError("bad VTUNE")
    return vtune_v/LM358_GAIN_NOMINAL

def minimum_output_high(headroom=LM358_OUTPUT_HEADROOM_V_ASSUMED,load_a=.025):
    if headroom<0 or load_a<0:raise ValueError("bad headroom")
    return lm317_window()[0]-RC_SERIES_OHM*load_a-headroom

def lm358_dc_point(pd_filtered_v,rail_v,headroom=LM358_OUTPUT_HEADROOM_V_ASSUMED):
    if pd_filtered_v<0 or rail_v<=0 or headroom<0:
        raise ValueError("bad operating point")
    return min(max(pd_filtered_v*LM358_GAIN_NOMINAL,0),
               max(rail_v-headroom,0))

def protection_logic(*,vin_ok,boost_ok,reg20_ok,ref_ok,pll_lock,retune_done):
    # Pure requirement contract, not physical interlock.
    allowed=all((vin_ok,boost_ok,reg20_ok,ref_ok,pll_lock,retune_done))
    return {"rx_unmute_candidate":allowed,
            "tx_enabled":False,"fab_authorized":False}

def budget_summary():
    return {
      "boost_duty_points":[vars(duty_budget(v)) for v in VIN_LEVELS],
      "boost_v_nom":boost_divider_v(),
      "boost_illustrative_v_window":boost_divider_window(),
      "lm317_v_nom":lm317_output(),
      "lm317_illustrative_v_window":lm317_window(),
      "minimum_regulator_load_a_in_model":bleeder_min_load_amps(),
      "minimum_load_required_max_a":MIN_LOAD_LM317_MAX_A,
      "bleeder_watt_nom":bleeder_watts_nominal(),
      "bleeder_watt_worst_assumption":bleeder_watts_max_assumed(),
      "passive_rc_40khz_db_ideal_unloaded":rc_ideal_db(40e3),
      "lm358_gain":LM358_GAIN_NOMINAL,
      "vco_requested_vtune_control_input_range_v":[vtune_input_for_output(8),vtune_input_for_output(15)],
      "vco_output_headroom_assumed_min_v":minimum_output_high(),
      "lm317_dropout_assumed_min_v":boost_divider_window()[0]-lm317_window()[1],
      "device_models_validated":False,"PLL_closed_loop_validated":False,
      "hardware_validated":False,"fabrication_authorized":False,"tx_authorized":False
    }
if __name__=="__main__":
 import json
 print(json.dumps(budget_summary(),indent=2))
