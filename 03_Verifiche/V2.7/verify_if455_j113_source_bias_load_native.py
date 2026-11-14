#!/usr/bin/env python3
"""THT onsemi J113 existing bench: source resistor sensitivity under 1.5/2k.

36 native ngspice AC runs with 3 resistor trials x 3 generic VTO x 2
illustrative Idss x 2 resistor-only ceramic input loads.
Models reuse the previous 6V generic NJF, unchanged native KiCad9 J113
pin1 D/pin2 S/pin3 G and IF455 tank; NO OEM J113 simulation or noise,
distortion, large-signal, input/output matching, or PCB qualification.
"""
from pathlib import Path
import math
import subprocess
import tempfile

from verify_interboard_audio_contract_native import exported_nets,require
from verify_if455_two_port_source_impedance_native import TANK
from verify_if455_j113_ceramic_load_native import (
    SCH,spice_deck,VTO,IDSS,N
)

R_SOURCE=(680,1000,2200)
LOAD=(2000,1500)
F=455000

def native_ac(folder,vto,idss,load,rs):
    source=spice_deck(vto,idss,load)
    marker="R1802 source_j 0 2.2k"
    assert source.count(marker)==1,"Prior native model changed"
    source=source.replace(marker,f"R1802 source_j 0 {rs}")
    path=folder/"screen.cir"
    path.write_text(source,encoding="utf-8")
    out=subprocess.run(["ngspice","-b","-o",str(folder/"native.log"),str(path)],
                       cwd=folder,capture_output=True,text=True)
    out.check_returncode()
    log=(folder/"native.log").read_text(encoding="utf-8",errors="replace")
    assert "Error:" not in log and "fatal" not in log.lower(),log[-1500:]
    file=folder/"results.dat"
    assert file.is_file(),(vto,idss,load,rs)
    data=[tuple(map(float,x.split())) for x in file.read_text().splitlines() if x.strip()]
    assert len(data)==N and all(len(x)==3 and all(math.isfinite(t) for t in x) for x in data)
    assert abs(data[0][0]-445000)<1
    assert abs(data[N//2][0]-F)<1
    assert abs(data[-1][0]-465000)<1
    assert data[N//2][1]>0 and data[N//2][2]>0
    return data

def main():
    sch=SCH.read_text(encoding="utf-8")
    assert "2k2_SOURCE_SELF_BIAS_DRAFT" in sch
    assert "ONSEMI_J113_TO92_1D_2S_3G_ONLY_CANDIDATE" in sch
    results={}
    with tempfile.TemporaryDirectory(prefix="tht_j113_source_bias_load_") as tmp:
        root=Path(tmp)
        native=exported_nets(SCH,root/"j113.net")
        tank=exported_nets(TANK,root/"tank.net")
        require(native,"JFET_GATE",("Q1801","3"),("C1801","2"),("R1801","1"))
        require(native,"JFET_SOURCE",("Q1801","2"),("R1802","1"),("C1802","1"))
        require(native,"VLAB6_JFET_ONLY",("Q1801","1"),("J1803","1"))
        require(native,"JFET_AC_OUT",("C1802","2"),("J1802","1"),("R1803","1"))
        require(tank,"IF455_SOURCE",("J1601","1"),("C1601","1"))
        assert "FB455_11070_UNQUALIFIED" not in sch
        for rs in R_SOURCE:
            for vto in VTO:
                for idss in IDSS:
                    for load in LOAD:
                        dest=root/f"rs{rs}_v{abs(vto)}_i{idss}_z{load}"
                        dest.mkdir()
                        data=native_ac(dest,vto,idss,load,rs)
                        _,tankv,buffer=data[N//2]
                        transfer=buffer/tankv
                        assert 0<transfer<2.5,(rs,vto,idss,load,transfer)
                        results[(rs,vto,idss,load)]=(tankv,buffer)
                        print("J113_GENERIC_SOURCE_BIAS_LOAD_NGSPICE",{
                            "trial_source_R_ohm":rs,"generic_VTO_V":vto,
                            "generic_Idss_A":idss,"dummy_filter_input_R_ohm":load,
                            "tank_per_1V_at_455":round(tankv,9),
                            "buffer_per_1V_at_455":round(buffer,9),
                            "buffer_over_tank_at_455":round(transfer,9),
                            "relative_445_to_455":round(data[0][2]/buffer,7),
                            "relative_465_to_455":round(data[-1][2]/buffer,7),
                            "measured_DC_bias":False,"OEM_J113_model":False},flush=True)
        assert len(results)==36
        # Match the independently CI-proven original Rs=2.2k, worst corner.
        worst=results[(2200,-3.0,0.002,2000)][1]
        assert abs(worst-0.261831624)<1e-6,("original J113 baseline changed",worst)
        for vto in VTO:
            for idss in IDSS:
                for load in LOAD:
                    base=results[(2200,vto,idss,load)][1]
                    for rs in (680,1000):
                        ratio=results[(rs,vto,idss,load)][1]/base
                        assert math.isfinite(ratio) and ratio>0
                        print("J113_GENERIC_SOURCE_RESISTOR_RELATIVE_TO_NATIVE_2200",{
                            "VTO_V":vto,"Idss_A":idss,"dummy_input_ohm":load,
                            "source_resistor_trial_ohm":rs,
                            "Vout_455_ratio_vs_2k2":round(ratio,9),
                            "actual_noise_and_intermodulation_verified":False},flush=True)
    print("PASS_NATIVE_KICAD9_J113_36_SOURCE_RESISTOR_CERAMIC_DUMMY_AC_CORNERS_NOT_OEM_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
