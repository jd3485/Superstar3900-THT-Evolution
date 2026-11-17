#!/usr/bin/env python3
"""Native two-THT-stage gate clamp SHORT/dual OPEN stress audit.

Physical pin-net topology is verified with actual KiCad9 export. Fault
equations are ideal DC extremes, not an OEM transient/I-V/SOA guarantee.
"""
import itertools
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets,require
from verify_two_complete_pmos_stages_native import SCH,EXPECTED
from verify_two_stage_twin_zener_single_open_native import STAGES,properties

SOURCES=(0.,13.8,20.,24.,36.,48.)
RGS_VALUES=(44650.,47000.,49350.)
RSINK_VALUES=(9500.,10000.,10500.)
DRIVERS=("DISABLED","ENABLED","CE_SHORT")
CLAMPS=("BOTH_OPEN","ONE_SHORT")

def theoretical_corner(vs,rgs,rsink,driver,clamp):
    """Return |Vgs|, Rgs dissipation, series sink dissipation [ideal]."""
    if driver=="DISABLED":
        return 0.,0.,0.
    if clamp=="ONE_SHORT":
        # One hypothetical ideal Zener short directly clamps gate-to-source.
        # Real short impedance, external source and BJT stresses omitted.
        return 0.,0.,vs*vs/rsink
    i=vs/(rgs+rsink)  # Both Zeners OPEN, perfect hard sink.
    return i*rgs,i*i*rgs,i*i*rsink

def main():
    raw=SCH.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="dual_stage_clamp_extremes_") as d:
        nets=exported_nets(SCH,Path(d)/"fault.net")
    assert len(nets)==14 and sum(map(len,nets.values()))==54
    assert set(nets)==set(EXPECTED)
    for net,ends in EXPECTED.items():
        require(nets,net,*ends)
        assert nets[net]==ends
    assert nets["FLOATING_COMMON_SOURCE_LAB"].isdisjoint(nets["FLOATING_SOURCE_B_LAB"])
    assert nets["COMMON_GATE_LAB"].isdisjoint(nets["COMMON_GATE_B_LAB"])
    results={}
    for name,source,gate,diodes,rgs_ref,sink_ref in STAGES:
        sink_driver={"A":("Q806","DRIVER_SINK_LAB"),"B":("Q816","DRIVER_SINK_B_LAB")}[name]
        assert {(d,"1") for d in diodes}|{(rgs_ref,"1")}<=nets[source]
        assert {(d,"2") for d in diodes}|{(rgs_ref,"2"),(sink_ref,"2")}<=nets[gate]
        assert {(sink_ref,"1"),(sink_driver[0],"3")}<=nets[sink_driver[1]]
        for d in diodes:
            value,foot=properties(raw,d)
            assert value.startswith("1N4106-1_")
            assert foot=="Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal"
        assert properties(raw,rgs_ref)[0].startswith("47k_")
        assert properties(raw,sink_ref)[0].startswith("10k_")
        count=0
        dual_open_over20=0
        max_unprotected_vgs=0.
        max_rgs_dissipation=0.
        max_sink_short_dissipation=0.
        forced_gate_on=0
        for vs,rgs,rsink,driver,clamp in itertools.product(
            SOURCES,RGS_VALUES,RSINK_VALUES,DRIVERS,CLAMPS):
            vgs,p_pull,p_sink=theoretical_corner(vs,rgs,rsink,driver,clamp)
            assert 0.<=vgs<=vs+1e-12
            if driver=="CE_SHORT" and clamp=="BOTH_OPEN" and vgs>0:
                forced_gate_on+=1
            if driver!="DISABLED" and clamp=="BOTH_OPEN":
                dual_open_over20+=vgs>20.
                max_unprotected_vgs=max(max_unprotected_vgs,vgs)
                max_rgs_dissipation=max(max_rgs_dissipation,p_pull)
            if driver!="DISABLED" and clamp=="ONE_SHORT":
                assert vgs==0. and p_pull==0.
                max_sink_short_dissipation=max(max_sink_short_dissipation,p_sink)
            if driver=="DISABLED":
                assert (vgs,p_pull,p_sink)==(0.,0.,0.)
            count+=1
        assert count==324
        assert dual_open_over20==38
        assert forced_gate_on==45
        assert abs(max_unprotected_vgs-40.25148683092608)<1e-9
        assert abs(max_sink_short_dissipation-(48.**2/9500.))<1e-12
        assert max_rgs_dissipation>0.
        results[name]={
            "ideal_static_cases":count,
            "both_zener_open_gate_over_abs20V_cases":dual_open_over20,
            "one_ideal_short_max_sink_resistor_W":round(max_sink_short_dissipation,6),
            "both_open_max_absVgs_V":round(max_unprotected_vgs,6),
            "both_open_max_Rgs_W":round(max_rgs_dissipation,6),
            "hypothetical_CE_short_uncommanded_gate_bias_cases":forced_gate_on}
    assert results["A"]==results["B"]
    print("TWO_THT_STAGE_GATE_CLAMP_EXTREME_FAULTS",{
        "native_components":24,"native_pins":54,"native_nets":14,
        "synthetic_cases":648,"per_stage":results,
        "oem_zener_short_impedance_verified":False,
        "driver_sink_SOA_and_resistor_pulse_qualified":False,
        "fault_case_48V_hardware_authorized":False,
        "both_stages_fail_closed_qualified":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True},flush=True)
    print("PASS_NATIVE_TWO_STAGE_CLAMP_SHORT_OPEN_DRIVER_648_NONFAB",flush=True)

if __name__=="__main__":
    main()
