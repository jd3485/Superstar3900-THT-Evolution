#!/usr/bin/env python3
"""Native KiCad9 Q804/Q805/Q806 gate stress and fault KCL screen, NOT hardware safety.
No vendor I/V curves, transient or independent supervisor. Never energize.
"""
from pathlib import Path
import itertools
import math
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets, require

SCH = ROOT / "04_KiCad/V2.7_DRAFT/MAIN_SECONDARY_OVP_Q804_Q805_Q806_DRIVER/MAIN_SECONDARY_OVP_Q804_Q805_Q806_NPN_LAB_V2_7_DRAFT.kicad_sch"

def solve_bisect(vs, rgs, rgate, vz, rz):
    """Independent nodal KCL, synthetic finite zener dynamic resistance."""
    def balance(v):
        return (vs-v)/rgate - v/rgs - max(0.0, (v-vz)/rz)
    lo,hi=0.0,vs
    for _ in range(90):
        mid=(lo+hi)/2
        if balance(mid)>0:lo=mid
        else:hi=mid
    v=(lo+hi)/2
    assert abs(balance(v)) < 1e-11, (vs,rgs,rgate,vz,rz,balance(v))
    return v

def main():
    text=SCH.read_text(encoding="utf-8")
    for token in ("R2101", "R2102", "D2101", "Q804", "Q805", "Q806",
                  "KSP42BU_NPN_CANDIDATE", "47k_GATE_SOURCE_OFF_DEFAULT_CANDIDATE",
                  "10k_GATE_DRIVER_SERIES_UNQUALIFIED",
                  "NO FAB / NO TX / NO BATTERIA / NO VEICOLO"):
        assert token in text, ("Schematic missing prerequisite",token)
    with tempfile.TemporaryDirectory(prefix="q806_gate_stress_native_") as tmp:
        nets=exported_nets(SCH,Path(tmp)/"q806_gate_stress.net")
    require(nets,"COMMON_GATE_LAB",("Q804","1"),("Q805","1"),
            ("R2101","2"),("D2101","2"),("R2102","2"))
    require(nets,"FLOATING_COMMON_SOURCE_LAB",("Q804","3"),("Q805","3"),
            ("R2101","1"),("D2101","1"))
    require(nets,"DRIVER_SINK_LAB",("Q806","3"),("R2102","1"))
    require(nets,"LAB_RETURN_ONLY",("Q806","1"))
    assert not nets["FLOATING_COMMON_SOURCE_LAB"] & nets["LAB_RETURN_ONLY"]

    runs=0
    peak_r2102=(-1,None)
    peak_d2101=(-1,None)
    worst_open_vgs=(-1,None)
    exceed_vgs=0
    zener_on=0
    worst_error=0.0
    for vs,rgs,rgate,vz,rz in itertools.product(
         (0.,5.,8.,12.,13.8,16.,20.,24.,36.,48.),
         (44650.,47000.,49350.),
         (9500.,10000.,10500.),
         (11.,12.,13.),
         (0.1,1.,10.)
    ):
        # KSP42 ON is *assumed* to sink hard. Source voltage vs is imposed,
        # not a claim for real floating common source or reverse-polarity.
        v_open = vs*rgs/(rgs+rgate)
        v_clamped_ideal = min(v_open,vz)
        v_numeric=solve_bisect(vs,rgs,rgate,vz,rz)
        if v_open>vz:
            zener_on+=1
            assert vz <= v_numeric <= v_open+1e-10
            # Resistive-zener KCL: Igate == Ipullup + Izener.
            iz=max(0.0,(v_numeric-vz)/rz)
        else:
            iz=0.
            assert math.isclose(v_numeric,v_open,rel_tol=1e-10,abs_tol=1e-10)
        ig=(vs-v_numeric)/rgate
        ip=v_numeric/rgs
        worst_error=max(worst_error,abs(ig-ip-iz))
        pr=ig*ig*rgate
        pd=v_numeric*iz
        if pr>peak_r2102[0]:peak_r2102=(pr,(vs,rgs,rgate,vz,rz))
        if pd>peak_d2101[0]:peak_d2101=(pd,(vs,rgs,rgate,vz,rz))
        if v_open>worst_open_vgs[0]:worst_open_vgs=(v_open,(vs,rgs,rgate))
        if v_open>20.0:exceed_vgs+=1
        # Independent closed-form solution for a linearized dynamic zener.
        if v_open>vz:
            analytical=(vs/rgate+vz/rz)/(1/rgate+1/rgs+1/rz)
        else:
            analytical=v_open
        assert math.isclose(analytical,v_numeric,rel_tol=2e-11,abs_tol=2e-10)
        assert v_numeric>=v_clamped_ideal-1e-10
        runs+=1

    assert runs==10*3**4==810
    assert zener_on>0 and exceed_vgs>0
    assert worst_error<1e-11
    # Explicit nominal no-Zener case at 48V; hard sink exceeds MOSFET max.
    nominal_open_vgs=48*47000/(47000+10000)
    assert nominal_open_vgs>39.5 and nominal_open_vgs<39.6
    # A KSP42 C-E short produces ON-inducing gate bias even with ENABLE=0.
    shorted_ce_vgs=13.8*47000/(47000+10000)
    assert shorted_ce_vgs>11.0
    # A 10uA hypothetical leakage causes nonzero OFF-state bias (not an OEM limit).
    hypothetical_leak_vgs=10e-6*47000
    assert math.isclose(hypothetical_leak_vgs,0.47,abs_tol=1e-12)
    print("Q806_NATIVE_GATE_STRESS_INDEPENDENT_KCL",{
        "cases":runs,"finite_synthetic_zener_rz_ohm":(0.1,1.,10.),
        "r2102_peak_W":round(peak_r2102[0],7),"r2102_peak_case":peak_r2102[1],
        "d2101_peak_W":round(peak_d2101[0],7),"d2101_peak_case":peak_d2101[1],
        "peak_open_zener_vgs_V":round(worst_open_vgs[0],6),
        "open_zener_over_20V_cases":exceed_vgs,
        "nominal_48V_open_zener_vgs_V":round(nominal_open_vgs,6),
        "Q806_CE_short_13v8_vgs_abs_V":round(shorted_ce_vgs,6),
        "hypothetical_10uA_off_leak_vgs_V":hypothetical_leak_vgs,
        "max_independent_KCL_error_A":worst_error,
        "OEM_zener_IV_and_recovery_verified":False,
        "actual_KSP42_leakage_and_failure_rate_verified":False,
        "floating_source_and_transient_stress_qualified":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_NATIVE_KICAD9_Q806_GATE_810_KCL_ZENER_STRESS_CASES_NONFAB",flush=True)

if __name__=="__main__":
    main()
