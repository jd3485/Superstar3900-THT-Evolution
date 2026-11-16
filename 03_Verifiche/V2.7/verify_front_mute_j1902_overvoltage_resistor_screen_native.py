#!/usr/bin/env python3
"""Analytical postmute connector overvoltage thermal screen, NOT qualification.

Hypothetical externally forced J1902/1 voltage relative to intact AF_GND.
Worst-case ideal NC contact: R1902 (1k) + R1901 (100k) are parallel
bleed paths; maximum R1902 power assumes K1901 NC grounded.
The audio signal source and cable fault voltage are NOT OEM qualified.
"""
from __future__ import annotations
from math import isclose,isfinite,sqrt
from pathlib import Path
import tempfile
from verify_interboard_audio_contract_native import exported_nets,require

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"04_KiCad/V2.7_DRAFT"
RELAY=BASE/"FRONT_MUTE_NC_RELAY/FRONT_NC_MUTE_CONTACT_THT_V2_7_DRAFT.kicad_sch"
PARENT=BASE/"FRONT_CONTROL_PARTIAL_V2_7_DRAFT.kicad_sch"
AUDIO=BASE/"AUDIO_RX_MONO_LM386_V2_7_DRAFT.kicad_sch"
R_SERIES=1000.0
R_BLEED=100000.0
SCREEN_TOL=.05
P_NOMINAL_HYPOTHETICAL=.25
P_DERATED_HYPOTHETICAL=.10
SOURCES_V=(6.,12.,15.,20.,24.,30.)

def worst_power(volts,resistance,shorted=False):
    """Voltage is FORCED at J1902/1; ideal low-ohm NC return, not coil source."""
    if not isfinite(volts) or not isfinite(resistance) or resistance<=0:
        raise ValueError("finite voltage, positive resistance required")
    if shorted: return 0.
    return volts*volts/(resistance*(1-SCREEN_TOL))

def allowable_voltage(power_w,resistance):
    if not isfinite(power_w) or power_w<=0 or not isfinite(resistance) or resistance<=0:
        raise ValueError("positive finite power and resistance required")
    return sqrt(power_w*resistance*(1-SCREEN_TOL))

def check_native():
    with tempfile.TemporaryDirectory(prefix="tht_front_mute_ov_") as td:
        d=Path(td)
        relay=exported_nets(RELAY,d/"relay.net")
        parent=exported_nets(PARENT,d/"parent.net")
        main=exported_nets(AUDIO,d/"audio.net")
    require(relay,"AMP_INPUT_MUTED",("J1902","1"),("R1902","2"),("R1901","1"))
    require(relay,"AF_GND",("J1902","2"),("R1901","2"),("K1901","2"))
    require(relay,"RELAY_COM_AUDIO",("K1901","1"),("R1902","1"))
    require(main,"AUDIO_IN",("J1202","1"),("C1201","1"))
    require(main,"GND",("J1202","2"),("U1201","4"))
    assert len(parent)==22
    assert any({("J1902","1"),("R1902","2"),("R1901","1")}.issubset(net) for net in parent.values())
    assert not any({("J1902","1"),("J1302","1")}.issubset(net) for net in parent.values())
    text=RELAY.read_text(encoding="utf-8")
    assert text.count('1k_SERIES_AUDIO_INPUT_CANDIDATE')==1
    assert text.count('100k_AMP_INPUT_BLEED_CANDIDATE')==1
    assert "UNQUALIFIED" in text and "NO FAB / NO TX" in text

def main():
    check_native()
    bound_nom=allowable_voltage(P_NOMINAL_HYPOTHETICAL,R_SERIES)
    bound_derated=allowable_voltage(P_DERATED_HYPOTHETICAL,R_SERIES)
    assert isclose(bound_nom,sqrt(237.5))
    assert isclose(bound_derated,sqrt(95))
    assert bound_nom<20 and bound_derated<12
    examples=[]
    for v in SOURCES_V:
        pseries=worst_power(v,R_SERIES)
        pbleed=worst_power(v,R_BLEED)
        assert isclose(pseries/pbleed,R_BLEED/R_SERIES)
        assert pseries>=0 and pbleed>=0
        examples.append((v,round(pseries,5),round(pbleed,6)))
    assert worst_power(20,R_SERIES)>0.4
    assert worst_power(20,R_BLEED)<0.005
    # If NC is open, R1902 carries no DC current from this forced
    # connector source (unless an independent COM ground fault occurs).
    nc_open_r1902_power_dc=0.
    assert nc_open_r1902_power_dc==0.
    for invalid in (float("nan"),float("inf")):
        try:worst_power(invalid,R_SERIES)
        except ValueError:pass
        else:raise AssertionError("Nonfinite fault voltage accepted")
    print("FRONT_MUTE_J1902_FORCED_OVERVOLTAGE_SCREEN",{
        "example_V_R1902_W_R1901_W":examples,
        "R1902_1k_hypothetical_0p25W_limit_V":bound_nom,
        "R1902_1k_hypothetical_0p10W_limit_V":bound_derated,
        "real_fault_voltage_bound_known":False,
        "actual_R1902_MPN_power_derating_verified":False,
        "contact_or_cable_qualified":False,
        "hardware_safe_or_failsafe_demonstrated":False,
        "NO_FAB_NO_TX":True},flush=True)
    print("PASS_NATIVE_KICAD9_FRONT_MUTE_J1902_OVERVOLTAGE_RESISTOR_SCREEN_NONFAB",flush=True)

if __name__=="__main__":
    main()
