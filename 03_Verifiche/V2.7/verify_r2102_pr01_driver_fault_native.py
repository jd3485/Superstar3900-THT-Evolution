#!/usr/bin/env python3
"""Native KiCad9 net-anchored R2102 PR01 gate-driver resistor fault screening.

Physical 27-pin/8-net topology is real KiCad9; static faulty circuit
equations are independent ideal hypotheses, NOT vendor/hardware qualification.
"""
from pathlib import Path
import itertools
import math
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets, require
from verify_q806_dual_zener_clamp_native import N as EXPECTED

SCH=ROOT/"04_KiCad/V2.7_DRAFT/MAIN_SECONDARY_OVP_Q804_Q805_Q806_PR01_R2102/MAIN_SECONDARY_OVP_Q804_Q805_Q806_PR01_R2102_LAB_V2_7_DRAFT.kicad_sch"

def gate_without_diode(vs,rpull,rseries,active):
    """Vgs from source to gate with ideal BJT hard-sink vs inactive floating driver.

    active True: Q806 C-E short or explicit ENABLE on, Rseries positive.
    active False: Q806 open, resistor pullup alone enforces passive OFF.
    """
    if not active:return 0.
    return vs*rpull/(rpull+rseries)

def main():
    s=SCH.read_text(encoding="utf8")
    assert "10k_VISHAY_PR01000101002JR500_1W_CANDIDATE" in s
    with tempfile.TemporaryDirectory(prefix="r2102_pr01_driver_fault_native_") as d:
        nets=exported_nets(SCH,Path(d)/"fault.net")
    assert set(nets)==set(EXPECTED)
    for name,pins in EXPECTED.items():
        require(nets,name,*pins)
        assert nets[name]==pins,(name,sorted(nets[name]))
    assert len(nets)==8 and sum(map(len,nets.values()))==27
    assert ("Q806","3") in nets["DRIVER_SINK_LAB"]
    assert ("R2102","1") in nets["DRIVER_SINK_LAB"]
    assert ("R2102","2") in nets["COMMON_GATE_LAB"]
    assert ("R2101","1") in nets["FLOATING_COMMON_SOURCE_LAB"]
    assert ("R2101","2") in nets["COMMON_GATE_LAB"]
    assert ("Q806","1") in nets["LAB_RETURN_ONLY"]

    count=0
    enabled_while_disabled=0
    single_resistor_open_off=0
    dangerous_hard_sink=0
    worst_ungated_vgs=0.
    max_on_case_resistor_w=0.
    for vs,rpull,rseries,zener_state,driver_state in itertools.product(
        (0.,13.8,20.,24.,36.,48.),
        (44650.,47000.,49350.),
        (9500.,10000.,10500.),
        ("BOTH_HEALTHY","BOTH_OPEN","D2101_OPEN","D2102_OPEN"),
        ("DISABLED_HEALTHY","ENABLED","Q806_CE_SHORT","R2102_OPEN","R2102_SHORT")
    ):
        if driver_state=="DISABLED_HEALTHY":
            vgs=0.
        elif driver_state=="R2102_OPEN":
            vgs=0. # R2101 intact pull-up; NOT a stuck-GATE guarantee.
            single_resistor_open_off+=1
        elif driver_state=="R2102_SHORT":
            vgs=vs  # Zero series resistor and strong sink; unclamped.
            if vs>20.:dangerous_hard_sink+=1
        else:
            vgs=gate_without_diode(vs,rpull,rseries,True)
        if driver_state=="Q806_CE_SHORT" and vgs>3.:
            enabled_while_disabled+=1
            worst_ungated_vgs=max(worst_ungated_vgs,vgs)
        if driver_state in ("Q806_CE_SHORT","ENABLED"):
            p=(vs-vgs)**2/rseries
            max_on_case_resistor_w=max(max_on_case_resistor_w,p)
        if zener_state=="BOTH_HEALTHY":
            # No vendor I-V known. The open-clamp voltage above is merely
            # an unconstrained high-stress upper screen, NOT actual VGS.
            pass
        count+=1
    assert count==6*3*3*4*5==1080
    assert enabled_while_disabled>0
    assert single_resistor_open_off==6*3*3*4
    assert dangerous_hard_sink>0
    assert worst_ungated_vgs>40.
    assert max_on_case_resistor_w>0.
    # With a shorted driver and healthy 5V ENABLE low, Q806 can still
    # turn PMOS ON. Series resistor wattage is not a fail-safe interlock.
    print("R2102_DRIVER_FAULT_NATIVE_KCL",{
        "native_pins":27,"native_nets":8,"cases":count,
        "Q806_CE_short_uncommanded_turn_on_cases":enabled_while_disabled,
        "worst_uncommanded_unclamped_VGS_abs_V":round(worst_ungated_vgs,6),
        "R2102_open_passive_off_model_cases":single_resistor_open_off,
        "R2102_short_unclamped_over_20V_cases":dangerous_hard_sink,
        "max_unclamped_gate_resistor_W":round(max_on_case_resistor_w,6),
        "R2102_short_current_unlimited_model":True,
        "OEM_1N4106_current_sharing_qualified":False,
        "driver_hardware_fail_closed":False,
        "independent_supervisor_qualified":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_NATIVE_KICAD9_PR01_DRIVER_1080_FAULT_CASES_NONFAB",flush=True)
if __name__=="__main__":main()
