#!/usr/bin/env python3
"""KiCad9 native ERC/netlist contrast: five-sheet FRONT abstract vs 6-pin OEM candidate.
No product relay qualification, populated PCB or board DRC.
"""
from pathlib import Path
import tempfile
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets
from verify_front_partial_hierarchy_native import SCH as ABSTRACT
from verify_front_g5v1_six_terminal_oem_pin_map_native import OEM_TO_EXISTING_NET

CAND=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_CONTROL_PARTIAL_G5V1_SIXPIN_CANDIDATE.kicad_sch"
OLD_RELAY="FRONT_MUTE_NC_RELAY/FRONT_NC_MUTE_CONTACT_THT_V2_7_DRAFT.kicad_sch"
NEW_RELAY="FRONT_MUTE_NC_RELAY/FRONT_G5V1_SIXPIN_POSTMUTE_HIERARCHICAL_CANDIDATE.kicad_sch"

def pinmap(nets):
    result={}
    for name, members in nets.items():
        for member in members:
            assert member not in result,(member,name,result[member])
            result[member]=name.rsplit("/",1)[-1]
    return result

def main():
    assert CAND.with_suffix(".kicad_pro").is_file()
    old_text=ABSTRACT.read_text(encoding="utf8")
    text=CAND.read_text(encoding="utf8")
    assert OLD_RELAY in old_text
    assert OLD_RELAY not in text
    assert text.count(NEW_RELAY)==1
    assert text.count('(pin "AMP_INPUT_MUTED" passive')==1
    assert text.count('(pin "AF_GND" passive')==2
    assert '(xy 205.74 237.49) (xy 217.17 237.49)' in text
    assert '(xy 205.74 242.57) (xy 217.17 242.57)' in text
    original_relay=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_MUTE_NC_RELAY/FRONT_G5V1_SIXPIN_ISOLATED_NATIVE_CANDIDATE.kicad_sch"
    routed_relay=ROOT/"04_KiCad/V2.7_DRAFT"/NEW_RELAY
    assert original_relay.is_file() and routed_relay.is_file()
    original_text=original_relay.read_text(encoding="utf8")
    routed_text=routed_relay.read_text(encoding="utf8")
    assert routed_text.count('(hierarchical_label "AMP_INPUT_MUTED"')==1
    assert routed_text.count('(hierarchical_label "AF_GND"')==2
    assert '(hierarchical_label "AMP_INPUT_MUTED"' not in original_text
    # The actual J1301/1 demod input must be exported to the FRONT parent,
    # while the original standalone volume benchmark stays unchanged.
    child=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_VOLUME/FRONT_VOLUME_THT_V2_7_DRAFT_FRONT_HIERARCHICAL_CANDIDATE.kicad_sch"
    standalone=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_VOLUME/FRONT_VOLUME_THT_V2_7_DRAFT.kicad_sch"
    assert standalone.is_file() and child.is_file()
    assert "FRONT_VOLUME/FRONT_VOLUME_THT_V2_7_DRAFT_FRONT_HIERARCHICAL_CANDIDATE.kicad_sch" in text
    assert text.count('(pin "DEMOD_AUDIO" passive')==1
    assert text.count('(label "DEMOD_AUDIO" (at 165.1 111.76 0)')==1
    assert "(xy 142.24 111.76) (xy 165.1 111.76)" in text
    assert child.read_text(encoding="utf8").count('(hierarchical_label "DEMOD_AUDIO"')==1
    assert '(hierarchical_label "DEMOD_AUDIO"' not in standalone.read_text(encoding="utf8")
    assert "NO FAB / NO TX" in text
    assert text.count("(sheet (at ")==5
    assert text.count('(pin "COIL_PLUS_LAB" passive')==2
    assert text.count('(pin "COIL_MINUS_LAB" passive')==2
    with tempfile.TemporaryDirectory(prefix="front_6pin_hierarchy_") as td:
        d=Path(td)
        for sch,short in ((ABSTRACT,"abstract"),(CAND,"sixpin")):
            report=d/(short+".erc")
            run=subprocess.run(["kicad-cli","sch","erc","--exit-code-violations",
                                "-o",str(report),str(sch)],cwd=ROOT,
                                capture_output=True,text=True,timeout=120)
            if report.exists():print(short+"_ERC",report.read_text(encoding="utf8"),flush=True)
            print(short+"_ERC_RETURN",run.returncode,run.stdout,run.stderr,flush=True)
            run.check_returncode()
        old=exported_nets(ABSTRACT,d/"old.net")
        new=exported_nets(CAND,d/"candidate.net")
    om=pinmap(old); nm=pinmap(new)
    expected={("K1901",pin):name for pin,name in OEM_TO_EXISTING_NET.items()}
    candidate_relay={key:value for key,value in nm.items() if key[0]=="K1901"}
    assert candidate_relay==expected,(candidate_relay,expected)
    assert {k:v for k,v in om.items() if k[0]=="K1901"}=={
        ("K1901","1"):"RELAY_COM_AUDIO",
        ("K1901","2"):"AF_GND",
        ("K1901","3"):"VOL_WIPER_TO_AMP",
        ("K1901","4"):"COIL_PLUS_LAB",
        ("K1901","5"):"COIL_MINUS_LAB"}
    unaffected_old={k:v for k,v in om.items() if k[0]!="K1901"}
    unaffected_new={k:v for k,v in nm.items() if k[0]!="K1901"}
    assert unaffected_old==unaffected_new,(
        "non-relay endpoints changed",
        sorted(set(unaffected_old.items())-set(unaffected_new.items())),
        sorted(set(unaffected_new.items())-set(unaffected_old.items())))
    assert len(nm)==len(om)+1,(len(nm),len(om))
    assert len(old)==len(new)==22,(len(old),len(new))
    assert nm[("K1901","5")]=="RELAY_COM_AUDIO"
    assert nm[("K1901","6")]=="RELAY_COM_AUDIO"
    # Neither preexisting AF/driver isolation nor the audio-mute boundary may collapse.
    assert nm[("J1902","1")]=="AMP_INPUT_MUTED"
    assert nm[("J1302","1")]=="VOL_WIPER_TO_AMP"
    for left,right in (("AF_GND","DRIVER_GND"),("COIL_PLUS_LAB","COIL_MINUS_LAB"),
                       ("METER_RETURN","AF_GND"),("ILLUM_RETURN_LAB","AF_GND"),
                       ("RELAY_COM_AUDIO","AMP_INPUT_MUTED")):
        assert any(net.rsplit("/",1)[-1]==left for net in new),left
        assert any(net.rsplit("/",1)[-1]==right for net in new),right
        assert left!=right
    print("PASS_KICAD9_FRONT_5SHEETS_G5V1_SIX_PHYSICAL_PINS_72_ENDPOINTS_22_NETS_ERC0_CANDIDATE",{
        "original_endpoint_count":len(om),
        "candidate_endpoint_count":len(nm),
        "native_net_count":len(new),
        "all_other_component_pin_to_net_unchanged":True,
        "candidate_relay_pins":candidate_relay,
        "PCB_DRC_performed":False,
        "OEM_coil_contact_hardware_qualified":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True},flush=True)

if __name__=="__main__":
    main()
