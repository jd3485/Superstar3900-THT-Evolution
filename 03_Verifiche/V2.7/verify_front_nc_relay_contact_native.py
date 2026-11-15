#!/usr/bin/env python3
"""Native KiCad9 test for standalone, unqualified THT NC relay audio-mute contact.

De-energized SPDT contact modeled by symbol annotation: COM=amp, NC=AF_GND,
NO=wiper. KiCad ERC/netlist CANNOT prove the mechanical position of a relay.
No qualified coil voltage, contact minimum-load or driver. Not product safety.
"""
from __future__ import annotations
from pathlib import Path
import subprocess
import tempfile
from verify_interboard_audio_contract_native import exported_nets,require

ROOT=Path(__file__).resolve().parents[2]
SCH=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_MUTE_NC_RELAY/FRONT_NC_MUTE_CONTACT_THT_V2_7_DRAFT.kicad_sch"
FRONT=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_VOLUME/FRONT_VOLUME_THT_V2_7_DRAFT.kicad_sch"
AUDIO=ROOT/"04_KiCad/V2.7_DRAFT/AUDIO_RX_MONO_LM386_V2_7_DRAFT.kicad_sch"
BOARD=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_PLACEMENT/FRONT_CONTROL_13REFS_PLACEMENT_NONFAB.kicad_pcb"

def main():
    raw=SCH.read_text(encoding="utf-8")
    # Project symbol library is physically present and resolved. The first
    # CI attempt exposed four KiCad9 missing-library ERC violations; this
    # local registration fixes the *cause*, never waives warnings.
    local=SCH.parent
    project=SCH.with_suffix(".kicad_pro")
    assert project.exists(), "KiCad9 project required to load local sym-lib-table"
    assert '"schematic": {}' in project.read_text(encoding="utf-8")
    table=(local/"sym-lib-table").read_text(encoding="utf-8")
    library=(local/"TH_MUTE.kicad_sym").read_text(encoding="utf-8")
    assert '(name "TH_MUTE")' in table
    assert '${KIPRJMOD}/TH_MUTE.kicad_sym' in table
    assert '(symbol "RELAY_SPDT_NC_MUTE_THT"' in library
    assert '(symbol "LAB_2PIN"' in library
    assert "NC=GND (NO POWER)" in library
    assert raw.count('(symbol (lib_id "TH_MUTE:RELAY_SPDT_NC_MUTE_THT")')==1
    assert raw.count('(symbol (lib_id "TH_MUTE:LAB_2PIN")')==3
    assert raw.count('(pin passive line ')==7
    assert all(f'(property "Reference" "{ref}"' in raw
               for ref in ("K1901","J1901","J1902","J1903"))
    assert "NC=GND (NO POWER)" in raw and "UNQUALIFIED" in raw
    assert '(property "Footprint" ""' in raw
    assert '(attr through_hole)' not in raw # abstract symbol, no physical package assigned
    assert "NO FAB / NO TX" in raw
    # No change to actual FRONT board, no coils or fake mute connectors mounted.
    board=BOARD.read_text(encoding="utf-8")
    assert "K1901" not in board and board.count('(segment ')==35
    assert board.count('(footprint "TH_FRONT:Potentiometer_THT_3Pin_PROVISIONAL"')==2
    with tempfile.TemporaryDirectory(prefix="tht_front_nc_mute_") as td:
        d=Path(td)
        erc=d/"erc.rpt"
        run=subprocess.run(["kicad-cli","sch","erc","--exit-code-violations",
                            "-o",str(erc),str(SCH)],
                           capture_output=True,text=True,cwd=ROOT,timeout=120)
        print("FRONT_RELAY_CANDIDATE_KICAD9_ERC",run.stdout,run.stderr,flush=True)
        if erc.exists():
            print(erc.read_text(encoding="utf-8"),flush=True)
        run.check_returncode()
        relay=exported_nets(SCH,d/"mute.net")
        front=exported_nets(FRONT,d/"front.net")
        audio=exported_nets(AUDIO,d/"audio.net")
    expected={
        "AMP_INPUT_MUTED":{("K1901","1"),("J1902","1")},
        "AF_GND":{("K1901","2"),("J1901","2"),("J1902","2")},
        "VOL_WIPER_TO_AMP":{("K1901","3"),("J1901","1")},
        "COIL_PLUS_LAB":{("K1901","4"),("J1903","1")},
        "COIL_MINUS_LAB":{("K1901","5"),("J1903","2")},
    }
    assert len(relay)==5,(relay,expected)
    for name,pins in expected.items():
        require(relay,name,*pins)
        assert relay[name]==pins,(name,relay[name],pins)
    require(front,"VOL_WIPER_TO_AMP",("RV1301","2"),("J1302","1"))
    require(front,"AF_GND",("RV1301","3"),("J1302","2"))
    require(audio,"AUDIO_IN",("J1202","1"),("C1201","1"))
    require(audio,"GND",("J1202","2"),("U1201","4"))
    assert not (relay["COIL_PLUS_LAB"] & relay["AF_GND"])
    assert not (relay["COIL_MINUS_LAB"] & relay["AF_GND"])
    assert not (relay["AMP_INPUT_MUTED"] & relay["VOL_WIPER_TO_AMP"])
    print("FRONT_NC_MUTE_NATIVE_NETS",{n:sorted(p) for n,p in relay.items()},flush=True)
    print("FRONT_NC_MUTE_LIMITS",{
        "KiCad9_native_ERC_and_pin_net_verified":True,
        "relay_deenergized_NC_contact_GND_mechanically_verified":False,
        "coil_driver_or_power_good_present":False,
        "coil_supply_qualified":False,
        "minimum_signal_dry_contact_OEM_qualified":False,
        "external_AF_GND_open_fault_prevented":False,
        "board_modified":False,
        "product_fail_safe_certified":False,
        "NO_FAB_NO_TX":True},flush=True)
    print("PASS_KICAD9_FRONT_NC_RELAY_THT_5PIN_3LABPORTS_5_ISOLATED_NETS_ERC0_NONFAB",flush=True)

if __name__=="__main__":main()
