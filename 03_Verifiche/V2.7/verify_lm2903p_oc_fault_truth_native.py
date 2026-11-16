#!/usr/bin/env python3
"""KiCad9 physical THT LM2903P dual open-collector window fault truth table.

The exact 30 pins/8 nets derive from native KiCad9 netlist. 2.5V reference
and 5V supply are hypothetical EXTERNAL inputs, not implemented sources.
"""
from pathlib import Path
import itertools
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets,require
from verify_lm2903p_pdip8_window_native import SCH,NET

def open_collector_window(vsense,uvref,ovref):
    # LM2903 OUT LOW if IN+ < IN- (ignore input offsets/transients).
    # U2201A pin3+ sense, pin2- UVLO reference.
    # U2201B pin5+ OVP reference, pin6- sense.
    oc1_sink=vsense<uvref
    oc2_sink=ovref<vsense
    return not (oc1_sink or oc2_sink)

def main():
    with tempfile.TemporaryDirectory(prefix="lm2903p_fault_truth_net_") as tmp:
        nets=exported_nets(SCH,Path(tmp)/"truth.net")
    assert set(nets)==set(NET)
    for net,pins in NET.items():
        require(nets,net,*pins)
        assert nets[net]==pins,(net,sorted(nets[net]))
    assert sum(map(len,nets.values()))==30
    assert ("U2201","1") in nets["WINDOW_GOOD_OC_BIASED_LAB"]
    assert ("U2201","7") in nets["WINDOW_GOOD_OC_BIASED_LAB"]
    assert ("U2201","3") in nets["VIN_SENSE"]
    assert ("U2201","6") in nets["VIN_SENSE"]
    assert ("R2207","1") in nets["EXTERNAL_5V_UNQUALIFIED"]
    assert ("J2202","1") in nets["EXTERNAL_5V_UNQUALIFIED"]
    assert ("J2203","1") in nets["EXTERNAL_VREF_2V5_UNQUALIFIED"]

    tested=0
    normal_high=0
    low_on_good_vin=0
    low_when_ref_lost=0
    input_overstressed=0
    powerless_ambiguous=0
    ref_loss_zero_boundary_ambiguous=0
    for ah,al,oh,ol,uh,ul,vref,vin,mode in itertools.product(
        (.99,1.01),(.99,1.01),(.99,1.01),(.99,1.01),
        (.99,1.01),(.99,1.01),(2.475,2.525),
        (0.,8.,13.8,16.,48.),
        ("NOMINAL","R2202_BOTTOM_OPEN","R2202_BOTTOM_SHORT",
         "REFERENCE_LOST","SUPPLY_5V_LOST")
    ):
        sense=vin*(5000*al)/(100000*ah+5000*al)
        uv=vref*20000*ul/(85000*uh+20000*ul)
        ov=vref*20000*ol/(50000*oh+20000*ol)
        if mode=="NOMINAL":
            result=open_collector_window(sense,uv,ov)
            assert result==(vin==13.8)
            if result:normal_high+=1
        elif mode=="R2202_BOTTOM_OPEN":
            # Comparator pins can be driven to raw VIN, no TVS/clamp.
            exposed=vin
            if exposed>5.:
                input_overstressed+=1
            # The ideal overvoltage comparator would sink at VIN>15V,
            # but its overstressed silicon cannot be relied upon.
        elif mode=="R2202_BOTTOM_SHORT":
            result=open_collector_window(0.,uv,ov)
            assert not result
        elif mode=="REFERENCE_LOST":
            if vin>0.:
                result=open_collector_window(sense,0.,0.)
                assert not result
                low_when_ref_lost+=1
            else:
                # equal input voltages are indeterminate without offsets
                ref_loss_zero_boundary_ambiguous+=1
        else:
            # With VCC=0, R2207 also lacks power; logical high is NOT
            # guaranteed even if outputs cease sinking current.
            powerless_ambiguous+=1
        tested+=1
    assert tested==128*5*5==3200
    assert normal_high==128
    assert input_overstressed==128*4
    assert low_when_ref_lost==128*4
    assert powerless_ambiguous==128*5
    assert ref_loss_zero_boundary_ambiguous==128
    print("LM2903P_THT_NATIVE_OPEN_COLLECTOR_FAULT_TRUTH",{
        "native_pins":30,"native_nets":8,"fault_cases":tested,
        "healthy_nominal_13v8_OC_high_scenarios":normal_high,
        "bottom_open_pin_above_5V_cases":input_overstressed,
        "VREF_lost_ideal_low_cases":low_when_ref_lost,
        "VREF_zero_input_boundary_ambiguous":ref_loss_zero_boundary_ambiguous,
        "VCC_lost_OC_output_unqualified_cases":powerless_ambiguous,
        "external_supply_source_implemented":False,
        "input_clamp_implemented":False,
        "independent_hardware_disconnect_implemented":False,
        "Q806_CE_short_failclosed":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_NATIVE_KICAD9_LM2903P_OC_30PIN_8NET_3200_FAULT_TRUTH_NONFAB",flush=True)
if __name__=="__main__":main()
