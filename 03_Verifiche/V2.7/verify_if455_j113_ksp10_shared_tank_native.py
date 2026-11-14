#!/usr/bin/env python3
"""Common-source common-IF455-tank generic J113 vs KSP10 load comparison.

54 real ngspice runs: two device families x relevant generic parameter
corners x the SAME 50ohm source, tank, 6V rail, input coupling 10p/10n,
and resistor dummy loads 100k/2k/1.5k. J113: 6 NJF corners;
KSP10: 3 BJT beta corners. No vendor transistor models, noise,
strong-signal IMD, ceramic frequency response, LO-driven mixer, or
physical filter selection. Existing KiCad9 standalone netlists guarded.
"""
from pathlib import Path
import math
import subprocess
import tempfile

from verify_interboard_audio_contract_native import exported_nets, require
from verify_if455_two_port_source_impedance_native import TANK
from verify_if455_j113_ceramic_load_native import (
    SCH as J113_SCH, VTO, IDSS
)
from verify_if455_ksp10_generic_bjt_bias_ac import (
    SCH as KSP10_SCH, BETAS
)

COUPLINGS_PF=(10,10000)
LOADS=(100000,2000,1500)
FREQUENCY=455000
CASES=54

def circuit(device,parameter,load,gate_coupling_pf):
    assert device in ("J113","KSP10")
    assert gate_coupling_pf in COUPLINGS_PF
    assert load in LOADS
    prefix=[
        "* Common IF455 tank: 50-ohm generator and passive candidate, 6V bench",
        "VSIGNAL src 0 DC 0 AC 1",
        "RGEN src gen 50",
        "C1601 gen tank 10p",
        "L1601 tank ltail 1m",
        "RCOIL ltail 0 16.5",
        "C1602 tank 0 82p",
        "C1603 tank 0 30p",
        "R1601 tank 0 47k",
        "C1604 tank out 10p",
        "R1602 out 0 100k",
        "VLAB vcc 0 DC 6",
        f"CIN out input {gate_coupling_pf}p",
    ]
    if device=="J113":
        vto,idss=parameter
        beta=idss/(vto*vto)
        components=[
            "RGATE input 0 1Meg",
            "JFET vcc input source_j JGEN",
            "RSOURCE source_j 0 2.2k",
            "COUT source_j bufferout 10n",
            f"R_DUMMY bufferout 0 {load}",
            f".model JGEN NJF(BETA={beta:.14g} VTO={vto} LAMBDA=0.02 CGS=5p CGD=2p RD=20 RS=20)",
        ]
    else:
        gain=parameter
        components=[
            "RBIAS_TOP vcc input 22k",
            "RBIAS_BOTTOM input 0 10k",
            "QBJT vcc input emitter QGEN",
            "REMITTER emitter 0 2.2k",
            "COUT emitter bufferout 10n",
            f"R_DUMMY bufferout 0 {load}",
            f".model QGEN NPN(Is=1e-14 Bf={gain} Vaf=100 Cje=5p Cjc=1p Tf=0.3n Tr=20n)",
        ]
    return "\n".join(prefix+components+[
        ".control","set wr_singlescale",
        f"ac lin 2 {FREQUENCY} {FREQUENCY+1}",
        "wrdata transfer.dat vm(out) vm(bufferout) vm(input)",
        "quit",".endc",".end",""
    ])

def native_case(folder,device,parameter,load,cp):
    file=folder/"shared.cir"
    file.write_text(circuit(device,parameter,load,cp),encoding="utf-8")
    log=folder/"native.log"
    proc=subprocess.run(["ngspice","-b","-o",str(log),str(file)],
                        cwd=folder,capture_output=True,text=True)
    proc.check_returncode()
    output=log.read_text(encoding="utf-8",errors="replace")
    assert "Error:" not in output and "fatal" not in output.lower(),output[-1500:]
    data=folder/"transfer.dat"
    assert data.is_file(),(device,parameter,load,cp)
    rows=[tuple(map(float,line.split())) for line in data.read_text().splitlines() if line.strip()]
    assert 1<=len(rows)<=2 and all(len(x)==4 and all(math.isfinite(v) for v in x) for x in rows)
    freq,tankout,bufferout,inputvoltage=rows[0]
    assert abs(freq-FREQUENCY)<1
    assert 0<tankout<3 and 0<bufferout<10 and inputvoltage>0,(
        device,parameter,load,cp,rows[0])
    return tankout,bufferout,inputvoltage

def main():
    jsch=J113_SCH.read_text(encoding="utf-8")
    bsch=KSP10_SCH.read_text(encoding="utf-8")
    assert "ONSEMI_J113_TO92_1D_2S_3G_ONLY_CANDIDATE" in jsch
    assert "ONSEMI_KSP10BU_TO92_CANDIDATE" in bsch
    assert "2k2_SOURCE_SELF_BIAS_DRAFT" in jsch
    assert "2k2_EMITTER_SET_DRAFT" in bsch
    parameters={
        "J113":tuple((vto,idss) for vto in VTO for idss in IDSS),
        "KSP10":tuple(BETAS),
    }
    assert len(parameters["J113"])==6 and len(parameters["KSP10"])==3
    outcomes={}
    with tempfile.TemporaryDirectory(prefix="tht_j113_ksp10_common_tank_") as tmp:
        root=Path(tmp)
        jnets=exported_nets(J113_SCH,root/"j113.net")
        bnets=exported_nets(KSP10_SCH,root/"ksp10.net")
        tnets=exported_nets(TANK,root/"tank.net")
        require(jnets,"JFET_GATE",("Q1801","3"),("C1801","2"))
        require(jnets,"JFET_SOURCE",("Q1801","2"),("C1802","1"))
        require(jnets,"VLAB6_JFET_ONLY",("Q1801","1"))
        require(bnets,"IFBUF_BASE_BIAS",("Q1701","1"),("C1701","2"))
        require(bnets,"IFBUF_EMITTER",("Q1701","2"),("C1702","1"))
        require(bnets,"VLAB6_IFBUF_ONLY",("Q1701","3"))
        require(tnets,"IF455_SOURCE",("J1601","1"),("C1601","1"))
        require(tnets,"IF455_TANK",("C1601","2"),("L1601","1"))
        for dev in ("J113","KSP10"):
            for parameter in parameters[dev]:
                for cp in COUPLINGS_PF:
                    for load in LOADS:
                        folder=root/f"case{len(outcomes):02}"
                        folder.mkdir()
                        tank,output,drive=native_case(folder,dev,parameter,load,cp)
                        outcomes[dev,parameter,cp,load]=(tank,output,drive)
                        print("IF455_COMMON_TANK_NATIVE_COMPARISON",{
                            "device_generic":dev,
                            "JFET_VTO_Idss_or_BJT_beta":parameter,
                            "input_coupling_pF":cp,
                            "same_resistive_filter_dummy_ohm":load,
                            "same_generator_V_AC":1,
                            "same_source_R_ohm":50,
                            "same_rail_V_DC":6,
                            "tank_out_VperV":round(tank,9),
                            "buffer_out_VperV":round(output,9),
                            "buffer_out_over_tank_out":round(output/tank,9),
                            "device_input_magnitude_V":round(drive,9),
                            "manufacturer_device_model":False,
                            "ceramic_complex_impedance_modeled":False},flush=True)
        assert len(outcomes)==CASES,(len(outcomes),CASES)
        # Independent historical anchor: exactly replicate the J113 10p
        # IF455 tank-to-follower 2k load at its previously tested corner.
        old=outcomes["J113",(-3.0,0.002),10,2000][1]
        assert abs(old-0.261831624)<1e-6,("J113 prior native baseline drift",old)
        for dev in ("J113","KSP10"):
            for parameter in parameters[dev]:
                for cp in COUPLINGS_PF:
                    reference=outcomes[dev,parameter,cp,100000][1]
                    for load in (2000,1500):
                        relative=outcomes[dev,parameter,cp,load][1]/reference
                        assert 0<relative<1.01 and math.isfinite(relative)
                        print("IF455_COMMON_TANK_LOAD_RELATIVE_TO_100K",{
                            "device_generic":dev,"corner":parameter,
                            "coupling_pF":cp,"resistive_input_ohm":load,
                            "voltage_ratio_loaded_to_100k":round(relative,9)},flush=True)
        for beta in BETAS:
            # KSP10's real candidate couples via 10nF, unlike J113's 10pF:
            # quantify loading of the *same* source tank by Cinput.
            for load in LOADS:
                r10p=outcomes["KSP10",beta,10,load]
                r10n=outcomes["KSP10",beta,10000,load]
                assert all(math.isfinite(x) for x in r10p+r10n)
                print("IF455_KSP10_COUPLING_CHANGES_TANK",{
                    "beta":beta,"load":load,
                    "tank_out_at_10p":round(r10p[0],9),
                    "tank_out_at_10n":round(r10n[0],9),
                    "tank_voltage_10n_over_10p":round(r10n[0]/r10p[0],9)},flush=True)
    print("PASS_NATIVE_KICAD9_IF455_SHARED_TANK_54_NGSPICE_J113_KSP10_COUPLING_LOAD_CORNERS_NO_OEM_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
