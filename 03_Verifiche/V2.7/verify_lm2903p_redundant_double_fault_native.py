#!/usr/bin/env python3
"""THT LM2903P KiCad9 redundant sensor **DOUBLE** resistor fault screens.

The exported KiCad9 netlist is mandatory. Double OPEN/SHORT static
models are deliberately NOT physical vendor SPICE, and do not prove
fail-closed or safe operation at hypothetical source48V.
"""
from pathlib import Path
import itertools
import math
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets,require
from verify_lm2903p_redundant_sense_native import NET,SCH

PARTS=("R2208","R2201","R2202","R2209")
SOURCES=(0.,6.,7.,7.5,8.,8.5,9.,10.,13.8,15.,16.,18.,24.,36.,48.)
FAULTS=("OPEN","SHORT")

def voltage(vsource,values,errors):
    resist=dict(values)
    for name,mode in errors:
        assert name in resist and mode in FAULTS
        resist[name]=float("inf") if mode=="OPEN" else 0.
    upper=resist["R2208"]+resist["R2201"]
    lower1,lower2=resist["R2202"],resist["R2209"]
    if lower1==0. or lower2==0.:return 0.
    denominator=(1./lower1+1./lower2)
    lower=(float("inf") if denominator==0. else 1./denominator)
    if not math.isfinite(upper):return 0.
    if not math.isfinite(lower):return vsource
    if upper==0.:return vsource
    return vsource*lower/(upper+lower)

def main():
    with tempfile.TemporaryDirectory(prefix="lm2903p_double_fault_native_") as d:
        nets=exported_nets(SCH,Path(d)/"red_dual.net")
    assert set(nets)==set(NET)
    for net,pins in NET.items():
        require(nets,net,*pins)
        assert nets[net]==pins,(net,sorted(nets[net]))
    assert sum(map(len,nets.values()))==34 and len(nets)==9
    assert nets["VIN_SENSE"]==NET["VIN_SENSE"]
    assert nets["SENSE_SERIES_MID"]==NET["SENSE_SERIES_MID"]

    total=0
    over_cm=0
    over_abs=0
    failed_window_high=0
    worst=0.
    exposed_fault_pairs=set()
    exposed_at_48=set()
    false_high_fault_pairs=set()
    for tolerance in itertools.product((.99,1.01),repeat=8):
        a,b,c,d,oh,ol,uh,ul=tolerance
        values=dict(R2208=100000.*a,R2201=100000.*b,
                    R2202=10000.*c,R2209=10000.*d)
        uv=2.5*(20000.*ul)/(185000.*uh+20000.*ul)
        ov=2.5*(20000.*ol)/(116000.*oh+20000.*ol)
        for pair,states,vin in itertools.product(
            itertools.combinations(PARTS,2),
            itertools.product(FAULTS,repeat=2),
            SOURCES
        ):
            fault=tuple(zip(pair,states))
            vs=voltage(vin,values,fault)
            assert math.isfinite(vs) and 0.<=vs<=vin+1e-12
            worst=max(worst,vs)
            if vs>3.:
                over_cm+=1
                exposed_fault_pairs.add(fault)
            if vs>36.:
                over_abs+=1
                if vin==48.:exposed_at_48.add(fault)
            if (vin<9. or vin>16.) and uv<vs<ov:
                failed_window_high+=1
                false_high_fault_pairs.add(fault)
            total+=1
    assert total==2**8*6*4*15==92160
    assert over_cm>0 and over_abs>0
    assert worst==48.
    expected_abs={
        (("R2208","SHORT"),("R2201","SHORT")),
        (("R2202","OPEN"),("R2209","OPEN"))
    }
    assert exposed_at_48==expected_abs,exposed_at_48
    assert over_abs==2*2**8
    # In this EXACT two-distinct-resistor OPEN/SHORT grid, no false\n    # window-high was found outside nominal 9..16V; this does NOT\n    # clear the 3072 single-fault false-good cases in PR #313.\n    assert failed_window_high==0
    print("LM2903P_REDUNDANT_DOUBLE_FAULT_NATIVE_MODEL",{
        "actual_native_pins":34,"actual_native_nets":9,
        "synthetic_2resistor_fault_cases":total,
        "above_5V_supply_common_mode_3V_cases":over_cm,
        "above_Ti_LM2903P_36V_absolute_input_max_cases":over_abs,
        "worst_sense_voltage_with_source48V_V":worst,
        "double_fault_patterns_exceeding_36V_at_source48V":[
            ",".join(name+"_"+state for name,state in item)
            for item in sorted(exposed_at_48)
        ],
        "false_window_good_outside_9to16V_cases":failed_window_high,
        "false_good_fault_pattern_count":len(false_high_fault_pairs),
        "TI_OEM_input_abs_max_V":36.,
        "5V_functional_common_mode_max_V":3.,
        "actual_source48V_qualified":False,
        "independent_reference_supply_present":False,
        "independent_series_switch_present":False,
        "surge_dynamic_bias_qualification":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_NATIVE_KICAD9_LM2903P_REDUNDANT_34PIN_9NET_92160_DOUBLE_FAULT_NONFAB",flush=True)
if __name__=="__main__":main()
