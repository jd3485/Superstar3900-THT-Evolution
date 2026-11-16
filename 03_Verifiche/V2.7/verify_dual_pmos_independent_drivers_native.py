#!/usr/bin/env python3
"""Native KiCad9 physical split Q804/Q805 gate/driver candidate; NOT safety proof."""
from pathlib import Path
import subprocess
import sys
import tempfile
import itertools

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets, require
from verify_q806_dual_zener_clamp_native import N as BASE

SCH=ROOT/"04_KiCad/V2.7_DRAFT/MAIN_SECONDARY_OVP_DUAL_INDEPENDENT_GATES/MAIN_SECONDARY_OVP_DUAL_INDEPENDENT_GATES_LAB_V2_7_DRAFT.kicad_sch"
NET={key:set(members) for key,members in BASE.items()}
NET["FLOATING_COMMON_SOURCE_LAB"].add(("R2110","1"))
NET["COMMON_GATE_LAB"].difference_update({("Q805","1"),("D2102","2")})
NET["GATE_B_LAB"]={("Q805","1"),("D2102","2"),("R2110","2"),("R2111","2")}
NET["DRIVER_SINK_B_LAB"]={("R2111","1"),("Q807","3")}
NET["ENABLE_B_5V_LAB"]={("J2104","1"),("R2112","1")}
NET["Q807_BASE_LAB"]={("Q807","2"),("R2112","2"),("R2113","1")}
NET["LAB_RETURN_ONLY"].update({("J2104","2"),("Q807","1"),("R2113","2")})
# Additional four new nets and a split gate means 12 total.
def main():
    source=SCH.read_text(encoding="utf8")
    assert source.count('(symbol (lib_id "LAB_OVP:')==18
    assert source.count('"IRF9540NPBF_SECONDARY_UNQUALIFIED"')==2
    assert source.count("KSP42BU_NPN_CANDIDATE")==2
    assert source.count("1N4106-1_")==2
    for ref in ("Q804","Q805","Q806","Q807","R2101","R2110",
                "R2102","R2111","R2103","R2112","R2104","R2113",
                "D2101","D2102","J2101","J2102","J2103","J2104"):
        assert source.count('(property "Reference" "'+ref+'"')==1,ref
    with tempfile.TemporaryDirectory(prefix="split_pmos_gates_") as t:
        erc=Path(t)/"split_pmos.erc"
        result=subprocess.run(["kicad-cli","sch","erc","--exit-code-violations",
                               "-o",str(erc),str(SCH)],cwd=ROOT,
                              capture_output=True,text=True)
        print("SPLIT_PMOS_THT_ERC",result.stdout,result.stderr,flush=True)
        if erc.exists():print(erc.read_text(encoding="utf8"),flush=True)
        result.check_returncode()
        nets=exported_nets(SCH,Path(t)/"split_pmos.net")
    assert set(nets)==set(NET),(set(nets)^set(NET))
    for net,expected in NET.items():
        require(nets,net,*expected)
        assert nets[net]==expected,(net,sorted(nets[net]^expected))
    assert len(nets)==12 and sum(map(len,nets.values()))==40
    assert len(set.union(*nets.values()))==40
    assert nets["GATE_B_LAB"].isdisjoint(nets["COMMON_GATE_LAB"])
    assert nets["DRIVER_SINK_B_LAB"].isdisjoint(nets["DRIVER_SINK_LAB"])
    assert nets["ENABLE_B_5V_LAB"].isdisjoint(nets["ENABLE_LOGIC_5V_LAB"])
    assert nets["Q807_BASE_LAB"].isdisjoint(nets["Q806_BASE_LAB"])
    assert ("Q804","3") in nets["FLOATING_COMMON_SOURCE_LAB"]
    assert ("Q805","3") in nets["FLOATING_COMMON_SOURCE_LAB"]
    assert ("Q804","2") in nets["PRIMARY_IN_DRAIN_LAB"]
    assert ("Q805","2") in nets["SECONDARY_OUT_DRAIN_LAB"]

    # Abstract driver-fault Boolean screen, NOT FET vendor I/V or load current.
    # Independent C-E stuck sinks should not command both PMOS gates in
    # fault-free other channel. TWO faults or common-cause remain unqualified.
    cases=0
    lone_faults=0
    both_on_when_disabled=0
    for enable_a,enable_b,stuck_a,stuck_b in itertools.product((0,1),repeat=4):
        driven_a=bool(enable_a or stuck_a)
        driven_b=bool(enable_b or stuck_b)
        if (not enable_a and not enable_b) and (stuck_a!=stuck_b):
            assert driven_a!=driven_b
            lone_faults+=1
        if (not enable_a and not enable_b) and driven_a and driven_b:
            both_on_when_disabled+=1
        cases+=1
    assert cases==16 and lone_faults==2 and both_on_when_disabled==1
    print("DUAL_PMOS_SPLIT_GATE_THT_TOPOLOGY",{
        "native_parts":18,"native_pins":40,"native_nets":12,
        "isolated_gates_and_bjt_sink_paths":True,
        "boolean_enable_fault_cases":cases,
        "single_driver_short_with_both_enables_off_and_only_one_gate_driven":lone_faults,
        "two_driver_shorts_both_gate_driven":both_on_when_disabled,
        "external_enable_supplies_and_common_source_return_UNQUALIFIED":True,
        "actual_fail_closed_qualified":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_NATIVE_KICAD9_Q804_Q805_SEPARATE_GATES_40PIN_12NET_NONFAB",flush=True)

if __name__=="__main__":main()
