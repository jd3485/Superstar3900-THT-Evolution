#!/usr/bin/env python3
"""Standalone LM2903P THT UVLO/OVP candidate window DC resistor screening.

NO LM2903P CAD here yet. These are externally supplied 5V/reference AND
resistor ratio synthetic design equations, NOT functional independent safety.
"""
import itertools
import math

# Sensor: Rhigh=100k, Rlow=5k (max 48V hypothetical to < 5V nominal).
# Reference external precision 2.5V (yet to be engineered/qualified).
# Two threshold dividers: 2.5*(20/(50+20))=.714286,
# 2.5*(20/(85+20))=.476190.
# This is a comparator input-stage candidate only, NOT driver interlock.
VREF_NOM=2.5
SENSE_HI=100000.
SENSE_LO=5000.
OVP_REF_HI=50000.
OVP_REF_LO=20000.
UVLO_REF_HI=85000.
UVLO_REF_LO=20000.
TOL=.01

def ratio(rhigh,rlow):
    return rlow/(rhigh+rlow)

def main():
    count=0
    uvlo_thresholds=[]
    ovp_thresholds=[]
    healthy=0
    over_48_in_cm=0
    unsafe_sense_open=0
    for rh,rl,ovh,ovl,uvh,uvl,vref in itertools.product(
        (1-TOL,1+TOL),
        (1-TOL,1+TOL),
        (1-TOL,1+TOL),
        (1-TOL,1+TOL),
        (1-TOL,1+TOL),
        (1-TOL,1+TOL),
        (2.475,2.525)
    ):
        rs=ratio(SENSE_HI*rh,SENSE_LO*rl)
        tov=vref*ratio(OVP_REF_HI*ovh,OVP_REF_LO*ovl)/rs
        tuv=vref*ratio(UVLO_REF_HI*uvh,UVLO_REF_LO*uvl)/rs
        uvlo_thresholds.append(tuv)
        ovp_thresholds.append(tov)
        if tuv<13.8<tov:healthy+=1
        if 48.*rs >= 3.5:over_48_in_cm+=1
        # Worst single bottom leg open: comparator input rises to source
        # without input protection even if nominal current is low.
        if 48.>5.:unsafe_sense_open+=1
        count+=1
    assert count==128 and healthy==128
    assert max(uvlo_thresholds)<13.8<min(ovp_thresholds)
    assert min(ovp_thresholds)>14. and max(ovp_thresholds)<16.
    assert min(uvlo_thresholds)>9. and max(uvlo_thresholds)<11.
    assert over_48_in_cm==0
    assert unsafe_sense_open==count
    # Comparator output collectors on LM2903P are open; pullups are
    # mandatory, and even with good window they cannot directly act as
    # an independent series hardware disconnect.
    print("LM2903P_SECONDARY_WINDOW_PASSIVE_DIVIDER_SCREEN",{
        "corner_cases":count,
        "UVLO_nominal_V":round(VREF_NOM*ratio(UVLO_REF_HI,UVLO_REF_LO)/ratio(SENSE_HI,SENSE_LO),6),
        "OVP_nominal_V":round(VREF_NOM*ratio(OVP_REF_HI,OVP_REF_LO)/ratio(SENSE_HI,SENSE_LO),6),
        "UVLO_corner_min_max_V":[round(min(uvlo_thresholds),5),round(max(uvlo_thresholds),5)],
        "OVP_corner_min_max_V":[round(min(ovp_thresholds),5),round(max(ovp_thresholds),5)],
        "48V_nominal_sense_input_V":round(48*ratio(SENSE_HI,SENSE_LO),5),
        "48V_nominal_within_5V_common_mode_nominal":True,
        "single_lower_leg_OPEN_unprotected_cases":unsafe_sense_open,
        "full_48V_fault_input_electrically_qualified":False,
        "LM2903P_PDIP8_KiCad9_native_ERC_verified":False,
        "independent_5V_supply_ref_implemented":False,
        "hardware_series_disconnect_implemented":False,
        "Q806_CE_SHORT_FAILCLOSED":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_LM2903P_WINDOW_128_PASSIVE_CORNERS_NONFAB",flush=True)

if __name__=="__main__":
    main()
