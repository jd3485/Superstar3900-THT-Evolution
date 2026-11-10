"""V0.7 THT VTUNE supply: transparent first-pass calculations, NOT a real switcher model.

Assumptions: input 11.0..15.5 V after protection, boost 24 V,
MC34063ABN DIP8, 40 kHz engineering target, 470uH, 1ohm current sense,
LM317T TO-220 regulator with 240ohm/3.24kohm.
Actual IC switch timing, compensation, transient and EMI are NOT simulated here.
"""
from __future__ import annotations
import math
from dataclasses import dataclass

VIN_MIN_V=11.0
VIN_NOMINAL_V=13.8
VIN_MAX_V=15.5
BOOST_TARGET_V=24.0
BOOST_LOAD_DESIGN_A=.015
SWITCH_HZ_ASSUMED=40_000.0
DIODE_FORWARD_V_ASSUMED=.5
SWITCH_SAT_V_ASSUMED=1.0
L_BOOST_H=470e-6
R_SENSE_OHM=1.0
SENSE_TRIP_V_TYP=.33
BOOST_FB_TOP_OHM=21_800.0
BOOST_FB_BOTTOM_OHM=1_200.0
BOOST_VREF_TYP_V=1.25
LM317_FB_TOP_OHM=3_240.0
LM317_FB_BOTTOM_OHM=240.0
LM317_VREF_TYP_V=1.25
LM317_IADJ_TYP_A=50e-6
RC_FILTER_R_OHM=47.0
RC_FILTER_C_F=47e-6
VCO_REQUIRED_MAX_VTUNE=15.0
LM358_HIGH_HEADROOM_ASSUMED_V=2.0
LM317_DROPOUT_DESIGN_ASSUMED_V=3.0

@dataclass(frozen=True)
class BoostPoint:
    vin_v:float
    on_off_ratio:float
    duty_nominal:float
    on_time_us:float
    off_time_us:float
    inductor_delta_i_a:float
    sense_limit_a_typ:float
    exceeds_typ_sense_limit:bool

def boost_point(vin_v:float):
    if not 0 < vin_v < BOOST_TARGET_V or vin_v<=SWITCH_SAT_V:
        raise ValueError("invalid step up condition")
    ratio=(BOOST_TARGET_V+DIODE_FORWARD_V_ASSUMED-vin_v)/(vin_v-SWITCH_SAT_V_ASSUMED)
    duty=ratio/(1+ratio)
    if not (0<duty<.8):raise ValueError("duty beyond preliminary IC envelope")
    ton=duty/SWITCH_HZ_ASSUMED
    delta=(vin_v-SWITCH_SAT_V_ASSUMED)*ton/L_BOOST_H
    limit=SENSE_TRIP_V_TYP/R_SENSE_OHM
    return BoostPoint(vin_v,ratio,duty,ton*1e6,(1/SWITCH_HZ_ASSUMED-ton)*1e6,
                      delta,limit,delta>=limit)

def booster_target_v(vref=BOOST_VREF_TYP_V,rtop=BOOST_FB_TOP_OHM,rbottom=BOOST_FB_BOTTOM_OHM):
    if min(vref,rtop,rbottom)<=0:raise ValueError("nonphysical divider")
    return vref*(1+rtop/rbottom)

def booster_tolerance_window(vref_tol=.02,r_tol=.01):
    return (
        booster_target_v(BOOST_VREF_TYP_V*(1-vref_tol),
                         BOOST_FB_TOP_OHM*(1-r_tol),BOOST_FB_BOTTOM_OHM*(1+r_tol)),
        booster_target_v(BOOST_VREF_TYP_V*(1+vref_tol),
                         BOOST_FB_TOP_OHM*(1+r_tol),BOOST_FB_BOTTOM_OHM*(1-r_tol))
    )

def lm317_target_v(vref=LM317_VREF_TYP_V,iadj=LM317_IADJ_TYP_A,
                   rtop=LM317_FB_TOP_OHM,rbottom=LM317_FB_BOTTOM_OHM):
    if min(vref,rtop,rbottom)<=0 or iadj<0:raise ValueError("nonphysical LM317")
    return vref*(1+rtop/rbottom)+iadj*rtop

def lm317_rough_window(vref_low=1.2,vref_high=1.3,
                       iadj_low=0.,iadj_high=100e-6):
    return (lm317_target_v(vref_low,iadj_low),lm317_target_v(vref_high,iadj_high))

def inductor_energy_rate_w(delta_i_a,frequency_hz=SWITCH_HZ_ASSUMED):
    if delta_i_a<0 or frequency_hz<=0:raise ValueError("nonphysical energy")
    return .5*L_BOOST_H*delta_i_a**2*frequency_hz

def ideal_rc_magnitude_db(f_hz,r=RC_FILTER_R_OHM,c=RC_FILTER_C_F):
    if f_hz<0 or r<=0 or c<=0:raise ValueError("nonphysical RC")
    return -10*math.log10(1+(2*math.pi*f_hz*r*c)**2)

def rail_gates(*,boost_ok,linear_reg_ok,vref_ok,pll_lock,retune_done):
    # Software contract only; hardware implementation is an OPEN gate.
    safe=all((boost_ok,linear_reg_ok,vref_ok,pll_lock,retune_done))
    return {"rx_unmute_candidate":safe,"rf_tx_enable":False,
            "fabrication_authorized":False}

def summary():
    worst=boost_point(VIN_MIN_V)
    nom=boost_point(VIN_NOMINAL_V)
    vmax=boost_point(VIN_MAX_V)
    boostlo,boosthi=booster_tolerance_window()
    lmin,lmax=lm317_rough_window()
    return {
        "points":[vars(x) for x in (worst,nom,vmax)],
        "target_boost_v":booster_target_v(),
        "boost_voltage_ideal_tolerance_range_v":[boostlo,boosthi],
        "target_rail_v":lm317_target_v(),
        "rail_rough_range_v":[lmin,lmax],
        "headroom_worst_assumptions_v":boostlo-lmax,
        "regulator_headroom_assumption_v":LM317_DROPOUT_DESIGN_ASSUMED_V,
        "lm358_min_high_swing_estimate_v":lmin-LM358_HIGH_HEADROOM_ASSUMED_V,
        "vco_high_vtune_required_v":VCO_REQUIRED_MAX_VTUNE,
        "switch_hz_target_only":SWITCH_HZ_ASSUMED,
        "peak_inductor_current_margin_note":"calculated deltaI not necessarily peakI under CCM",
        "min_inductor_energy_rate_w_dcm_upper_bound":inductor_energy_rate_w(worst.inductor_delta_i_a),
        "output_power_target_w":BOOST_LOAD_DESIGN_A*BOOST_TARGET_V,
        "ripple_rc_40khz_ideal_db":ideal_rc_magnitude_db(40e3),
        "regulation_verified":False,"switch_model_vendor_verified":False,
        "vtune_output_current_verified":False,
        "hardware_qualified":False,"tx_enabled":False,"fab_authorized":False
    }
if __name__=="__main__":
    import json
    print(json.dumps(summary(),indent=2))
