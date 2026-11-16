#!/usr/bin/env python3
"""Independent A/B resistor tolerances: KiCad9 netlist anchored double-VREF fault study.

The earlier 101376-case sweep reused the SAME eight tolerance bits for both
physical channels. This test treats the sixteen real channel resistors as
independently variable. Pure ideal-DC screening, never safety qualification.
"""
from pathlib import Path
import sys
import tempfile

sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets, require
from verify_dual_lm2903p_split_vref_native import SCH,NET,good
from verify_dual_lm2903p_split_vref_double_fault_native import VIN,VREF

def main():
    with tempfile.TemporaryDirectory(prefix="dual_ref_independent_tolerances_") as d:
        nets=exported_nets(SCH,Path(d)/"split_independent.net")
    assert set(nets)==set(NET) and len(nets)==14
    for net,pins in NET.items():
        require(nets,net,*pins)
        assert nets[net]==pins,(net,nets[net])
    assert sum(map(len,nets.values()))==60
    assert ("U2201","8") in nets["EXTERNAL_5V_UNQUALIFIED"]
    assert ("U2202","8") in nets["EXTERNAL_5V_UNQUALIFIED"]
    assert ("J2203","1") in nets["EXTERNAL_VREF_2V5_UNQUALIFIED"]
    assert ("J2205","1") in nets["EXTERNAL_VREF_B_2V5_UNQUALIFIED"]
    assert nets["VIN_SENSE_A"].isdisjoint(nets["VIN_SENSE_B"])
    # Each physical channel owns eight separate resistor values. Counting
    # independently gives 256^2 possibilities, without a 26M nested loop.
    normal=[]
    for mask in range(256):
        normal.append(tuple(1.01 if mask & (1<<i) else .99 for i in range(8)))
    agree={(vin,ref):sum(good(vin,ref,t) for t in normal)
           for vin in VIN for ref in VREF}
    count=len(normal)**2*len(VIN)*len(VREF)**2
    false_good={}
    nominal_good=0
    for vin in VIN:
        for ra in VREF:
            for rb in VREF:
                cases=agree[vin,ra]*agree[vin,rb]
                if (vin<9 or vin>16) and cases:
                    pair=(ra,rb)
                    false_good[pair]=false_good.get(pair,0)+cases
                if vin==13.8 and ra==rb==2.5:
                    nominal_good+=cases
    assert count==25_952_256
    assert nominal_good==65_536
    assert false_good=={(1.25,1.25):131_072,(5.,5.):100_688},false_good
    assert sum(false_good.values())==231_760
    print("DUAL_LM2903P_INDEPENDENT_CHANNEL_TOLERANCES",{
        "native_THT_pins":60,"native_nets":14,
        "independent_A_B_resistor_tolerance_vectors":65536,
        "ideal_DC_fault_combinations":count,
        "healthy_13v8_reference_nominal_GOOD":nominal_good,
        "out_of_window_false_GOOD_count":sum(false_good.values()),
        "ref_A_B_1v25_false_GOOD":false_good[(1.25,1.25)],
        "ref_A_B_5v_false_GOOD":false_good[(5.,5.)],
        "common_supply_and_OC_remain_unqualified":True,
        "physical_fail_closed_series_switch_present":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_NATIVE_KICAD9_SPLIT_REF_INDEPENDENT_16R_25952256_NONFAB",flush=True)

if __name__=="__main__":
    main()
