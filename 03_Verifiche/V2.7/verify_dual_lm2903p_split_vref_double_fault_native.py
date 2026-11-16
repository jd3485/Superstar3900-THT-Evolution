#!/usr/bin/env python3
"""KiCad9 native THT split-reference dual LM2903P 101376 double-reference DC faults.

CAUTION: the two physical J2203/J2205 headers are separate nets, but
do NOT prove independent safe reference generation. No PCB or power path.
"""
from pathlib import Path
import itertools
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets,require
from verify_dual_lm2903p_split_vref_native import SCH,NET,good

VIN=(0.,6.,7.,8.,10.,13.8,16.,20.,24.,30.,48.)
VREF=(0.,1.25,2.475,2.5,2.525,5.)

def main():
    with tempfile.TemporaryDirectory(prefix="dual_split_vref_correlated_native_") as d:
        nets=exported_nets(SCH,Path(d)/"correlated.net")
    assert len(nets)==14 and set(nets)==set(NET)
    for name,pins in NET.items():
        require(nets,name,*pins)
        assert nets[name]==pins,(name,sorted(nets[name]))
    assert sum(map(len,nets.values()))==60
    assert ("J2203","1") in nets["EXTERNAL_VREF_2V5_UNQUALIFIED"]
    assert ("J2205","1") in nets["EXTERNAL_VREF_B_2V5_UNQUALIFIED"]
    assert ("J2205","1") not in nets["EXTERNAL_VREF_2V5_UNQUALIFIED"]
    assert ("J2203","1") not in nets["EXTERNAL_VREF_B_2V5_UNQUALIFIED"]
    assert ("U2201","8") in nets["EXTERNAL_5V_UNQUALIFIED"]
    assert ("U2202","8") in nets["EXTERNAL_5V_UNQUALIFIED"]

    count=0
    falseGood=0
    pairCounts={}
    nominalGood=0
    for mask,vin,ra,rb in itertools.product(range(256),VIN,VREF,VREF):
        tol=[1.01 if mask & (1 << i) else .99 for i in range(8)]
        both=good(vin,ra,tol) and good(vin,rb,tol)
        if (vin<9. or vin>16.) and both:
            falseGood+=1
            key=(ra,rb)
            pairCounts[key]=pairCounts.get(key,0)+1
        if vin==13.8 and ra==2.5 and rb==2.5 and both:
            nominalGood+=1
        count+=1
    assert count==256*11*6*6==101376
    assert nominalGood==256
    assert falseGood==1028
    assert pairCounts=={(1.25,1.25):512,(5.,5.):516},pairCounts
    print("DUAL_THT_SPLIT_REF_CORRELATED_NATIVE",{
        "native_pins":60,"native_nets":14,
        "hypothetical_DC_test_cases":count,
        "both_refs_healthy_13v8_good_corners":nominalGood,
        "two_independent_ref_faults_false_GOOD_cases":falseGood,
        "reference_pair_1v25_1v25_false_GOOD":pairCounts[(1.25,1.25)],
        "reference_pair_5v_5v_false_GOOD":pairCounts[(5.,5.)],
        "separate_connector_headers_present":True,
        "separate_reference_OEM_sources_present":False,
        "shared_5V_supply_present":True,
        "physical_series_disconnect_present":False,
        "simultaneous_VREF_protection_qualified":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_NATIVE_KICAD9_SPLIT_LM2903P_DOUBLE_VREF_60PIN_14NET_101376_NONFAB",flush=True)

if __name__=="__main__": main()
