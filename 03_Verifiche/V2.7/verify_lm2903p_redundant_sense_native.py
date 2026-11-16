#!/usr/bin/env python3
"""Native KiCad9 THT LM2903P redundant dual-series/dual-parallel sensing.

Single resistor OPEN/SHORT remains below 5V-supply nominal common-mode 3V
for a hypothetical 48V source under ideal DC assumptions. No hardware
safety certification, no transient or comparator/supply supervision.
"""
from pathlib import Path
import itertools
import math
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets,require
SCH=ROOT/"04_KiCad/V2.7_DRAFT/MAIN_SECONDARY_LM2903P_REDUNDANT_SENSE/MAIN_SECONDARY_LM2903P_REDUNDANT_SENSE_LAB_V2_7_DRAFT.kicad_sch"
from verify_lm2903p_pdip8_window_native import NET as OLD
NET={k:set(v) for k,v in OLD.items()}
NET["VIN_RAW_LAB"]={("J2201","1"),("R2208","1")}
NET["SENSE_SERIES_MID"]={("R2208","2"),("R2201","1")}
NET["VIN_SENSE"]={("R2201","2"),("R2202","1"),("R2209","1"),("U2201","3"),("U2201","6")}
NET["LAB_RETURN"].add(("R2209","2"))
M = ("NORMAL","R2208_OPEN","R2208_SHORT","R2201_OPEN","R2201_SHORT",
     "R2202_OPEN","R2202_SHORT","R2209_OPEN","R2209_SHORT")

def v_sense(src,rs1,rs2,rl1,rl2,mode):
    vals=dict(R2208=rs1,R2201=rs2,R2202=rl1,R2209=rl2)
    if mode!="NORMAL":
        part,state=mode.split("_")[-2:]
        assert part in vals
        vals[part]=float("inf") if state=="OPEN" else 0.
    top=vals["R2208"]+vals["R2201"]
    l1,l2=vals["R2202"],vals["R2209"]
    if l1==0 or l2==0:return 0.
    bottom=1./(1./l1+1./l2)
    if not math.isfinite(top):return 0.
    return src*bottom/(top+bottom)

def main():
    sch=SCH.read_text(encoding="utf8")
    assert sch.count('(symbol (lib_id "LAB_WINDOW:')==14
    for token in ("R2208","R2209","100k_SENSE_TOP_FIRST_IN_SERIES",
                  "10k_SENSE_BOTTOM_PARALLEL_2_OF_2",
                  "NO FAB / NO TX / NO BATTERIA / NO VEICOLO"):
        assert token in sch,token
    with tempfile.TemporaryDirectory(prefix="lm2903p_redundant_native_") as d:
        temp=Path(d)
        erc=temp/"red.erc"
        p=subprocess.run(["kicad-cli","sch","erc","--exit-code-violations",
            "-o",str(erc),str(SCH)],capture_output=True,text=True,cwd=ROOT)
        print("LM2903P_REDUNDANT_NATIVE_ERC",p.stdout,p.stderr,flush=True)
        if erc.exists():print(erc.read_text(encoding="utf8"),flush=True)
        p.check_returncode()
        nets=exported_nets(SCH,temp/"redundant.net")
    assert len(nets)==9 and set(nets)==set(NET),(set(nets)^set(NET))
    for key,pins in NET.items():
        require(nets,key,*pins)
        assert nets[key]==pins,(key,sorted(nets[key]))
    assert sum(map(len,nets.values()))==34
    assert ("U2201","1") in nets["WINDOW_GOOD_OC_BIASED_LAB"]
    assert ("U2201","7") in nets["WINDOW_GOOD_OC_BIASED_LAB"]
    assert ("U2201","8") in nets["EXTERNAL_5V_UNQUALIFIED"]

    count=0
    healthy_nominal_windows=0
    maximum_single_fault_at_48=0.
    worst_common_mode_margin=1e9
    nominal_thresh=[1e9,0.,1e9,0.]
    singles_high_on_13v8=0
    false_fault_window_outside_nominal_band=0
    for tolerances in itertools.product((.99,1.01),repeat=8):
        rt1,rt2,rb1,rb2,oh,ol,uh,ul=tolerances
        rs1,rs2=100000*rt1,100000*rt2
        rl1,rl2=10000*rb1,10000*rb2
        vref=2.5
        ov=vref*(20000*ol/(116000*oh+20000*ol))
        uv=vref*(20000*ul/(185000*uh+20000*ul))
        sense_normal=v_sense(1.,rs1,rs2,rl1,rl2,"NORMAL")
        nominal_thresh[0]=min(nominal_thresh[0],uv/sense_normal)
        nominal_thresh[1]=max(nominal_thresh[1],uv/sense_normal)
        nominal_thresh[2]=min(nominal_thresh[2],ov/sense_normal)
        nominal_thresh[3]=max(nominal_thresh[3],ov/sense_normal)
        assert uv/sense_normal<13.8<ov/sense_normal
        for src,mode in itertools.product((0.,6.,7.,7.5,8.,8.5,9.,10.,13.8,15.,16.,18.,24.,36.,48.),M):
            vs=v_sense(src,rs1,rs2,rl1,rl2,mode)
            assert vs>=0.
            assert vs<=3.,(src,mode,vs) # ideal 5V LM2903 CM 0..3V
            worst_common_mode_margin=min(worst_common_mode_margin,3.-vs)
            if src==48. and mode!="NORMAL":
                maximum_single_fault_at_48=max(maximum_single_fault_at_48,vs)
            if src==13.8 and mode=="NORMAL":
                assert uv<vs<ov
                healthy_nominal_windows+=1
            if src==13.8 and mode!="NORMAL" and uv<vs<ov:
                singles_high_on_13v8+=1
            if mode!="NORMAL" and (src<9. or src>16.) and uv<vs<ov:
                false_fault_window_outside_nominal_band+=1
            count+=1
    assert count==2**8*15*len(M)==34560
    assert healthy_nominal_windows==256
    assert 2.2<maximum_single_fault_at_48<2.4
    assert worst_common_mode_margin>.6
    assert 9.<nominal_thresh[0]<nominal_thresh[1]<11.
    assert 14.<nominal_thresh[2]<nominal_thresh[3]<16.
    assert false_fault_window_outside_nominal_band>0
    # No single sense resistor fault should falsely signal "normal"
    # at source 48V, even with ±1% resistors.
    print("LM2903P_REDUNDANT_2SERIES_2PARALLEL_SENSE_NATIVE",{
        "native_pins":34,"native_nets":9,"part_count":14,
        "synthetic_fault_corners":count,
        "healthy_13v8_nominal_window_cases":healthy_nominal_windows,
        "single_resistor_fault_max_48V_sense_V":round(maximum_single_fault_at_48,6),
        "min_5V_common_mode_margin_V":round(worst_common_mode_margin,6),
        "UVLO_min_max_V":[round(x,5) for x in nominal_thresh[:2]],
        "OVP_min_max_V":[round(x,5) for x in nominal_thresh[2:]],
        "single_fault_13v8_still_signals_window_cases":singles_high_on_13v8,
        "single_fault_false_good_outside_normal_window_cases":false_fault_window_outside_nominal_band,
        "all_double_faults_qualified":False,
        "VIN_48V_hardware_allowed":False,
        "absolute_input_36V_fault_reached_single_resistor":False,
        "input_surge_negative_reverse_qualified":False,
        "comparator_bias_offset_temp_qualified":False,
        "VCC5V_VREF2V5_supplied":False,
        "independent_power_disconnect_implemented":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_NATIVE_KICAD9_LM2903P_REDUNDANT_34PIN_9NET_34560_CORNERS_NONFAB",flush=True)
if __name__=="__main__":main()
