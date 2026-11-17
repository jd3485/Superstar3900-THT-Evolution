#!/usr/bin/env python3
"""All fifteen conductive mounting partitions of four drain-connected TO-220 tabs.

KiCad9 schematic pinned; hypothetical conductive mounting only, not actual
isolator reliability, thermal/clearance check or hardware safety proof.
"""
from collections import Counter
from itertools import combinations, product
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets,require
from verify_two_complete_pmos_stages_native import SCH,EXPECTED
from verify_two_stage_to220_tab_drain_short_native import (
    PMOS, EXPECTED_DRAINS, LABELS, conducts
)

def partitions(sequence):
    """Enumerate set partitions: one mounting conductor per block."""
    if not sequence:
        yield ()
        return
    first,*rest=sequence
    for blocks in partitions(rest):
        yield ((first,),)+blocks
        for i in range(len(blocks)):
            updated=list(blocks)
            updated[i]=(first,)+updated[i]
            yield tuple(updated)

def mechanical_shorts(blocks):
    return tuple(pair for block in blocks for pair in combinations(block,2))

def main():
    with tempfile.TemporaryDirectory(prefix="to220_partition_") as td:
        nets=exported_nets(SCH,Path(td)/"partition.net")
    assert set(nets)==set(EXPECTED)
    for name,pins in EXPECTED.items():
        require(nets,name,*pins)
        assert nets[name]==pins
    assert len(nets)==14 and sum(map(len,nets.values()))==54
    for ref,net in EXPECTED_DRAINS.items():
        assert (ref,"2") in nets[net],(ref,net)
    groups=list(partitions(PMOS))
    # Bell(4)=15; no duplicated mechanical partition.
    normalized={tuple(sorted(tuple(sorted(b)) for b in blocks)) for blocks in groups}
    assert len(groups)==len(normalized)==15
    counts=Counter()
    for blocks in groups:
        shorts=mechanical_shorts(blocks)
        for ena,enb in product((False,True),repeat=2):
            forward,reverse=conducts(shorts,ena,enb)
            assert forward==reverse,(blocks,ena,enb,forward,reverse)
            counts[(ena,enb,forward)]+=1
            if not shorts and not ena and not enb:
                assert not forward
        # IN, MID, OUT always distinct is a sufficient mechanically isolated rule.
        drain_classes=[{LABELS[EXPECTED_DRAINS[ref]] for ref in block}
                       for block in blocks]
        if all(len(nodes)==1 for nodes in drain_classes):
            assert not conducts(shorts,False,False)[0]
    expected={
        (False,False,True):7,(False,False,False):8,
        (True,False,True):10,(True,False,False):5,
        (False,True,True):10,(False,True,False):5,
        (True,True,True):15
    }
    assert dict(counts)==expected,(counts,expected)
    print("THT_TO220_MOUNTING_CONDUCTOR_PARTITIONS",{
      "native_components":24,"native_pins":54,"native_nets":14,
      "distinct_mounting_partitions":15,"tested_stage_states":60,
      "bypass_count_both_off":7,
      "bypass_count_exactly_one_stage_on_each":10,
      "bypass_count_both_on":15,
      "OEM_tab_equals_drain_pin2_unqualified_mounting":True,
      "no_real_pcb_heatsink_insulation_or_drc":True,
      "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_NATIVE_TO220_INSULATION_PARTITION_60_NONFAB",flush=True)

if __name__=="__main__":
    main()
