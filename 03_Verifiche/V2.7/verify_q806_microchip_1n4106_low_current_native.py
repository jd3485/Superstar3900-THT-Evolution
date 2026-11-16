#!/usr/bin/env python3
"""Native KiCad9 THT Microchip 1N4106-1 twin low-current Zener candidate.
Verifies physical pins/nets and OEM IZT feasibility, NOT a vendor I/V model.
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
from verify_q806_dual_zener_clamp_native import N as EXPECTED, solution

SCH=ROOT/"04_KiCad/V2.7_DRAFT/MAIN_SECONDARY_OVP_Q804_Q805_Q806_LOW_CURRENT_ZENER/MAIN_SECONDARY_OVP_Q804_Q805_Q806_LOW_CURRENT_ZENER_LAB_V2_7_DRAFT.kicad_sch"

def main():
    txt=SCH.read_text(encoding="utf8")
    assert txt.count('(symbol (lib_id "LAB_OVP:')==12
    assert txt.count("1N4106-1_MICROCHIP_250UA_CANDIDATE")==1
    assert txt.count("1N4106-1_SECOND_PARALLEL_250UA_LAB")==1
    assert txt.count("Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal")>=2
    assert "1N4742A_GATE_SOURCE_12V_CANDIDATE" not in txt
    assert "1N4742A_SECOND_PARALLEL_CLAMP_LAB" not in txt
    assert "NO FAB / NO TX / NO BATTERIA / NO VEICOLO" in txt
    with tempfile.TemporaryDirectory(prefix="microchip_zener_native_") as d:
        tmp=Path(d)
        report=tmp/"microchip.erc"
        run=subprocess.run(["kicad-cli","sch","erc","--exit-code-violations",
                            "-o",str(report),str(SCH)],capture_output=True,text=True,cwd=ROOT)
        print("MICROCHIP_ZENER_NATIVE_ERC",run.stdout,run.stderr,flush=True)
        if report.exists():print(report.read_text(encoding="utf8"),flush=True)
        run.check_returncode()
        nets=exported_nets(SCH,tmp/"microchip.net")
    assert set(nets)==set(EXPECTED)
    for name,ends in EXPECTED.items():
        require(nets,name,*ends)
        assert nets[name]==ends,(name,sorted(nets[name]))
    pins=[x for ends in nets.values() for x in ends]
    assert len(pins)==len(set(pins))==27 and len(nets)==8
    assert not nets["LAB_RETURN_ONLY"]&nets["FLOATING_COMMON_SOURCE_LAB"]
    assert ("D2101","1") in nets["FLOATING_COMMON_SOURCE_LAB"]
    assert ("D2102","2") in nets["COMMON_GATE_LAB"]

    izt=0.000250 # OEM datasheet defines VZ at 250 microamp; not global I-V curve
    zzt_max=200. # ohm at IZT alone; NOT dynamic bound elsewhere
    vz_nom=12.0
    vz_min,vz_max=11.4,12.6
    assert vz_min<vz_nom<vz_max
    checked=0
    per_diode_low_current=0
    single_current_at_risk_min=1e9
    worst_open_risk_src=0.
    max_oneopen_ideal=0.
    # 6*3*3*3*3*4 == 1944 candidate cases;
    # synthetic Rz is NEVER OEM extrapolation.
    for vs,rgs,rg,vz,rz,mode in itertools.product(
        (0.,13.8,20.,24.,36.,48.),
        (44650.,47000.,49350.),
        (9500.,10000.,10500.),
        (11.,12.,13.),
        (0.1,1.,10.),
        ("HEALTHY","D2101_OPEN","D2102_OPEN","BOTH_OPEN")
    ):
        active={"HEALTHY":2,"D2101_OPEN":1,"D2102_OPEN":1,"BOTH_OPEN":0}[mode]
        v=solution(vs,rgs,rg,vz,rz,active)
        ideal_open_vgs=vs*rgs/(rgs+rg)
        if active==1:
            max_oneopen_ideal=max(max_oneopen_ideal,v)
        if active>0:
            # Current available at hypothetical Zener knee, AFTER pullup.
            avail=max(0.,(vs-vz)/rg-vz/rgs)
            if avail/active<izt:
                per_diode_low_current+=1
        if ideal_open_vgs>20.:
            # Worst gate-source risk under an OPEN clamp.
            worst_open_risk_src=max(worst_open_risk_src,vs)
            single_current_at_risk_min=min(single_current_at_risk_min,
                max(0.,(vs-vz_max)/rg-vz_max/rgs))
        checked+=1
    assert checked==1944 and per_diode_low_current>0
    assert worst_open_risk_src==48.
    assert max_oneopen_ideal<20.
    # Around a gate-source margin boundary of 20V, even min-current
    # conditions in the ideal 12.6V knee case reach IZT (not validation
    # of full I-V, breakdown at other currents or thermal behavior).
    for rgs,rg in itertools.product((44650.,47000.,49350.),(9500.,10000.,10500.)):
        source_when_unclamped_vgs_20=20.*(rgs+rg)/rgs
        required_for_one_izt=vz_max+rg*(vz_max/rgs+izt)
        assert required_for_one_izt<source_when_unclamped_vgs_20
    # The previous 1N4742A requires 21mA IZT; upper current R2102 path
    # is <=48V/9.5k even if no Zener exists.
    assert 48./9500. < .021
    print("MICROCHIP_1N4106_THT_NATIVE_AND_OEM_IZT_SCREEN",{
        "physical_pins":len(pins),"nets":len(nets),"ideal_cases":checked,
        "OEM_test_current_uA":250.,"OEM_max_impedance_at_IZT_ohm":zzt_max,
        "ideal_per_diode_below_IZT_cases":per_diode_low_current,
        "ideal_one_zener_open_max_VGS_abs_V":round(max_oneopen_ideal,6),
        "minimum_available_current_at_open_20V_risk_A":round(single_current_at_risk_min,8),
        "OEM_full_current_Vz_guaranteed":False,
        "OEM_thermal_transient_and_tolerance_qualified":False,
        "parallel_diode_current_sharing_qualified":False,
        "DO35_pin_pad_mechanical_OEM_audit_complete":False,
        "independent_supervisor_present":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_NATIVE_KICAD9_MICROCHIP_1N4106_27PIN_8NET_1944_IDEAL_NONFAB",flush=True)

if __name__=="__main__":main()
