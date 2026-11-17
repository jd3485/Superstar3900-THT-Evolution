#!/usr/bin/env python3
"""FRONT NC mute relay: OEM six-through-hole vs five-terminal abstract gate.

No manufacturer pin map is inferred. This rejects claiming the current K1901
five-electrical-pin symbol, with blank footprint, is ready for G5V-1 DC5.
"""
import math
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets
from verify_front_partial_hierarchy_native import SCH as FRONT

RELAY=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_MUTE_NC_RELAY/FRONT_NC_MUTE_CONTACT_THT_V2_7_DRAFT.kicad_sch"
DRIVER=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_MUTE_COIL_DRIVER/FRONT_NC_MUTE_DUAL_ENABLE_COIL_DRIVER_V2_7_DRAFT.kicad_sch"
# Aratas (formerly Omron Components), G5V-1 Rev K048-E1, pp. 1 and 4.
# The published bottom-view drilling plan has SIX 1.0mm diameter holes.
OEM_THT_HOLES=6
OEM_NOMINAL_V=5.
OEM_NOMINAL_COIL_OHM=167.
OEM_RESISTANCE_TOL=.10
OEM_RATED_COIL_CURRENT_MA=30.
OEM_NOMINAL_POWER_MW=150.
OEM_STANDARD_MUST_OPERATE_MAX_FRACTION=.80

def main():
    relay=RELAY.read_text(encoding="utf8")
    driver=DRIVER.read_text(encoding="utf8")
    assert relay.count('(property "Reference" "K1901"')==1
    assert relay.count('(property "Footprint" ""') >= 1
    assert 'UNQUALIFIED_RELAY_SPDT_THT_NC_MUTE' in relay
    assert "NO FAB / NO TX" in relay
    assert "BC33725BU_ONSEMI_CANDIDATE_NOT_DRIVER_RELEASE" in driver
    with tempfile.TemporaryDirectory(prefix="front_relay_oem_gate_") as td:
        net=exported_nets(FRONT,Path(td)/"front.net")
    pins={}
    for name,ends in net.items():
        for ref,pin in ends:
            if ref=="K1901":
                assert pin not in pins,(pin,name,pins[pin])
                pins[pin]=name.rsplit("/",1)[-1]
    expected={
        "1":"RELAY_COM_AUDIO",
        "2":"AF_GND",
        "3":"VOL_WIPER_TO_AMP",
        "4":"COIL_PLUS_LAB",
        "5":"COIL_MINUS_LAB"
    }
    assert pins==expected,(pins,expected)
    assert OEM_THT_HOLES==6 and len(pins)==5
    assert "G5V-1" not in relay # no premature OEM replacement
    min_r=OEM_NOMINAL_COIL_OHM*(1-OEM_RESISTANCE_TOL)
    max_r=OEM_NOMINAL_COIL_OHM*(1+OEM_RESISTANCE_TOL)
    i_min=OEM_NOMINAL_V/max_r
    i_max=OEM_NOMINAL_V/min_r
    p_min=OEM_NOMINAL_V**2/max_r
    p_max=OEM_NOMINAL_V**2/min_r
    assert i_min < OEM_RATED_COIL_CURRENT_MA/1000. < i_max
    assert p_min < OEM_NOMINAL_POWER_MW/1000. < p_max
    assert math.isclose(OEM_STANDARD_MUST_OPERATE_MAX_FRACTION*OEM_NOMINAL_V,4.)
    # A 6-hole active-production family is NOT a pin-compatible OEM K1901
    # replacement until a separately reviewed 6-pad footprint/pin-map is made.
    print("FRONT_G5V1_OEM_CANDIDATE_NONFAB",{
      "native_front_relay_K1901_pins":pins,
      "abstract_symbol_electrical_terminals":len(pins),
      "oem_bottom_view_pcb_holes":OEM_THT_HOLES,
      "direct_footprint_substitution_permitted":False,
      "G5V1_family_status_production_web_20261117":True,
      "oem_coil_5V_current_mA_10pct_range":[round(i_min*1000,3),round(i_max*1000,3)],
      "oem_coil_5V_power_mW_10pct_range":[round(p_min*1000,3),round(p_max*1000,3)],
      "oem_standard_must_operate_at_or_below_4V_at_23C":True,
      "coil_driver_PVT_and_contact_mute_qualified":False,
      "six_terminal_OEM_mapping_not_assumed":True,
      "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True},flush=True)
    print("PASS_NATIVE_FRONT_MUTE_G5V1_6PAD_OEM_MISMATCH_GATE_NONFAB",flush=True)

if __name__=="__main__":main()
