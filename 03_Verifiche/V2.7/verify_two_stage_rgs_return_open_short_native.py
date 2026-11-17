#!/usr/bin/env python3
"""Synthetic isolated PMOS two-stage Rgs OPEN/SHORT return and sink faults.

Native KiCad9 pin/net/footprint anchoring. This is NOT a hardware safety
verification, vendor transistor transient, or qualified clamp model.
"""
from __future__ import annotations
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

CAP = (1e-9, 10e-9, 100e-9)  # hypothetical C, not OEM Qg/Ciss
INITIAL = (5., 12.)            # hypothetical gate-source initial ON bias
SINK = (0., 25e-6, 100e-6)     # hypothetical persistent external sink
SECONDS = (0., 50e-6, 500e-6, 5e-3)
RGS = {"NOM": 47000., "OPEN": math.inf, "SHORT": 0.}

def ideal_vgs(rgs_state, cap, initial, sink, seconds):
    """Unclamped first-order bias; OPEN has no DC return.

    Values for OPEN and persistent sink represent ideal uncapped mathematical
    growth, NOT actual MOSFET gate or Zener voltages.
    """
    r = RGS[rgs_state]
    if r == 0:
        return 0.
    if math.isinf(r):
        return initial + sink * seconds / cap
    final = sink * r
    return final + (initial - final) * math.exp(-seconds/(r*cap))

def main():
    raw = SCH.read_text(encoding="utf8")
    with tempfile.TemporaryDirectory(prefix="two_stage_return_fault_") as td:
        nets = exported_nets(SCH, Path(td)/"return.net")
    assert set(nets) == set(EXPECTED)
    for name, pins in EXPECTED.items():
        require(nets, name, *pins)
        assert nets[name] == pins
    assert len(nets) == 14 and sum(map(len, nets.values())) == 54
    summary = {}
    for stage, source, gate, diodes, pull, sink_res in STAGES:
        assert (pull, "1") in nets[source]
        assert (pull, "2") in nets[gate]
        assert (sink_res, "2") in nets[gate]
        assert properties(raw,pull)[0].startswith("47k_")
        assert properties(raw,sink_res)[0].startswith("10k_")
        assert nets[source].isdisjoint(nets[gate])
        for diode in diodes:
            assert (diode, "1") in nets[source]
            assert (diode, "2") in nets[gate]
        count = short = floating = runaway = 0
        max_open_uncapped = 0.
        for state, cap, initial, sink, t in itertools.product(
            RGS, CAP, INITIAL, SINK, SECONDS
        ):
            v = ideal_vgs(state,cap,initial,sink,t)
            assert math.isfinite(v) and v >= 0.
            if state == "SHORT":
                assert v == 0.
                short += 1
            elif state == "OPEN":
                assert v >= initial
                floating += (sink == 0.)
                runaway += (sink > 0. and t > 0.)
                max_open_uncapped = max(max_open_uncapped,v)
                if sink == 0:
                    assert v == initial  # floating charged node: no recovery
            else:
                final = sink * RGS[state]
                assert min(initial,final)-1e-9 <= v <= max(initial,final)+1e-9
                if t == 0:
                    assert v == initial
            count += 1
        assert count == 216
        assert (short,floating,runaway) == (72,24,36)
        # An unbounded/open-gate result MUST NOT be called a physical gate voltage.
        assert max_open_uncapped > 500.
        summary[stage] = {
            "synthetic_cases":count,
            "ideal_rgs_short_cases":short,
            "rgs_open_floating_no_sink_cases":floating,
            "rgs_open_sink_unbounded_growth_cases":runaway,
            "max_open_case_is_unphysical":True
        }
    assert summary["A"] == summary["B"]
    print("TWO_STAGE_RGS_OPEN_SHORT_UNQUALIFIED",{
        "native_components":24,"native_pins":54,"native_nets":14,
        "total_synthetic_cases":432,"stages":summary,
        "zener_and_miller_omitted":True,
        "gate_return_open_cannot_guarantee_off":True,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_NATIVE_THT_TWO_STAGE_RGS_FAULT_432_NONFAB",flush=True)

if __name__ == "__main__":
    main()
