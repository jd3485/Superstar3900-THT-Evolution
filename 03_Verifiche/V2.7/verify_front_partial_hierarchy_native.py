#!/usr/bin/env python3
"""KiCad9 hierarchical FRONT integration pilot, five real THT sheets with four explicit inter-sheet nets.

Intended future FRONT parent but NOT an approved product schematic: existing
volume, LED, S-meter, relay contact and dual NPN coil driver sheets are included without making power,
return, cable or S-meter driver electrical interconnections. Fail on ERC violations
and accidental net merging across child pages.
"""
from pathlib import Path
import re
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
SCH=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_CONTROL_PARTIAL_V2_7_DRAFT.kicad_sch"
CHILDREN=(
    ROOT/"04_KiCad/V2.7_DRAFT/FRONT_VOLUME/FRONT_VOLUME_THT_V2_7_DRAFT.kicad_sch",
    ROOT/"04_KiCad/V2.7_DRAFT/FRONT_ILLUM_BENCH/FRONT_ILLUM_BENCH_V2_7_DRAFT.kicad_sch",
    ROOT/"04_KiCad/V2.7_DRAFT/FRONT_SMETER/FRONT_SMETER_THT_V2_7_DRAFT.kicad_sch",
    ROOT/"04_KiCad/V2.7_DRAFT/FRONT_MUTE_NC_RELAY/FRONT_NC_MUTE_CONTACT_THT_V2_7_DRAFT.kicad_sch",
    ROOT/"04_KiCad/V2.7_DRAFT/FRONT_MUTE_COIL_DRIVER/FRONT_NC_MUTE_DUAL_ENABLE_COIL_DRIVER_V2_7_DRAFT.kicad_sch",
)
PARTITIONS={
    "DEMOD_AUDIO":{("J1301","1"),("RV1301","1")},
    "AF_GND":{("J1301","2"),("RV1301","3"),("J1302","2")},
    "VOL_WIPER_TO_AMP":{("RV1301","2"),("J1302","1")},
    "ILLUM_5V_LAB":{("J2201","1"),("R2201","1"),("R2202","1")},
    "ILLUM_RETURN_LAB":{("J2201","2"),("D2201","1"),("D2202","1")},
    "ILLUM_LED1_A":{("R2201","2"),("D2201","2")},
    "ILLUM_LED2_A":{("R2202","2"),("D2202","2")},
    "METER_DRIVE_CANDIDATE":{("J1801","1"),("RV1801","1")},
    "METER_TRIM_OUTPUT":{("RV1801","2"),("R1801","1")},
    "METER_LIMIT_STAGE1":{("R1801","2"),("R1802","1")},
    "METER_POS_LIMITED":{("R1802","2"),("J1802","1")},
    "METER_RETURN":{("J1801","2"),("RV1801","3"),("J1802","2")},
    "AMP_INPUT_MUTED":{("J1902","1"),("R1901","1"),("R1902","2")},
    "RELAY_COM_AUDIO":{("K1901","1"),("R1902","1")},
    "COIL_PLUS_LAB":{("K1901","4"),("J1903","1")},
    "COIL_MINUS_LAB":{("K1901","5"),("J1903","2")},
    "SERIES_MID":{("Q1911","3"),("Q1912","1"),("R1913","2")},
    "DRIVER_GND":{("Q1912","3"),("R1914","2"),("J1911","2"),("J1912","2"),("J1913","2"),("C1911","2"),("C1912","2")},
    "DRIVE1_BASE":{("Q1911","2"),("R1911","2"),("R1913","1")},
    "DRIVE2_BASE":{("Q1912","2"),("R1912","2"),("R1914","1")},
    "ENABLE_AUDIO_LAB":{("J1912","1"),("R1911","1")},
    "POWER_GOOD_LAB":{("J1913","1"),("R1912","1")},
}


def verify():
    sch=SCH.read_text(encoding="utf-8")
    assert sch.count("(sheet (at ")==5
    assert sch.count('(property "Sheetfile"')==5
    assert "FRONT_VOLUME/FRONT_VOLUME_THT_V2_7_DRAFT.kicad_sch" in sch
    assert "FRONT_ILLUM_BENCH/FRONT_ILLUM_BENCH_V2_7_DRAFT.kicad_sch" in sch
    assert "FRONT_SMETER/FRONT_SMETER_THT_V2_7_DRAFT.kicad_sch" in sch
    assert "FRONT_MUTE_NC_RELAY/FRONT_NC_MUTE_CONTACT_THT_V2_7_DRAFT.kicad_sch" in sch
    assert "FRONT_MUTE_COIL_DRIVER/FRONT_NC_MUTE_DUAL_ENABLE_COIL_DRIVER_V2_7_DRAFT.kicad_sch" in sch
    assert all(x.exists() for x in CHILDREN)
    project=SCH.with_suffix(".kicad_pro")
    symtab=SCH.parent/"sym-lib-table"
    fptab=SCH.parent/"fp-lib-table"
    assert project.is_file() and symtab.is_file() and fptab.is_file()
    sym=symtab.read_text(encoding="utf-8")
    fp=fptab.read_text(encoding="utf-8")
    for item in ("TH_FRONT", "TH_FRONT_ILLUM", "TH_SMETER", "TH_AUDIO", "TH_MUTE", "TH_COIL"):
        assert '(name "'+item+'")' in sym,item
    for item in ("TH_FRONT", "TH_FRONT_ILLUM_LAB"):
        assert '(name "'+item+'")' in fp,item
    assert sch.count("(wire (pts ")==10 and "(junction " not in sch
    assert sch.count('(pin "VOL_WIPER_TO_AMP" passive')==2
    assert sch.count('(pin "AF_GND" passive')==2
    assert sch.count('(pin "COIL_PLUS_LAB" passive')==2
    assert sch.count('(pin "COIL_MINUS_LAB" passive')==2
    assert sch.count('(pin "METER_DRIVE_CANDIDATE" passive')==1
    assert sch.count('(pin "METER_RETURN" passive')==1
    assert sch.count('(label "METER_DRIVE_CANDIDATE"')==1
    assert sch.count('(label "METER_RETURN"')==1
    assert '<escape>' not in sch
    assert "NO FAB / NO TX" in sch
    with tempfile.TemporaryDirectory(prefix="tht_front_partial_hierarchy_") as temp:
        d=Path(temp)
        erc=d/"erc.rpt"
        cp=subprocess.run(["kicad-cli","sch","erc","--exit-code-violations",
                           "-o",str(erc),str(SCH)],cwd=ROOT,capture_output=True,text=True,timeout=120)
        print("FRONT_PARTIAL_HIERARCHY_ERC_STDOUT",cp.stdout,cp.stderr,flush=True)
        if erc.exists():
            print("FRONT_PARTIAL_HIERARCHY_ERC_REPORT",erc.read_text(encoding="utf-8"),flush=True)
        cp.check_returncode()
        net=d/"front.net"
        cp=subprocess.run(["kicad-cli","sch","export","netlist","-o",str(net),str(SCH)],
            cwd=ROOT,capture_output=True,text=True,timeout=120)
        print("FRONT_PARTIAL_HIERARCHY_EXPORT",cp.stdout,cp.stderr,flush=True)
        cp.check_returncode()
        raw=net.read_text(encoding="utf-8")
    assert "(nets" in raw
    # Hierarchical local net names are sheet-prefixed; ensure no new
    # unintentional tie between audio/AGC and LED switching return.
    blocks=raw.rsplit("(nets",1)[1]
    headers=list(re.finditer(
        r'\(net\s+\(code\s+"?\d+"?\)\s+\(name\s+"([^"]+)"\)',blocks))
    found={}
    for i,h in enumerate(headers):
        block=blocks[h.end():headers[i+1].start() if i+1<len(headers) else len(blocks)]
        members=set(re.findall(
            r'\(node\s+\(ref\s+"([^"]+)"\)\s+\(pin\s+"([^"]+)"\)',block))
        label=h.group(1).rsplit("/",1)[-1]
        found.setdefault(label,[]).append(members)
    assert set(found)==set(PARTITIONS),(found.keys(),PARTITIONS.keys())
    joined={
        "AF_GND":{("J1301","2"),("RV1301","3"),("J1302","2"),
                  ("K1901","2"),("J1901","2"),("J1902","2"),("R1901","2")},
        "VOL_WIPER_TO_AMP":{("RV1301","2"),("J1302","1"),("K1901","3"),("J1901","1")},
        "COIL_PLUS_LAB":{("K1901","4"),("J1903","1"),("J1911","1"),("D1911","1"),("J1914","1"),("C1911","1"),("C1912","1")},
        "COIL_MINUS_LAB":{("K1901","5"),("J1903","2"),("J1914","2"),("D1911","2"),("Q1911","1")},
    }
    for name,expected in PARTITIONS.items():
        candidates=found[name]
        if name in joined:
            assert candidates==[joined[name]],(name,candidates,joined[name])
            continue
        assert candidates==[expected],(name,candidates,expected)
    all_nets=[pins for group in found.values() for pins in group]
    assert len(all_nets)==22,len(all_nets)
    assert len(set().union(*all_nets))==sum(map(len,all_nets))==71
    assert all(len(found[name])==1 for name in joined)
    assert found["COIL_PLUS_LAB"][0].isdisjoint(found["COIL_MINUS_LAB"][0])
    assert found["METER_DRIVE_CANDIDATE"][0].isdisjoint(found["METER_RETURN"][0])
    assert found["METER_RETURN"][0].isdisjoint(found["AF_GND"][0])
    assert found["METER_RETURN"][0].isdisjoint(found["DRIVER_GND"][0])
    assert found["METER_RETURN"][0].isdisjoint(found["ILLUM_RETURN_LAB"][0])
    assert found["DRIVER_GND"][0].isdisjoint(found["AF_GND"][0])
    assert found["ILLUM_RETURN_LAB"][0].isdisjoint(found["DRIVER_GND"][0])
    print("PASS_KICAD9_FRONT_HIERARCHY_5SHEETS_32REFS_22NETS_71PINS_4REAL_AUDIO_COIL_JOINS_ERC0_NONFAB",{
        "child_sheets":5,
        "THT_components":32,
        "hierarchical_nets":22,
        "actual_volume_to_mute_signal_and_AF_GND_connections":2,
        "actual_coil_plus_minus_connections":2,
        "pin_endpoints":71,
        "relay_oem_qualified":False,
        "relay_coil_interconnected_in_parent":True,
        "relay_coil_qualified_for_product":False,
        "MAIN_FRONT_harness_qualified":False,
        "S_meter_passive_candidate_sheet_included":True,
        "S_meter_two_native_hierarchical_ports_present":True,
        "S_meter_return_AF_GND_joined":False,
        "S_meter_driver_FSD_coil_qualified":False,
        "hardware_production_PCB_exists":False,
        "NO_FAB_NO_TX":True,
    },flush=True)


if __name__=="__main__":
    verify()
