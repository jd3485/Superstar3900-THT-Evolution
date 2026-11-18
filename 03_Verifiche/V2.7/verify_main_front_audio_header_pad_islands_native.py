#!/usr/bin/env python3
"""KiCad9 NONFAB pad islands: MAIN audio headers, FRONT AF plus candidate relay.

All physical pad nets are compared with actual hierarchical master KiCad9 nets.
FRONT includes four AF refs and K1901 6-terminal relay footprint placement;
new relay pins remain deliberately unrouted, with no claimed physical mute.
No product board outline, manufacturing DRC or safety qualification.
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
        ("J1902","2"):"AF_GND",
        ("RV1301","1"):"DEMOD_AUDIO",
        ("RV1301","2"):"VOL_WIPER_TO_AMP",
        ("RV1301","3"):"AF_GND",
        ("J1302","1"):"VOL_WIPER_TO_AMP",
        ("J1302","2"):"AF_GND",
        ("K1901","1"):"AF_GND",
        ("K1901","2"):"COIL_PLUS_LAB",
        ("K1901","5"):"RELAY_COM_AUDIO",
        ("K1901","6"):"RELAY_COM_AUDIO",
        ("K1901","9"):"COIL_MINUS_LAB",
        ("K1901","10"):"VOL_WIPER_TO_AMP"}),
}
FOOTPRINT="Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical"

def main():
    with tempfile.TemporaryDirectory(prefix="tht_2pcb_af_pad_islands_") as td:
        d=Path(td)
        for board,(sch,pcb,wanted) in BOARDS.items():
            assert pcb.with_suffix(".kicad_pro").is_file()
            raw=pcb.read_text(encoding="utf8")
            assert raw.startswith("(kicad_pcb (version 20241229)")
            assert raw.count('(footprint "'+FOOTPRINT+'"')==(
                2 if board=="MAIN" else 3)
            assert raw.count('(footprint "TH_MUTE_OEM_CANDIDATE:G5V-1_DC5_OEM_6PIN_CANDIDATE"')==(0 if board=="MAIN" else 1)
            assert raw.count('(footprint "TH_FRONT:Potentiometer_THT_3Pin_PROVISIONAL"')==(
                0 if board=="MAIN" else 1)
            assert raw.count('(pad "1" thru_hole')==(2 if board=="MAIN" else 5)
            assert raw.count('(pad "2" thru_hole')==(2 if board=="MAIN" else 5)
            assert raw.count('(pad "3" thru_hole')==(0 if board=="MAIN" else 1)
            for pin in ("5","6","9","10"):
                assert raw.count('(pad "'+pin+'" thru_hole')==(0 if board=="MAIN" else 1)
            segments=re.findall(
                r'\(segment \(start ([\d.]+) ([\d.]+)\) '
                r'\(end ([\d.]+) ([\d.]+)\) '
                r'\(width ([\d.]+)\) \(layer "([^"]+)"\) '
                r'\(net (\d+)\) \(uuid "([^"]+)"\)\)',raw)
            assert raw.count("(segment ")==len(segments)
            if board=="FRONT":
                expected_routes=[
                    (2,"F.Cu",(40,47.54),(90,47.54)),
                    (1,"F.Cu",(40,45),(40,40)),
                    (1,"F.Cu",(40,40),(50,40)),
                    (1,"F.Cu",(50,40),(50,35)),
                    (1,"F.Cu",(50,35),(58,35)),
                    (4,"B.Cu",(60.54,35),(60.54,28)),
                    (4,"B.Cu",(60.54,28),(75,28)),
                    (4,"B.Cu",(75,28),(75,35)),
                    (2,"F.Cu",(63.08,35),(63.08,47.54)),
                    (2,"F.Cu",(75,37.54),(75,47.54)),
                ]
                def ordered(net,layer,a,c):
                    return (net,layer,tuple(sorted((a,c))))
                actual=[ordered(int(net),layer,
                    (float(x1),float(y1)),(float(x2),float(y2)))
                    for x1,y1,x2,y2,width,layer,net,uuid in segments
                    if float(width)==0.5]
                assert len(segments)==len(actual)==10
                assert sorted(actual)==sorted(ordered(*row) for row in expected_routes),(
                    "FRONT unapproved copper geometry",actual)
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
            assert len(pcb_net)==(5 if board=="MAIN" else 8)
            pads={}
            blocks=raw.split('\n(footprint "')[1:]
            assert len(blocks)==(2 if board=="MAIN" else 5)
            refs=set()
            for block in blocks:
                refmatch=re.search(r'\(property "Reference" "([^"]+)"',block)
                assert refmatch,block[:200]
                ref=refmatch.group(1)
                assert ref not in refs
                refs.add(ref)
                assert "(attr through_hole)" in block
                assert (("TH_FRONT:Potentiometer_THT_3Pin_PROVISIONAL" if ref=="RV1301"
                    else "TH_MUTE_OEM_CANDIDATE:G5V-1_DC5_OEM_6PIN_CANDIDATE" if ref=="K1901"
                    else FOOTPRINT)) in block.split('"',1)[0]
                allpads=re.findall(
                    r'\(pad "(\d+)" thru_hole (?:rect|circle) \(at [^)]+\) '
                    r'\(size [^)]+\) \(drill [^)]+\) '
                    r'\(layers "\*\.Cu" "\*\.Mask"\) '
                    r'\(net (\d+) "([^"]+)"\)',block)
                assert len(allpads)==(6 if ref=="K1901" else 3 if ref=="RV1301" else 2),(board,ref,allpads)
                for pin,net_id,netname in allpads:
                    assert pcb_net[netname]==int(net_id)
                    assert (ref,pin) not in pads,(board,ref,pin)
                    pads[(ref,pin)]=netname
            assert pads==wanted,(board,pads,wanted)
            if board=="FRONT":
                expected_relay={"1":("AF_GND",80,55),"2":("COIL_PLUS_LAB",80,57.54),
                    "5":("RELAY_COM_AUDIO",80,65.16),"10":("VOL_WIPER_TO_AMP",85.08,55),
                    "9":("COIL_MINUS_LAB",85.08,57.54),"6":("RELAY_COM_AUDIO",85.08,65.16)}
                relay_block=next(b for b in blocks if '(property "Reference" "K1901"' in b)
                for pad,(net,x,y) in expected_relay.items():
                    assert pads[("K1901",pad)]==net
                    localx,localy=x-80,y-55
                    assert f'(pad "{pad}" thru_hole' in relay_block
                    assert f'(at {localx:g} {localy:g})' in relay_block

                # K1901 must remain electrically unrouted in this revision.
                assert not any(int(n) in (5,6,7) for *_,n,uuid in segments)
            if board=="FRONT":
                # All 9 physical THT pads from the four provisional footprints.
                from math import hypot
                physical={
                    ("J1301","1"):((40.,45.),1.,1),
                    ("J1301","2"):((40.,47.54),1.,2),
                    ("J1902","1"):((90.,45.),1.,3),
                    ("J1902","2"):((90.,47.54),1.,2),
                    ("RV1301","1"):((58.,35.),.9,1),
                    ("RV1301","2"):((60.54,35.),.9,4),
                    ("RV1301","3"):((63.08,35.),.9,2),
                    ("J1302","1"):((75.,35.),1.,4),
                    ("J1302","2"):((75.,37.54),1.,2),
                }
                assert set(physical)==set(wanted)
                wires=[(int(net),(float(x1),float(y1)),(float(x2),float(y2)),
                        float(width),layer)
                       for x1,y1,x2,y2,width,layer,net,uuid in segments]
                def dist(pt,a,c):
                    dx,dy=c[0]-a[0],c[1]-a[1]
                    length=dx*dx+dy*dy
                    assert length>0
                    t=max(0.,min(1.,((pt[0]-a[0])*dx+(pt[1]-a[1])*dy)/length))
                    return hypot(pt[0]-a[0]-t*dx,pt[1]-a[1]-t*dy)
                # THT pads exist on both F.Cu and B.Cu: cross-net tracks
                # must stay >= 0.20 mm apart from every foreign pad rim.
                for net,a,c,width,layer in wires:
                    for point,rad,pad_net in physical.values():
                        if net!=pad_net:
                            assert dist(point,a,c)-rad-width/2>=0.2-1e-8,(
                                "Copper shorts or crowds a foreign pad",
                                net,pad_net,a,c,point,layer)
                # Ensure all connected schematic pad sets are actually
                # linked by copper; copper endpoints may join mid-segment.
                def onseg(pt,a,c):
                    return dist(pt,a,c)<1e-7
                for net in (1,2,4):
                    group=[(a,c) for n,a,c,w,layer in wires if n==net]
                    required=[point for point,rad,n in physical.values() if n==net]
                    assert group and len(required)>=2
                    reachable={0}
                    changed=True
                    while changed:
                        changed=False
                        for i,(a,c) in enumerate(group):
                            if i in reachable:continue
                            if any(onseg(a,x,y) or onseg(c,x,y) or
                                   onseg(x,a,c) or onseg(y,a,c)
                                   for j,(x,y) in enumerate(group) if j in reachable):
                                reachable.add(i);changed=True
                    assert len(reachable)==len(group),(net,"unconnected copper",reachable)
                    assert all(any(onseg(pt,a,c) for a,c in group) for pt in required),(
                        net,"unattached THT pad",required)
                # K1901 is now placed but unrouted: detect any legacy copper
                # crossing its six plated through-hole pads on either layer.
                for pad,(net,x,y) in expected_relay.items():
                    for tracknet,a,c,width,layer in wires:
                        if tracknet!=net:
                            assert dist((x,y),a,c)-1.0-width/2>=0.2-1e-8,(
                                "K1901 foreign-net copper clearance",pad,tracknet)
                # AMP_INPUT_MUTED is a separate pad; post-mute path not routed.
                assert not any(n==3 for n,a,c,w,layer in wires)
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
            assert len(refs)==(2 if board=="MAIN" else 5)
            assert len(pads)==(4 if board=="MAIN" else 15)
    print("PASS_KICAD9_MAIN_FRONT_TWO_SEPARATE_NONFAB_AUDIO_PCB_PAD_ISLANDS_4REF_8THT_PADS",{
        "MAIN":("J1502","J1202"),
        "FRONT":("J1301","J1902","RV1301","J1302","K1901"),
        "independent_MAIN_nets":4,
        "independent_FRONT_nets":3,
        "shared_FRONT_AF_GND_pad_assignments":4,
        "FRONT_volume_to_wiper_10_physical_segments":True,
        "all_pads_mapped_to_native_schematic_labels":True,
        "native_kicad9_pos_export_both_islands":True,
        "no_edge_no_vias_no_extra_components":True,
        "FRONT_AF_GND_copper_branched_to_volume_and_header":True,
        "MAIN_returns_unrouted_and_isolated":True,
        "production_DRC_and_routing_claimed":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True},flush=True)

if __name__=="__main__":
    main()
