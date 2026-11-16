#!/usr/bin/env python3
"""Native KiCad9 twin-THT-Zener Q806 lab pin nets and theoretical single OPEN.
Neither two redundant parts nor these static models qualify safety or VIN48.
"""
from pathlib import Path
import itertools
import math
import subprocess
import tempfile
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets,require
SCH=ROOT/"04_KiCad/V2.7_DRAFT/MAIN_SECONDARY_OVP_Q804_Q805_Q806_DUAL_ZENER/MAIN_SECONDARY_OVP_Q804_Q805_Q806_DUAL_ZENER_LAB_V2_7_DRAFT.kicad_sch"
N={
 "PRIMARY_IN_DRAIN_LAB":{("J2101","1"),("Q804","2")},
 "FLOATING_COMMON_SOURCE_LAB":{("Q804","3"),("Q805","3"),("D2101","1"),("D2102","1"),("R2101","1")},
 "COMMON_GATE_LAB":{("Q804","1"),("Q805","1"),("D2101","2"),("D2102","2"),("R2101","2"),("R2102","2")},
 "SECONDARY_OUT_DRAIN_LAB":{("J2102","1"),("Q805","2")},
 "DRIVER_SINK_LAB":{("R2102","1"),("Q806","3")},
 "ENABLE_LOGIC_5V_LAB":{("J2103","1"),("R2103","1")},
 "Q806_BASE_LAB":{("Q806","2"),("R2103","2"),("R2104","1")},
 "LAB_RETURN_ONLY":{("J2101","2"),("J2102","2"),("J2103","2"),("Q806","1"),("R2104","2")}
}

def solution(vs,rgs,rg,vz,rz,available):
    # Synthetic equal Zener knee for both components, no OEM I/V.
    if available==0:return vs*rgs/(rgs+rg)
    def f(v):
        return (vs-v)/rg-v/rgs-available*max(0.0,(v-vz)/rz)
    low,high=0.0,vs
    for _ in range(80):
        mid=(low+high)/2
        if f(mid)>0:low=mid
        else:high=mid
    v=(low+high)/2
    assert abs(f(v))<1e-10
    return v

def main():
    s=SCH.read_text(encoding="utf-8")
    assert s.count('(symbol (lib_id "LAB_OVP:')==12
    assert "D2102" in s and "NO FAB / NO TX / NO BATTERIA / NO VEICOLO" in s
    with tempfile.TemporaryDirectory(prefix="dual_zener_lab_") as t:
        p=Path(t)
        erc=p/"dual.erc"
        result=subprocess.run(["kicad-cli","sch","erc","--exit-code-violations",
                               "-o",str(erc),str(SCH)],
                              capture_output=True,text=True,cwd=ROOT)
        print("TWIN_ZENER_NATIVE_ERC",result.stdout,result.stderr,flush=True)
        if erc.exists():print(erc.read_text(encoding="utf-8"),flush=True)
        result.check_returncode()
        nets=exported_nets(SCH,p/"dual.net")
    assert set(nets)==set(N)
    for name,members in N.items():
        require(nets,name,*members)
        assert nets[name]==members,(name,sorted(nets[name]))
    allpins=[p for nodes in nets.values() for p in nodes]
    assert len(allpins)==len(set(allpins))==27 and len(nets)==8
    assert not (nets["LAB_RETURN_ONLY"]&nets["FLOATING_COMMON_SOURCE_LAB"])
    over_open_one=0
    over_double_open=0
    cases=0
    maximum_single=0.0
    maximum_double=0.0
    for vs,rgs,rg,vz,rz,mode in itertools.product(
        (0.,13.8,20.,24.,36.,48.),
        (44650.,47000.,49350.),
        (9500.,10000.,10500.),
        (11.,12.,13.),
        (.1,1.,10.),
        ("HEALTHY","D2101_OPEN","D2102_OPEN","BOTH_OPEN")
    ):
        active={"HEALTHY":2,"D2101_OPEN":1,"D2102_OPEN":1,"BOTH_OPEN":0}[mode]
        v=solution(vs,rgs,rg,vz,rz,active)
        vnom=vs*rgs/(rgs+rg)
        if active:
            closed_form=((vs/rg)+active*vz/rz)/(1/rg+1/rgs+active/rz) if vnom>vz else vnom
        else:
            closed_form=vnom
        assert math.isclose(v,closed_form,rel_tol=1e-10,abs_tol=1e-10)
        if active==1:
            maximum_single=max(maximum_single,v)
            if v>20.:over_open_one+=1
        if active==0:
            maximum_double=max(maximum_double,v)
            if v>20.:over_double_open+=1
        cases+=1
    assert cases==6*3**4*4==1944
    # NO generic guarantee: only the selected synthetic domain bounds this.
    assert maximum_single<20 and over_open_one==0
    assert maximum_double>20 and over_double_open>0
    print("Q806_TWIN_ZENER_IDEAL_STRESS",{
        "cases":cases,"native_pins":27,"native_nets":8,
        "one_zener_open_max_VGS_abs_V":round(maximum_single,6),
        "one_open_over_20V_cases":over_open_one,
        "both_open_max_VGS_abs_V":round(maximum_double,6),
        "both_open_over_20V_cases":over_double_open,
        "shared_mechanical_electrical_faults_qualified":False,
        "OEM_zener_current_sharing_verified":False,
        "driver_CE_short_failclosed":False,
        "48V_input_allowed":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_NATIVE_KICAD9_Q806_TWIN_ZENER_27PIN_8NET_1944_IDEAL_FAULT_CASES_NONFAB",flush=True)

if __name__=="__main__":main()
