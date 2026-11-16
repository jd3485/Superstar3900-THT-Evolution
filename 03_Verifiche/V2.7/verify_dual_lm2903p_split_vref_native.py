#!/usr/bin/env python3
"""KiCad9 THT double LM2903P separate external VREF input single-fault veto.

This bench circuit has SHARED VCC5V, RETURN, VIN, open collector output.
EXTERNAL sources are not electrically implemented or safe rated.
"""
from pathlib import Path
import itertools
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets,require
from verify_dual_lm2903p_window_native import NET as OLD

SCH=ROOT/"04_KiCad/V2.7_DRAFT/MAIN_DUAL_LM2903P_SPLIT_EXTERNAL_VREF/MAIN_DUAL_LM2903P_SPLIT_EXTERNAL_VREF_LAB_V2_7_DRAFT.kicad_sch"
NET={k:set(pins) for k,pins in OLD.items()}
NET["EXTERNAL_VREF_2V5_UNQUALIFIED"].difference_update({("R2214","1"),("R2216","1")})
NET["EXTERNAL_VREF_B_2V5_UNQUALIFIED"]={("R2214","1"),("R2216","1"),("J2205","1")}
NET["LAB_RETURN"].add(("J2205","2"))
SRC=(0.,6.,7.,8.,10.,13.8,16.,20.,24.,30.,48.)
REF=(0.,1.25,2.475,2.5,2.525,5.)

def good(vin,vref,tol):
    a,b,c,d,oh,ol,uh,ul=tol
    low=1./(1./(10000.*c)+1./(10000.*d))
    sensed=vin*low/(100000.*a+100000.*b+low)
    uv=vref*(20000.*ul)/(185000.*uh+20000.*ul)
    ov=vref*(20000.*ol)/(116000.*oh+20000.*ol)
    return uv<sensed<ov

def main():
    s=SCH.read_text(encoding="utf8")
    assert s.count('(symbol (lib_id "LAB_WINDOW:')==24
    for ref in ("J2203","J2205","U2201","U2202","R2214","R2216"):
        assert f'"{ref}"' in s
    with tempfile.TemporaryDirectory(prefix="dual_lm2903p_split_ref_native_") as d:
        report=Path(d)/"split.erc"
        p=subprocess.run(["kicad-cli","sch","erc","--exit-code-violations",
                          "-o",str(report),str(SCH)],capture_output=True,text=True,cwd=ROOT)
        print("SPLIT_VREF_NATIVE_ERC",p.stdout,p.stderr,flush=True)
        if report.exists():print(report.read_text(encoding="utf8"),flush=True)
        p.check_returncode()
        nets=exported_nets(SCH,Path(d)/"split.net")
    assert len(nets)==14 and set(nets)==set(NET),(set(nets)^set(NET))
    for name,pins in NET.items():
        require(nets,name,*pins)
        assert nets[name]==pins,(name,sorted(nets[name]))
    assert sum(map(len,nets.values()))==60
    assert ("U2201","8") in nets["EXTERNAL_5V_UNQUALIFIED"]
    assert ("U2202","8") in nets["EXTERNAL_5V_UNQUALIFIED"]
    assert ("R2203","1") in nets["EXTERNAL_VREF_2V5_UNQUALIFIED"]
    assert ("R2214","1") in nets["EXTERNAL_VREF_B_2V5_UNQUALIFIED"]
    assert ("U2201","1") in nets["WINDOW_GOOD_OC_BIASED_LAB"]
    assert ("U2202","1") in nets["WINDOW_GOOD_OC_BIASED_LAB"]

    cases=0
    outside_good=0
    nominal_good=0
    false_off_at_nominal=0
    for mask,vin,failed,reference in itertools.product(range(256),SRC,("A","B"),REF):
        tol=[1.01 if mask&(1<<i) else .99 for i in range(8)]
        ra,rb=(reference,2.5) if failed=="A" else (2.5,reference)
        both=good(vin,ra,tol) and good(vin,rb,tol)
        if (vin<9. or vin>16.) and both:outside_good+=1
        if vin==13.8 and reference==2.5 and both:nominal_good+=1
        if vin==13.8 and not both:false_off_at_nominal+=1
        cases+=1
    assert cases==256*11*2*6==33792
    assert outside_good==0
    assert nominal_good==512
    assert false_off_at_nominal>0 # single bad REF disables even with healthy VIN
    print("SPLIT_LM2903P_THT_NATIVE_SINGLE_VREF_FAULT",{
        "native_pins":60,"native_nets":14,"THT_parts":24,
        "tested_ideal_cases":cases,
        "single_channel_fault_false_good_VIN_outside_9to16V":outside_good,
        "healthy_13v8_nominal_both_refs_2v5_cases":nominal_good,
        "healthy_13v8_false_off_on_reference_fault_cases":false_off_at_nominal,
        "shared_power_5V_ground_and_OC":True,
        "independent_5V_and_VREF_OEM_sources_implemented":False,
        "common_cause_both_refs_fault_qualified":False,
        "independent_series_switch_present":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_NATIVE_KICAD9_SPLIT_LM2903P_VREF_60PIN_14NET_33792_NONFAB",flush=True)
if __name__=="__main__":main()
