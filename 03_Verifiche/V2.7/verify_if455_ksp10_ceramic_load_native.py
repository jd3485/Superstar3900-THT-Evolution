#!/usr/bin/env python3
"""KSP10BU *generic* BJT emitter follower: native ceramic input dummy loads.

27 ngspice bias+AC cases: 5.5/6.0/6.5V rails x BETA=40/80/160
x 100k existing reference / 2k / 1.5k resistive loads.
No vendor transistor SPICE, ceramic transfer, noise, two-tone IMD,
temperature dependence, LO-driven mixer, current or PCB qualification.
"""
from pathlib import Path
import math
import subprocess
import tempfile

from verify_interboard_audio_contract_native import exported_nets, require
from verify_if455_two_port_source_impedance_native import TANK
from verify_if455_ksp10_generic_bjt_bias_ac import (
    DECK, SCH, RAILS, BETAS, read_rows
)

LOADS=(100000,2000,1500)

def run_case(directory,original,rail,beta,load):
    src=original.replace(".param rail=6 gain=80",
                         f".param rail={rail} gain={beta}")
    assert src!=original or (rail,beta)==(6.0,80)
    marker="R1704 output 0 100k"
    assert src.count(marker)==1
    src=src.replace(marker,f"R1704 output 0 {load}")
    file=directory/"candidate.cir"
    file.write_text(src,encoding="utf-8")
    log=directory/"native.log"
    proc=subprocess.run(["ngspice","-b","-o",str(log),str(file)],
                        cwd=directory,capture_output=True,text=True)
    proc.check_returncode()
    output=log.read_text(encoding="utf-8",errors="replace")
    assert "Error:" not in output and "fatal" not in output.lower(),output[-1600:]
    bias=read_rows(directory/"ifbuf_bias.dat",4)
    ac=read_rows(directory/"ifbuf_ac.dat",3)
    assert len(ac)==3,(rail,beta,load,ac)
    assert abs(ac[1][0]-455000)<1,(rail,beta,load,ac)
    base,emitter,collector=bias[-1][1:]
    output,stimulus=ac[1][1:3]
    assert abs(collector-rail)<0.03,(rail,beta,load,collector)
    assert 0<emitter<base<collector<7
    assert 0.35<base-emitter<1.1
    assert stimulus>0 and output>0
    ratio=output/stimulus
    assert 0<ratio<1.1 and math.isfinite(ratio)
    return base,emitter,ratio

def main():
    source=DECK.read_text(encoding="utf-8")
    sch=SCH.read_text(encoding="utf-8")
    assert source.count(".param rail=6 gain=80")==1
    assert source.count("R1704 output 0 100k")==1
    for token in ("22k_TOP_BIAS_DRAFT","10k_BOTTOM_BIAS_DRAFT",
                  "2k2_EMITTER_SET_DRAFT","ONSEMI_KSP10BU_TO92_CANDIDATE"):
        assert token in sch
    outputs={}
    with tempfile.TemporaryDirectory(prefix="tht_ksp10_ceramic_ac_") as tmp:
        root=Path(tmp)
        nets=exported_nets(SCH,root/"ksp10.net")
        tank=exported_nets(TANK,root/"if455.net")
        require(nets,"IF455_TANK_OUT",("J1701","1"),("C1701","1"))
        require(nets,"IFBUF_BASE_BIAS",("Q1701","1"),("C1701","2"))
        require(nets,"IFBUF_EMITTER",("Q1701","2"),("R1703","1"),("C1702","1"))
        require(nets,"VLAB6_IFBUF_ONLY",("Q1701","3"),("J1703","1"))
        require(nets,"IFBUF_AC_OUT",("C1702","2"),("R1704","1"),("J1702","1"))
        require(tank,"IF455_SOURCE",("J1601","1"),("C1601","1"))
        for rail in RAILS:
            for beta in BETAS:
                for load in LOADS:
                    directory=root/f"rail{rail}_b{beta}_load{load}"
                    directory.mkdir()
                    base,emitter,ratio=run_case(directory,source,rail,beta,load)
                    outputs[rail,beta,load]=(base,emitter,ratio)
                    print("KSP10_GENERIC_CERAMIC_INPUT_DUMMY_NATIVE",{
                        "lab_rail_V":rail,"generic_BETA":beta,
                        "resistive_input_dummy_ohm":load,
                        "DC_base_V":round(base,9),"DC_emitter_V":round(emitter,9),
                        "DC_emitter_mA":round(emitter/2200*1000,9),
                        "AC455_out_over_50ohm_generator":round(ratio,9),
                        "actual_filter_or_OEM_BJT_qualified":False},flush=True)
        assert len(outputs)==27
        # PR99 original verified reference: 6V, beta80, 100k load.
        original=outputs[6.0,80,100000][2]
        assert abs(original-0.970670)<0.00003,original
        for rail in RAILS:
            for beta in BETAS:
                ref=outputs[rail,beta,100000][2]
                for load in (2000,1500):
                    ratio=outputs[rail,beta,load][2]/ref
                    assert 0<ratio<1.01
                    # DC bias cannot change with a capacitively-coupled
                    # output resistor under the tested ideal DC model.
                    assert abs(outputs[rail,beta,load][1]-
                               outputs[rail,beta,100000][1])<1e-5
                    print("KSP10_GENERIC_CERAMIC_LOAD_RELATIVE_TO_100K",{
                        "rail_V":rail,"beta":beta,"load_ohm":load,
                        "AC455_output_ratio_to_100k":round(ratio,9),
                        "actual_OEM_noise_IMD_pass":False},flush=True)
    print("PASS_NATIVE_KICAD9_KSP10_27_CERAMIC_LOAD_GENERIC_BJT_AC_BIAS_CORNERS_NO_OEM_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
