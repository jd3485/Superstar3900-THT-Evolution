#!/usr/bin/env python3
"""Native KiCad9 netlist test of isolated six-terminal G5V-1 candidate.
NOT a FRONT product migration, OEM approval, PCB, DRC or relay safety proof.
"""
from pathlib import Path
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets
from verify_front_partial_hierarchy_native import SCH as FRONT
from verify_front_g5v1_six_terminal_oem_pin_map_native import OEM_TO_EXISTING_NET
from verify_front_g5v1_oem_sixpad_footprint_candidate_native import EXPECTED as PADS

CANDIDATE=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_MUTE_NC_RELAY/FRONT_G5V1_SIXPIN_ISOLATED_NATIVE_CANDIDATE.kicad_sch"
EXPECTED={str(k):v for k,v in OEM_TO_EXISTING_NET.items()}
def relay_pins(sch,ref):
    with tempfile.TemporaryDirectory(prefix="front_g5v1_native_") as td:
        nets=exported_nets(sch,Path(td)/"front.net")
    pins={}
    for net,members in nets.items():
        for r,p in members:
            if r==ref:
                assert p not in pins, ("duplicate pin",p)
                pins[p]=net.rsplit("/",1)[-1]
    return pins

def main():
    text=CANDIDATE.read_text(encoding="utf8")
    assert "TH_MUTE:G5V1_DC5_SIXPIN_CANDIDATE" in text
    assert 'TH_MUTE_OEM_CANDIDATE:G5V-1_DC5_OEM_6PIN_CANDIDATE' in text
    assert "NO FAB" in text
    assert set(EXPECTED)==set(PADS)=={"1","2","5","6","9","10"}
    assert EXPECTED["5"]==EXPECTED["6"]=="RELAY_COM_AUDIO"
    actual=relay_pins(CANDIDATE,"K1901")
    assert actual==EXPECTED,(actual,EXPECTED)
    old=relay_pins(FRONT,"K1901")
    assert old=={"1":"RELAY_COM_AUDIO","2":"AF_GND","3":"VOL_WIPER_TO_AMP",
                 "4":"COIL_PLUS_LAB","5":"COIL_MINUS_LAB"},old
    assert len(old)==5 and len(actual)==6
    print("PASS_FRONT_G5V1_ISOLATED_SIX_PIN_NATIVE_NETLIST_NO_PRODUCT_MIGRATION",flush=True)
if __name__=="__main__":
    main()
