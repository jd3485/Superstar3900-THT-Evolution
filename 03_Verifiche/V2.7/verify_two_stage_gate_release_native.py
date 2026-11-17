#!/usr/bin/env python3
"""Ideal gate release from a hypothetical initially ON PMOS bias, KiCad9 anchored.

Not an OEM gate-charge, Miller, real switching, or safety/timing qualification.
The external sink is hypothetically persistent; no claim of guaranteed OFF.
"""
import itertools
import math
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets, require
from verify_two_complete_pmos_stages_native import SCH, EXPECTED
from verify_two_stage_twin_zener_single_open_native import STAGES, properties

RGS = (44650., 47000., 49350.)  # 47k +/- 5%, not OEM population
CAP = (1e-9, 10e-9, 100e-9)      # assumed total capacitance, not Ciss
SINK = (0., 5e-6, 25e-6, 100e-6)  # hypothetical persistent gate sink
INITIAL_ABS_VGS = (5., 12.)       # ideal initial ON bias, not measured
ELAPSED_TAU = (0., 1., 2., 3., 5.)
N_STEPS = 1024

def exact(v0, r, sink, elapsed):
    final = sink * r
    return final + (v0 - final) * math.exp(-elapsed)

def independently_integrated(v0, r, sink, elapsed):
    """Implicit trapezoidal integration of dV/d(t/tau) = sink*r-V."""
    if elapsed == 0:
        return v0
    dt = elapsed / N_STEPS
    a = (1. - dt/2.) / (1. + dt/2.)
    b = (dt * sink * r) / (1. + dt/2.)
    v = v0
    for _ in range(N_STEPS):
        v = a * v + b
    return v

def main():
    schematic = SCH.read_text(encoding="utf8")
    with tempfile.TemporaryDirectory(prefix="two_stage_release_") as td:
        nets = exported_nets(SCH, Path(td)/"release.net")
    assert set(nets) == set(EXPECTED)
    for name, pins in EXPECTED.items():
        require(nets, name, *pins)
        assert nets[name] == pins
    assert len(nets) == 14 and sum(map(len, nets.values())) == 54

    results = {}
    for stage, source, gate, diodes, pull, sink_resistor in STAGES:
        assert (pull, "1") in nets[source]
        assert (pull, "2") in nets[gate]
        assert (sink_resistor, "2") in nets[gate]
        assert properties(schematic, pull)[0].startswith("47k_")
        assert properties(schematic, sink_resistor)[0].startswith("10k_")
        for diode in diodes:
            assert (diode, "1") in nets[source] and (diode, "2") in nets[gate]
        cases = above_2 = above_4 = late_above_4 = 0
        minimum = float("inf")
        for r, cap, sink, v0, elapsed in itertools.product(
                RGS, CAP, SINK, INITIAL_ABS_VGS, ELAPSED_TAU):
            v = exact(v0, r, sink, elapsed)
            numeric = independently_integrated(v0, r, sink, elapsed)
            assert abs(v - numeric) < 1e-4, (stage, r, cap, sink, v0, elapsed, v, numeric)
            assert min(v0, sink*r)-1e-10 <= v <= max(v0, sink*r)+1e-10
            if elapsed == 0:
                assert v == v0
            if sink == 0 and elapsed > 0:
                assert v < v0
            assert r * cap > 0
            above_2 += v >= 2.
            above_4 += v >= 4.
            late_above_4 += v >= 4. and elapsed == 5.
            minimum = min(minimum, v)
            cases += 1
        assert (cases, above_2, above_4, late_above_4) == (360, 189, 171, 18)
        assert 0.0336 < minimum < 0.0338
        results[stage] = dict(cases=cases, ge2_marker=above_2,
                              ge4_marker=above_4, ge4_at_five_tau=late_above_4)
    assert results["A"] == results["B"]
    print("THT_TWO_STAGE_GATE_RELEASE", {
        "native_components":24, "native_pins":54, "native_nets":14,
        "synthetic_cases":720, "per_stage":results,
        "tau_min_us":44.65, "tau_max_ms":4.935,
        "ideal_rc_with_constant_sink_not_oem":True,
        "no_guaranteed_off_no_real_vth_no_switch_timing":True,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True}, flush=True)
    print("PASS_NATIVE_THT_TWO_STAGE_GATE_RELEASE_720_NONFAB", flush=True)

if __name__ == "__main__":
    main()
