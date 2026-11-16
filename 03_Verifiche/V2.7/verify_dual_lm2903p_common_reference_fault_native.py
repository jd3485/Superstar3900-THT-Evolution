#!/usr/bin/env python3
"""Native THT dual LM2903P common VREF fault: shared source invalidates redundancy.

The dual-comparator and both resistor networks are physically present
in KiCad9. VREF values 0,1.25,5 are hypothetical faults, NOT qualified
reference behavior; no OEM comparator output IV/offset modeled.
"""
from pathlib import Path
import itertools
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets,require
from verify_dual_lm2903p_window_native import SCH,NET

VIN=(0.,6.,7.,8.,10.,13.8,16.,20.,24.,30.,48.)
VREF=(0.,1.25,2.475,2.5,2.525,5.)

def main():
    with tempfile.TemporaryDirectory(prefix="dual_common_ref_native_") as d:
        nets=exported_nets(SCH,Path(d)/"ref.net")
    assert len(nets)==13 and set(nets)==set(NET)
    for name,pins in NET.items():
        require(nets,name,*pins)
        assert nets[name]==pins,(name,sorted(nets[name]))
    assert sum(map(len,nets.values()))==58
    for end in (("R2203","1"),("R2205","1"),("R2214","1"),("R2216","1"),("J2203","1")):
        assert end in nets["EXTERNAL_VREF_2V5_UNQUALIFIED"],end
    for end in (("U2201","8"),("U2202","8"),("J2202","1"),("R2207","1")):
        assert end in nets["EXTERNAL_5V_UNQUALIFIED"],end
    for end in (("U2201","1"),("U2201","7"),("U2202","1"),("U2202","7"),("R2207","2")):
        assert end in nets["WINDOW_GOOD_OC_BIASED_LAB"],end

    tested=0
    unsafe_false_good=0
    nominal_scenario_good=0
    false_good_vref_1v25=0
    false_good_vref_5v=0
    for mask,vref,vin in itertools.product(range(256),VREF,VIN):
        vals=[1.01 if mask&(1<<i) else .99 for i in range(8)]
        rt1,rt2,rb1,rb2,oh,ol,uh,ul=vals
        rlow1,rlow2=10000.*rb1,10000.*rb2
        rlow=rlow1*rlow2/(rlow1+rlow2)
        div=rlow/(100000.*rt1+100000.*rt2+rlow)
        sense=vin*div
        uv=vref*20000.*ul/(185000.*uh+20000.*ul)
        ov=vref*20000.*ol/(116000.*oh+20000.*ol)
        # BOTH sensed channels share this SAME reference rail.
        # Two comparator output channels cannot veto correlated
        # false-GOOD when their shared reference is wrong.
        both_good=(uv<sense<ov)
        if vin==13.8 and vref==2.5 and both_good:nominal_scenario_good+=1
        if (vin<9. or vin>16.) and both_good:
            unsafe_false_good+=1
            if vref==1.25:false_good_vref_1v25+=1
            if vref==5.:false_good_vref_5v+=1
        tested+=1
    assert tested==256*len(VIN)*len(VREF)==16896
    assert nominal_scenario_good==256
    assert unsafe_false_good==1028
    assert false_good_vref_1v25==512
    assert false_good_vref_5v==516
    print("DUAL_LM2903P_THT_NATIVE_COMMON_REFERENCE_LOSS",{
        "native_pins":58,"native_nets":13,
        "source_vref_shared_by_both_channels":True,
        "case_count":tested,"healthy_good_cases_at_13v8_ref2v5":nominal_scenario_good,
        "false_good_outside_nominal_9_to_16V_cases":unsafe_false_good,
        "false_good_at_VREF1v25_cases":false_good_vref_1v25,
        "false_good_at_VREF5v_cases":false_good_vref_5v,
        "common_ground_failure_qualified":False,
        "VREF_output_fault_behavior_OEM_qualified":False,
        "external_5V_supply_implemented":False,
        "independent_series_switch_implemented":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_NATIVE_KICAD9_DUAL_LM2903P_COMMON_VREF_58PIN_13NET_16896_NONFAB",flush=True)
if __name__=="__main__":main()
