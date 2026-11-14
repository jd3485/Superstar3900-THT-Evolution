#!/usr/bin/env python3
"""Fail-closed DC fault envelope for bench-only R1903; NOT hardware qualification.

Assumptions: ideal sustained source, external lower-clamp Vf=0.2V,
Yageo MFR1WS 1W@70C linearly derated to 0W@155C (2024-04-03 v4).
Source current is NOT guaranteed identical to MCP6002 internal pin current.
No pulse, tolerance drift, self-heating, thermal mounting, or ESD modeled.
"""
import math

R_NOM = 120000.0
R_TOL = 0.005
R_MIN = R_NOM * (1.0 - R_TOL)
VF_ASSUMED = 0.2
ABS_INPUT_STRESS_A = 0.002
P70_W = 1.0
MAX_WORKING_V = 400.0


def power_derated(t_c):
    if not math.isfinite(t_c):
        raise ValueError("temperature must be finite")
    return P70_W if t_c <= 70.0 else P70_W * max(0.0, (155.0 - t_c) / 85.0)


def max_dc_source_magnitude_by_resistor(t_c):
    """Upper bound solely for idealized resistor dissipation/RCWV, NOT safety."""
    return VF_ASSUMED + min(MAX_WORKING_V, math.sqrt(R_MIN * power_derated(t_c)))


def fault_model(source_magnitude_v, t_c):
    if not math.isfinite(source_magnitude_v) or source_magnitude_v < 0:
        raise ValueError("expected finite nonnegative source magnitude")
    v_res = max(0.0, source_magnitude_v - VF_ASSUMED)
    i = v_res / R_MIN
    p = v_res * i
    rated = power_derated(t_c)
    return {
        "source_magnitude_V": source_magnitude_v,
        "temp_C": t_c,
        "current_from_source_A_model_only": i,
        "resistor_W_model_only": p,
        "resistor_derated_limit_W": rated,
        "resistor_DC_envelope_pass_model_only": rated > 0 and p <= rated
           and v_res <= MAX_WORKING_V,
        "source_current_below_amp_abs_stress_model_only": i < ABS_INPUT_STRESS_A,
        "MCP6002_pin_protection_qualified": False,
        "ESD_and_pulses_qualified": False,
        "PCB_and_mounting_qualified": False,
        "no_fab": True,
    }


def verify():
    # At hot conditions the resistor derating, not a 2 mA chip *stress*
    # ceiling, becomes first constraint. Do not interpret either as
    # permission for real input faults.
    samples = {t: fault_model(200.0, t) for t in (25, 70, 85, 100, 125, 130, 150, 155)}
    assert all(samples[t]["resistor_DC_envelope_pass_model_only"]
               for t in (25, 70, 85, 100, 125))
    assert all(not samples[t]["resistor_DC_envelope_pass_model_only"]
               for t in (130, 150, 155))
    assert all(samples[t]["source_current_below_amp_abs_stress_model_only"]
               for t in samples)  # NOT pin current qualification!
    cutoff_t = 155.0 - 85.0 * ((200.0 - VF_ASSUMED)**2 / R_MIN / P70_W)
    assert 125.0 < cutoff_t < 130.0
    assert max_dc_source_magnitude_by_resistor(125) > 200.0
    assert max_dc_source_magnitude_by_resistor(130) < 200.0
    assert max_dc_source_magnitude_by_resistor(155) == VF_ASSUMED
    assert max_dc_source_magnitude_by_resistor(130) < (
        VF_ASSUMED + ABS_INPUT_STRESS_A * R_MIN)
    # Distinguish physical 400 V max, sqrt(P*R) limit, and 2 mA
    # absolute maximum. 400 V is NOT allowed for this R at 70 C.
    assert max_dc_source_magnitude_by_resistor(70) < MAX_WORKING_V
    assert not fault_model(250, 70)["source_current_below_amp_abs_stress_model_only"]
    for bad_t in (float("nan"), float("inf"), -float("inf")):
        try:
            power_derated(bad_t)
        except ValueError:
            pass
        else:
            raise AssertionError("nonfinite temperature accepted")
    try:
        fault_model(float("nan"), 25)
    except ValueError:
        pass
    else:
        raise AssertionError("nonfinite source accepted")
    print("SMETER_R1903_YAGEO_FAULT_ENVELOPE_FAIL_CLOSED", {
        "MPN_candidate": "MFR1WSDRE52-120K",
        "resistor_Rmin_ohm": R_MIN,
        "negative_source_200V_derating_cutoff_C_ideal": round(cutoff_t, 4),
        "model_DC_source_limit_125C_V": round(max_dc_source_magnitude_by_resistor(125), 5),
        "model_DC_source_limit_130C_V": round(max_dc_source_magnitude_by_resistor(130), 5),
        "model_source_current_200V_mA": round(samples[130]["current_from_source_A_model_only"] * 1000, 6),
        "125C_model_pass": samples[125]["resistor_DC_envelope_pass_model_only"],
        "130C_model_pass": samples[130]["resistor_DC_envelope_pass_model_only"],
        "actual_MCP6002_internal_current_qualified": False,
        "manufacturer_active_status_confirmed": False,
        "pulse_power_off_self_heating_and_PCB_qualified": False,
        "NO_FAB_NO_TX": True,
    }, flush=True)


if __name__ == "__main__":
    verify()
