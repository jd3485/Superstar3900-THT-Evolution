#!/usr/bin/env python3
"""Isolated KiCad9 THT R2102 Vishay PR01 10k 1W candidate OEM derating screen.
The board is NOT physically qualified. No fabricated or energized hardware.
"""
from pathlib import Path
import itertools
import math
import re
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets,require
from verify_q806_dual_zener_clamp_native import N as EXPECTED

SCH=ROOT/"04_KiCad/V2.7_DRAFT/MAIN_SECONDARY_OVP_Q804_Q805_Q806_PR01_R2102/MAIN_SECONDARY_OVP_Q804_Q805_Q806_PR01_R2102_LAB_V2_7_DRAFT.kicad_sch"
PR01_P70_W=1.0
PR01_P70_TEMP_C=70.
PR01_ZERO_TEMP_C=200.
PR01_R_OHM=10000.
PR01_TOL=.05

def pr01_derated(temp_c):
    """OEM Vishay PR01 graph 1W P70 from 70C linearly to zero at 200C.
    Only static ambient derating, not pulse power or actual body temperature.
    """
    return PR01_P70_W*max(0.,min(1.,(PR01_ZERO_TEMP_C-temp_c)/
                       (PR01_ZERO_TEMP_C-PR01_P70_TEMP_C)))

def main():
    s=SCH.read_text(encoding="utf8")
    assert s.count('(symbol (lib_id "LAB_OVP:')==12
    assert "10k_VISHAY_PR01000101002JR500_1W_CANDIDATE" in s
    assert "1N4106-1_MICROCHIP_250UA_CANDIDATE" in s
    assert "1N4106-1_SECOND_PARALLEL_250UA_LAB" in s
    assert "NO FAB / NO TX / NO BATTERIA / NO VEICOLO" in s
    # Check footprint on R2102 instance, not default embedded resistor.
    match=re.search(r'\(property "Reference" "R2102".*?\(property "Footprint" "([^"]+)"',
                    s,flags=re.S)
    assert match is not None
    assert match.group(1)=="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal"
    with tempfile.TemporaryDirectory(prefix="pr01_r2102_native_nonfab_") as d:
        tmp=Path(d)
        report=tmp/"pr01.erc"
        p=subprocess.run(["kicad-cli","sch","erc","--exit-code-violations",
                          "-o",str(report),str(SCH)],capture_output=True,text=True,cwd=ROOT)
        print("PR01_R2102_NATIVE_ERC",p.stdout,p.stderr,flush=True)
        if report.exists():print(report.read_text(encoding="utf8"),flush=True)
        p.check_returncode()
        nets=exported_nets(SCH,tmp/"pr01.net")
    assert set(nets)==set(EXPECTED) and len(nets)==8
    for net,pins in EXPECTED.items():
        require(nets,net,*pins)
        assert nets[net]==pins,(net,sorted(nets[net]))
    assert sum(map(len,nets.values()))==27
    assert ("R2102","1") in nets["DRIVER_SINK_LAB"]
    assert ("R2102","2") in nets["COMMON_GATE_LAB"]

    count=0
    min_headroom_125=1e9
    negative_at_175=0
    peak_power=(0,None)
    over_derating=0
    for src,temp,rval,mode in itertools.product(
        (0.,8.,13.8,16.,24.,36.,48.),
        (-40.,25.,70.,85.,100.,125.,150.,175.,200.),
        (PR01_R_OHM*(1-PR01_TOL),PR01_R_OHM,PR01_R_OHM*(1+PR01_TOL)),
        ("ZENER_SHORT_GATE_TO_SOURCE","GATE_12V_CLAMP_SYNTHETIC","Q806_OFF")
    ):
        # 'Short' is a worst heating hypothesis with Q806 C-E hard sink.
        # Values are NOT vendor I-V curves, actual Vsource, or startup.
        if mode=="ZENER_SHORT_GATE_TO_SOURCE":
            vr=src
        elif mode=="GATE_12V_CLAMP_SYNTHETIC":
            vr=max(0.,src-12.)
        else:
            vr=0.
        watts=vr*vr/rval
        limit=pr01_derated(temp)
        if watts>peak_power[0]:peak_power=(watts,(src,temp,rval,mode))
        if watts>limit+1e-12:over_derating+=1
        if temp==125. and mode=="ZENER_SHORT_GATE_TO_SOURCE":
            min_headroom_125=min(min_headroom_125,limit-watts)
        if temp==175. and watts>limit and mode=="ZENER_SHORT_GATE_TO_SOURCE":
            negative_at_175+=1
        count+=1
    assert count==7*9*3*3==567
    assert 0.24<peak_power[0]<0.25
    assert min_headroom_125>0.3
    assert negative_at_175>0 and over_derating>0
    assert math.isclose(pr01_derated(125.),75/130,rel_tol=1e-14)
    assert math.isclose(pr01_derated(175.),25/130,rel_tol=1e-14)
    # Fault-power crosses 1 W derating curve about 168.5C at Rmin.
    crossover=200.-130.*(48.**2/(PR01_R_OHM*(1-PR01_TOL)))
    assert 168.<crossover<169.
    # Inverse derating bound: fault source voltage limit at each ambient
    # under a SHORT clamp and R2102 at its -5% tolerance. This is NOT
    # an allowable VIN rating of the radio, only a steady-state screen.
    max_source_125=math.sqrt(pr01_derated(125.)*PR01_R_OHM*(1-PR01_TOL))
    max_source_175=math.sqrt(pr01_derated(175.)*PR01_R_OHM*(1-PR01_TOL))
    nominal_13v8_short_power=13.8**2/(PR01_R_OHM*(1-PR01_TOL))
    assert max_source_125>48.>max_source_175
    assert .019<nominal_13v8_short_power<.021
    print("PR01_R2102_NATIVE_DERATING_FAULT_SCREEN",{
        "pins":27,"nets":8,"static_cases":count,
        "pr01_oem_nominal_1W_at_70C":True,
        "pr01_125C_static_derated_W":round(pr01_derated(125.),6),
        "fault_R2102_peak_W":round(peak_power[0],6),
        "min_static_headroom_125C_W":round(min_headroom_125,6),
        "thermal_limit_exceeded_model_cases":over_derating,
        "short_fault_limit_crossover_degC":round(crossover,5),
        "max_synthetic_fault_source_125C_V":round(max_source_125,5),
        "max_synthetic_fault_source_175C_V":round(max_source_175,5),
        "nominal_13v8_short_power_W":round(nominal_13v8_short_power,6),
        "PR01_exact_MPN_OEM_lifecycle_verified":False,
        "PR01_OEM_mechanical_pad_alignment_verified":False,
        "PR01_pulse_short_safe_qualified":False,
        "actual_source_48V_allowed":False,
        "independent_OVP_supervisor_present":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_NATIVE_KICAD9_THT_PR01_R2102_27PIN_8NET_567_DERATING_NONFAB",flush=True)
if __name__=="__main__":
    main()
