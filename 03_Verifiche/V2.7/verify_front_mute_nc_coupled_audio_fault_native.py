#!/usr/bin/env python3
"""Hypothetical cable-injected audio fault envelope at FRONT K1901 mute output.

Native KiCad9 pin-net anchors verify exact contact/bleed/input topology.
Not a cable EMI limit, relay contact qualification or a fail-safe proof.
AF_GND-open is explicitly unbounded/not calculable in a shared-return model.
"""
from __future__ import annotations
import cmath
import math
from itertools import product
from pathlib import Path
import tempfile
from verify_interboard_audio_contract_native import exported_nets, require

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"04_KiCad/V2.7_DRAFT"
RELAY=BASE/"FRONT_MUTE_NC_RELAY/FRONT_NC_MUTE_CONTACT_THT_V2_7_DRAFT.kicad_sch"
MAIN=BASE/"AUDIO_RX_MONO_LM386_V2_7_DRAFT.kicad_sch"
PARENT=BASE/"FRONT_CONTROL_PARTIAL_V2_7_DRAFT.kicad_sch"
R_SERIES=1000.0
R_BLEED=100000.0
R_INPUT=10000.0
C_INPUT=100e-9
R_IN=50000.0
FREQUENCIES=(100.0,300.0,1000.0,3000.0,10000.0)
COUPLING_CAPACITANCE_F=(10e-12,100e-12,1e-9,10e-9)
NC_CONTACT_RESISTANCE_OHM=(0.1,1.0,100.0)

def impedance_reduction(f,cc,contact_ohm,nc_connected,af_gnd_connected=True):
    """H(f)=V(LM386 pin3)/V(injected cable source); illustrative 1V source."""
    if not af_gnd_connected:
        raise ValueError("Shared AF_GND open: no defined reference in this model")
    if not(f>0 and cc>0 and contact_ohm>=0):
        raise ValueError("invalid finite circuit parameters")
    if not all(math.isfinite(v) for v in (f,cc,contact_ohm)):
        raise ValueError("nonfinite circuit parameter")
    w=2*math.pi*f
    zcouple=1/(1j*w*cc)
    za=R_INPUT+1/(1j*w*C_INPUT)
    zinput=za+R_IN
    yshunt=1/R_BLEED + (1/(R_SERIES+contact_ohm) if nc_connected else 0.0)
    znode=1/(yshunt+1/zinput)
    return (znode/(zcouple+znode))*(R_IN/zinput)

def nodal_kcl(f,cc,contact_ohm,nc_connected,af_gnd_connected=True):
    """Independent two-node complex KCL at postmute M and LM386 input I."""
    if not af_gnd_connected:
        raise ValueError("No AF_GND: undefined reference")
    if not(f>0 and cc>0 and contact_ohm>=0):
        raise ValueError("invalid circuit parameters")
    if not all(math.isfinite(v) for v in (f,cc,contact_ohm)):
        raise ValueError("nonfinite circuit parameter")
    w=2*math.pi*f
    yc=1j*w*cc
    ys=1/R_BLEED + (1/(R_SERIES+contact_ohm) if nc_connected else 0.0)
    ya=1/(R_INPUT+1/(1j*w*C_INPUT))
    yr=1/R_IN
    a=yc+ys+ya
    b=-ya
    c=ya+yr
    d=a*c-b*b
    assert abs(d)>0
    vm=yc*c/d
    vi=-b*yc/d
    assert abs((vm-1)*yc+vm*ys+(vm-vi)*ya)<1e-9
    assert abs((vi-vm)*ya+vi*yr)<1e-9
    return vi

def native_pins():
    with tempfile.TemporaryDirectory(prefix="tht_mute_coupling_") as td:
        d=Path(td)
        relay=exported_nets(RELAY,d/"relay.net")
        audio=exported_nets(MAIN,d/"audio.net")
        parent=exported_nets(PARENT,d/"parent.net")
    require(relay,"RELAY_COM_AUDIO",("K1901","1"),("R1902","1"))
    require(relay,"AMP_INPUT_MUTED",("R1902","2"),("R1901","1"),("J1902","1"))
    require(relay,"AF_GND",("K1901","2"),("R1901","2"),("J1902","2"))
    require(audio,"AUDIO_IN",("J1202","1"),("C1201","1"))
    require(audio,"PRE_IN",("C1201","2"),("R1201","1"))
    require(audio,"AMP_IN",("R1201","2"),("U1201","3"))
    assert len(parent)==22
    assert any({("J1902","1"),("R1901","1"),("R1902","2")}.issubset(p) for p in parent.values())
    assert any({("J1902","2"),("R1901","2"),("K1901","2")}.issubset(p) for p in parent.values())
    for path,needle in ((RELAY,"1k_SERIES_AUDIO_INPUT_CANDIDATE"),
                        (RELAY,"100k_AMP_INPUT_BLEED_CANDIDATE"),
                        (MAIN,"100nF_50V_INPUT"),(MAIN,"10k_0p25W_INPUT")):
        assert needle in path.read_text(encoding="utf-8"),(path,needle)

def main():
    native_pins()
    checked=0
    minimum_degradation=float("inf")
    maximum_degradation=0.0
    example={}
    for f,cc,rc in product(FREQUENCIES,COUPLING_CAPACITANCE_F,NC_CONTACT_RESISTANCE_OHM):
        intact=impedance_reduction(f,cc,rc,True)
        nc_open=impedance_reduction(f,cc,rc,False)
        assert abs(intact-nodal_kcl(f,cc,rc,True))<3e-12
        assert abs(nc_open-nodal_kcl(f,cc,rc,False))<3e-12
        assert all(math.isfinite(v) for z in (intact,nc_open) for v in (z.real,z.imag))
        assert abs(nc_open)>abs(intact),(f,cc,rc,intact,nc_open)
        ratio=abs(nc_open)/abs(intact)
        minimum_degradation=min(minimum_degradation,ratio)
        maximum_degradation=max(maximum_degradation,ratio)
        if f==1000 and cc==1e-9 and rc==1.0:
            example={"frequency_Hz":f,"coupling_F":cc,"NC_contact_ohm":rc,
                     "intact_input_gain":abs(intact),"NC_open_input_gain":abs(nc_open),
                     "NC_open_to_intact_gain_ratio":ratio}
        checked+=1
    assert checked==60 and example
    # Pure DC shunt limits ignore R_INPUT/C_INPUT and coupling injection.
    grounded_nc_shunt=1/(1/R_BLEED+1/(R_SERIES+1.0))
    assert math.isclose(grounded_nc_shunt,991.0792962445917,rel_tol=1e-12)
    assert math.isclose(R_BLEED/grounded_nc_shunt,100.9000999000999,rel_tol=1e-12)
    for fn in (impedance_reduction,nodal_kcl):
        try:fn(1000,1e-9,1.0,False,False)
        except ValueError:pass
        else:raise AssertionError("AF_GND-open must fail closed")
    print("FRONT_MUTE_NC_COUPLED_AUDIO_FAULT_ENVELOPE",{
        "cases_two_solvers_two_contact_states":checked*2,
        "coupling_capacitances_F":COUPLING_CAPACITANCE_F,
        "NC_contact_resistance_ohm_scenarios":NC_CONTACT_RESISTANCE_OHM,
        "grounded_nc_shunt_ohm":grounded_nc_shunt,
        "NC_open_to_intact_DC_shunt_impedance_ratio":100.9000999000999,
        "minimum_AC_gain_ratio_NC_open_vs_intact":minimum_degradation,
        "maximum_AC_gain_ratio_NC_open_vs_intact":maximum_degradation,
        "sample":example,
        "shared_AF_GND_open_safely_bounded":False,
        "injection_coupling_OEM_cable_qualified":False,
        "relay_OEM_qualified":False,"NO_FAB_NO_TX":True},flush=True)
    print("PASS_NATIVE_KICAD9_FRONT_MUTE_120_AC_INJECTION_FAULT_CASES_AF_GND_OPEN_FAIL_CLOSED_NONFAB",flush=True)

if __name__=="__main__":
    main()
