#!/usr/bin/env python3
"""Guard against drift between actual native KiCad relay passives and AC solvers.

The ERC/netlist verifies connectivity, but not that the mathematical constants
match actual component instance values. No fabrication/component qualification.
"""
from pathlib import Path
import re
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets
from verify_front_g5v1_sixpin_dual_com_impedance_ac_native import (
    SERIES,BLEED,INPUT_R,INPUT_C,LM386_RIN)
import verify_front_mute_welded_no_ac_native as welded
import verify_front_mute_nc_coupled_audio_fault_native as coupled
from verify_front_g5v1_sixpin_ac_contact_fault_native import FRONT as SIX_PARENT
from verify_front_g5v1_sixpin_dual_com_impedance_ac_native import MUTE
MAIN=ROOT/"04_KiCad/V2.7_DRAFT/AUDIO_RX_MONO_LM386_V2_7_DRAFT.kicad_sch"

def component_value(source,ref):
    # Parse component *instance* (not the cached library symbol).
    pattern=(r'\(symbol\s+\(lib_id\s+"[^"]+"\)[^\n]*\n'
             r'\(property\s+"Reference"\s+"'+re.escape(ref)+r'"[^\n]*\n'
             r'\(property\s+"Value"\s+"([^"]+)"')
    matches=re.findall(pattern,source)
    assert len(matches)==1,(ref,matches)
    return matches[0]

def ohms(label):
    match=re.fullmatch(r'(\d+(?:\.\d+)?)([kKmM]?)(?:_.*)?',label)
    assert match is not None,label
    # KiCad labels use 1k, 100k, etc.
    return float(match.group(1))*{'':1.,'k':1000.,'K':1000.,'M':1e6,'m':1e-3}[match.group(2)]

def farads(label):
    match=re.fullmatch(r'(\\d+(?:\\.\\d+)?)(pF|nF|uF|µF|mF|F)(?:_.*)?',label)
    assert match is not None,label
    factors={'pF':1e-12,'nF':1e-9,'uF':1e-6,'µF':1e-6,'mF':1e-3,'F':1.}
    return float(match.group(1))*factors[match.group(2)]

def main():
    with tempfile.TemporaryDirectory(prefix="front_sixpin_value_lock_") as td:
        front=exported_nets(SIX_PARENT,Path(td)/"front.net")
        audio=exported_nets(MAIN,Path(td)/"main.net")
    def locate(nets,ref,pin):
        matches=[n.rsplit("/",1)[-1] for n,people in nets.items() if (ref,pin) in people]
        assert len(matches)==1,(ref,pin,matches)
        return matches[0]
    # Instance reference, actual pin partition, and actual declared value
    # must all agree with the independent numerical AC implementations.
    assert locate(front,"R1901","1")=="AMP_INPUT_MUTED"
    assert locate(front,"R1901","2")=="AF_GND"
    assert locate(front,"R1902","1")=="RELAY_COM_AUDIO"
    assert locate(front,"R1902","2")=="AMP_INPUT_MUTED"
    assert locate(audio,"C1201","1")=="AUDIO_IN"
    assert locate(audio,"C1201","2")=="PRE_IN"
    assert locate(audio,"U1201","3")=="AMP_IN"
    assert locate(audio,"R1201","1")=="PRE_IN"
    assert locate(audio,"R1201","2")=="AMP_IN"
    mute_text=MUTE.read_text(encoding="utf-8")
    main_text=MAIN.read_text(encoding="utf-8")
    r1901=ohms(component_value(mute_text,"R1901"))
    r1902=ohms(component_value(mute_text,"R1902"))
    r1201=ohms(component_value(main_text,"R1201"))
    c1201=farads(component_value(main_text,"C1201"))
    assert abs(farads("100nF_50V_INPUT")-1e-7)<1e-20
    assert abs(farads("1uF")-1e-6)<1e-18
    for bad in ("100pF_EXTRA)","10nX","", "100nFgarbage"):
        try:
            farads(bad)
        except AssertionError:
            pass
        else:
            raise AssertionError(("invalid capacitor value accepted",bad))
    assert r1901==100000.,r1901
    assert r1902==1000.,r1902
    assert r1201==10000.,r1201
    assert abs(c1201-100e-9)<1e-20,c1201
    assert (BLEED,SERIES,INPUT_R)==(r1901,r1902,r1201)
    assert (welded.R_BLEED,welded.R_SERIES,welded.R_INPUT)==(r1901,r1902,r1201)
    assert (coupled.R_BLEED,coupled.R_SERIES,coupled.R_INPUT)==(r1901,r1902,r1201)
    assert abs(INPUT_C-c1201)<1e-20
    assert abs(welded.C_INPUT-c1201)<1e-20
    assert abs(coupled.C_INPUT-c1201)<1e-20
    assert (INPUT_C,LM386_RIN)==(welded.C_INPUT,welded.RIN)
    assert (INPUT_C,LM386_RIN)==(coupled.C_INPUT,coupled.R_IN)
    # Symbol value is not a measured part tolerance or operating guarantee.
    print("PASS_G5V1_SIXPIN_NATIVE_COMPONENT_INSTANCE_AC_MODEL_VALUE_LOCK",{
        "mute_bleed_R1901_ohm":r1901,
        "mute_series_R1902_ohm":r1902,
        "main_audio_R1201_ohm":r1201,
        "main_audio_C1201_farads":c1201,
        "AC_solver_resistor_instances_checked":3,
        "AC_solver_capacitor_instances_checked":1,
        "physical_PVT_or_PCB_DRC_qualified":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True},flush=True)
if __name__=="__main__":main()
