#!/usr/bin/env python3
"""Synthetic PMOS gate RC decay/recovery sensitivity on real KiCad9 THT nets.

Assumes constant source, no Zener action, no Miller coupling and an IDEAL
linear Rgs||Cgs with a hypothetical constant gate leakage current. No
dynamic OEM model or safe OFF timing is inferred.
"""
import itertools
import math
import sys
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets,require
from verify_two_complete_pmos_stages_native import SCH,EXPECTED
from verify_two_stage_twin_zener_single_open_native import STAGES,properties

RGS=(44650.,47000.,49350.)
CGATE=(1e-9,10e-9,100e-9)  # assumed total gate capacitance, NOT OEM
LEAK=(0.,5e-6,25e-6,100e-6)  # hypothetical sink currents
RAIL=(13.8,48.)  # 48 V mathematical fault only
TAU_FACTORS=(0.,1.,3.,5.)

def trajectory(rail, r, cap, leak, factor):
    tau=r*cap
    steady=min(rail,leak*r)
    # Gate initially held at source => drop 0; simple first-order response.
    return steady*(-math.expm1(-factor)),tau,steady

def main():
    sch=SCH.read_text(encoding="utf8")
    with tempfile.TemporaryDirectory(prefix="two_stage_gate_rc_") as td:
        nets=exported_nets(SCH,Path(td)/"rc.net")
    assert set(nets)==set(EXPECTED)
    for net, pins in EXPECTED.items():
        require(nets,net,*pins)
        assert nets[net]==pins
    assert len(nets)==14 and sum(map(len,nets.values()))==54

    summary={}
    for stage,source,gate,diodes,pull,sink in STAGES:
        assert {(pull,"1")}<=nets[source]
        assert {(pull,"2"),(sink,"2")}<=nets[gate]
        assert properties(sch,pull)[0].startswith("47k_")
        assert properties(sch,sink)[0].startswith("10k_")
        for diode in diodes:
            assert (diode,"1") in nets[source]
            assert (diode,"2") in nets[gate]
        cases=0;above2=0;above4=0;worst=0.
        for r,cap,leak,rail,factor in itertools.product(RGS,CGATE,LEAK,RAIL,TAU_FACTORS):
            v,tau,steady=trajectory(rail,r,cap,leak,factor)
            assert 0<=v<=steady+1e-12
            if factor==0: assert v==0.
            if leak==0: assert v==0.
            if factor==5 and steady>0: assert v/steady>0.99
            assert tau==r*cap
            above2+=v>=2.
            above4+=v>=4.
            worst=max(worst,v)
            cases+=1
        assert cases==288
        # Expected per stage: deterministic analytic conditions to detect changes.
        assert (above2,above4)==(48,12),(above2,above4)
        assert 4.8<worst<4.935
        summary[stage]={"cases":cases,"hypothetical_ge2V_cases":above2,
           "hypothetical_ge4V_cases":above4,"max_ideal_absVgs_V":round(worst,6)}
    assert summary["A"]==summary["B"]
    assert abs(min(RGS)*min(CGATE)*1e6-44.65)<1e-9
    assert abs(max(RGS)*max(CGATE)*1e3-4.935)<1e-9
    print("THT_TWO_STAGE_GATE_RC_STEP_SYNTHETIC",{
       "native_components":24,"native_pins":54,"native_nets":14,
       "total_synthetic_cases":576,"per_stage":summary,
       "hypothetical_tau_min_us":44.65,
       "hypothetical_tau_max_ms":4.935,
       "capacitances_are_not_OEM_Ciss":True,
       "gate_leakage_not_OEM":True,
       "thresholds_are_arbitrary_not_MOSFET_Vth":True,
       "no_Miller_nonlinear_charge_or_supply_dynamics":True,
       "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True},flush=True)
    print("PASS_NATIVE_THT_TWO_STAGE_GATE_RC_576_NONFAB",flush=True)
if __name__=="__main__":main()
