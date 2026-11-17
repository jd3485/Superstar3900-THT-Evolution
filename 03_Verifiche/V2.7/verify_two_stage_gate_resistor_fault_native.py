#!/usr/bin/env python3
"""Two-stage KiCad9-native gate resistors: synthetic OPEN/SHORT combinations.

The only fault-envelope here assumes BOTH gate Zeners OPEN, a conservative
ideal voltage stress case, not a physical prediction of Zener behavior.
Gate floating, hard shorts and transistor/device physics are NOT solved.
"""
import itertools
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets,require
from verify_two_complete_pmos_stages_native import SCH,EXPECTED
from verify_two_stage_twin_zener_single_open_native import STAGES,properties

def corner(vs,rgs,rsink,pull_state,sink_state,driver):
    """Return (state, |Vgs|, Rgs W, Rsink W) for ideal DC assumptions."""
    if driver=="SINK" and pull_state=="SHORT" and sink_state=="SHORT":
        return ("HARD_SOURCE_TO_RETURN_SHORT",None,None,None)
    if pull_state=="OPEN" and (sink_state=="OPEN" or driver=="OFF"):
        return ("FLOATING_GATE_UNKNOWN",None,None,None)
    if driver=="OFF" or sink_state=="OPEN" or pull_state=="SHORT":
        drop=0.
    elif pull_state=="OPEN" or sink_state=="SHORT":
        drop=vs
    else:
        drop=vs*rgs/(rgs+rsink)
    p_pull=drop*drop/rgs if pull_state=="NOM" else 0.
    p_sink=(vs-drop)**2/rsink if driver=="SINK" and sink_state=="NOM" else 0.
    return ("DEFINED_IDEAL_DC",drop,p_pull,p_sink)

def main():
    sch=SCH.read_text(encoding="utf8")
    with tempfile.TemporaryDirectory(prefix="two_stage_gate_resistor_fault_") as d:
        nets=exported_nets(SCH,Path(d)/"gate_resistor.net")
    assert set(nets)==set(EXPECTED)
    for name,pins in EXPECTED.items():
        require(nets,name,*pins)
        assert nets[name]==pins
    assert len(nets)==14 and sum(map(len,nets.values()))==54
    results={}
    drivers={"A":("Q806","DRIVER_SINK_LAB"),"B":("Q816","DRIVER_SINK_B_LAB")}
    for stage,source,gate,diodes,pull,sink in STAGES:
        q,sinknet=drivers[stage]
        assert {(pull,"1")} <= nets[source]
        assert {(pull,"2"),(sink,"2")} <= nets[gate]
        assert {(sink,"1"),(q,"3")} <= nets[sinknet]
        assert {(d,"1") for d in diodes} <= nets[source]
        assert {(d,"2") for d in diodes} <= nets[gate]
        assert properties(sch,pull)[0].startswith("47k_")
        assert properties(sch,sink)[0].startswith("10k_")
        for diode in diodes:
            val,foot=properties(sch,diode)
            assert val.startswith("1N4106-1_")
            assert foot=="Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal"
        n=0
        floating=0
        hard_shorts=0
        over20=0
        max_vgs=0.
        max_pull_w=0.
        max_sink_w=0.
        for vs,rgs,rsink,pull_state,sink_state,driver in itertools.product(
            (0.,13.8,20.,24.,36.,48.),
            (44650.,47000.,49350.),
            (9500.,10000.,10500.),
            ("NOM","OPEN","SHORT"),
            ("NOM","OPEN","SHORT"),
            ("OFF","SINK")):
            state,drop,p_pull,p_sink=corner(
                vs,rgs,rsink,pull_state,sink_state,driver)
            floating+=state=="FLOATING_GATE_UNKNOWN"
            hard_shorts+=state=="HARD_SOURCE_TO_RETURN_SHORT"
            if state=="DEFINED_IDEAL_DC":
                assert 0.<=drop<=vs+1e-12
                over20+=drop>20.
                max_vgs=max(max_vgs,drop)
                max_pull_w=max(max_pull_w,p_pull)
                max_sink_w=max(max_sink_w,p_sink)
            else:
                assert drop is None and p_pull is None and p_sink is None
            n+=1
        assert n==972
        assert (floating,hard_shorts,over20)==(216,54,100)
        assert max_vgs==48.
        assert abs(max_pull_w-(48.**2/44650.))<1e-12
        assert abs(max_sink_w-(48.**2/9500.))<1e-12
        results[stage]={
            "synthetic_cases":n,
            "floating_gate_unknown_states":floating,
            "ideal_hard_source_return_short_states":hard_shorts,
            "defined_static_over_abs20V_states":over20,
            "maximum_ideal_absVgs_V":max_vgs,
            "max_Rgs_static_W":round(max_pull_w,6),
            "max_Rsink_static_W":round(max_sink_w,6)}
    assert results["A"]==results["B"]
    print("TWO_STAGE_THT_GATE_RESISTOR_FAULT_ENVELOPE",{
        "physical_schematic_pins":54,"physical_nets":14,
        "synthetic_total":1944,"per_stage":results,
        "both_zener_open_assumed_not_vendor_verified":True,
        "floating_gate_behavior_qualified":False,
        "hard_short_fuse_energy_and_thermal_qualified":False,
        "48V_hardware_authorized":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True},flush=True)
    print("PASS_NATIVE_TWO_STAGE_THT_GATE_R_OPEN_SHORT_1944_NONFAB",flush=True)

if __name__=="__main__":
    main()
