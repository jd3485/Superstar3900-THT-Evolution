#!/usr/bin/env python3
"""KiCad9 isolated NONFAB physical pads on each PCB, two audio headers each.

Each pad-net uses the label of its actual MAIN/FRONT master netlist, with
physical connector ref/pin and installed thru-hole pad mapping. These islands
contain ONLY four connector pads each, NOT the complete assembled PCBs.
NO board edge, zones, physical interboard cable or production DRC. FRONT\ncontains ONLY one real F.Cu AF_GND conductor between the two return pads;\nMAIN still contains no copper at all.
"""
from pathlib import Path
from collections import defaultdict
import re
import subprocess
import tempfile
from verify_interboard_audio_contract_native import exported_nets
from verify_main_front_dual_af_harness_native import MAIN,FRONT,unique_net

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"04_KiCad/V2.7_DRAFT"
BOARDS={
    "MAIN":(MAIN,BASE/"MAIN_AUDIO_2HEADER_PAD_ISLAND_NONFAB.kicad_pcb",{
        ("J1502","1"):"AM_DEMOD_AF_BENCH",
        ("J1502","2"):"IF_BENCH_GND",
        ("J1202","1"):"AUDIO_IN",
        ("J1202","2"):"GND"}),
    "FRONT":(FRONT,BASE/"FRONT_AUDIO_2HEADER_PAD_ISLAND_NONFAB.kicad_pcb",{
        ("J1301","1"):"DEMOD_AUDIO",
        ("J1301","2"):"AF_GND",
        ("J1902","1"):"AMP_INPUT_MUTED",
        ("J1902","2"):"AF_GND"}),
}
FOOTPRINT="Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical"

def main():
    with tempfile.TemporaryDirectory(prefix="tht_2pcb_af_pad_islands_") as td:
        d=Path(td)
        for board,(sch,pcb,wanted) in BOARDS.items():
            assert pcb.with_suffix(".kicad_pro").is_file()
            raw=pcb.read_text(encoding="utf8")
            assert raw.startswith("(kicad_pcb (version 20241229)")
            assert raw.count('(footprint "'+FOOTPRINT+'"')==2
            assert raw.count('(pad "1" thru_hole')==2
            assert raw.count('(pad "2" thru_hole')==2
            segments=re.findall(
                r'\(segment \(start ([\d.]+) ([\d.]+)\) '
                r'\(end ([\d.]+) ([\d.]+)\) '
                r'\(width ([\d.]+)\) \(layer "([^"]+)"\) '
                r'\(net (\d+)\) \(uuid "([^"]+)"\)\)',raw)
            assert raw.count("(segment ")==len(segments)
            if board=="FRONT":
                assert len(segments)==1,("Unexpected extra copper segments",segments)
                x1,y1,x2,y2,width,layer,net,uuid=segments[0]
                assert (float(x1),float(y1),float(x2),float(y2))==(
                    40.0,47.54,90.0,47.54),segments
                assert float(width)==0.5 and layer=="F.Cu" and net=="2"
                # Two return pads are at (40,47.54) and (90,47.54),
                # two separate signal pads at y=45. A straight F.Cu
                # trace 0.5 mm wide stays >= 1.29 mm edge-to-edge
                # from each 2 mm wide signal pad (2.54-1-0.25).
                assert min(abs(45.0-float(y1)),abs(45.0-float(y2)))-1.0-float(width)/2>=1.29
            else:
                assert not segments,("MAIN IF and LM386 returns must stay isolated",segments)
            assert raw.count("(via ")==0
            assert "(zone " not in raw and '(layer "Edge.Cuts")' not in raw
            assert "(gr_rect " not in raw and "(gr_poly " not in raw
            assert "NO DRC0 / NO FAB / NO TX" in raw
            pcb_net={name:int(num) for num,name in
                re.findall(r'^\(net (\d+) "([^"]*)"\)$',raw,re.M)}
            assert pcb_net.get("")==0
            assert set(pcb_net)-{""}==set(wanted.values())
            assert len(pcb_net)==(5 if board=="MAIN" else 4)
            pads={}
            blocks=raw.split('\n(footprint "')[1:]
            assert len(blocks)==2
            refs=set()
            for block in blocks:
                refmatch=re.search(r'\(property "Reference" "([^"]+)"',block)
                assert refmatch,block[:200]
                ref=refmatch.group(1)
                assert ref not in refs
                refs.add(ref)
                assert "(attr through_hole)" in block
                assert FOOTPRINT in block.split('"',1)[0]
                allpads=re.findall(
                    r'\(pad "(\d+)" thru_hole (?:rect|circle) \(at [^)]+\) '
                    r'\(size [^)]+\) \(drill [^)]+\) '
                    r'\(layers "\*\.Cu" "\*\.Mask"\) '
                    r'\(net (\d+) "([^"]+)"\)',block)
                assert len(allpads)==2,(board,ref,allpads)
                for pin,net_id,netname in allpads:
                    assert pcb_net[netname]==int(net_id)
                    assert (ref,pin) not in pads,(board,ref,pin)
                    pads[(ref,pin)]=netname
            assert pads==wanted,(board,pads,wanted)
            nets=exported_nets(sch,d/(board+".net"))
            for endpoint,netname in wanted.items():
                matches=[name for name,members in nets.items()
                         if endpoint in members]
                assert len(matches)==1,(board,endpoint,matches)
                # KiCad hierarchy names may be absolute paths. Preserve
                # the pin net's leaf name, never silently join unlike nets.
                assert matches[0].rsplit("/",1)[-1]==netname,(
                    board,endpoint,matches,netname)
            # KiCad9 must successfully parse the actual physical board
            # and export both footprint placements.
            out=d/(board+".pos")
            cp=subprocess.run(["kicad-cli","pcb","export","pos",
                "--format","ascii","--side","front","-o",str(out),str(pcb)],
                cwd=ROOT,capture_output=True,text=True,timeout=120)
            print(board+"_PAD_ISLAND_NATIVE_POS",cp.returncode,
                  cp.stdout,cp.stderr,flush=True)
            cp.check_returncode()
            positions=out.read_text(encoding="utf8")
            for ref in refs:
                assert re.search(r'(?m)^\s*'+re.escape(ref)+r'\s',positions),(board,ref)
            assert len(refs)==2 and len(pads)==4
    print("PASS_KICAD9_MAIN_FRONT_TWO_SEPARATE_NONFAB_AUDIO_PCB_PAD_ISLANDS_4REF_8THT_PADS",{
        "MAIN":("J1502","J1202"),
        "FRONT":("J1301","J1902"),
        "independent_MAIN_nets":4,
        "independent_FRONT_nets":3,
        "shared_FRONT_AF_GND_pad_assignments":2,
        "all_pads_mapped_to_native_schematic_labels":True,
        "native_kicad9_pos_export_both_islands":True,
        "no_edge_no_vias_no_extra_components":True,\n        "FRONT_AF_GND_routed_on_F_Cu_once":True,\n        "MAIN_returns_unrouted_and_isolated":True,
        "production_DRC_and_routing_claimed":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True},flush=True)

if __name__=="__main__":
    main()
