#!/usr/bin/env python3
"""Two physical THT anti-series stages, each with 2 × Zener 1N4106-1.

Native KiCad9 pin contract plus SYNTHETIC gate clamp stress domain, not
vendor I/V, life-time, thermal, EMI, certification or real fail-OFF.
"""
import itertools
from pathlib import Path
import re
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets,require
from verify_two_complete_pmos_stages_native import SCH,EXPECTED
from verify_q806_dual_zener_clamp_native import solution

STAGES=(
  ("A","FLOATING_COMMON_SOURCE_LAB","COMMON_GATE_LAB",
    ("D2101","D2102"),"R2101","R2102"),
  ("B","FLOATING_SOURCE_B_LAB","COMMON_GATE_B_LAB",
    ("D2111","D2112"),"R2111","R2112"),
)
def properties(text,ref):
    m=re.search(r'\(property "Reference" "'+re.escape(ref)+r'"',text)
    assert m,ref
    sub=text[m.end():m.end()+480]
    value=re.search(r'\(property "Value" "([^"]+)"',sub)
    foot=re.search(r'\(property "Footprint" "([^"]+)"',sub)
    assert value and foot,ref
    return value.group(1),foot.group(1)

def main():
    raw=SCH.read_text(encoding="utf8")
    with tempfile.TemporaryDirectory(prefix="two_stage_zener_clamp_") as td:
        nets=exported_nets(SCH,Path(td)/"clamps.net")
    assert set(nets)==set(EXPECTED)
    for k,v in EXPECTED.items():
        require(nets,k,*v)
        assert nets[k]==v
    assert sum(map(len,nets.values()))==54 and len(nets)==14
    for st,source,gate,diodes,rgs,rseries in STAGES:
        assert { (d,"1") for d in diodes}|{(rgs,"1")}<=nets[source],st
        assert { (d,"2") for d in diodes}|{(rgs,"2"),(rseries,"2")}<=nets[gate],st
        for d in diodes:
            val,foot=properties(raw,d)
            assert val.startswith("1N4106-1_") and foot=="Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal",(d,val,foot)
        assert properties(raw,rgs)[0].startswith("47k_")
        assert properties(raw,rseries)[0].startswith("10k_")
    assert nets[STAGES[0][1]].isdisjoint(nets[STAGES[1][1]])
    assert nets[STAGES[0][2]].isdisjoint(nets[STAGES[1][2]])

    total=0
    per_stage={}
    for st,source,gate,diodes,rgs,rseries in STAGES:
        one_open_over20=0
        both_open_over20=0
        less_than_250uA=0
        clamp_missing_knee=0
        maximum_single=0.
        maximum_double=0.
        for vs,rgs_ohm,rg_ohm,vz,rz,mode in itertools.product(
             (0.,13.8,20.,24.,36.,48.),
             (44650.,47000.,49350.),
             (9500.,10000.,10500.),
             (11.,12.,13.),
             (.1,1.,10.),
             ("BOTH_PRESENT","FIRST_OPEN","SECOND_OPEN","BOTH_OPEN")):
            active={"BOTH_PRESENT":2,"FIRST_OPEN":1,"SECOND_OPEN":1,"BOTH_OPEN":0}[mode]
            drop=solution(vs,rgs_ohm,rg_ohm,vz,rz,active)
            assert 0<=drop<=vs+1e-9
            if active==1:
                maximum_single=max(maximum_single,drop)
                one_open_over20+=drop>20.0
            if active==0:
                maximum_double=max(maximum_double,drop)
                both_open_over20+=drop>20.0
            # 1N4106-1 nominal 250 uA Zener TEST current is not a
            # guaranteed full I-V curve over these synthetic corners.
            if active:
                available=max(0.,(vs-vz)/rg_ohm-vz/rgs_ohm)
                less_than_250uA+=available/active<0.000250
                clamp_missing_knee+=vs*rgs_ohm/(rg_ohm+rgs_ohm)<=vz
            total+=1
        assert one_open_over20==0 and both_open_over20>0
        assert less_than_250uA>0 and clamp_missing_knee>0
        assert maximum_double>20.0 and maximum_single<20.0
        per_stage[st]={"synthetic_cases":1944,
                       "single_zener_open_over_abs20V_cases_ideal":one_open_over20,
                       "both_zener_open_over_abs20V_cases_ideal":both_open_over20,
                       "synthetic_per_diode_below_250uA_test_current_cases":less_than_250uA,
                       "below_synthetic_knee_cases":clamp_missing_knee,
                       "single_open_max_absVgs_ideal_V":round(maximum_single,6),
                       "both_open_max_absVgs_ideal_V":round(maximum_double,6)}
    assert total==3888 and per_stage["A"]==per_stage["B"]
    print("TWO_PMOS_COMPLETE_STAGES_TWIN_ZENER_ISOLATED_BOUNDS",{
        "native_components":24,"native_pins":54,"native_nets":14,
        "synthetic_total":total,"per_stage":per_stage,
        "oem_1N4106_IV_curve_across_PVT_verified":False,
        "parallel_current_sharing_qualified":False,
        "maximum_real_Vgs_and_driver_supply_qualified":False,
        "48V_hardware_authorized":False,
        "single_gate_Zener_OPEN_OEM_protection_qualified":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True},flush=True)
    print("PASS_NATIVE_KICAD9_TWO_STAGE_TWIN_ZENER_54PIN_14NET_3888_SYNTHETIC_NONFAB",flush=True)
if __name__=="__main__":main()
