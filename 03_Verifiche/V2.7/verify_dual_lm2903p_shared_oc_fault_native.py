#!/usr/bin/env python3
"""KiCad9 dual LM2903P shared open-collector single-node common-cause fault.

The ideal output logic does not create a separate fail-OFF power disconnect.
An externally *forced* HIGH is a hypothetical boundary condition; in a real
SHORT-to-5V, transistor sink contention/current and component failure are
UNQUALIFIED. OPEN pull-up/unpowered behavior is undefined, not 'safe'.
"""
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets,require
from verify_dual_lm2903p_split_vref_native import SCH,NET,good
from verify_dual_lm2903p_split_vref_double_fault_native import VIN

def main():
    with tempfile.TemporaryDirectory(prefix="dual_lm2903p_oc_common_fault_") as d:
        nets=exported_nets(SCH,Path(d)/"oc_fault.net")
    assert len(nets)==14 and set(nets)==set(NET)
    for name,pins in NET.items():
        require(nets,name,*pins)
        assert nets[name]==pins,(name,sorted(nets[name]))
    assert sum(map(len,nets.values()))==60
    oc=nets["WINDOW_GOOD_OC_BIASED_LAB"]
    assert oc=={("U2201","1"),("U2201","7"),("U2202","1"),
                ("U2202","7"),("R2207","2"),("J2204","1")},oc
    assert ("R2207","1") in nets["EXTERNAL_5V_UNQUALIFIED"]
    assert ("U2201","8") in nets["EXTERNAL_5V_UNQUALIFIED"]
    assert ("U2202","8") in nets["EXTERNAL_5V_UNQUALIFIED"]
    assert ("J2204","2") in nets["LAB_RETURN"]
    assert ("J2204","1") not in nets["EXTERNAL_5V_UNQUALIFIED"]
    assert ("J2204","1") not in nets["LAB_RETURN"]

    healthy_normal_good=0
    forced_high_outside=0
    forced_low_healthy_off=0
    naturally_outside_good=0
    cases=0
    for mask_a in range(256):
        tol_a=tuple(1.01 if mask_a & (1<<i) else .99 for i in range(8))
        for mask_b in range(256):
            tol_b=tuple(1.01 if mask_b & (1<<i) else .99 for i in range(8))
            for vin in VIN:
                # Independent A/B resistor PVT; BOTH references externally ideal
                # at 2.5V here, separating OC fault from common VREF faults.
                window_good=good(vin,2.5,tol_a) and good(vin,2.5,tol_b)
                if vin==13.8 and window_good:healthy_normal_good+=1
                if (vin<9 or vin>16) and window_good:naturally_outside_good+=1
                # Two hypothetical forced node potentials, irrespective of
                # whether a real output transistor can survive contention:
                if vin<9 or vin>16:forced_high_outside+=1
                if vin==13.8:forced_low_healthy_off+=1
                cases+=1
    assert cases==256**2*len(VIN)==720896
    assert healthy_normal_good==65536
    assert naturally_outside_good==0
    assert forced_high_outside==524288
    assert forced_low_healthy_off==65536
    print("THT_SPLIT_REF_SHARED_OC_FAULT_BOUNDARY",{
        "native_pins":60,"native_nets":14,"independent_16R_tolerance_cases":256**2,
        "hypothetical_ideal_DC_cases_per_fault_mode":cases,
        "healthy_13v8_NORMAL_GOOD":healthy_normal_good,
        "normal_outside_window_false_GOOD":naturally_outside_good,
        "forced_external_HIGH_outside_window_false_GOOD":forced_high_outside,
        "forced_external_LOW_13v8_false_OFF":forced_low_healthy_off,
        "output_floating_on_pullup_open_or_5V_lost":"UNDEFINED_NOT_PROVEN_OFF",
        "output_contention_on_short_to_5V":"NOT_OEM_MODELED",
        "real_independent_series_power_disconnect_present":False,
        "physical_output_safety_qualified":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_NATIVE_KICAD9_DUAL_LM2903P_COMMON_OC_60PIN_14NET_720896_NONFAB",flush=True)

if __name__=="__main__":
    main()
