#!/usr/bin/env python3
"""Provisional OEM G5V-1 DC5 six-terminal-to-FRONT-K1901 net mapping gate.

Read from ARATAS/Omron K048-E1 bottom-view terminal arrangement p4.
This is NOT a footprint/PCB approval. No new sheet connection is made.
"""
import itertools
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets
from verify_front_partial_hierarchy_native import SCH as FRONT

# OEM drawing p4 BOTTOM VIEW (pin numbers, *not* KiCad x/y positions):
# 1=NC, 10=NO, 5 and 6 are both linked COM contact leads.
# 2 and 9 are the polarity-independent coil.
OEM_BOTTOM_VIEW={
 "1":"NC_TO_AF_GND",
 "2":"COIL_PLUS_LAB",
 "5":"RELAY_COM_AUDIO",
 "6":"RELAY_COM_AUDIO",
 "9":"COIL_MINUS_LAB",
 "10":"NO_FROM_FRONT_VOLUME",
}
ABSTRACT_PIN_TO_NET={
 "1":"RELAY_COM_AUDIO",
 "2":"AF_GND",
 "3":"VOL_WIPER_TO_AMP",
 "4":"COIL_PLUS_LAB",
 "5":"COIL_MINUS_LAB",
}
OEM_TO_EXISTING_NET={
 "1":"AF_GND",
 "2":"COIL_PLUS_LAB",
 "5":"RELAY_COM_AUDIO",
 "6":"RELAY_COM_AUDIO",
 "9":"COIL_MINUS_LAB",
 "10":"VOL_WIPER_TO_AMP",
}
def mute_graph(contact, common_missing):
    """One ideal relay contact, or a broken NC/NO/COM terminal bond."""
    assert contact in ("NC","NO","OPEN")
    nets={pin:net for pin,net in OEM_TO_EXISTING_NET.items()
          if pin not in common_missing}
    paired = ({"NC":"1","NO":"10","OPEN":None})[contact]
    if not paired or not any(c in nets for c in ("5","6")):
        return frozenset()
    return frozenset((nets[paired],"RELAY_COM_AUDIO"))

def main():
    assert len(OEM_BOTTOM_VIEW)==6 and len(OEM_TO_EXISTING_NET)==6
    assert set(OEM_BOTTOM_VIEW)=={"1","2","5","6","9","10"}
    assert OEM_TO_EXISTING_NET["5"]==OEM_TO_EXISTING_NET["6"]
    assert OEM_TO_EXISTING_NET["1"]=="AF_GND"
    assert OEM_TO_EXISTING_NET["10"]=="VOL_WIPER_TO_AMP"
    assert {OEM_TO_EXISTING_NET["2"],OEM_TO_EXISTING_NET["9"]}=={
        "COIL_PLUS_LAB","COIL_MINUS_LAB"}
    with tempfile.TemporaryDirectory(prefix="front_g5v1_sixpad_") as td:
        nets=exported_nets(FRONT,Path(td)/"front.net")
    actual={}
    for name,pins in nets.items():
        for ref,pin in pins:
            if ref=="K1901":
                assert pin not in actual
                actual[pin]=name.rsplit("/",1)[-1]
    assert actual==ABSTRACT_PIN_TO_NET,(actual,ABSTRACT_PIN_TO_NET)
    # Explicit migration, no assumption that the two numbered systems match.
    assert {p:actual[p] for p in actual}==ABSTRACT_PIN_TO_NET
    assert OEM_TO_EXISTING_NET["5"]==actual["1"]
    assert OEM_TO_EXISTING_NET["6"]==actual["1"]
    assert OEM_TO_EXISTING_NET["1"]==actual["2"]
    assert OEM_TO_EXISTING_NET["10"]==actual["3"]
    assert OEM_TO_EXISTING_NET["2"]==actual["4"]
    assert OEM_TO_EXISTING_NET["9"]==actual["5"]
    states=0;normally_closed=normally_open=lost_both_common=0
    for contact,common5_missing,common6_missing in itertools.product(
           ("NC","NO","OPEN"),(False,True),(False,True)):
        missing={pin for pin,broken in (("5",common5_missing),("6",common6_missing)) if broken}
        out=mute_graph(contact,missing)
        if contact=="NC" and out:
            assert out==frozenset(("AF_GND","RELAY_COM_AUDIO"))
            normally_closed+=1
        elif contact=="NO" and out:
            assert out==frozenset(("VOL_WIPER_TO_AMP","RELAY_COM_AUDIO"))
            normally_open+=1
        else:
            assert not out
        lost_both_common += len(missing)==2
        states+=1
    assert (states,normally_closed,normally_open,lost_both_common)==(12,3,3,3)
    assert mute_graph("NC",set())==frozenset(("AF_GND","RELAY_COM_AUDIO"))
    assert mute_graph("NO",set())==frozenset(("VOL_WIPER_TO_AMP","RELAY_COM_AUDIO"))
    print("FRONT_G5V1_OEM_SIX_TERMINAL_MIGRATION_PROPOSAL",{
      "native_current_K1901_pins":actual,
      "proposed_oem_pin_to_net":OEM_TO_EXISTING_NET,
      "oem_pins_5_and_6_both_common":True,
      "synthetic_contact_common_open_cases":states,
      "NC_with_electrical_common_cases":normally_closed,
      "NO_with_electrical_common_cases":normally_open,
      "double_common_open_cannot_fail_mute":True,
      "actual_6pad_top_side_footprint_or_relay_migrated":False,
      "coil_driver_powergood_qualified":False,
      "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True},flush=True)
    print("PASS_NATIVE_FRONT_G5V1_SIX_TERMINAL_PIN_MAP_12_NONFAB",flush=True)

if __name__=="__main__":main()
