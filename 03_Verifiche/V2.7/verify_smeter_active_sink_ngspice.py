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


def simulate(vdd, vset, rcoil=500, beta=100):
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
