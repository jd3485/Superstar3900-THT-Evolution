#!/usr/bin/env python3
"""Native KiCad9 S-meter passive input load, idealized finite-source screening.

This is source loading for historical 10k potentiometer / two 100k guards,
NOT a qualified meter driver or approved MAIN-FRONT implementation.
"""
from itertools import product
from math import isclose,isfinite
from pathlib import Path
import tempfile
from verify_interboard_audio_contract_native import exported_nets,require

ROOT=Path(__file__).resolve().parents[2]
SCH=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_SMETER/FRONT_SMETER_THT_V2_7_DRAFT.kicad_sch"
POT=10000.
LIMIT=100000.
V_OPEN=(5.,9.,11.,15.,20.)
SOURCE_R=(0.,100.,1000.)
COIL=(1000.,20000.,40000.)
SHORTS=(0,1,2)
WIPER=(0.,.1,.5,.9,1.)

def reduction(v_open,r_source,r_coil,shorts,wiper):
    """Exact Thevenin loaded pot, signed source current and meter current."""
    if not all(isfinite(x) for x in (v_open,r_source,r_coil,wiper)):
        raise ValueError("finite inputs required")
    if r_source<0 or r_coil<=0 or shorts not in SHORTS or not 0<=wiper<=1:
        raise ValueError("nonphysical setup")
    rh=POT*(1-wiper)
    rl=POT*wiper
    rm=(2-shorts)*LIMIT+r_coil
    parallel=0. if rl==0 else 1/(1/rl+1/rm)
    zin=rh+parallel
    terminal=v_open if r_source==0 else v_open*zin/(r_source+zin)
    vw=terminal if rh==0 else terminal*parallel/zin
    meter=vw/rm
    source=terminal/zin
    pot=source if rl==0 else vw/rl
    return terminal,source,meter,pot

def kcl(v_open,r_source,r_coil,shorts,wiper):
    """Independent two-node nodal conductance equations with known V_open."""
    if not all(isfinite(x) for x in (v_open,r_source,r_coil,wiper)):
        raise ValueError("nonfinite")
    if r_source<0 or r_coil<=0 or shorts not in SHORTS or not 0<=wiper<=1:
        raise ValueError("invalid")
    rh=POT*(1-wiper)
    rl=POT*wiper
    rm=(2-shorts)*LIMIT+r_coil
    if rh==0:
        # Wiper and source terminal physically the same node.
        g=1/POT+1/rm
        node=v_open if r_source==0 else v_open/(1+r_source*g)
        return node,node*g,node/rm,node/POT
    if rl==0:
        # Wiper and return physically the same node.
        node=v_open if r_source==0 else v_open/(1+r_source/rh)
        return node,node/rh,0.,node/rh
    # KCL on source terminal (T) and wiper (W).
    gs=1/r_source if r_source else 0.
    gh=1/rh
    gl=1/rl
    gm=1/rm
    if r_source==0:
        t=v_open
        w=gh*t/(gh+gl+gm)
        return t,(t-w)*gh,w*gm,w*gl
    a=gs+gh;b=-gh;c=gh+gl+gm
    det=a*c-b*b
    t=gs*v_open*c/det
    w=gs*v_open*gh/det
    return t,(t-w)*gh,w*gm,w*gl

def native():
    with tempfile.TemporaryDirectory(prefix="tht_smeter_loading_") as td:
        nets=exported_nets(SCH,Path(td)/"meter.net")
    expected={
        "METER_DRIVE_CANDIDATE":{("J1801","1"),("RV1801","1")},
        "METER_RETURN":{("J1801","2"),("RV1801","3"),("J1802","2")},
        "METER_TRIM_OUTPUT":{("RV1801","2"),("R1801","1")},
        "METER_LIMIT_STAGE1":{("R1801","2"),("R1802","1")},
        "METER_POS_LIMITED":{("R1802","2"),("J1802","1")}}
    assert set(nets)==set(expected)
    for n,pins in expected.items():
        require(nets,n,*pins)
        assert nets[n]==pins
    txt=SCH.read_text(encoding="utf-8")
    for val in ("10k_LINEAR_B_THT_DRAFT_PROVISIONAL",
                "100k_0P25W_CANDIDATE_NO_FSD_QUAL",
                "100k_0P25W_REDUNDANT_CANDIDATE_NO_FSD_QUAL"):
        assert txt.count(val)==1,val

def main():
    native()
    n=0;maximum_error=0.
    for v,rs,rc,shorts,w in product(V_OPEN,SOURCE_R,COIL,SHORTS,WIPER):
        a=reduction(v,rs,rc,shorts,w)
        b=kcl(v,rs,rc,shorts,w)
        for x,y in zip(a,b):
            assert isfinite(x) and isfinite(y)
            err=abs(x-y)/max(abs(x),abs(y),1e-12)
            maximum_error=max(maximum_error,err)
            assert err<1e-10,(v,rs,rc,shorts,w,a,b)
        terminal,isrc,im,ipot=a
        assert isrc>=0 and im>=0 and ipot>=0
        if rs:
            assert isclose(v-terminal,rs*isrc,rel_tol=1e-10,abs_tol=1e-10)
        else:assert isclose(v,terminal)
        # KCL split at wiper into meter branch and lower potentiometer
        # branch; at wiper zero the return branch includes upper track.
        assert isclose(isrc,ipot+im,rel_tol=1e-10,abs_tol=1e-10)
        assert isrc>=ipot-1e-12 and isrc>=im-1e-12
        n+=1
    assert n==675
    t,source,meter,pot=reduction(11.,0.,20000.,0,1.)
    assert isclose(t,11.) and isclose(meter,50e-6)
    assert isclose(pot,1.1e-3) and isclose(source,1.15e-3)
    assert isclose(t*pot,0.0121)
    # 1k source resistance already degrades the nominal 50uA @11V case.
    tv,sv,mv,pv=reduction(11.,1000.,20000.,0,1.)
    assert tv<11. and mv<50e-6
    assert isclose(sv,pv+mv)
    a=reduction(5.,0.,20000.,0,1.)
    assert isclose(a[1],.5e-3+5/220000)
    for bad in (float("nan"),float("inf")):
        try:reduction(11.,bad,20000.,0,1.)
        except ValueError:pass
        else:raise AssertionError("nonfinite source impedance accepted")
    print("FRONT_SMETER_SOURCE_LOADING_THEVENIN_KCL",{
        "cases":n,"max_relative_independent_KCL_error":maximum_error,
        "11V_20kcoil_nominal_50uA_meter_source_current_mA":source*1000,
        "11V_20kcoil_nominal_50uA_pot_current_mA":pot*1000,
        "11V_pot_total_power_mW":t*pot*1000,
        "11V_1k_source_resistance_loaded_terminal_V":tv,
        "11V_1k_source_resistance_meter_current_uA":mv*1e6,
        "actual_MAIN_source_driver_exists":False,
        "meter_FSD_OEM_qualified":False,
        "pot_power_derating_qualified":False,
        "NO_FAB_NO_TX":True},flush=True)
    print("PASS_NATIVE_KICAD9_SMETER_675_SOURCE_LOADING_INDEPENDENT_KCL_CASES_NONFAB",flush=True)

if __name__=="__main__":main()
