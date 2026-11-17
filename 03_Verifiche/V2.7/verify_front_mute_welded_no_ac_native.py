#!/usr/bin/env python3
"""Native FRONT mute: hypothetical welded NO concurrent NC and AC cable injection.

Independent Norton reduction versus complex 2-node nodal solve. Unknown return
opens fail closed; no OEM contact welding frequency or physical voltage promise.
"""
from __future__ import annotations
import cmath
import itertools
import math
import tempfile
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets,require

BASE=ROOT/"04_KiCad/V2.7_DRAFT"
FRONT=BASE/"FRONT_MUTE_NC_RELAY/FRONT_NC_MUTE_CONTACT_THT_V2_7_DRAFT.kicad_sch"
MAIN=BASE/"AUDIO_RX_MONO_LM386_V2_7_DRAFT.kicad_sch"
PARENT=BASE/"FRONT_CONTROL_PARTIAL_V2_7_DRAFT.kicad_sch"

R_SERIES=1000.
R_BLEED=100000.
R_INPUT=10000.
C_INPUT=100e-9
RIN=50000.
FREQ=(300.,1000.,3000.)
CC=(10e-12,100e-12,1e-9,10e-9)
CONTACT=(0.1,10.,math.inf)
RSRC=(10000.,50000.) # hypothetical source resistance on NO
def conductance(r):
    return 0. if math.isinf(r) else 1/r

def parameters(freq,cc,nc,no,rsource):
    assert freq>0 and cc>0 and nc>=0 and no>=0 and rsource>0
    w=2*math.pi*freq
    ys=1/R_SERIES
    ybleed=1/R_BLEED
    yamp=1/(R_INPUT+1/(1j*w*C_INPUT)+RIN)
    ycouple=1j*w*cc
    ync=conductance(nc)
    yno=0. if math.isinf(no) else 1/(rsource+no)
    return ys,ybleed,yamp,ycouple,ync,yno

def collapsed(freq,cc,nc,no,rsource):
    """COM Norton equivalent collapsed into post-mute M node."""
    ys,yb,ya,yc,yn,yo=parameters(freq,cc,nc,no,rsource)
    denom=ys+yn+yo
    gpath=ys*(yn+yo)/denom
    injected_from_no=ys*yo/denom
    vm=(yc+injected_from_no)/(yc+yb+ya+gpath)
    return vm*(RIN*ya)

def nodal(freq,cc,nc,no,rsource):
    """Independently solve two-node complex KCL at COM and OUT."""
    ys,yb,ya,yc,yn,yo=parameters(freq,cc,nc,no,rsource)
    a=ys+yn+yo
    d=ys+yb+ya+yc
    det=a*d-ys*ys
    assert abs(det)>0.
    vc=(d*yo+ys*yc)/det
    vm=(ys*yo+a*yc)/det
    assert abs(a*vc-ys*vm-yo)<1e-10
    assert abs(-ys*vc+d*vm-yc)<1e-10
    return vm*RIN*ya

def native():
    with tempfile.TemporaryDirectory(prefix="front_mute_welded_no_") as td:
        d=Path(td)
        relay=exported_nets(FRONT,d/"front_relay.net")
        main=exported_nets(MAIN,d/"main_audio.net")
        parent=exported_nets(PARENT,d/"front_parent.net")
    require(relay,"RELAY_COM_AUDIO",("K1901","1"),("R1902","1"))
    require(relay,"VOL_WIPER_TO_AMP",("K1901","3"),("J1901","1"))
    require(relay,"AF_GND",("K1901","2"),("R1901","2"),("J1902","2"))
    require(relay,"AMP_INPUT_MUTED",("R1902","2"),("R1901","1"),("J1902","1"))
    require(main,"AUDIO_IN",("J1202","1"),("C1201","1"))
    require(main,"PRE_IN",("C1201","2"),("R1201","1"))
    require(main,"AMP_IN",("R1201","2"),("U1201","3"))
    assert len(parent)==22
    assert any({("J1902","1"),("R1902","2"),("R1901","1")}.issubset(p) for p in parent.values())
    assert "100k_AMP_INPUT_BLEED_CANDIDATE" in FRONT.read_text()
    assert "1k_SERIES_AUDIO_INPUT_CANDIDATE" in FRONT.read_text()
    assert "100nF_50V_INPUT" in MAIN.read_text()
    assert "10k_0p25W_INPUT" in MAIN.read_text()

def solve(freq,cc,nc,no,rsource,af_gnd_intact,fn):
    if not af_gnd_intact:
        raise ValueError("Shared AF_GND disconnected; no verified physical return/reference")
    return fn(freq,cc,nc,no,rsource)

def main():
    native()
    count=0
    large=0
    maximum_delta=0.
    samples=[]
    for f,cc,nc,no,rs in itertools.product(FREQ,CC,CONTACT,CONTACT,RSRC):
        a=solve(f,cc,nc,no,rs,True,collapsed)
        b=solve(f,cc,nc,no,rs,True,nodal)
        assert abs(a-b)<1e-11,(f,cc,nc,no,rs,a,b)
        assert all(math.isfinite(x) for v in (a,b) for x in (v.real,v.imag))
        assert abs(a)<1.000000001
        maximum_delta=max(maximum_delta,abs(a-b))
        # Each unqualified NO welded contact may inject audio even while NC
        # is nominally closed. Compare to the same hypothetical cap injection
        # with NO disconnected, *not* to an actual device failure rate.
        if math.isfinite(no):
            noopen=collapsed(f,cc,nc,math.inf,rs)
            if abs(a)>abs(noopen): large+=1
        if f==1000 and cc==1e-9 and nc==.1 and rs==10000.:
            samples.append({"NO_ohm":no,"amp_abs_V_per_1V_src":abs(a)})
        for fn in (collapsed,nodal):
            try:solve(f,cc,nc,no,rs,False,fn)
            except ValueError:pass
            else:raise AssertionError("AF_GND open must not be silently bounded")
        count+=1
    assert count==216 and len(samples)==3
    assert large>0
    print("FRONT_K1901_WELDED_NO_NC_AC_FAULT_SCREEN",{
      "native_grounded_two_solver_cases":count,
      "AF_GND_open_unbounded_cases_rejected":count,
      "welded_NO_adds_audio_relative_to_open_NO_cases":large,
      "source_resistances_ohm_hypothetical":RSRC,
      "NC_resistances_ohm_hypothetical":CONTACT,
      "NO_resistances_ohm_hypothetical":CONTACT,
      "max_solver_discrepancy":maximum_delta,
      "example_1kHz_1nF_0p1ohm_NC":samples,
      "welded_NO_permanent_mute_proven":False,
      "physical_coil_or_relay_qualified":False,
      "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_NATIVE_FRONT_MUTE_WELDED_NO_216_AC_AND_216_UNBOUNDED_NONFAB",flush=True)

if __name__=="__main__":main()
