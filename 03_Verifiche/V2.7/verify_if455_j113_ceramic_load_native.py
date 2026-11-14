#!/usr/bin/env python3
"""Small-signal AC stress of existing native onsemi-J113 IF455 bench follower.

Uses explicit 6V bias and a GENERIC ngspice NJF (NOT vendor compact model).
J113 gate/lead pin contract is protected by native KiCad9 netlist export.
18 AC sweeps: generic VTO -0.5/-1.5/-3V x assumed Idss 2/10mA x
100k/2k/1.5k downstream effective load. Real 2k/1.5k ceramic input
Z(f), manufacturer output termination, noise, IMD, and LO-driven
mixer impedance are NOT represented. No hardware/PCB modification.
"""
from pathlib import Path
import math
import subprocess
import tempfile
from verify_interboard_audio_contract_native import exported_nets, require
from verify_if455_two_port_source_impedance_native import TANK

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"04_KiCad/V2.7_DRAFT/IF455_J113_SOURCE_FOLLOWER"
SCH=BASE/"IF455_J113_SOURCE_FOLLOWER_THT_V2_7_DRAFT.kicad_sch"
VTO=(-0.5,-1.5,-3.0)
IDSS=(0.002,0.010)
LOAD=(100000,2000,1500)
FREQ=(445000,455000,465000)
N=81

def spice_deck(vto,idss,load):
    beta=idss/(vto*vto)
    return "\n".join([
        "* J113 GENERIC NJF 6V bench bias; load is resistor, NOT ceramic",
        "V_SIGNAL src 0 DC 0 AC 1",
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
        "C1801 out gate 10p",
        "R1801 gate 0 1Meg",
        "JQ1801 vcc gate source_j JGEN",
        "R1802 source_j 0 2.2k",
        "C1802 source_j bufferout 10n",
        f"R_FILTER_INPUT_DUMMY bufferout 0 {load}",
        f".model JGEN NJF(BETA={beta:.14g} VTO={vto} LAMBDA=0.02 CGS=5p CGD=2p RD=20 RS=20)",
        ".control", "set wr_singlescale",
        f"ac lin {N} 445000 465000",
        "wrdata results.dat vm(out) vm(bufferout)",
        "quit",".endc",".end",""
    ])

def ngspice_ac(folder,vto,idss,load):
    path=folder/"j113.cir"
    path.write_text(spice_deck(vto,idss,load),encoding="utf-8")
    p=subprocess.run(["ngspice","-b","-o",str(folder/"log.txt"),str(path)],
                     cwd=folder,text=True,capture_output=True)
    p.check_returncode()
    log=(folder/"log.txt").read_text(encoding="utf-8",errors="replace")
    assert "Error:" not in log and "fatal" not in log.lower(),log[-1600:]
    data=folder/"results.dat"
    assert data.is_file(),(vto,idss,load)
    rows=[tuple(map(float,line.split())) for line in data.read_text().splitlines() if line.strip()]
    assert len(rows)==N,(len(rows),vto,idss,load)
    assert all(len(row)==3 and all(math.isfinite(x) for x in row) for row in rows)
    for i,freq in ((0,445000),(N//2,455000),(N-1,465000)):
        assert abs(rows[i][0]-freq)<1,(i,rows[i],freq)
    return rows

def main():
    sch=SCH.read_text(encoding="utf-8")
    assert 'ONSEMI_J113_TO92_1D_2S_3G_ONLY_CANDIDATE' in sch
    assert '2k2_SOURCE_SELF_BIAS_DRAFT' in sch
    with tempfile.TemporaryDirectory(prefix="tht_j113_fb455_load_") as tmp:
        root=Path(tmp)
        native=exported_nets(SCH,root/"j113.net")
        tank=exported_nets(TANK,root/"tank.net")
        require(native,"JFET_GATE",("Q1801","3"),("C1801","2"),("R1801","1"))
        require(native,"JFET_SOURCE",("Q1801","2"),("R1802","1"),("C1802","1"))
        require(native,"VLAB6_JFET_ONLY",("Q1801","1"),("J1803","1"))
        require(native,"JFET_AC_OUT",("C1802","2"),("J1802","1"),("R1803","1"))
        require(tank,"IF455_SOURCE",("J1601","1"),("C1601","1"))
        assert "FB455_11070_UNQUALIFIED" not in sch
        results={}
        for vto in VTO:
            for idss in IDSS:
                for load in LOAD:
                    folder=root/f"v{abs(vto)}_i{idss}_load{load}"
                    folder.mkdir()
                    points=ngspice_ac(folder,vto,idss,load)
                    f,pre,post=points[N//2]
                    assert pre>0 and post>0 and math.isfinite(post/pre)
                    assert post<10,("suspect unstable ideal model",vto,idss,load,post)
                    record={"generic_VTO_V":vto,
                            "generic_Idss_A":idss,
                            "resistive_output_load_ohm":load,
                            "tank_out_per_1V_source_at_455":round(pre,9),
                            "buffer_out_per_1V_source_at_455":round(post,9),
                            "buffer_out_over_tank_out_at_455":round(post/pre,9),
                            "minus_10k_output_ratio_to_455":round(points[0][2]/post,8),
                            "plus_10k_output_ratio_to_455":round(points[-1][2]/post,8),
                            "ceramic_filter_frequency_response_modeled":False,
                            "actual_J113_vendor_model_used":False}
                    print("IF455_J113_GENERIC_CERAMIC_LOAD_AC",record,flush=True)
                    results[(vto,idss,load)]=(pre,post)
        assert len(results)==18
        for vto in VTO:
            for idss in IDSS:
                baseline=results[vto,idss,100000][1]
                for load in (2000,1500):
                    ratio=results[vto,idss,load][1]/baseline
                    assert ratio>0 and math.isfinite(ratio)
                    print("J113_GENERIC_LOADED_OVER_BENCH_100K",{
                        "VTO_V":vto,"Idss_A":idss,"load_ohm":load,
                        "relative_Vout_at_455":round(ratio,9)},flush=True)
    print("PASS_NATIVE_KICAD9_J113_18_NGSPICE_455K_CERAMIC_RESISTIVE_LOAD_CORNERS_GENERIC_NO_OEM_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
