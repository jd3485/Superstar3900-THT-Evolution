#!/usr/bin/env python3
"""KiCad9-native PMOS TO-220 drain-tab short hazard, isolated THT lab.

IRF9540NPbF TO-220AB tab is electrically connected to DRAIN (pin 2)
per OEM package data. No PCB/heatsink exists or is qualified here.
"""
from __future__ import annotations
from itertools import combinations
import sys
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets,require
from verify_two_complete_pmos_stages_native import SCH,EXPECTED,direction

PMOS=("Q804","Q805","Q814","Q815")
NODES=("IN","MID","OUT")
CONTACT_PAIRS=tuple(combinations(PMOS,2))
EXPECTED_DRAINS={
    "Q804":"PRIMARY_IN_DRAIN_LAB",
    "Q805":"SECONDARY_OUT_DRAIN_LAB",
    "Q814":"SECONDARY_OUT_DRAIN_LAB",
    "Q815":"FINAL_SECONDARY_OUT_LAB",
}
LABELS={
    "PRIMARY_IN_DRAIN_LAB":"IN",
    "SECONDARY_OUT_DRAIN_LAB":"MID",
    "FINAL_SECONDARY_OUT_LAB":"OUT",
}
def conducts(shorts, enable_a=False, enable_b=False):
    """Ideal intrinsic body-diode graph plus hypothetical tab contacts."""
    edges=[("IN","SA"),("MID","SA"),("MID","SB"),("OUT","SB")]
    if enable_a: edges += [("SA","IN"),("SA","MID")]
    if enable_b: edges += [("SB","MID"),("SB","OUT")]
    for a,b in shorts:
        u=LABELS[EXPECTED_DRAINS[a]]
        v=LABELS[EXPECTED_DRAINS[b]]
        edges.extend([(u,v),(v,u)])
    def reachable(src,dst):
        seen={src};stack=[src]
        while stack:
            x=stack.pop()
            for u,v in edges:
                if u==x and v not in seen:
                    seen.add(v);stack.append(v)
        return dst in seen
    return reachable("IN","OUT"),reachable("OUT","IN")

def main():
    sch=SCH.read_text(encoding="utf8")
    with tempfile.TemporaryDirectory(prefix="two_stage_tab_short_") as td:
        nets=exported_nets(SCH,Path(td)/"tabs.net")
    assert set(nets)==set(EXPECTED)
    for name,pins in EXPECTED.items():
        require(nets,name,*pins)
        assert nets[name]==pins
    assert len(nets)==14 and sum(map(len,nets.values()))==54
    for ref,drain_net in EXPECTED_DRAINS.items():
        assert (ref,"2") in nets[drain_net]
        assert sch.count('(property "Reference" "'+ref+'"')==1
    assert nets[EXPECTED_DRAINS["Q804"]].isdisjoint(nets[EXPECTED_DRAINS["Q815"]])
    assert direction(False,False)==(False,False)
    assert conducts(())==(False,False)
    single=[(pair,conducts((pair,))) for pair in CONTACT_PAIRS]
    assert len(single)==6
    assert [p for p,v in single if v!=(False,False)] == [("Q804","Q815")]
    assert all(v in ((False,False),(True,True)) for _,v in single)
    double=[(pairs,conducts(pairs)) for pairs in combinations(CONTACT_PAIRS,2)]
    assert len(double)==15
    assert sum(v==(True,True) for _,v in double)==9
    assert conducts(CONTACT_PAIRS)==(True,True) # uninsulated common sink
    assert conducts((("Q805","Q814"),))==(False,False) # same mid copper only
    # No PCB/thermal model exists; these are graph connectivity hazards,
    # not transient/voltage, actual mounting, current or hardware proof.
    print("THT_TWO_STAGE_TO220_TAB_DRAIN_SHORT_HAZARD",{
       "native_physical_components":24,"native_pins":54,"native_nets":14,
       "pmos_to220_tab_equals_drain_pin2":True,
       "single_tab_contact_pairs":6,
       "single_pairs_bypass_full_off_isolation":1,
       "two_contact_pair_combinations":15,
       "two_pair_combinations_bypass":9,
       "common_metal_heatsink_uninsulated_full_bypass":True,
       "real_insulated_mounting_verified":False,
       "no_actual_pcb_no_drc_or_fabrication":True,
       "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_NATIVE_THT_TWO_STAGE_TO220_TAB_SHORT_21_NONFAB",flush=True)

if __name__=="__main__":
    main()
