#!/usr/bin/env python3
"""Physical KiCad9 THT dual comparator windows, shared power/reference.

Each channel has its own 2x100k series/2x10k parallel sense path.
The dual wired-open-collector veto is NOT an independent power cut.
"""
from pathlib import Path
import itertools
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets,require
from verify_lm2903p_redundant_sense_native import NET as OLD
from verify_lm2903p_redundant_sense_native import v_sense
SCH=ROOT/"04_KiCad/V2.7_DRAFT/MAIN_DUAL_LM2903P_INDEPENDENT_SENSE/MAIN_DUAL_LM2903P_INDEPENDENT_SENSE_LAB_V2_7_DRAFT.kicad_sch"
NET={k:set(v) for k,v in OLD.items()}
NET["VIN_RAW_LAB"].add(("R2210","1"))
NET["LAB_RETURN"].update({("U2202","4"),("R2212","2"),("R2213","2"),("R2215","2"),("R2217","2")})
NET["WINDOW_GOOD_OC_BIASED_LAB"].update({("U2202","1"),("U2202","7")})
NET["EXTERNAL_5V_UNQUALIFIED"].add(("U2202","8"))
NET["EXTERNAL_VREF_2V5_UNQUALIFIED"].update({("R2214","1"),("R2216","1")})
NET["SENSE_SERIES_MID_B"]={("R2210","2"),("R2211","1")}
NET["VIN_SENSE_B"]={("R2211","2"),("R2212","1"),("R2213","1"),("U2202","3"),("U2202","6")}
NET["OVP_REF_B"]={("R2214","2"),("R2215","1"),("U2202","5")}
NET["UVLO_REF_B"]={("R2216","2"),("R2217","1"),("U2202","2")}

SRC=(0.,6.,7.,7.5,8.,8.5,9.,10.,13.8,15.,16.,18.,24.,36.,48.)
FAULTS=("NORMAL","R2208_OPEN","R2208_SHORT","R2201_OPEN","R2201_SHORT",
        "R2202_OPEN","R2202_SHORT","R2209_OPEN","R2209_SHORT")
def good(vsense,uv,ov):
    return uv<vsense<ov
def main():
    source=SCH.read_text(encoding="utf8")
    assert source.count('(symbol (lib_id "LAB_WINDOW:')==23
    with tempfile.TemporaryDirectory(prefix="dual_lm2903p_tht_native_") as d:
        erc=Path(d)/"dual.erc"
        r=subprocess.run(["kicad-cli","sch","erc","--exit-code-violations",
                          "-o",str(erc),str(SCH)],capture_output=True,text=True,cwd=ROOT)
        print("DUAL_LM2903P_NATIVE_ERC",r.stdout,r.stderr,flush=True)
        if erc.exists():print(erc.read_text(encoding="utf8"),flush=True)
        r.check_returncode()
        nets=exported_nets(SCH,Path(d)/"dual.net")
    assert len(nets)==13 and set(nets)==set(NET),(set(nets)^set(NET))
    for name,pins in NET.items():
        require(nets,name,*pins)
        assert nets[name]==pins,(name,sorted(nets[name]))
    assert sum(map(len,nets.values()))==58
    assert ("U2201","1") in nets["WINDOW_GOOD_OC_BIASED_LAB"]
    assert ("U2202","7") in nets["WINDOW_GOOD_OC_BIASED_LAB"]
    assert ("U2202","8") in nets["EXTERNAL_5V_UNQUALIFIED"]
    assert ("U2202","3") in nets["VIN_SENSE_B"]
    assert ("U2202","6") in nets["VIN_SENSE_B"]

    n=0
    false_single_good=0
    healthy_good=0
    max_sense=0.
    for mask,vin,channel,fault in itertools.product(
        range(256),SRC,("A","B"),FAULTS):
        tol=[1.01 if mask&(1<<i) else .99 for i in range(8)]
        a,b,c,d,oh,ol,uh,ul=tol
        top1,top2=100000*a,100000*b
        low1,low2=10000*c,10000*d
        uv=2.5*20000*ul/(185000*uh+20000*ul)
        ov=2.5*20000*ol/(116000*oh+20000*ol)
        if channel=="A":
            valA=v_sense(vin,top1,top2,low1,low2,fault)
            valB=v_sense(vin,top1,top2,low1,low2,"NORMAL")
        else:
            valA=v_sense(vin,top1,top2,low1,low2,"NORMAL")
            valB=v_sense(vin,top1,top2,low1,low2,fault)
        assert 0.<=valA<=3. and 0.<=valB<=3.
        max_sense=max(max_sense,valA,valB)
        both=good(valA,uv,ov) and good(valB,uv,ov)
        if vin<9 or vin>16:
            if fault!="NORMAL" and both:false_single_good+=1
            assert not both,(vin,channel,fault,valA,valB)
        if vin==13.8 and fault=="NORMAL" and both:healthy_good+=1
        n+=1
    assert n==256*15*2*9==69120
    assert false_single_good==0
    assert healthy_good==512
    print("DUAL_LM2903P_THT_TWO_SENSE_WINDOW_MODEL",{
       "native_pins":58,"native_nets":13,"part_count":23,
       "fault_corner_count":n,
       "false_GOOD_when_either_sensing_channel_single_resistor_fault_VIN_outside_9to16V":false_single_good,
       "healthy_normal_13v8_good_cases":healthy_good,
       "max_ideal_single_fault_sense_input_V":round(max_sense,6),
       "both_channels_share_EXTERNAL_5V_and_VREF":True,
       "both_outputs_share_open_collector_wire":True,
       "common_cause_supply_or_ref_qualified":False,
       "transient_offsets_bias_qualified":False,
       "independent_hardware_series_switch_present":False,
       "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_NATIVE_KICAD9_DUAL_LM2903P_THT_58PIN_13NET_69120_CORNERS_NONFAB",flush=True)
if __name__=="__main__":main()
