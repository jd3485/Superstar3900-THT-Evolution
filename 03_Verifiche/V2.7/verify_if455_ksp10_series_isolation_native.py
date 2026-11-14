#!/usr/bin/env python3
"""KSP10 IF455 isolation resistor screen: 30 native AC cases.

Uses the same 10nF KSP10 input coupling and 455kHz tank/source
as PR156/158. Rseries is SPICE-only, 0/1k/4.7k/10k/47k ohm.
Three generic beta corners x 1.5k/2k resistive ceramic dummies.
Only amplitude/tank voltage are characterized; not real OEM noise,
filter, impedance spectrum, stability, transistor linearity or PCB.
"""
from pathlib import Path
import math
import subprocess
import tempfile

from verify_interboard_audio_contract_native import exported_nets,require
from verify_if455_two_port_source_impedance_native import TANK
from verify_if455_ksp10_generic_bjt_bias_ac import SCH as KSP10_SCH,BETAS
from verify_if455_j113_ksp10_shared_tank_native import circuit

RS=(0,1000,4700,10000,47000)
LOADS=(1500,2000)
FREQ=455000

def deck(beta,load,series):
    raw=circuit("KSP10",beta,load,10000)
    needle="CIN out input 10000p"
    assert raw.count(needle)==1
    if series:
        raw=raw.replace(needle,f"RS_ISO out cin_top {series}\nCIN cin_top input 10000p")
    return raw

def run_case(folder,beta,load,series):
    path=folder/"interface.cir"
    path.write_text(deck(beta,load,series),encoding="utf-8")
    proc=subprocess.run(["ngspice","-b","-o",str(folder/"run.log"),str(path)],
                        cwd=folder,capture_output=True,text=True)
    proc.check_returncode()
    log=(folder/"run.log").read_text(encoding="utf-8",errors="replace")
    assert "Error:" not in log and "fatal" not in log.lower(),log[-2000:]
    data=folder/"transfer.dat"
    assert data.exists()
    rows=[tuple(map(float,line.split())) for line in data.read_text().splitlines() if line.strip()]
    assert 1<=len(rows)<=2 and all(len(x)==4 and all(math.isfinite(q) for q in x) for x in rows)
    f,tank,out,base=rows[0]
    assert abs(f-FREQ)<1
    assert 0<tank<3 and 0<out<5 and 0<base<5
    return tank,out,base

def main():
    native=KSP10_SCH.read_text(encoding="utf-8")
    assert "ONSEMI_KSP10BU_TO92_CANDIDATE" in native
    assert "2k2_EMITTER_SET_DRAFT" in native
    results={}
    with tempfile.TemporaryDirectory(prefix="ksp10_if455_series_isolation_") as t:
        root=Path(t)
        pins=exported_nets(KSP10_SCH,root/"ksp10.net")
        tanknets=exported_nets(TANK,root/"tank.net")
        require(pins,"IFBUF_BASE_BIAS",("Q1701","1"),("C1701","2"))
        require(pins,"IFBUF_EMITTER",("Q1701","2"),("R1703","1"))
        require(pins,"VLAB6_IFBUF_ONLY",("Q1701","3"),("J1703","1"))
        require(tanknets,"IF455_SOURCE",("J1601","1"),("C1601","1"))
        require(tanknets,"IF455_TANK",("C1601","2"),("L1601","1"))
        for beta in BETAS:
            for load in LOADS:
                for series in RS:
                    folder=root/f"beta{beta}_load{load}_series{series}"
                    folder.mkdir()
                    result=run_case(folder,beta,load,series)
                    results[beta,load,series]=result
                    print("KSP10_IF455_SERIES_ISOLATION_NATIVE",{
                        "generic_BJT_beta":beta,
                        "ceramic_resistor_only_dummy_ohm":load,
                        "temporary_Rseries_ohm":series,
                        "CIN_original_pF":10000,
                        "tank_out_VperV":round(result[0],9),
                        "buffer_out_VperV":round(result[1],9),
                        "base_input_VperV":round(result[2],9),
                        "real_transistor_filter_validated":False},flush=True)
        assert len(results)==30
        original=results[80,2000,0]
        assert abs(original[0]-0.124579814)<1e-6
        assert abs(original[1]-0.119093670)<1e-6
        for beta in BETAS:
            for load in LOADS:
                reference=results[beta,load,0]
                for series in RS:
                    tank,out,_=results[beta,load,series]
                    tank_ratio=tank/reference[0]
                    out_ratio=out/reference[1]
                    assert tank_ratio>0 and out_ratio>0
                    print("KSP10_IF455_ISOLATION_RELATIVE_TO_DIRECT",{
                        "beta":beta,"load":load,"Rseries_ohm":series,
                        "tank_ratio_to_no_series":round(tank_ratio,8),
                        "output_ratio_to_no_series":round(out_ratio,8),
                        "power_noise_selectivity_qualified":False},flush=True)
    print("PASS_NATIVE_KICAD9_KSP10_30_IF455_SERIES_ISOLATION_RESISTOR_TANK_OUTPUT_CASES_NO_OEM_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
