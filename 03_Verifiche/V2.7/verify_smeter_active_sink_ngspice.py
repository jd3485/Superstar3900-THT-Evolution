#!/usr/bin/env python3
"""Independent ngspice BENCH screen for candidate analog S-meter current sink.

No vendor macro, no FSD selection, no 5V supply/AGC or power-off qualification.
Never derive a production current limit or a KiCad/PCB claim from this test.
"""
from pathlib import Path
import math
import re
import subprocess
import tempfile

CIR = Path(__file__).with_name("SMETER_ACTIVE_SINK_BENCH_V2_7.cir")
ROOT = Path(__file__).resolve().parents[2]


def simulate(vdd, vset, rcoil=500, beta=100, ce_short=False):
    if not all(math.isfinite(x) for x in (vdd, vset, rcoil, beta)):
        raise ValueError("non-finite case")
    if vdd < 0 or vset < 0 or rcoil <= 0 or beta < 1:
        raise ValueError("invalid supply/command/coil")
    src = CIR.read_text(encoding="utf-8")
    for token in (
        "Q2101 METER_LOW BASE SENSE Q3904_GENERIC",
        "RSENSE SENSE 0 10000",
        "RPULL BASE 0 100000",
        "BAMP DRIVE 0 V = min(max(5000*(V(CMD)-V(SENSE)),0),max(V(VDD),0))",
        "not 2N3904 vendor model",
    ):
        assert token in src, ("missing model topology/qualifier", token)
    src = src.replace("VDD VDD 0 5\n", f"VDD VDD 0 {vdd}\n")
    src = src.replace("VSET CMD 0 0.5\n", f"VSET CMD 0 {vset}\n")
    src = src.replace("RCOIL VDD METER_LOW 500\n", f"RCOIL VDD METER_LOW {rcoil}\n")
    # BF is a parameter of the GENERIC BJT only; never call it a vendor hFE limit.
    assert src.count("BF=100 VAF=80") == 1
    src = src.replace("BF=100 VAF=80", f"BF={beta} VAF=80")
    assert src.count("VDD VDD 0 ") == 1
    assert src.count("VSET CMD 0 ") == 1
    assert src.count("RCOIL VDD METER_LOW ") == 1
    # Deliberate single-fault test: collector-emitter hard short bypasses
    # transistor drive control. Retain the transistor so the circuit model
    # otherwise remains identical to the clean bench. This is not an ESD test.
    if ce_short:
        assert src.count(".op\n.end\n") == 1
        src = src.replace(".op\n.end\n", "RCE_SHORT METER_LOW SENSE 0.001\n.op\n.end\n")
    src = src.replace(".op\n.end\n",
        ".control\nset noaskquit\nop\nlet meter_ua = -i(vdd)*1e6\n"
        "print meter_ua\nquit\n.endc\n.end\n")
    with tempfile.TemporaryDirectory(prefix="tht_smeter_sink_") as temp:
        netlist = Path(temp)/"bench.cir"
        netlist.write_text(src, encoding="utf-8")
        cp = subprocess.run(["ngspice", "-b", str(netlist)],
                            cwd=ROOT, capture_output=True, text=True, timeout=30)
    output = cp.stdout + "\n" + cp.stderr
    assert cp.returncode == 0, output[-4000:]
    match = re.search(r"meter_ua\s*=\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)", output, re.I)
    assert match, ("missing real ngspice operating-point evidence", output[-3000:])
    return float(match.group(1))


def main():
    baseline = simulate(5, 0.5)
    low = simulate(5, 0.1)
    zero = simulate(5, 0)
    power_off = simulate(0, 0.5)
    different_coil = simulate(5, 0.5, 5000)
    overload = simulate(5, 1.0)
    # Candidate Velleman AIM60005 webpage lists 50uA FSD, 20kohm total
    # input resistance; input resistance is not certified coil-only R.
    candidate_meter = simulate(5, 0.5, rcoil=20000)
    beta40 = simulate(5, 0.5, beta=40)
    beta200 = simulate(5, 0.5, beta=200)
    # Fail-closed counterexample on the real ngspice circuit topology:
    # even with command held at ZERO, a single Q2101 C-E short supplies
    # dangerous coil current from VDD. The 20k load is an OEM-candidate
    # INPUT resistance, not verified winding resistance or overload rating.
    ce_short_candidate = simulate(5, 0, rcoil=20000, ce_short=True)
    # Distributor TME specifies 2kΩ for identical Velleman AIM60005;
    # manufacturer page states 20kΩ, unresolved 10x contradiction.
    ce_short_2k_distributor_case = simulate(5, 0, rcoil=2000, ce_short=True)
    ce_short_low_impedance = simulate(5, 0, rcoil=500, ce_short=True)
    ce_short_poweroff_ideal = simulate(0, 0, rcoil=20000, ce_short=True)
    # This checks the assumed ideal servo only. It is NOT a measured
    # current tolerance, output compliance or fault isolation guarantee.
    assert 45 < baseline < 55, baseline
    assert 8 < low < 12, low
    assert abs(zero) < 0.5, zero
    assert abs(power_off) < 0.5, power_off
    assert 45 < different_coil < 55, different_coil
    assert 45 < candidate_meter < 55, candidate_meter
    # Current is sensed at EMITTER; collector/meter current is smaller
    # because Icollector = Iemitter - Ibase (beta dependent).
    # BF=40/200 here are model sweeps, NOT 2N3904 guaranteed hFE at 50uA.
    assert beta40 < baseline < beta200, (beta40, baseline, beta200)
    assert 47 < beta40 < 50 and 49 < beta200 < 50
    # Independent resistor-network cross-check, not vendor device proof:
    # 5V / (Rcoil + RSENSE) ignores 1mohm shorts and tiny leakage.
    expected_ce_short_20k_uA = 5/(20000+10000)*1e6
    expected_ce_short_500_uA = 5/(500+10000)*1e6
    expected_ce_short_2k_uA = 5/(2000+10000)*1e6
    assert math.isclose(ce_short_candidate, expected_ce_short_20k_uA, rel_tol=0.03)
    assert math.isclose(ce_short_low_impedance, expected_ce_short_500_uA, rel_tol=0.03)
    assert math.isclose(ce_short_2k_distributor_case, expected_ce_short_2k_uA, rel_tol=0.03)
    assert ce_short_2k_distributor_case > 8*50
    assert ce_short_candidate < ce_short_2k_distributor_case < ce_short_low_impedance
    assert ce_short_candidate > 3*50  # hypothetical 50uA meter is NOT protected
    assert ce_short_low_impedance > 8*50
    assert abs(ce_short_poweroff_ideal) < 0.1
    assert zero < 0.5 and ce_short_candidate > 150  # OFF command cannot isolate fault
    for beta_bad in (0, -1, float('inf'), float('nan')):
        try:
            simulate(5, 0.5, beta=beta_bad)
        except ValueError:
            pass
        else:
            raise AssertionError('bad generic beta accepted')
    assert overload > baseline * 1.5  # dangerous absent an OEM FSD cap
    assert max(baseline, overload) < 200000 # unrelated transistor absolute maximum
    print("SMETER_CURRENT_SINK_NGSPICE_GENERIC_MODEL_ONLY", {
        "at_5V_cmd0p5V_coil500ohm_uA": baseline,
        "at_5V_cmd0p1V_coil500ohm_uA": low,
        "cmd0_uA": zero,
        "bench_power_off_uA": power_off,
        "at_5V_cmd0p5V_coil5kohm_uA": different_coil,
        "unsafe_cmd1V_uA": overload,
        "velleman_AIM60005_candidate_input_resistance_ohm": 20000,
        "velleman_AIM60005_candidate_modeled_coil_current_uA": candidate_meter,
        "BJT_generic_beta40_coil_uA": beta40,
        "BJT_generic_beta200_coil_uA": beta200,
        "Q2101_CE_SHORT_CMD0_5V_20k_candidate_uA": ce_short_candidate,
        "Q2101_CE_SHORT_CMD0_5V_500ohm_lab_uA": ce_short_low_impedance,
        "Q2101_CE_SHORT_CMD0_5V_2k_distributor_uA": ce_short_2k_distributor_case,
        "AIM60005_internal_ohms_OEM_vs_distributor_discrepancy": "OEM 20000 vs TME 2000, NOT QUALIFIED",
        "Q2101_CE_SHORT_CMD0_VDD0_ideal_uA": ce_short_poweroff_ideal,
        "single_CE_short_fail_closed": False,
        "independent_hard_current_disconnect_present": False,
        "vendor_hFE_at_50uA_guaranteed": False,
        "movement_OEM_active_status_and_overload_qualified": False,
        "BJT_model_is_vendor": False,
        "OPAMP_model_is_vendor": False,
        "current_cap_fsd_qualified": False,
        "unpowered_external_meter_supply_fault_qualified": False,
        "KiCad_native_schematic_for_this_active_sink_exists": True,
        "KiCad_to_SPICE_equivalence_certified": False,
        "NO_FAB_NO_TX": True,
    }, flush=True)


if __name__ == "__main__":
    main()
