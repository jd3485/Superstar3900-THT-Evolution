#!/usr/bin/env python3
"""AM455 detector-to-FRONT volume-to-LM386 loaded AC transfer.

Linear PASSIVE network ONLY, driven by an ideal AF voltage at the detector
capacitor. It omits diode nonlinear loading, demodulation, AGC, noise,
LM386 active transfer/THD, cable parasitics and all return-path impedances.
No OEM PVT or hardware qualification. Not an IF receiver sensitivity test.
"""
from __future__ import annotations
import cmath
import math
from pathlib import Path
import tempfile
from verify_interboard_audio_contract_native import exported_nets, require

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"04_KiCad/V2.7_DRAFT"
DEMOD=BASE/"AM455_ENVELOPE/AM455_ENVELOPE_THT_V2_7_DRAFT.kicad_sch"
FRONT=BASE/"FRONT_VOLUME/FRONT_VOLUME_THT_V2_7_DRAFT.kicad_sch"
AUDIO=BASE/"AUDIO_RX_MONO_LM386_V2_7_DRAFT.kicad_sch"
VALUES={
    "R1502":100000.0, "C1502":100e-9, "RV1301":10000.0,
    "C1201":100e-9, "R1201":10000.0,
}
FREQUENCIES=(100.0,300.0,1000.0,3000.0,10000.0)
WIPER_FRACTIONS=(0.01,0.10,0.50,0.90,0.99)
INPUT_RIN=(25000.0,50000.0,75000.0)
# Input resistance 50k is TI typical, 25k and 75k are
# illustrative bounds, NOT OEM specified min/max.

def parallel(*zs:complex)->complex:
    return 1/sum(1/z for z in zs)

def direct(f:float, position:float, rin:float)->complex:
    """Series/parallel circuit reduction, output is LM386 pin3 / detector AF."""
    assert f>0 and 0<position<1 and rin>0
    omega=2*math.pi*f
    zc_det=1/(1j*omega*VALUES["C1502"])
    zc_amp=1/(1j*omega*VALUES["C1201"])
    rtop=(1-position)*VALUES["RV1301"]
    rbottom=position*VALUES["RV1301"]
    zamp=zc_amp+VALUES["R1201"]+rin
    zwiper=parallel(rbottom,zamp)
    zload=parallel(VALUES["R1502"],rtop+zwiper)
    return zload/(zc_det+zload)*zwiper/(rtop+zwiper)*rin/zamp

def nodal(f:float,position:float,rin:float)->complex:
    """Independent KCL solve for detector out(A), wiper(W), amp IC pin3(I)."""
    omega=2*math.pi*f
    ydet=1j*omega*VALUES["C1502"]
    yshunt=1/VALUES["R1502"]
    yup=1/((1-position)*VALUES["RV1301"])
    ydown=1/(position*VALUES["RV1301"])
    yinput=1/(VALUES["R1201"]+1/(1j*omega*VALUES["C1201"]))
    yin=1/rin
    # KCL: detector source is ideal 1V before C1502.
    rows=[
        [ydet+yshunt+yup,-yup,0j],
        [-yup,yup+ydown+yinput,-yinput],
        [0j,-yinput,yinput+yin],
    ]
    rhs=[ydet,0j,0j]
    # Complex Gaussian elimination with partial pivoting; not a re-use of
    # the series/parallel formula above.
    for k in range(3):
        pivot=max(range(k,3),key=lambda i:abs(rows[i][k]))
        assert abs(rows[pivot][k])>1e-15
        rows[k],rows[pivot]=rows[pivot],rows[k]
        rhs[k],rhs[pivot]=rhs[pivot],rhs[k]
        scale=rows[k][k]
        for j in range(k,3): rows[k][j]/=scale
        rhs[k]/=scale
        for i in range(3):
            if i==k:continue
            factor=rows[i][k]
            for j in range(k,3): rows[i][j]-=factor*rows[k][j]
            rhs[i]-=factor*rhs[k]
    # Explicit residual from the *original* KCL, not just the reduced form.
    a,w,ic=rhs
    eq1=(a-1)*ydet+a*yshunt+(a-w)*yup
    eq2=(w-a)*yup+w*ydown+(w-ic)*yinput
    eq3=(ic-w)*yinput+ic*yin
    assert max(map(abs,(eq1,eq2,eq3)))<1e-8,(f,position,rin,eq1,eq2,eq3)
    return ic

def check_actual_cad():
    for sch,labels in (
        (DEMOD,("100nF_50V_FILM","100k_1PCT_0P25W")),
        (FRONT,("10k_LINEAR_B_THT_FOOTPRINT_PROVISIONAL",)),
        (AUDIO,("100nF_50V_INPUT","10k_0p25W_INPUT","LM386N-1/NOPB"))):
        raw=sch.read_text(encoding="utf-8")
        assert all(label in raw for label in labels),(sch,labels)
    with tempfile.TemporaryDirectory(prefix="tht_af_load_nets_") as d:
        t=Path(d)
        demod=exported_nets(DEMOD,t/"demod.net")
        front=exported_nets(FRONT,t/"front.net")
        audio=exported_nets(AUDIO,t/"amp.net")
    require(demod,"AM_DEMOD_AF_BENCH",("C1502","2"),("R1502","1"),("J1502","1"))
    require(demod,"IF_BENCH_GND",("R1502","2"),("J1502","2"))
    require(front,"DEMOD_AUDIO",("J1301","1"),("RV1301","1"))
    require(front,"VOL_WIPER_TO_AMP",("RV1301","2"),("J1302","1"))
    require(front,"AF_GND",("J1301","2"),("RV1301","3"),("J1302","2"))
    require(audio,"AUDIO_IN",("J1202","1"),("C1201","1"))
    require(audio,"PRE_IN",("C1201","2"),("R1201","1"))
    require(audio,"AMP_IN",("R1201","2"),("U1201","3"))
    require(audio,"GND",("J1202","2"),("U1201","4"))
    # Do not silently assume physical return/chassis equivalence.
    assert "AUDIO_6V_LAB" not in front and "AUDIO_6V_LAB" not in demod

def main():
    check_actual_cad()
    count=0
    examples=[]
    for rin in INPUT_RIN:
        for fraction in WIPER_FRACTIONS:
            for f in FREQUENCIES:
                a=direct(f,fraction,rin)
                b=nodal(f,fraction,rin)
                err=abs(a-b)
                assert err<3e-10,(f,fraction,rin,a,b,err)
                assert 0<abs(a)<1,(f,fraction,rin,a)
                assert all(math.isfinite(x) for x in (a.real,a.imag,b.real,b.imag))
                count+=1
                if rin==50000 and f in (100,1000,10000):
                    examples.append((int(f),fraction,round(abs(a),7),round(cmath.phase(a)*180/math.pi,4)))
        for f in FREQUENCIES:
            mags=[abs(direct(f,p,rin)) for p in WIPER_FRACTIONS]
            assert all(x<y for x,y in zip(mags,mags[1:])),(rin,f,mags)
    assert count==len(FREQUENCIES)*len(WIPER_FRACTIONS)*len(INPUT_RIN)==75
    assert abs(direct(1000,.99,50000))>abs(direct(100,.99,50000))
    assert abs(direct(1000,.99,50000))>abs(direct(1000,.1,50000))
    print("AF_PASSIVE_TRANSFER_SAMPLE_FREQ_HZ_WIPER_FRACTION_MAG_PHASE_DEG",examples,flush=True)
    print("AF_PASSIVE_MODEL_LIMITS",{
        "C1502_F":VALUES["C1502"],"R1502_ohm":VALUES["R1502"],
        "RV1301_ohm":VALUES["RV1301"],"C1201_F":VALUES["C1201"],
        "R1201_ohm":VALUES["R1201"],"LM386_Rin_ohm_scenario":INPUT_RIN,
        "active_gain_included":False,"diode_model_included":False,
        "cable_ground_noise_included":False,"vendor_PVT_qualified":False,
        "physical_harness_qualified":False,"NO_FAB_NO_TX":True},flush=True)
    print("PASS_AF_AM455_FRONT_LM386_75_AC_KCL_CASES_NATIVE_KICAD_PIN_NETS_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
