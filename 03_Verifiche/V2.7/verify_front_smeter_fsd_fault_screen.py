#!/usr/bin/env python3
"""Fail-closed FRONT meter coil DC current screen; analytical, not hardware signoff.

Based on native FRONT schematic J1801 -> RV1801 wiper -> R1801 -> R1802
-> J1802 coil -> return; potentiometer 1-to-3 winding shunts the source.
Ignore Rcoil only to get a conservative upper bound on current at a
low-impedance wiper. The candidate source has no known max DC voltage,
meter coil ohms/full-scale current, cable faults, or driver capability.
"""
from math import isclose, isfinite

R_LIMIT = 100_000.0
R_TOL_SCREEN = 0.05 # illustrative tolerance; exact MPN not selected
P_RESISTOR_NOMINAL = 0.25 # do NOT assume full power at actual temp


def screen(v_drive, shorted_resistors=0, coil_ohm=0.0, fsd_a=None):
    """Conservative overcurrent bound at minimum wiper source impedance."""
    if not isfinite(v_drive) or not isfinite(coil_ohm) or coil_ohm < 0:
        raise ValueError("finite drive and nonnegative coil resistance required")
    if shorted_resistors not in (0, 1, 2):
        raise ValueError("only 0, 1, or 2 shorted series resistors")
    if fsd_a is not None and (not isfinite(fsd_a) or fsd_a <= 0):
        raise ValueError("FSD must be positive")
    live = 2-shorted_resistors
    r_series_min = live*R_LIMIT*(1-R_TOL_SCREEN)
    r_total_min = r_series_min+coil_ohm
    current_bound_a = abs(v_drive)/r_total_min if r_total_min else float("inf")
    resistor_w_each = current_bound_a**2*R_LIMIT*(1+R_TOL_SCREEN)
    # An FSD-based "PASS" is an idealized screen only. Never claim
    # qualification without actual FSD, source clamp, coil, cable, PVT.
    return {
        "source_V": v_drive,
        "live_series_resistors": live,
        "coil_current_upper_bound_A_ideal": current_bound_a,
        "each_resistor_W_upper_bound_ideal": resistor_w_each,
        "FSD_A_assumed": fsd_a,
        "possible_FSD_exceedance_model": (
            None if fsd_a is None else current_bound_a > fsd_a),
        "resistor_nominal_0p25W_exceeded_model": resistor_w_each > P_RESISTOR_NOMINAL,
        "meter_and_cable_qualified": False,
        "no_fab_no_tx": True,
    }


def verify():
    # PVT envelope examples: 20V ideal fixed voltage source; no meter
    # resistance provides worst-case current; 5% illustrative bound.
    v = 20.0
    healthy = screen(v)
    one_short = screen(v, shorted_resistors=1)
    both_short = screen(v, shorted_resistors=2)
    assert isclose(healthy["coil_current_upper_bound_A_ideal"],20/(190000))
    assert isclose(one_short["coil_current_upper_bound_A_ideal"],20/(95000))
    assert both_short["coil_current_upper_bound_A_ideal"] == float("inf")
    assert one_short["coil_current_upper_bound_A_ideal"] == 2*healthy["coil_current_upper_bound_A_ideal"]
    assert screen(0)["coil_current_upper_bound_A_ideal"] == 0
    assert screen(-20)["coil_current_upper_bound_A_ideal"] == healthy["coil_current_upper_bound_A_ideal"]
    assert screen(20,coil_ohm=1000)["coil_current_upper_bound_A_ideal"] < healthy["coil_current_upper_bound_A_ideal"]
    # Example sensitivities do not select a real meter.
    assert screen(20,fsd_a=50e-6)["possible_FSD_exceedance_model"] is True
    assert screen(20,fsd_a=200e-6)["possible_FSD_exceedance_model"] is False
    assert screen(20,shorted_resistors=1,fsd_a=200e-6)["possible_FSD_exceedance_model"] is True
    assert screen(20)["possible_FSD_exceedance_model"] is None
    assert screen(400)["resistor_nominal_0p25W_exceeded_model"]
    for bad in (float("nan"),float("inf")):
        try:
            screen(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("nonfinite drive accepted")
    print("FRONT_SMETER_FSD_CURRENT_FAULT_SCREEN_FAIL_CLOSED",{
        "R1801_R1802_candidate_ohm_each":R_LIMIT,
        "R_tolerance_used_illustrative":R_TOL_SCREEN,
        "drive_20V_two_resistors_max_uA":round(healthy["coil_current_upper_bound_A_ideal"]*1e6,4),
        "drive_20V_one_short_max_uA":round(one_short["coil_current_upper_bound_A_ideal"]*1e6,4),
        "drive_20V_two_shorts_no_bounded_current":True,
        "actual_source_max_voltage_known":False,
        "actual_meter_FSD_known":False,
        "actual_coil_resistance_known":False,
        "pot_input_winding_and_wiper_faults_qualified":False,
        "thermal_and_transient_qualified":False,
        "NO_FAB_NO_TX":True,
    },flush=True)

if __name__=="__main__":
    verify()
