#!/usr/bin/env python3
"""Native KiCad9 DC input-return resistor R1203 pilot and loaded AF tradeoff.

A 220k resistor from LM386 AMP_IN (pin3) to MAIN-local GND provides a
passive DC return if the FRONT cable disconnects. It is not a mute:
contact welded NO, power sequencing, GND floating, speaker transients
and inductive return currents remain unqualified.
225 normal and 225 volume-pin3-open cases across 5 frequency x
5 volume x 3 Rin x 3 Rbleed tolerance, two independent AC solvers.
"""
from __future__ import annotations
import math
import subprocess
import tempfile
from itertools import product
from pathlib import Path
from verify_interboard_audio_contract_native import exported_nets,require
from verify_am455_front_lm386_loaded_ac_native import (
    FREQUENCIES,WIPER_FRACTIONS,INPUT_RIN,direct,nodal,check_actual_cad
)
from verify_front_volume_open_low_fault_kcl_native import (
    series_parallel_open_low,independent_kcl_open_low
)
ROOT=Path(__file__).resolve().parents[2]
SCHEM=ROOT/"04_KiCad/V2.7_DRAFT/AUDIO_RX_MONO_LM386_V2_7_DRAFT.kicad_sch"
BOARD=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_PLACEMENT/FRONT_CONTROL_13REFS_PLACEMENT_NONFAB.kicad_pcb"
R_BLEED=(217800.,220000.,222200.)
def main():
    check_actual_cad()
    raw=SCHEM.read_text(encoding="utf-8")
    assert raw.count('(property "Reference" "R1203"')==1
    assert '220k_1PCT_0P25W_AMP_IN_BLEEDER_CANDIDATE' in raw
    assert raw.count('(symbol (lib_id "TH_AUDIO:R")')==3
    assert 'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal' in raw
    board=BOARD.read_text(encoding="utf-8")
    assert "R1203" not in board and board.count('(segment ')==35
    with tempfile.TemporaryDirectory(prefix="tht_main_amp_input_bleeder_") as d:
        p=Path(d)
        report=p/"amp_erc.rpt"
        run=subprocess.run(["kicad-cli","sch","erc","--exit-code-violations",
                            "-o",str(report),str(SCHEM)],
                            cwd=ROOT,capture_output=True,text=True,timeout=120)
        print("R1203_MAIN_AUDIO_NATIVE_ERC",run.stdout,run.stderr,flush=True)
        if report.exists():print(report.read_text(encoding="utf-8"),flush=True)
        run.check_returncode()
        nets=exported_nets(SCHEM,p/"audio.net")
    require(nets,"AMP_IN",("U1201","3"),("R1201","2"),("R1203","1"))
    require(nets,"GND",("U1201","4"),("J1202","2"),("R1203","2"))
    require(nets,"AUDIO_IN",("J1202","1"),("C1201","1"))
    require(nets,"PRE_IN",("C1201","2"),("R1201","1"))
    assert ("R1203","1") not in nets["GND"]
    assert ("R1203","2") not in nets["AMP_IN"]
    total=0
    lost_max=0.
    max_fault=0.
    examples=[]
    for freq,pos,rin,bleed in product(
            FREQUENCIES,WIPER_FRACTIONS,INPUT_RIN,R_BLEED):
        effective=1/(1/rin+1/bleed)
        nominal=direct(freq,pos,rin)
        new_direct=direct(freq,pos,effective)
        independent=nodal(freq,pos,effective)
        assert abs(new_direct-independent)<3e-10,(freq,pos,rin,bleed)
        fault=series_parallel_open_low(freq,pos,effective)
        fault_nodal=independent_kcl_open_low(freq,pos,effective)
        assert abs(fault-fault_nodal)<3e-10,(freq,pos,rin,bleed)
        attenuation=abs(new_direct/nominal)
        assert .90<attenuation<1,(freq,pos,rin,bleed,attenuation)
        assert 0<abs(new_direct)<abs(fault)<1
        lost_max=max(lost_max,1-attenuation)
        max_fault=max(max_fault,abs(fault))
        if freq==1000. and rin==50000. and bleed==220000. and pos in (.01,.99):
            examples.append((pos,round(abs(nominal),6),round(abs(new_direct),6),
                             round(attenuation,6),round(abs(fault),6)))
        total+=1
    assert total==225
    assert len(examples)==2 and max_fault>.5
    assert lost_max<.10
    # With a disconnected wiper, only R1203 and the IC's input resistance
    # provide a DC return. This does NOT prove 0V during actual capacitive
    # injection or GND lift; it only rules out an open schematic path.
    print("LM386_R1203_220K_DC_RETURN_1KHZ_50K_EXAMPLES",examples,flush=True)
    print("LM386_R1203_NATIVE_BLEEDER_GATES",{
        "nominal_and_open_low_AC_cases_each":total,
        "resistor_ohms_nominal":220000,
        "resistor_1pct_corner_ohms":R_BLEED,
        "max_linear_nominal_transfer_loss_percent":round(100*lost_max,3),
        "max_open_low_fault_transfer":round(max_fault,6),
        "unplugged_FRONT_input_has_passive_MAIN_local_DC_return":True,
        "speaker_level_safety_or_harness_GND_failure_qualified":False,
        "mute_relays_NO_weld_bypass_mitigated":False,
        "PCB_changed":False,"NO_FAB_NO_TX":True},flush=True)
    print("PASS_NATIVE_KICAD9_MAIN_LM386_R1203_220K_AMP_INPUT_GND_225X2_AC_NONFAB",flush=True)
if __name__=="__main__": main()
