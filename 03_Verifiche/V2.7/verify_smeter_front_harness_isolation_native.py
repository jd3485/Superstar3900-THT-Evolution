#!/usr/bin/env python3
"""Fail-closed FRONT S-meter/audio cable-domain isolation, native KiCad9.

This is a FRONT-side provisional cable boundary, NOT an implemented MAIN
driver, PCB interconnect, verified polarized connector or safety approval.
"""
from pathlib import Path
import tempfile

from verify_interboard_audio_contract_native import exported_nets, require

ROOT=Path(__file__).resolve().parents[2]
FRONT_SMETER=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_SMETER/FRONT_SMETER_THT_V2_7_DRAFT.kicad_sch"
FRONT_AUDIO=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_VOLUME/FRONT_VOLUME_THT_V2_7_DRAFT.kicad_sch"
MAIN_AUDIO=ROOT/"04_KiCad/V2.7_DRAFT/AUDIO_RX_MONO_LM386_V2_7_DRAFT.kicad_sch"

METER_EXPECTED={
    "METER_DRIVE_CANDIDATE": {("J1801","1"),("RV1801","1")},
    "METER_TRIM_OUTPUT": {("RV1801","2"),("R1801","1")},
    "METER_POS_LIMITED": {("R1801","2"),("J1802","1")},
    "METER_RETURN": {("J1801","2"),("RV1801","3"),("J1802","2")},
}
AUDIO_EXPECTED={
    "DEMOD_AUDIO": {("J1301","1"),("RV1301","1")},
    "VOL_WIPER_TO_AMP": {("RV1301","2"),("J1302","1")},
    "AF_GND": {("J1301","2"),("RV1301","3"),("J1302","2")},
}
# No fabricated producer for the S-meter exists on MAIN: the only
# physically represented cable endpoints are the two FRONT J1801 pins.
# No assignment of these pins to a MAIN part or ground is permitted here.
METER_CABLE_FRONT={
    1: ("J1801","1","METER_DRIVE_CANDIDATE"),
    2: ("J1801","2","METER_RETURN"),
}

def assert_exact(nets,expected,domain):
    assert set(nets)==set(expected), (domain,"unexpected/missing nets",sorted(nets))
    for name,pins in expected.items():
        require(nets,name,*sorted(pins))
        assert nets[name]==pins,(domain,name,sorted(nets[name]),sorted(pins))
    members=[p for pins in nets.values() for p in pins]
    assert len(members)==len(set(members)),(domain,"shorted net pins")

def main():
    with tempfile.TemporaryDirectory(prefix="tht_meter_front_boundary_") as d:
        out=Path(d)
        smeter=exported_nets(FRONT_SMETER,out/"smeter.net")
        audio=exported_nets(FRONT_AUDIO,out/"front_audio.net")
        main_audio=exported_nets(MAIN_AUDIO,out/"main_audio.net")
    assert_exact(smeter,METER_EXPECTED,"FRONT_SMETER")
    assert_exact(audio,AUDIO_EXPECTED,"FRONT_VOLUME")
    assert len(METER_CABLE_FRONT)==2
    assert {v[0:2] for v in METER_CABLE_FRONT.values()}=={
        ("J1801","1"),("J1801","2")}
    for pin,(ref,pad,name) in METER_CABLE_FRONT.items():
        assert pin in (1,2) and (ref,pad) in smeter[name]
    # Front-end meter return must not be silently renamed AF_GND or GND.
    assert not (set(smeter)&set(audio))
    assert not (set(smeter)&set(main_audio))
    assert ("J1301","2") in audio["AF_GND"]
    assert ("J1302","2") in audio["AF_GND"]
    # The audio MAIN pilot has a supply; it must not be imported into the
    # analog meter contract or mistaken for an S-meter driver source.
    require(main_audio,"AUDIO_6V_LAB",("J1201","1"),("U1201","6"))
    assert all(not any(flag in net.upper() for flag in
                       ("TX","PTT","SUPPLY","VCC","POWER","AUDIO_6V"))
               for net in smeter)
    assert not any(ref.startswith("J12") or ref.startswith("U12")
                   for pins in smeter.values() for ref,_ in pins)
    print("FRONT_SMETER_CABLE_BOUNDARY_UNASSIGNED_MAIN",{
        "front_side_pin_1": "METER_DRIVE_CANDIDATE",
        "front_side_pin_2": "METER_RETURN",
        "main_side_source": None,
        "main_side_return": None,
        "meter_return_bonded_to_AF_GND": False,
        "actual_mating_cable_qualified": False},flush=True)
    print("PASS_NATIVE_KICAD9_FRONT_SMETER_AUDIO_DOMAIN_ISOLATION_NO_MAIN_DRIVER_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
