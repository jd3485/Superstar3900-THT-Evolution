#!/usr/bin/env python3
"""Real KiCad9 pinned two-stage PMOS topology; single/double synthetic faults.

Graph edges approximate ideal drain->source P-MOS body diodes and ON channels.
No OEM semiconductor I/V, driver threshold, load, thermal or safety claim.
"""
from pathlib import Path
import itertools
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets,require
from verify_two_complete_pmos_stages_native import SCH,EXPECTED

FETS={"Q804":("IN","SOURCE_A"),"Q805":("MID","SOURCE_A"),
      "Q814":("MID","SOURCE_B"),"Q815":("OUT","SOURCE_B")}
ALL_FAULTS=("Q806_CE_SHORT","Q816_CE_SHORT",
            "Q804_DS_SHORT","Q805_DS_SHORT","Q814_DS_SHORT","Q815_DS_SHORT")

def directed_path(en_a,en_b,faults):
    """Return forward and reverse reachability of ideal physical pin graph."""
    driven_a=en_a or "Q806_CE_SHORT" in faults
    driven_b=en_b or "Q816_CE_SHORT" in faults
    edges=[]
    for fet,(drain,source) in FETS.items():
        # Body diode of a P-channel device runs from drain to source.
        edges.append((drain,source))
        # Either channel switched ON or this MOSFET drain-source shorted.
        active=(driven_a if fet in ("Q804","Q805") else driven_b)
        if active or fet+"_DS_SHORT" in faults:
            edges.append((source,drain))
    def reachable(src,dst):
        seen={src};stack=[src]
        while stack:
            node=stack.pop()
            if node==dst:return True
            for a,b in edges:
                if node==a and b not in seen:
                    seen.add(b);stack.append(b)
        return False
    return reachable("IN","OUT"),reachable("OUT","IN")

def main():
    with tempfile.TemporaryDirectory(prefix="two_pmos_single_double_fault_") as d:
        nets=exported_nets(SCH,Path(d)/"stages.net")
    assert set(nets)==set(EXPECTED)
    for net,members in EXPECTED.items():
        require(nets,net,*members)
        assert nets[net]==members
    assert sum(map(len,nets.values()))==54 and len(nets)==14
    for q,drain,source,gate in (
        ("Q804","PRIMARY_IN_DRAIN_LAB","FLOATING_COMMON_SOURCE_LAB","COMMON_GATE_LAB"),
        ("Q805","SECONDARY_OUT_DRAIN_LAB","FLOATING_COMMON_SOURCE_LAB","COMMON_GATE_LAB"),
        ("Q814","SECONDARY_OUT_DRAIN_LAB","FLOATING_SOURCE_B_LAB","COMMON_GATE_B_LAB"),
        ("Q815","FINAL_SECONDARY_OUT_LAB","FLOATING_SOURCE_B_LAB","COMMON_GATE_B_LAB")):
        require(nets,drain,(q,"2"))
        require(nets,source,(q,"3"))
        require(nets,gate,(q,"1"))
    assert nets["COMMON_GATE_LAB"].isdisjoint(nets["COMMON_GATE_B_LAB"])
    assert nets["FLOATING_COMMON_SOURCE_LAB"].isdisjoint(nets["FLOATING_SOURCE_B_LAB"])
    assert ("Q806","3") in nets["DRIVER_SINK_LAB"]
    assert ("Q816","3") in nets["DRIVER_SINK_B_LAB"]

    assert directed_path(False,False,set())==(False,False)
    assert directed_path(True,False,set())==(False,False)
    assert directed_path(False,True,set())==(False,False)
    assert directed_path(True,True,set())==(True,True)

    # Off-command conditions: all 6 SINGLE synthetic fault types
    # should leave at least one complete anti-series stage OFF.
    singles={}
    for name in ALL_FAULTS:
        singles[name]=directed_path(False,False,{name})
    assert all(v==(False,False) for v in singles.values())

    # All C(6,2)=15 pairs of independent elementary fault labels.
    # An independently 'cut' stage CAN be bypassed by one DS short,
    # plus one stuck-driver in the OTHER stage. Two DS shorts may
    # align body diodes across both stages, enabling directed backfeed.
    pairs={}
    for a,b in itertools.combinations(ALL_FAULTS,2):
        pairs[(a,b)]=directed_path(False,False,{a,b})
    assert len(pairs)==15
    leaks={k:v for k,v in pairs.items() if v[0] or v[1]}
    expected={
      ("Q806_CE_SHORT","Q816_CE_SHORT"):(True,True),
      ("Q806_CE_SHORT","Q814_DS_SHORT"):(False,True),
      ("Q806_CE_SHORT","Q815_DS_SHORT"):(True,False),
      ("Q816_CE_SHORT","Q804_DS_SHORT"):(False,True),
      ("Q816_CE_SHORT","Q805_DS_SHORT"):(True,False),
      ("Q804_DS_SHORT","Q814_DS_SHORT"):(False,True),
      ("Q805_DS_SHORT","Q815_DS_SHORT"):(True,False)
    }
    assert leaks==expected,(leaks,expected)

    # Two driver-side shorts: both switch pairs commanded ON despite
    # both external enables OFF. This is a COMMON-CAUSE vulnerability.
    assert directed_path(False,False,{"Q806_CE_SHORT","Q816_CE_SHORT"})==(True,True)
    # Explicitly reject false claims of fail-OFF with any two faults.
    assert len(leaks)==7 and len(pairs)==15
    print("TWO_COMPLETE_PMOS_STAGE_FAULT_COVERAGE",{
      "native_components":24,"native_pins":54,"native_nets":14,
      "single_fault_cases":len(singles),
      "single_fault_directed_paths":sum(any(v) for v in singles.values()),
      "two_fault_cases":len(pairs),
      "two_fault_cases_with_at_least_one_direction_path":len(leaks),
      "two_stuck_drivers_bypass_both_stages":True,
      "real_current_or_temperature_qualified":False,
      "external_enables_supply_clamps_independent_qualified":False,
      "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_NATIVE_KICAD9_TWO_PMOS_STAGES_54PIN_14NET_21_FAULTS_NONFAB",flush=True)

if __name__=="__main__":
    main()
