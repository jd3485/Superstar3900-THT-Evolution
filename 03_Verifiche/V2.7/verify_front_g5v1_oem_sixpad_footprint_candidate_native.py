#!/usr/bin/env python3
"""OEM G5V-1 six-pad THT footprint candidate vs native FRONT five-pin K1901.

This checks six pad geometries, 1mm drilling, 2.54mm grid, OEM bottom
view to board top-view and untouched abstract K1901; NOT an approved release.
"""
import re
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets
from verify_front_partial_hierarchy_native import SCH as FRONT
from verify_front_g5v1_six_terminal_oem_pin_map_native import OEM_TO_EXISTING_NET

FOOT=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_MUTE_NC_RELAY/TH_MUTE_OEM_CANDIDATE.pretty/G5V-1_DC5_OEM_6PIN_CANDIDATE.kicad_mod"
RELAY=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_MUTE_NC_RELAY/FRONT_NC_MUTE_CONTACT_THT_V2_7_DRAFT.kicad_sch"
EXPECTED={"1":(0.,0.),"2":(0.,2.54),"5":(0.,10.16),
          "10":(5.08,0.),"9":(5.08,2.54),"6":(5.08,10.16)}
def main():
    raw=FOOT.read_text(encoding="utf8")
    assert raw.startswith('(footprint "G5V-1_DC5_OEM_6PIN_CANDIDATE"')
    assert '(attr through_hole)' in raw
    assert "NO FAB - SIX PAD CANDIDATE" in raw
    assert "(zone " not in raw and "(segment " not in raw
    assert "(model " not in raw
    assert "(pad " not in RELAY.read_text()
    assert '(property "Footprint" ""' in RELAY.read_text()
    pads=re.findall(r'\(pad "(\d+)" thru_hole (rect|circle) \(at ([\d.]+) ([\d.]+)\) '
      r'\(size ([\d.]+) ([\d.]+)\) \(drill ([\d.]+)\) '
      r'\(layers "\*\.Cu" "\*\.Mask"\)\)',raw)
    assert len(pads)==6,(len(pads),pads)
    found={}
    for n,shape,x,y,w,h,drill in pads:
        assert n not in found,n
        assert shape==("rect" if n=="1" else "circle")
        assert (float(w),float(h),float(drill))==(2.,2.,1.)
        found[n]=(float(x),float(y))
    assert found==EXPECTED,(found,EXPECTED)
    assert set(OEM_TO_EXISTING_NET)==set(found)
    assert OEM_TO_EXISTING_NET["5"]==OEM_TO_EXISTING_NET["6"]=="RELAY_COM_AUDIO"
    assert (found["5"][0],found["6"][0])==(0.,5.08)
    assert found["1"][1]==found["10"][1]==0.
    # True native hierarchy still carries original abstract K1901 pin 1-5.
    with tempfile.TemporaryDirectory(prefix="front_g5v1_footprint_gate_") as td:
        nets=exported_nets(FRONT,Path(td)/"front.net")
    actual={}
    for name,ends in nets.items():
        for ref,pin in ends:
            if ref=="K1901":
                assert pin not in actual
                actual[pin]=name.rsplit("/",1)[-1]
    assert actual=={
        "1":"RELAY_COM_AUDIO","2":"AF_GND","3":"VOL_WIPER_TO_AMP",
        "4":"COIL_PLUS_LAB","5":"COIL_MINUS_LAB"}
    assert set(actual)!=set(found),"Six-pad design cannot be substituted on five-pin K1901"
    print("THT_FRONT_G5V1_OEM_CANDIDATE_FOOTPRINT",{
        "six_THT_pad_coordinates_mm":found,
        "OEM_contact_and_coil_assignment":OEM_TO_EXISTING_NET,
        "native_K1901_five_abstract_pins_unmodified":True,
        "manufacturer_hole_diameter_mm":1,
        "ready_to_assign_footprint_to_K1901":False,
        "copper_board_or_DRCO_qualified":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True},flush=True)
    print("PASS_THT_FRONT_G5V1_6PAD_CANDIDATE_NOT_ON_BOARD_NONFAB",flush=True)

if __name__=="__main__":main()
