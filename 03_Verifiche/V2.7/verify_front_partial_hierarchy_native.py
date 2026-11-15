#!/usr/bin/env python3
"""KiCad9 hierarchical FRONT integration pilot, two isolated real THT sheets.

Intended future FRONT parent but NOT an approved product schematic: existing
volume and lab illumination sheets are included without making any power,
return, cable or S-meter electrical interconnections. Fail on ERC violations
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
)
PARTITIONS={
    "DEMOD_AUDIO":{("J1301","1"),("RV1301","1")},
    "AF_GND":{("J1301","2"),("RV1301","3"),("J1302","2")},
    "VOL_WIPER_TO_AMP":{("RV1301","2"),("J1302","1")},
    "ILLUM_5V_LAB":{("J2201","1"),("R2201","1"),("R2202","1")},
    "ILLUM_RETURN_LAB":{("J2201","2"),("D2201","1"),("D2202","1")},
    "ILLUM_LED1_A":{("R2201","2"),("D2201","2")},
    "ILLUM_LED2_A":{("R2202","2"),("D2202","2")},
}


def verify():
    sch=SCH.read_text(encoding="utf-8")
    assert sch.count("(sheet (at ")==2
    assert sch.count('(property "Sheetfile"')==2
    assert "FRONT_VOLUME/FRONT_VOLUME_THT_V2_7_DRAFT.kicad_sch" in sch
    assert "FRONT_ILLUM_BENCH/FRONT_ILLUM_BENCH_V2_7_DRAFT.kicad_sch" in sch
    assert all(x.exists() for x in CHILDREN)
    assert "(wire " not in sch and "(junction " not in sch
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
        assert label not in found,(label,"duplicate or tied logical net")
        found[label]=members
    assert set(found)==set(PARTITIONS),(found.keys(),PARTITIONS.keys())
    for name,expected in PARTITIONS.items():
        assert found[name]==expected,(name,found[name],expected)
    assert len(set().union(*found.values()))==sum(len(v) for v in found.values())==18
    print("PASS_KICAD9_FRONT_PARTIAL_HIERARCHY_2SHEETS_8REFS_7NETS_18PINS_ERC0_NO_CROSS_RAIL_NO_FAB",{
        "child_sheets":2,
        "THT_components":8,
        "independent_local_nets":7,
        "pin_endpoints":18,
        "MAIN_FRONT_harness_qualified":False,
        "S_meter_integrated":False,
        "hardware_production_PCB_exists":False,
        "NO_FAB_NO_TX":True,
    },flush=True)


if __name__=="__main__":
    verify()
