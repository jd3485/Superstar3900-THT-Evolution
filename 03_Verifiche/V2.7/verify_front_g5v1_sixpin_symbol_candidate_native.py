#!/usr/bin/env python3
"""OEM G5V-1 DC5 six-pin KiCad THT candidate vs untouched native K1901.

A separate library symbol is NOT inserted into the actual FRONT hierarchy.
Rejects shorting NC and NO or failing to duplicate COM pad 5+6.
"""
from pathlib import Path
import re
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets
from verify_front_partial_hierarchy_native import SCH as FRONT
from verify_front_g5v1_six_terminal_oem_pin_map_native import OEM_TO_EXISTING_NET
from verify_front_g5v1_oem_sixpad_footprint_candidate_native import FOOT,EXPECTED as PAD_LOCATIONS

SYM=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_MUTE_NC_RELAY/TH_MUTE_G5V1_SIX_TERMINAL_CANDIDATE.kicad_sym"
RELAY=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_MUTE_NC_RELAY/FRONT_NC_MUTE_CONTACT_THT_V2_7_DRAFT.kicad_sch"
LABELS={
 "1":"NC_AF_GND","10":"NO_VOL_WIPER",
 "2":"COIL_PLUS","9":"COIL_MINUS",
 "5":"COM_A","6":"COM_B"
}
def main():
    text=SYM.read_text(encoding="utf8")
    assert text.startswith("(kicad_symbol_lib (version 20231120)")
    assert "G5V1_DC5_SIX_TERMINAL_CANDIDATE" in text
    assert "NO FAB" in text
    assert "TH_MUTE_OEM_CANDIDATE:G5V-1_DC5_OEM_6PIN_CANDIDATE" in text
    assert FOOT.is_file()
    assert set(PAD_LOCATIONS)==set(LABELS)==set(OEM_TO_EXISTING_NET)
    matches=re.findall(
      r'\(name "([^"]+)" \(effects \(font \(size 1 1\)\)\)\) '
      r'\(number "(\d+)" \(effects \(font \(size 1 1\)\)\)\)',text)
    assert len(matches)==6,(matches,len(matches))
    pins={n:name for name,n in matches}
    assert pins==LABELS,(pins,LABELS)
    assert OEM_TO_EXISTING_NET["5"]==OEM_TO_EXISTING_NET["6"]=="RELAY_COM_AUDIO"
    assert OEM_TO_EXISTING_NET["1"]=="AF_GND"
    assert OEM_TO_EXISTING_NET["10"]=="VOL_WIPER_TO_AMP"
    assert {OEM_TO_EXISTING_NET["2"],OEM_TO_EXISTING_NET["9"]}=={"COIL_PLUS_LAB","COIL_MINUS_LAB"}
    assert text.count("(pin passive line")==6
    assert len(set(re.findall(r'\(at (-?\d+\.\d+ -?\d+\.\d+ \d+)\) \(length 5\.08\)',text)))==6
    old=RELAY.read_text(encoding="utf8")
    assert "G5V1_DC5_SIX_TERMINAL_CANDIDATE" not in old
    assert '(property "Footprint" ""' in old
    with tempfile.TemporaryDirectory(prefix="g5v1_6pin_symbol_") as td:
        nets=exported_nets(FRONT,Path(td)/"front.net")
    original={}
    for net,members in nets.items():
        for ref,pin in members:
            if ref=="K1901":
                assert pin not in original
                original[pin]=net.rsplit("/",1)[-1]
    assert original=={
      "1":"RELAY_COM_AUDIO","2":"AF_GND","3":"VOL_WIPER_TO_AMP",
      "4":"COIL_PLUS_LAB","5":"COIL_MINUS_LAB"}
    assert set(original)!=set(pins)
    print("FRONT_G5V1_6PIN_SYMBOL_CANDIDATE",{
      "candidate_oem_pad_to_net":OEM_TO_EXISTING_NET,
      "symbol_pin_names":pins,
      "physical_pads_present":set(PAD_LOCATIONS)==set(pins),
      "native_existing_K1901_still_5pin":True,
      "new_symbol_assigned_to_K1901":False,
      "real_FRONT_PCB_or_DRC":False,
      "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True},flush=True)
    print("PASS_G5V1_SIXPIN_SYMBOL_CANDIDATE_NATIVE_K1901_UNMODIFIED",flush=True)
if __name__=="__main__":main()
