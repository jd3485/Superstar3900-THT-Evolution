#!/usr/bin/env python3
"""Loaded AM455 envelope AF source model with UNKNOWN dynamic diode resistance.

Rsource 1k/10k/47k/100k values are illustrative Thevenin scenarios, NOT
measured diode impedance or OEM PVT. Passive AC envelope, not real nonlinear
455k AM detection, receiver sensitivity, AGC, noise or SSB/FM.
"""
from __future__ import annotations
import math
from pathlib import Path
import tempfile
from verify_interboard_audio_contract_native import exported_nets, require
from verify_am455_front_lm386_loaded_ac_native import (
    direct as downstream_transfer, parallel, FREQUENCIES,
    WIPER_FRACTIONS, INPUT_RIN, VALUES, check_actual_cad
)

ROOT=Path(__file__).resolve().parents[2]
DEMOD=ROOT/"04_KiCad/V2.7_DRAFT/AM455_ENVELOPE/AM455_ENVELOPE_THT_V2_7_DRAFT.kicad_sch"
RSOURCE_SCENARIOS=(1000.0,10000.0,47000.0,100000.0)
R_ENV=47000.0
C_ENV=1e-9

def reduced(f:float,p:float,rin:float,rs:float)->complex:
    """Two-port passive nodal reduction with finite source impedance."""
    omega=2*math.pi*f
    zamp=VALUES["R1201"]+1/(1j*omega*VALUES["C1201"])+rin
    zbot=parallel(p*VALUES["RV1301"],zamp)
    zaf=parallel(VALUES["R1502"],(1-p)*VALUES["RV1301"]+zbot)
    zcoupling=1/(1j*omega*VALUES["C1502"])
    zenv=parallel(R_ENV,1/(1j*omega*C_ENV),zcoupling+zaf)
    return zenv/(rs+zenv)*downstream_transfer(f,p,rin)

def nodal(f:float,p:float,rin:float,rs:float)->complex:
    """Independent 4-node complex KCL envelope(E), AF(A), wiper(W), IC(I)."""
    w=2*math.pi*f
    ys=1/rs
    yenv=1/R_ENV+1j*w*C_ENV
    yc=1j*w*VALUES["C1502"]
    yshunt=1/VALUES["R1502"]
    yup=1/((1-p)*VALUES["RV1301"])
    ydown=1/(p*VALUES["RV1301"])
    yinput=1/(VALUES["R1201"]+1/(1j*w*VALUES["C1201"]))
    yin=1/rin
    matrix=[
        [ys+yenv+yc,-yc,0j,0j],
        [-yc,yc+yshunt+yup,-yup,0j],
        [0j,-yup,yup+ydown+yinput,-yinput],
        [0j,0j,-yinput,yinput+yin]
    ]
    rhs=[ys,0j,0j,0j]
    n=4
    for k in range(n):
        pivot=max(range(k,n),key=lambda i:abs(matrix[i][k]))
        assert abs(matrix[pivot][k])>1e-15
        matrix[k],matrix[pivot]=matrix[pivot],matrix[k]
        rhs[k],rhs[pivot]=rhs[pivot],rhs[k]
        scale=matrix[k][k]
        for j in range(k,n):matrix[k][j]/=scale
        rhs[k]/=scale
        for i in range(n):
            if i==k:continue
            factor=matrix[i][k]
            for j in range(k,n):matrix[i][j]-=factor*matrix[k][j]
            rhs[i]-=factor*rhs[k]
    e,a,vol,ic=rhs
    residuals=(
        (e-1)*ys+e*yenv+(e-a)*yc,
        (a-e)*yc+a*yshunt+(a-vol)*yup,
        (vol-a)*yup+vol*ydown+(vol-ic)*yinput,
        (ic-vol)*yinput+ic*yin
    )
    assert max(map(abs,residuals))<1e-8,(f,p,rin,rs,residuals)
    return ic

def main():
    check_actual_cad()
    sch=DEMOD.read_text(encoding="utf-8")
    assert "47k_1PCT_0P25W" in sch and "1nF_50V_C0G" in sch
    assert '"Reference" "R1501"' in sch and '"Reference" "C1501"' in sch
    with tempfile.TemporaryDirectory(prefix="tht_am_env_source_") as t:
        nets=exported_nets(DEMOD,Path(t)/"demod.net")
    require(nets,"AM_RECTIFIED_ENV",("D1501","1"),("R1501","1"),
            ("C1501","1"),("C1502","1"))
    require(nets,"IF_BENCH_GND",("R1501","2"),("C1501","2"))
    require(nets,"AM_DEMOD_AF_BENCH",("C1502","2"),("J1502","1"))
    count=0
    samples=[]
    for rs in RSOURCE_SCENARIOS:
        for rin in INPUT_RIN:
            for p in WIPER_FRACTIONS:
                for f in FREQUENCIES:
                    v1=reduced(f,p,rin,rs)
                    v2=nodal(f,p,rin,rs)
                    assert abs(v1-v2)<3e-10,(rs,rin,p,f,v1,v2)
                    assert 0<abs(v1)<1
                    assert all(math.isfinite(q) for q in (v1.real,v1.imag))
                    count+=1
                    if rin==50000 and p==.99 and f in (100,1000,10000):
                        samples.append((int(rs),int(f),round(abs(v1),7)))
    assert count==300
    for rin in INPUT_RIN:
        for p in WIPER_FRACTIONS:
            for f in FREQUENCIES:
                gains=[abs(reduced(f,p,rin,rs)) for rs in RSOURCE_SCENARIOS]
                assert all(x>y for x,y in zip(gains,gains[1:])),(f,p,rin,gains)
    for f in FREQUENCIES:
        assert abs(reduced(f,.99,50000,47000))<abs(
            downstream_transfer(f,.99,50000))
    print("AM455_THEVENIN_SCENARIO_AF_TRANSFER_RSOURCE_FREQ_MAG",samples,flush=True)
    print("AM455_ENVELOPE_NOT_OEM_LIMITS",{
        "diode_dynamic_resistance_measured":False,
        "thevenin_scenarios_ohm":RSOURCE_SCENARIOS,
        "R1501_ohm":R_ENV,"C1501_F":C_ENV,
        "LM386_active_gain_included":False,
        "IF455_RF_detector_nonlinearity_included":False,
        "PVT_and_noise_qualified":False,
        "NO_FAB_NO_TX":True},flush=True)
    print("PASS_KICAD9_AM455_ENVELOPE_300_RSOURCE_AC_KCL_CASES_NOT_DIODE_OEM_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
