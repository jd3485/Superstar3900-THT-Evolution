#!/usr/bin/env python3
"""Estimate *illustrative typical* LM386 rail current from TI Fig. 6-7.

Source: TI SNAS545D, section 6.6, Figure 6-7, V_S=6V / R_L=8ohm.
The figure is graphical typical characterization, NOT guaranteed limits.
Digitized dissipation brackets are deliberately broad, not measured readings.
"""
import csv
from math import pi, sqrt, isclose
from pathlib import Path
from verify_audio_psu_lm317_native import vout_pvt_endpoints
from verify_audio_load_envelope import (
    speaker_ideal, junction_scenario_c,
    theta_required_c_per_w,
)

ROOT=Path(__file__).resolve().parents[2]
CSV=ROOT/"03_Verifiche/V2.7/LM386_GRAPH_6V_RAIL_CURRENT_BRACKETS.csv"
VS_GRAPH=6.0
R_TOP_OHMS=110.0
R_TOP_TOL=0.01
VREF_MIN=1.20
VREF_MAX=1.30


def class_b_ideal_average_supply_current(pout_w,ohms):
    """Class-B push-pull sine ideal, not an LM386 vendor current prediction."""
    return sqrt(2*pout_w/ohms)/pi


def estimate_bracket(pout_w,pdiss_low,pdiss_high):
    assert 0 < pout_w and 0 <= pdiss_low < pdiss_high
    return ((pout_w+pdiss_low)/VS_GRAPH,
            (pout_w+pdiss_high)/VS_GRAPH)


def min_bleeder_a():
    """LM317 R1401 = 110ohm ±1%, voltage reference low endpoint."""
    return VREF_MIN/(R_TOP_OHMS*(1+R_TOP_TOL))


def max_bleeder_a():
    """Feedback branch upper illustrative bound, not full I_ADJ/current."""
    return VREF_MAX/(R_TOP_OHMS*(1-R_TOP_TOL))


def run():
    with CSV.open(encoding="utf-8",newline="") as file:
        rows=list(csv.DictReader(file))
    assert len(rows)==2
    assert [float(r["pout_w"]) for r in rows]==[0.125,0.250]
    lowv,nominal,highv=vout_pvt_endpoints()
    assert lowv<nominal<highv
    assert min_bleeder_a()>0.010
    assert 0.010 < max_bleeder_a()<0.013
    # ThetaJA is an ASSUMPTION for illustration and not a package/PCB spec.
    T_AMB=60.0
    VIN_MAX=10.5
    THETA_ASSUMED=50.0
    results=[]
    for row in rows:
        pout=float(row["pout_w"])
        assert row["speaker_ohms"]=="8"
        p_lo=float(row["pdiss_low_w"])
        p_hi=float(row["pdiss_high_w"])
        assert row["basis"]=="manual_broad_TI_Fig_6_7_typical_only"
        assert 0.15<p_lo<p_hi<0.65, "Brackets must be plausible rough graph readings"
        i_lo,i_hi=estimate_bracket(pout,p_lo,p_hi)
        ideal=class_b_ideal_average_supply_current(pout,8)
        # Typical graphical figures exceed the ideal class-B sine benchmark.
        assert ideal<i_lo<i_hi, "Approximate read inconsistent with idealized sine floor"
        # Regulator supplies LM386 rail current PLUS its mandatory feedback bleed.
        i_reg_low=i_lo+min_bleeder_a()
        i_reg_high=i_hi+max_bleeder_a()
        assert 0.05<i_reg_low<i_reg_high<0.20
        tj=junction_scenario_c(VIN_MAX,lowv,i_reg_high,T_AMB,THETA_ASSUMED)
        assert tj < 125, "Would exceed assumed temperature *scenario*, still not certification"
        results.append((pout,round(i_lo,3),round(i_hi,3),
                        round(i_reg_low,3),round(i_reg_high,3),round(tj,1)))
    assert results[0][1]<results[1][1]
    assert 0.10<results[1][4]<0.16
    # DO NOT turn these typical estimates into a regulator ampere rating.
    assert theta_required_c_per_w(VIN_MAX,lowv,0.35,T_AMB)<40
    assert isclose(speaker_ideal(8,0.125).output_irms,0.125,rel_tol=1e-9)
    print("LM386_TYPICAL_FIGURE_GRAPH_RAIL_CURRENT_BRACKETS_NOT_GUARANTEED",results,flush=True)
    print("LM317_6V_LAB_GRAPH_THERMAL_ONLY_ASSUMED_THETA_50",flush=True)
    print("PASS_LM386_TYPICAL_CURRENT_GRAPH_ENVELOPE_NOT_VENDOR_SPICE_OR_FAB",flush=True)


if __name__=="__main__":
    run()
