#!/usr/bin/env python3
"""FRONT volume 10k open-low terminal fault: linear illustrative audio envelope.

Compare actual KiCad9 pin 1/2/3 connectivity with the distinct fault assumption:
RV1301 pin3 becomes electrically OPEN, while external AF_GND and LM386 input
return remain connected. No galvanic battery, hardware, RF, gain or noise test.
An unintended open low-end can bypass the low-volume attenuation; NOT a
manufacturer fault rate, product protection or actual user exposure rating.
"""
from __future__ import annotations
import math
from verify_am455_front_lm386_loaded_ac_native import (
    VALUES, FREQUENCIES, INPUT_RIN, WIPER_FRACTIONS, check_actual_cad, direct
)

def series_parallel_open_low(freq: float, fraction: float, rin: float) -> complex:
    """Independent two-branch reduction with removed RV1301 pin3 connection."""
    omega=2*math.pi*freq
    zdet=1/(1j*omega*VALUES["C1502"])
    zamp=1/(1j*omega*VALUES["C1201"])+VALUES["R1201"]+rin
    rtop=(1-fraction)*VALUES["RV1301"]
    zload=1/(1/VALUES["R1502"]+1/(rtop+zamp))
    return zload/(zdet+zload)*zamp/(rtop+zamp)*rin/zamp

def independent_kcl_open_low(freq: float, fraction: float, rin: float) -> complex:
    """Separate three-node linear KCL, never reuse reduction above."""
    omega=2*math.pi*freq
    ydet=1j*omega*VALUES["C1502"]
    ysh=1/VALUES["R1502"]
    ytop=1/((1-fraction)*VALUES["RV1301"])
    yamp=1/(VALUES["R1201"]+1/(1j*omega*VALUES["C1201"]))
    yin=1/rin
    matrix=[
        [ydet+ysh+ytop,-ytop,0j],
        [-ytop,ytop+yamp,-yamp],
        [0j,-yamp,yamp+yin],
    ]
    rhs=[ydet,0j,0j]
    originals=[row[:] for row in matrix]
    original_rhs=rhs[:]
    for k in range(3):
        pivot=max(range(k,3),key=lambda i:abs(matrix[i][k]))
        assert abs(matrix[pivot][k])>1e-15
        matrix[k],matrix[pivot]=matrix[pivot],matrix[k]
        rhs[k],rhs[pivot]=rhs[pivot],rhs[k]
        factor=matrix[k][k]
        for j in range(k,3):matrix[k][j]/=factor
        rhs[k]/=factor
        for i in range(3):
            if i==k:continue
            multiple=matrix[i][k]
            for j in range(k,3):matrix[i][j]-=multiple*matrix[k][j]
            rhs[i]-=multiple*rhs[k]
    residuals=[sum(originals[i][j]*rhs[j] for j in range(3))-original_rhs[i] for i in range(3)]
    assert max(map(abs,residuals))<1e-8,(freq,fraction,rin,residuals)
    return rhs[2]

def main()->None:
    # Native export confirms the *healthy* electrical mapping. The open
    # terminal exists in this model only and never edits the product CAD.
    check_actual_cad()
    count=0
    samples=[]
    for rin in INPUT_RIN:
        for fraction in WIPER_FRACTIONS:
            for frequency in FREQUENCIES:
                healthy=direct(frequency,fraction,rin)
                fault=series_parallel_open_low(frequency,fraction,rin)
                kcl=independent_kcl_open_low(frequency,fraction,rin)
                assert abs(fault-kcl)<3e-10,(frequency,fraction,rin,fault,kcl)
                assert 0<abs(healthy)<abs(fault)<1,(frequency,fraction,rin,healthy,fault)
                assert all(math.isfinite(v) for v in (fault.real,fault.imag,kcl.real,kcl.imag))
                count+=1
                if frequency==1000 and rin==50000:
                    samples.append((fraction,round(abs(healthy),6),round(abs(fault),6),
                                    round(abs(fault)/abs(healthy),3)))
    assert count==75
    assert samples[0][3]>50, samples
    assert samples[-1][3]<2, samples
    # With intact downstream input-to-AF_GND, an ideal open WIPER or
    # open upper terminal yields zero AC at the amplifier input: real
    # parasitic coupling and transients are NOT modeled here.
    print("FRONT_POT_PIN3_OPEN_1KHZ_50K_RIN_WIPER_NOMINAL_FAULT_RATIO",samples,flush=True)
    print("FRONT_POT_OPEN_LOW_LIMITATIONS",{
        "linear_audio_only":True,"fault_mode":"RV1301 pin3/low track open",
        "modelled_cases":count,"nominal_wiper_and_source_ground_unchanged":True,
        "open_wiper_and_open_high_ideal_pin3_ac":0,
        "input_parasitics_and_pop_transients_included":False,
        "no_manufacturer_fault_probability_or_hardware_test":True,
        "OEM_potentiometer_and_panel_qualified":False,"NO_FAB_NO_TX":True},flush=True)
    print("PASS_FRONT_POT_OPEN_LOW_75_INDEPENDENT_AC_KCL_FAULT_CASES_NATIVE_KICAD_PIN_CONTRACT_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":main()
