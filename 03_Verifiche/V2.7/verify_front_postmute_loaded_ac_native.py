#!/usr/bin/env python3
"""Independent loaded AC check including the actual post-volume relay NO path.

AM455 C1502/R1502 -> FRONT RV1301 -> ideal energized NO contact ->
R1902 1k -> R1901 100k shunt -> C1201/R1201 -> hypothetical LM386 Rin.
Ideal relay contact is CLOSED (NO selected) for this *receive-audio* model.
Neither failure-mode mute nor RF operation nor OEM relay qualification is proven.
"""
from __future__ import annotations
import math
from pathlib import Path
from itertools import product
import tempfile
from verify_interboard_audio_contract_native import exported_nets, require
from verify_am455_front_lm386_loaded_ac_native import direct as legacy_direct

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"04_KiCad/V2.7_DRAFT"
DEMOD=BASE/"AM455_ENVELOPE/AM455_ENVELOPE_THT_V2_7_DRAFT.kicad_sch"
FRONT=BASE/"FRONT_VOLUME/FRONT_VOLUME_THT_V2_7_DRAFT.kicad_sch"
RELAY=BASE/"FRONT_MUTE_NC_RELAY/FRONT_NC_MUTE_CONTACT_THT_V2_7_DRAFT.kicad_sch"
MAIN=BASE/"AUDIO_RX_MONO_LM386_V2_7_DRAFT.kicad_sch"
VALUES={"r_detector":100000.,"c_detector":100e-9,"pot":10000.,
        "r_series":1000.,"r_bleed":100000.,"c_amp":100e-9,"r_amp":10000.}
FREQ=(100.,300.,1000.,3000.,10000.)
POSITION=(.01,.1,.5,.9,.99)
RIN=(25000.,50000.,75000.)

def parallel(a,b):
    return 1/(1/a+1/b)

def reduced(f,p,rin):
    """Independent passive impedance-chain reduction."""
    w=2*math.pi*f
    zdet=1/(1j*w*VALUES["c_detector"])
    zcap=1/(1j*w*VALUES["c_amp"])
    rtop=(1-p)*VALUES["pot"]
    rbottom=p*VALUES["pot"]
    zamp=zcap+VALUES["r_amp"]+rin
    zmuted=parallel(VALUES["r_bleed"],zamp)
    zrelay=VALUES["r_series"]+zmuted
    zwiper=parallel(rbottom,zrelay)
    za=parallel(VALUES["r_detector"],rtop+zwiper)
    return (za/(zdet+za)*zwiper/(rtop+zwiper)*
            zmuted/zrelay*rin/zamp)

def kcl(f,p,rin):
    """Independent four-node complex KCL: detector A, wiper W, mute M, amp I."""
    w=2*math.pi*f
    yd=1j*w*VALUES["c_detector"]
    ysh=1/VALUES["r_detector"]
    yup=1/((1-p)*VALUES["pot"])
    ydown=1/(p*VALUES["pot"])
    ys=1/VALUES["r_series"]
    ybleed=1/VALUES["r_bleed"]
    yi=1/(VALUES["r_amp"]+1/(1j*w*VALUES["c_amp"]))
    yr=1/rin
    matrix=[[yd+ysh+yup,-yup,0j,0j],
            [-yup,yup+ydown+ys,-ys,0j],
            [0j,-ys,ys+ybleed+yi,-yi],
            [0j,0j,-yi,yi+yr]]
    rhs=[yd,0j,0j,0j]
    original=[row[:] for row in matrix]
    for col in range(4):
        pivot=max(range(col,4),key=lambda i:abs(matrix[i][col]))
        assert abs(matrix[pivot][col])>1e-15
        matrix[col],matrix[pivot]=matrix[pivot],matrix[col]
        rhs[col],rhs[pivot]=rhs[pivot],rhs[col]
        scale=matrix[col][col]
        for j in range(col,4):matrix[col][j]/=scale
        rhs[col]/=scale
        for i in range(4):
            if i==col:continue
            factor=matrix[i][col]
            for j in range(col,4):matrix[i][j]-=factor*matrix[col][j]
            rhs[i]-=factor*rhs[col]
    assert max(abs(sum(original[i][j]*rhs[j] for j in range(4))-
                   (yd if i==0 else 0)) for i in range(4))<1e-9
    return rhs[-1]

def check_native():
    for path,part in ((DEMOD,'100nF_50V_FILM'),(FRONT,'10k_LINEAR_B'),
                      (RELAY,'1k_SERIES_AUDIO_INPUT_CANDIDATE'),
                      (RELAY,'100k_AMP_INPUT_BLEED_CANDIDATE'),
                      (MAIN,'100nF_50V_INPUT'),(MAIN,'10k_0p25W_INPUT')):
        assert part in path.read_text(encoding="utf-8"),(path,part)
    with tempfile.TemporaryDirectory(prefix="postmute_ac_native_") as td:
        d=Path(td)
        dem=exported_nets(DEMOD,d/"det.net")
        front=exported_nets(FRONT,d/"front.net")
        relay=exported_nets(RELAY,d/"relay.net")
        main=exported_nets(MAIN,d/"amp.net")
    require(dem,"AM_DEMOD_AF_BENCH",("C1502","2"),("R1502","1"))
    require(front,"VOL_WIPER_TO_AMP",("RV1301","2"),("J1302","1"))
    require(relay,"VOL_WIPER_TO_AMP",("K1901","3"),("J1901","1"))
    require(relay,"RELAY_COM_AUDIO",("K1901","1"),("R1902","1"))
    require(relay,"AMP_INPUT_MUTED",("R1902","2"),("R1901","1"),("J1902","1"))
    require(relay,"AF_GND",("R1901","2"),("K1901","2"),("J1902","2"))
    require(main,"AUDIO_IN",("J1202","1"),("C1201","1"))
    require(main,"PRE_IN",("C1201","2"),("R1201","1"))
    require(main,"AMP_IN",("R1201","2"),("U1201","3"))
    assert relay["AMP_INPUT_MUTED"].isdisjoint(relay["VOL_WIPER_TO_AMP"])
    assert "AUDIO_6V_LAB" not in relay

def main():
    check_native()
    cases=0
    max_delta=0.
    samples=[]
    for f,p,rin in product(FREQ,POSITION,RIN):
        a=reduced(f,p,rin)
        b=kcl(f,p,rin)
        assert abs(a-b)<3e-10,(f,p,rin,a,b)
        assert 0<abs(a)<1
        old=legacy_direct(f,p,rin)
        assert abs(a)<abs(old),(f,p,rin,a,old)
        max_delta=max(max_delta,abs(a-b))
        if f==1000 and rin==50000 and p in (.1,.5,.99):
            samples.append((f,p,round(abs(old),7),round(abs(a),7)))
        cases+=1
    assert cases==75
    print("FRONT_POSTMUTE_RELAY_RX_AC_PASSIVE",{
        "cases":cases,"R1902_series_ohm":VALUES["r_series"],
        "R1901_shunt_ohm":VALUES["r_bleed"],
        "old_vs_postmute_1kHz_50kRin_magnitude":samples,
        "max_independent_KCL_error":max_delta,
        "NO_contact_idealized_energized":True,
        "mute_off_fail_safe_proven":False,
        "relay_OEM_qualified":False,
        "MAIN_FRONT_harness_qualified":False,
        "NO_FAB_NO_TX":True},flush=True)
    print("PASS_FRONT_POSTMUTE_75_RX_AC_KCL_CASES_NATIVE_NETS_NONFAB",flush=True)

if __name__=="__main__":
    main()
