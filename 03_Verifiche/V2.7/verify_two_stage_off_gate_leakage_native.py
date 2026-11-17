#!/usr/bin/env python3
"""KiCad9-native off-state PMOS gate leakage sensitivity, ideal DC only.

No gate-charge dynamics, OEM BJT leakage data, FET thresholds, safety
qualification, fuse/TVS coordination or permission for 48 V hardware.
This is a hypothetical current sink from the floating source-referenced
gate to return with BJT commanded OFF and Zeners assumed OPEN.
"""
from pathlib import Path
import itertools
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets,require
from verify_two_complete_pmos_stages_native import SCH,EXPECTED
from verify_two_stage_twin_zener_single_open_native import STAGES,properties

RAILS=(0.,5.,9.,13.8,20.,48.)  # 48 V is a fault-screen ONLY
RGS=(44650.,47000.,49350.)
LEAK_UA=(0.,1.,5.,10.,25.,50.,100.)

def ideal_gate_stress(vsource, rgs_ohm, sink_leak_a):
    """Resistance-limited |Vgs| with ideal source/return and no Zener action.

    The min(vsource, I*R) limiter presumes gate cannot go below return:
    that is a synthetic bound, NOT a physical guaranteed clamp.
    """
    assert vsource>=0 and rgs_ohm>0 and sink_leak_a>=0
    return min(vsource,sink_leak_a*rgs_ohm)

def main():
    raw=SCH.read_text(encoding="utf8")
    with tempfile.TemporaryDirectory(prefix="two_stage_off_leakage_") as td:
        nets=exported_nets(SCH,Path(td)/"off_leakage.net")
    assert set(nets)==set(EXPECTED)
    for net,pins in EXPECTED.items():
        require(nets,net,*pins)
        assert nets[net]==pins
    assert len(nets)==14 and sum(map(len,nets.values()))==54

    stages={}
    for stage,source,gate,diodes,pull,sink in STAGES:
        assert {(pull,"1")} <= nets[source]
        assert {(pull,"2"),(sink,"2")} <= nets[gate]
        assert properties(raw,pull)[0].startswith("47k_")
        assert properties(raw,sink)[0].startswith("10k_")
        assert nets[source].isdisjoint(nets[gate])
        for d in diodes:
            assert (d,"1") in nets[source] and (d,"2") in nets[gate]
            assert properties(raw,d)[0].startswith("1N4106-1_")

        n=at_least_2=at_least_4=0
        max_drop=0.
        for v,r,i_ua in itertools.product(RAILS,RGS,LEAK_UA):
            stress=ideal_gate_stress(v,r,i_ua*1e-6)
            assert 0<=stress<=v+1e-12
            # Monotone in leakage and Rgs, NOT a measured transfer curve.
            assert stress<=ideal_gate_stress(v,r,max(LEAK_UA)*1e-6)+1e-12
            if v==0 or i_ua==0:
                assert stress==0.
            at_least_2+=stress>=2.
            at_least_4+=stress>=4.
            max_drop=max(max_drop,stress)
            n+=1
        assert n==126
        assert (at_least_2,at_least_4)==(30,15),(at_least_2,at_least_4)
        assert abs(max_drop-4.935)<1e-9
        # If Rgs opens, this DC return is absent. No safe Vgs may be inferred.
        stages[stage]={"bounded_ideal_dc_cases":n,
            "at_least_2V_hypothetical_cases":at_least_2,
            "at_least_4V_hypothetical_cases":at_least_4,
            "max_hypothetical_absVgs_V":max_drop,
            "Rgs_open_vgs_unknown":True}
    assert stages["A"]==stages["B"]
    print("TWO_STAGE_OFF_GATE_LEAKAGE_NATIVE_SCREEN",{
        "physical_components":24,"physical_pins":54,"physical_nets":14,
        "synthetic_total":252,"stages":stages,
        "gate_sink_current_grid_uA":LEAK_UA,
        "source_rail_grid_V":RAILS,
        "thresholds_2V_and_4V_are_screening_not_FET_specs":True,
        "driver_off_current_and_Zener_models_OEM_verified":False,
        "return_clamp_and_source_stiffness_guaranteed":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True},flush=True)
    print("PASS_NATIVE_THT_TWO_STAGE_OFF_GATE_LEAKAGE_252_NONFAB",flush=True)

if __name__=="__main__":
    main()
