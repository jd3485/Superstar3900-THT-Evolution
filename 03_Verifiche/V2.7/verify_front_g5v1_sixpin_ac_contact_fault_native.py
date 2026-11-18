#!/usr/bin/env python3
"""Native six-pad OEM FRONT contact AC screen; no component/PCB qualification.

Two previously independent numerical circuit solvers cross-checked under
a physical 6-pin COM5/COM6 fault matrix. Shared AF_GND loss is unbounded
and deliberately NOT simulated as a finite, safe voltage.
"""
from pathlib import Path
import itertools
import math
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets, require
from verify_front_mute_welded_no_ac_native import collapsed, nodal
from verify_front_g5v1_six_terminal_oem_pin_map_native import OEM_TO_EXISTING_NET

FRONT=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_CONTROL_PARTIAL_G5V1_SIXPIN_CANDIDATE.kicad_sch"
MUTE_CHILD=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_MUTE_NC_RELAY/FRONT_G5V1_SIXPIN_ISOLATED_NATIVE_CANDIDATE.kicad_sch"
FREQ=(300.,1000.,3000.)
COUPLING=(100e-12,1e-9,10e-9)
R_SOURCE=(10000.,50000.)
NC_CONTACT=(0.1,10.)
NO_CONTACT=(0.1,10.)
FLAGS=("coil_on","nc_stuck_open","no_welded","com5_open","com6_open","ground_open")

def main():
    with tempfile.TemporaryDirectory(prefix="g5v1_sixpin_ac_native_") as temp:
        native=exported_nets(FRONT,Path(temp)/"front.net")
    expected={str(p):v for p,v in OEM_TO_EXISTING_NET.items()}
    members={}
    for name,pins in native.items():
        for pin in pins:
            assert pin not in members,(pin,name)
            members[pin]=name.rsplit("/",1)[-1]
    assert {p:members[("K1901",p)] for p in expected}==expected
    assert members[("K1901","5")]==members[("K1901","6")]=="RELAY_COM_AUDIO"
    assert members[("R1902","1")]=="RELAY_COM_AUDIO"
    assert members[("R1902","2")]==members[("R1901","1")]==members[("J1902","1")]=="AMP_INPUT_MUTED"
    assert members[("R1901","2")]==members[("J1902","2")]=="AF_GND"
    assert "1k_SERIES_AUDIO_INPUT_CANDIDATE" in MUTE_CHILD.read_text()
    assert "100k_AMP_INPUT_BLEED_CANDIDATE" in FRONT.read_text()
    scenarios=0
    undefined_return=0
    numerical_cases=0
    dual_com_disconnected=0
    source_present_coil_off=0
    worst_discrepancy=0.0
    for bits in itertools.product((False,True),repeat=len(FLAGS)):
        state=dict(zip(FLAGS,bits))
        scenarios+=1
        # Individual physical COM solder opens; either surviving bond permits signal.
        common_open=state["com5_open"] and state["com6_open"]
        nc_conducts=(not state["coil_on"] and not state["nc_stuck_open"] and not common_open)
        no_conducts=((state["coil_on"] or state["no_welded"]) and not common_open)
        if common_open:dual_com_disconnected+=1
        if not state["coil_on"] and no_conducts:source_present_coil_off+=1
        if state["ground_open"]:
            # Shared reference could float; neither collapsed nor nodal is valid.
            undefined_return+=1
            continue
        for f,cc,rs,rcn,rco in itertools.product(FREQ,COUPLING,R_SOURCE,NC_CONTACT,NO_CONTACT):
            nc=rcn if nc_conducts else math.inf
            no=rco if no_conducts else math.inf
            a=collapsed(f,cc,nc,no,rs)
            b=nodal(f,cc,nc,no,rs)
            discrepancy=abs(a-b)
            assert discrepancy<3e-11,(state,f,cc,rs,rcn,rco,a,b)
            assert all(math.isfinite(v) for v in (a.real,a.imag,b.real,b.imag))
            worst_discrepancy=max(worst_discrepancy,discrepancy)
            numerical_cases+=1
    assert scenarios==64
    assert undefined_return==32
    assert dual_com_disconnected==16
    assert source_present_coil_off==12
    assert numerical_cases==32*len(FREQ)*len(COUPLING)*len(R_SOURCE)*len(NC_CONTACT)*len(NO_CONTACT)
    print("PASS_FRONT_G5V1_SIXPIN_64_CONTACT_STATES_DUAL_SOLVER_AC_NATIVE_NONQUALIFYING",{
        "state_count":scenarios,
        "shared_return_open_unbounded_cases":undefined_return,
        "both_COM_bonds_open_states":dual_com_disconnected,
        "coil_off_NO_welded_source_path_states":source_present_coil_off,
        "numerical_scenarios_with_defined_return":numerical_cases,
        "max_complex_voltage_solver_discrepancy":worst_discrepancy,
        "R1902_1k_R1901_100k_native":True,
        "coil_PVT_and_contact_qualified":False,
        "hardware_PCB_or_DRC":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True},flush=True)

if __name__=="__main__":
    main()
