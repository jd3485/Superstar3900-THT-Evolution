#!/usr/bin/env python3
"""KiCad9 native anti-series THT PMOS split-gate twin-clamp *candidate*.

Two Zener candidates per individual gate; screening in a synthetic algebraic
model. NOT proof of OEM clamp behavior, surge/ESD, independence or safety.
"""
from pathlib import Path
import itertools
import sys
import tempfile
import subprocess

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets,require
from verify_dual_pmos_independent_drivers_native import NET as BASE
from verify_q806_dual_zener_clamp_native import solution

SCH=ROOT/"04_KiCad/V2.7_DRAFT/MAIN_SECONDARY_OVP_DUAL_GATES_TWIN_ZENERS/MAIN_SECONDARY_OVP_DUAL_GATES_TWIN_ZENERS_LAB_V2_7_DRAFT.kicad_sch"
NET={key:set(members) for key,members in BASE.items()}
NET["FLOATING_COMMON_SOURCE_LAB"].update({("D2110","1"),("D2111","1")})
NET["COMMON_GATE_LAB"].add(("D2110","2"))
NET["GATE_B_LAB"].add(("D2111","2"))

def main():
    sch=SCH.read_text(encoding="utf-8")
    assert sch.count('(symbol (lib_id "LAB_OVP:')==20
    assert sch.count("KSP42BU_NPN_CANDIDATE")==2
    assert sch.count("1N4106-1_")==4
    for ref in ("D2101","D2102","D2110","D2111"):
        assert sch.count('(property "Reference" "'+ref+'"')==1,ref
        assert f'(reference "{ref}")' in sch,ref
    assert sch.count("Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal")>=4
    assert "NO FAB / NO TX / NO BATTERIA / NO VEICOLO" in sch
    with tempfile.TemporaryDirectory(prefix="dual_gate_twin_zener_native_") as t:
        erc=Path(t)/"twin.erc"
        run=subprocess.run(["kicad-cli","sch","erc","--exit-code-violations",
                            "-o",str(erc),str(SCH)],cwd=ROOT,
                           capture_output=True,text=True)
        print("DUAL_GATE_TWIN_ZENER_ERC",run.stdout,run.stderr,flush=True)
        if erc.exists():print(erc.read_text(encoding="utf8"),flush=True)
        run.check_returncode()
        nets=exported_nets(SCH,Path(t)/"twin.net")
    assert set(nets)==set(NET),(set(nets)^set(NET))
    for name,expected in NET.items():
        require(nets,name,*expected)
        assert nets[name]==expected,(name,sorted(nets[name]^expected))
    assert len(nets)==12 and sum(map(len,nets.values()))==44
    assert len(set.union(*nets.values()))==44
    assert NET["GATE_B_LAB"].isdisjoint(NET["COMMON_GATE_LAB"])
    assert ("Q804","2") in nets["PRIMARY_IN_DRAIN_LAB"]
    assert ("Q805","2") in nets["SECONDARY_OUT_DRAIN_LAB"]
    # Per-gate pair is physically separated from other pair: two
    # independent OPEN faults on same gate are needed to leave no clamp.
    assert {("D2101","2"),("D2110","2")} <= nets["COMMON_GATE_LAB"]
    assert {("D2102","2"),("D2111","2")} <= nets["GATE_B_LAB"]
    for ref in ("D2101","D2110","D2102","D2111"):
        assert (ref,"1") in nets["FLOATING_COMMON_SOURCE_LAB"]

    izt=0.000250 # OEM point specification, not proof of clamp I/V curve
    cases=0
    single_open_ideal_exceeds20=0
    both_open_exceeds20=0
    insufficient_izt_per_healthy_branch=0
    min_gate=1e9
    max_gate=0.
    for vs,rgs,rser,vz,rz,mode in itertools.product(
        (0.,13.8,20.,24.,36.,48.),
        (44650.,47000.,49350.),
        (9500.,10000.,10500.),
        (11.,12.,13.),
        (0.1,1.,10.),
        ("BOTH_PRESENT","FIRST_OPEN","SECOND_OPEN","BOTH_OPEN")
    ):
        count={"BOTH_PRESENT":2,"FIRST_OPEN":1,"SECOND_OPEN":1,"BOTH_OPEN":0}[mode]
        v=solution(vs,rgs,rser,vz,rz,count)
        # A shared source voltage is assumed externally imposed. No actual
        # powered gate/I-V/thermal/driver dynamics are modeled.
        if count==1 and v>20:single_open_ideal_exceeds20+=1
        if count==0 and v>20:both_open_exceeds20+=1
        if count:
            available=max(0.,(vs-vz)/rser-vz/rgs)
            if available/count<izt:insufficient_izt_per_healthy_branch+=1
        min_gate=min(min_gate,v)
        max_gate=max(max_gate,v)
        cases+=1
    assert cases==1944
    assert single_open_ideal_exceeds20==0
    assert both_open_exceeds20>0
    assert insufficient_izt_per_healthy_branch>0
    assert max_gate>20 and min_gate==0
    print("THT_TWIN_ZENER_PER_SPLIT_GATE_NATIVE_BOUNDARY",{
        "THT_parts":20,"native_pins":44,"native_nets":12,
        "hypothetical_current_knee_cases":cases,
        "one_parallel_clamp_open_ideal_VGS_above_20_cases":single_open_ideal_exceeds20,
        "both_clamps_open_ideal_VGS_above_20_cases":both_open_exceeds20,
        "IZT_250uA_not_reached_per_branch_synthetic_cases":insufficient_izt_per_healthy_branch,
        "OEM_full_IV_curve_qualified":False,
        "external_sense_and_two_independent_power_sources_qualified":False,
        "actual_safety_series_cut_qualified":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_NATIVE_KICAD9_DUAL_GATE_TWIN_CLAMPS_44PINS_12NET_1944_NONFAB",flush=True)

if __name__=="__main__":
    main()
