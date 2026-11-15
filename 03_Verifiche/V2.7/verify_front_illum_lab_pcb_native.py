#!/usr/bin/env python3
"""Native KiCad9 DRC and schematic-netlist versus routed bench PCB pad parity.

THIS IS A SEPARATE 80x55mm LAB EXERCISE; NOT PCB-FRONT product.
No gerbers, assembly signoff, OEM MPN, harness or real component footprint
measurement. Copper graph crosscheck is independent of PCB DRC.
"""
import re
import subprocess
import tempfile
from pathlib import Path
from verify_interboard_audio_contract_native import exported_nets

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_ILLUM_BENCH"
SCH=BASE/"FRONT_ILLUM_BENCH_V2_7_DRAFT.kicad_sch"
PCB=BASE/"FRONT_ILLUM_BENCH_V2_7_LABONLY.kicad_pcb"

def main():
    board=PCB.read_text(encoding="utf-8")
    assert "(kicad_pcb (version " in board
    assert (BASE/"fp-lib-table").is_file()
    assert (BASE/"FRONT_ILLUM_BENCH_V2_7_LABONLY.kicad_pro").is_file()
    assert (BASE/"TH_FRONT_ILLUM_LAB.pretty/LAB_HEADER_2P54.kicad_mod").is_file()
    assert (BASE/"TH_FRONT_ILLUM_LAB.pretty/LAB_RESISTOR_7P62.kicad_mod").is_file()
    assert (BASE/"TH_FRONT_ILLUM_LAB.pretty/LAB_LED_2P54.kicad_mod").is_file()
    assert board.count("(footprint ")==5
    assert board.count("(pad \"")==10
    assert board.count("(segment ")==12
    assert board.count('(layer "Edge.Cuts")')==1
    assert board.count('(attr through_hole)')==5
    assert '(net 1 "ILLUM_5V_LAB")' in board
    assert '(net 2 "ILLUM_RETURN_LAB")' in board
    assert not any(tok in board for tok in ('(via ', '(zone ', '(pad "" smd', '(model '))

    # Independent candidate pad-map anchored to 5 footprint instances.
    expected={
        "J2201":{("1","ILLUM_5V_LAB"),("2","ILLUM_RETURN_LAB")},
        "R2201":{("1","ILLUM_5V_LAB"),("2","ILLUM_LED1_A")},
        "R2202":{("1","ILLUM_5V_LAB"),("2","ILLUM_LED2_A")},
        "D2201":{("1","ILLUM_RETURN_LAB"),("2","ILLUM_LED1_A")},
        "D2202":{("1","ILLUM_RETURN_LAB"),("2","ILLUM_LED2_A")},
    }
    chunks=board.split("(footprint ")[1:]
    found={}
    by_net={}
    for chunk in chunks:
        ref=re.search(r'\(property "Reference" "([A-Z]\d+)"',chunk)
        assert ref,chunk[:180]
        ref=ref.group(1)
        assert ref in expected and ref not in found
        assert "(attr through_hole)" in chunk
        fp=chunk.split('(layer "F.Cu")',1)[0]
        assert fp.startswith('"TH_FRONT_ILLUM_LAB:LAB_'),fp
        if ref.startswith("J"):
            assert "LAB_HEADER_2P54" in fp
        elif ref.startswith("R"):
            assert "LAB_RESISTOR_7P62" in fp
        elif ref.startswith("D"):
            assert "LAB_LED_2P54" in fp
        pins=set()
        for number,net in re.findall(
                r'\(pad "(\d+)" thru_hole.*?\(net \d+ "([^"]+)"\)',chunk,re.S):
            pins.add((number,net))
            by_net.setdefault(net,set()).add((ref,number))
        found[ref]=pins
    assert found==expected,(found,expected)
    with tempfile.TemporaryDirectory(prefix="tht_illum_pcb_") as temp:
        folder=Path(temp)
        sch_nets=exported_nets(SCH,folder/"schema.net")
        assert set(by_net)==set(sch_nets),(by_net,sch_nets)
        for name,pins in by_net.items():
            assert pins==set(sch_nets[name]),(name,pins,sch_nets[name])
        assert sum(len(p) for p in by_net.values())==10
        rpt=folder/"pcb_drc.rpt"
        cmd=["kicad-cli","pcb","drc","--exit-code-violations","-o",str(rpt),str(PCB)]
        cp=subprocess.run(cmd,cwd=BASE,capture_output=True,text=True,timeout=120)
        print("FRONT_ILLUM_LAB_PCB_DRC_STDOUT",cp.stdout,cp.stderr,flush=True)
        if rpt.exists():
            print("FRONT_ILLUM_LAB_PCB_DRC_REPORT",rpt.read_text(encoding="utf-8"),flush=True)
        cp.check_returncode()
    print("PASS_KICAD9_FRONT_ILLUM_LAB_PCB_DRC0_SCHEMATIC_NETS4_PADS10_THT5_NO_FAB",{
        "footprints":5,"pad_endpoints":10,"nets":4,"routing_segments":12,
        "lab_only_board_outline_mm":"80x55",
        "is_product_FRONT_PCB":False,
        "OEM_pad_geometry_and_board_stackup_qualified":False,
        "NO_FAB_NO_TX":True
    },flush=True)

if __name__=="__main__":
    main()
