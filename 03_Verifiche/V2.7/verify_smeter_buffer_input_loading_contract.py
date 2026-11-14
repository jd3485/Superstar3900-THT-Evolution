#!/usr/bin/env python3
"""Design gate: hypothetical buffer INPUT loading on AM455 lab envelope.

Uses independent nodal KCL and closed-form parallel-R calculations;
does not qualify diode detection, op-amp input, ESD, meter FSD, or MAIN AGC.
"""
import math
from pathlib import Path
from verify_interboard_audio_contract_native import exported_nets, require
import tempfile

ROOT=Path(__file__).resolve().parents[2]
AM=ROOT/"04_KiCad/V2.7_DRAFT/AM455_ENVELOPE/AM455_ENVELOPE_THT_V2_7_DRAFT.kicad_sch"
R_DET=47000.0
C_DET=1e-9
R_POT=10000.0
# Nominal allowable DC detector load/error for a *future* buffer; no
# statement on diode dynamic impedance, leakage, PCB contamination.
MAX_LOSS=0.01
MIN_RIN=R_DET*(1-MAX_LOSS)/MAX_LOSS

def parallel(a,b):
    return a*b/(a+b)

def numeric_kcl(r_in,voltage=1.0):
    # Norton source adjusted to make unloaded detector node 1 V. Sink
    # current I=V/Rdet+V/Rin; node voltage is solved by bisection.
    target=voltage/R_DET
    lo,hi=0.0,voltage
    for _ in range(100):
        mid=(lo+hi)/2
        out=mid/R_DET+mid/r_in
        if out<target:lo=mid
        else:hi=mid
    return (lo+hi)/2

def main():
    s=AM.read_text(encoding="utf-8")
    for marker in ['(property "Value" "47k_1PCT_0P25W"',
                   '(property "Value" "1nF_50V_C0G"',
                   '(property "Value" "100nF_50V_FILM"']:
        assert marker in s,("Bench values changed; revisit envelope model",marker)
    with tempfile.TemporaryDirectory(prefix="tht_smeter_input_load_") as d:
        nets=exported_nets(AM,Path(d)/"am.net")
    require(nets,"AM_RECTIFIED_ENV",("D1501","1"),("R1501","1"),
            ("C1501","1"),("C1502","1"))
    require(nets,"AM_DEMOD_AF_BENCH",("C1502","2"),("J1502","1"))
    assert ("J1502","1") not in nets["AM_RECTIFIED_ENV"]
    cases=0
    for rin in (10000.0,47000.0,100000.0,1000000.0,
                4700000.0,5000000.0,10000000.0,22000000.0):
        reff=parallel(R_DET,rin)
        attenuation=reff/R_DET
        loss=1-attenuation
        f0=1/(2*math.pi*R_DET*C_DET)
        floaded=1/(2*math.pi*reff*C_DET)
        assert math.isclose(attenuation,numeric_kcl(rin),rel_tol=1e-12)
        assert math.isclose(floaded/f0,1/attenuation,rel_tol=1e-12)
        assert (loss<=MAX_LOSS)==(rin>=MIN_RIN),rin
        for v in (0.05,0.5,3.0,6.0):
            actual=numeric_kcl(rin,v)
            assert math.isclose(actual,v*attenuation,rel_tol=1e-12)
            cases+=1
    assert MIN_RIN==4653000.0
    assert parallel(R_DET,R_POT)<9000.0
    assert cases==32
    print("AM455_S_METER_BUFFER_INPUT_CONTRACT",{
        "source":"AM_RECTIFIED_ENV LAB ONLY",
        "Rdet_ohm":int(R_DET),"Cdet_F":C_DET,
        "max_static_linear_loading_loss":MAX_LOSS,
        "minimum_effective_input_impedance_ohm":int(MIN_RIN),
        "suggested_provisional_target_ohm":10000000,
        "10k_direct_trim_loss_fraction":round(1-parallel(R_DET,R_POT)/R_DET,5),
        "crosschecked_numeric_nodal_cases":cases,
        "real_buffer_qualified":False,
        "MAIN_AGC_source_qualified":False},flush=True)
    print("PASS_AM455_ENVELOPE_32_KCL_BUFFER_INPUT_IMPEDANCE_GATE_NO_REAL_DRIVER_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
