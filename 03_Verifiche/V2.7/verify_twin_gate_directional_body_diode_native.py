#!/usr/bin/env python3
"""Native KiCad9 anti-series P-FET directional body diode single-gate fault.

Diode/channel Boolean graph is a topology *counterexample*, NOT voltage
drop/current/SOA/vendor qualification.  Both sources shared, two gate drives.
"""
from pathlib import Path
import sys
import tempfile
import itertools
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets,require
from verify_dual_pmos_twin_clamps_native import SCH,NET

def connectivity(on_a,on_b):
    # Pin drain Q804 = INPUT, drain Q805 = OUTPUT, both sources = NODE S.
    # P-channel MOS intrinsic diodes DRAIN -> SOURCE; channel is bidirectional ON.
    # This is an ideal graph: no voltage drop, thresholds, leakage, load or SOA.
    vertices=("IN","SRC","OUT")
    edges=[("IN","SRC"),("OUT","SRC")] # diode Q804 and diode Q805
    if on_a: edges.append(("SRC","IN"))
    if on_b: edges.append(("SRC","OUT"))
    def reachable(origin,dest):
        seen={origin}
        stack=[origin]
        while stack:
            node=stack.pop()
            if node==dest:return True
            for a,b in edges:
                if a==node and b not in seen:
                    seen.add(b);stack.append(b)
        return False
    return reachable("IN","OUT"),reachable("OUT","IN")

def main():
    with tempfile.TemporaryDirectory(prefix="twin_gate_directional_") as d:
        nets=exported_nets(SCH,Path(d)/"direction.net")
    assert len(nets)==12 and sum(map(len,nets.values()))==44
    for k,v in NET.items():
        require(nets,k,*v)
        assert nets[k]==v,(k,nets[k]^v)
    assert ("Q804","2") in nets["PRIMARY_IN_DRAIN_LAB"]
    assert ("Q805","2") in nets["SECONDARY_OUT_DRAIN_LAB"]
    assert {("Q804","3"),("Q805","3")}<=nets["FLOATING_COMMON_SOURCE_LAB"]
    assert ("Q804","1") in nets["COMMON_GATE_LAB"]
    assert ("Q805","1") in nets["GATE_B_LAB"]
    assert nets["GATE_B_LAB"].isdisjoint(nets["COMMON_GATE_LAB"])
    truth={
        (False,False):(False,False),
        (True,False):(False,True),
        (False,True):(True,False),
        (True,True):(True,True)
    }
    assert all(connectivity(*k)==v for k,v in truth.items())
    cases=0;invalid_forward=0;invalid_reverse=0
    forward_examples=[]
    for enable_a,enable_b,stuck_a,stuck_b in itertools.product((False,True),repeat=4):
        on_a=enable_a or stuck_a
        on_b=enable_b or stuck_b
        fwd,rev=connectivity(on_a,on_b)
        if not enable_a and not enable_b and (stuck_a ^ stuck_b):
            if fwd:
                invalid_forward+=1
                forward_examples.append(("Q807_CE_SHORT",on_a,on_b))
            if rev:invalid_reverse+=1
        cases+=1
    assert cases==16
    assert invalid_forward==1 and invalid_reverse==1
    assert forward_examples==[("Q807_CE_SHORT",False,True)]
    # A single Q807 driver short can create a directional INPUT->OUTPUT
    # path despite Q804 OFF, through Q804 intrinsic body diode.
    # Neither two independent gates nor twin clamps prevent this.
    print("SPLIT_PMOS_BODY_DIODE_SINGLE_GATE_DIRECTIONAL",{
        "KiCad9_pins":44,"native_nets":12,
        "driver_fault_boolean_cases":cases,
        "single_CE_short_ENABLE_A_B_ZERO_forward_paths":invalid_forward,
        "single_CE_short_ENABLE_A_B_ZERO_reverse_paths":invalid_reverse,
        "Q807_stuck_low_input_to_output_via_Q804_body_diode":True,
        "Q806_stuck_low_output_to_input_via_Q805_body_diode":True,
        "diode_forward_drop_current_gate_threshold_SOA_measured":False,
        "independent_forward_power_cut_qualified":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_NATIVE_KICAD9_TWIN_GATE_BODY_DIODE_44PIN_12NET_16_NONFAB",flush=True)
if __name__=="__main__":main()
