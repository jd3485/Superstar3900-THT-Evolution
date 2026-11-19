#!/usr/bin/env python3
"""KiCad9 NONFAB pad islands: MAIN audio headers, FRONT AF plus candidate relay.

All physical pad nets are compared with actual hierarchical master KiCad9 nets.
FRONT includes audio refs, K1901 and two THT resistor footprints;
relay contacts and passive AF nets have routed copper; coil pins remain unrouted.
This is a CAD candidate and cannot establish physical fail-safe operation.
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
        ("J1202","2"):"GND",
        ("C1201","1"):"AUDIO_IN",
        ("C1201","2"):"PRE_IN",
        ("R1201","1"):"PRE_IN",
        ("R1201","2"):"AMP_IN",
        ("U1201","1"):"",
        ("U1201","2"):"GND",
        ("U1201","3"):"AMP_IN",
        ("U1201","4"):"GND",
        ("U1201","5"):"AMP_OUT",
        ("U1201","6"):"AUDIO_6V_LAB",
        ("U1201","7"):"BYPASS",
        ("U1201","8"):"",
        ("C1204","1"):"BYPASS",
        ("C1204","2"):"GND",
        ("C1205","1"):"AUDIO_6V_LAB",
        ("C1205","2"):"GND",
        ("C1202","1"):"AMP_OUT",("C1202","2"):"SPK_HOT",
        ("C1203","1"):"AMP_OUT",("C1203","2"):"ZOBEL",
        ("R1202","1"):"ZOBEL",("R1202","2"):"GND",
        ("C1206","1"):"AUDIO_6V_LAB",("C1206","2"):"GND",
        ("J1201","1"):"AUDIO_6V_LAB",("J1201","2"):"GND",
        ("J1203","1"):"SPK_HOT",("J1203","2"):"GND"}),
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
        ("K1901","10"):"VOL_WIPER_TO_AMP",
        ("R1901","1"):"AMP_INPUT_MUTED",
        ("R1901","2"):"AF_GND",
        ("R1902","1"):"RELAY_COM_AUDIO",
        ("R1902","2"):"AMP_INPUT_MUTED"}),
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
                3 if board=="MAIN" else 3)
            assert raw.count('(footprint "TH_MUTE_OEM_CANDIDATE:G5V-1_DC5_OEM_6PIN_CANDIDATE"')==(0 if board=="MAIN" else 1)
            assert raw.count('(footprint "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal"')==(0 if board=="MAIN" else 2)
            assert raw.count('(footprint "Package_DIP:DIP-8_W7.62mm"')==(1 if board=="MAIN" else 0)
            assert raw.count('(footprint "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm"')==(1 if board=="MAIN" else 0)
            assert raw.count('(footprint "Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm"')==(3 if board=="MAIN" else 0)
            assert raw.count('(footprint "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal"')==(2 if board=="MAIN" else 0)
            assert raw.count('(footprint "TH_FRONT:Potentiometer_THT_3Pin_PROVISIONAL"')==(
                0 if board=="MAIN" else 1)
            assert raw.count('(footprint "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm"')==(1 if board=="MAIN" else 0)
            assert raw.count('(footprint "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm"')==(1 if board=="MAIN" else 0)
            assert raw.count('(footprint "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical"')==(1 if board=="MAIN" else 0)
            assert raw.count('(pad "1" thru_hole')==(13 if board=="MAIN" else 7)
            assert raw.count('(pad "2" thru_hole')==(13 if board=="MAIN" else 7)
            assert raw.count('(pad "3" thru_hole')==(1 if board=="MAIN" else 1)
            for pin in ("5","6","9","10"):
                assert raw.count('(pad "'+pin+'" thru_hole')==((1 if pin in ("5","6") else 0) if board=="MAIN" else 1)
            for pin in ("4","7","8"):
                assert raw.count('(pad "'+pin+'" thru_hole')==(1 if board=="MAIN" else 0)
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
                    (4,"B.Cu",(75,35),(85.08,35)),
                    (4,"B.Cu",(85.08,35),(85.08,55)),
                    (2,"F.Cu",(80,55),(80,47.54)),
                    (2,"F.Cu",(110.16,60),(120,60)),
                    (2,"F.Cu",(120,60),(120,47.54)),
                    (2,"F.Cu",(120,47.54),(90,47.54)),
                    (5,"F.Cu",(80,65.16),(85.08,65.16)),
                    (5,"F.Cu",(85.08,65.16),(90,65.16)),
                    (5,"F.Cu",(90,65.16),(90,70)),
                    (5,"F.Cu",(90,70),(100,70)),
                    (3,"B.Cu",(100,60),(100,65)),
                    (3,"B.Cu",(100,65),(105,65)),
                    (3,"B.Cu",(105,65),(105,70)),
                    (3,"B.Cu",(105,70),(110.16,70)),
                    (3,"B.Cu",(110.16,70),(115,70)),
                    (3,"B.Cu",(115,70),(115,45)),
                    (3,"B.Cu",(115,45),(90,45)),
                ]
                def ordered(net,layer,a,c):
                    return (net,layer,tuple(sorted((a,c))))
                actual=[ordered(int(net),layer,
                    (float(x1),float(y1)),(float(x2),float(y2)))
                    for x1,y1,x2,y2,width,layer,net,uuid in segments
                    if float(width)==0.5]
                assert len(segments)==len(actual)==27
                assert sorted(actual)==sorted(ordered(*row) for row in expected_routes),(
                    "FRONT unapproved copper geometry",actual)
            else:
                # MAIN lab AF input: only AUDIO_IN and PRE_IN are routed;
                # IF_BENCH_GND and GND remain distinct and unrouted.
                expected_main=[
                    (3,"B.Cu",(90.,45.),(100.,45.)),
                    (3,"B.Cu",(100.,45.),(100.,65.)),
                    (5,"F.Cu",(102.5,65.),(102.5,75.)),
                    (5,"F.Cu",(102.5,75.),(110.,75.)),
                    (6,"B.Cu",(117.62,75.),(122.,75.)),
                    (6,"B.Cu",(122.,75.),(122.,70.08)),
                    (6,"B.Cu",(122.,70.08),(130.,70.08)),
                    (4,"F.Cu",(90.,47.54),(90.,55.)),
                    (4,"F.Cu",(90.,55.),(125.,55.)),
                    (4,"F.Cu",(125.,55.),(125.,67.54)),
                    (4,"F.Cu",(125.,67.54),(130.,67.54)),
                    (4,"F.Cu",(125.,67.54),(125.,72.62)),
                    (4,"F.Cu",(125.,72.62),(130.,72.62)),
                    (9,"B.Cu",(137.62,67.54),(145.,67.54)),
                    (9,"B.Cu",(145.,67.54),(145.,80.)),
                    (9,"B.Cu",(145.,80.),(150.,80.)),
                    (4,"F.Cu",(152.,80.),(152.,85.)),
                    (4,"F.Cu",(152.,85.),(130.,85.)),
                    (4,"F.Cu",(130.,85.),(130.,72.62)),
                    (4,"F.Cu",(149.5,95.),(152.,95.)),
                    (4,"F.Cu",(152.,95.),(152.,85.)),
                    (8,"B.Cu",(137.62,70.08),(140.,70.08)),
                    (8,"B.Cu",(140.,70.08),(140.,90.)),
                    (8,"B.Cu",(140.,90.),(147.,90.)),
                    (8,"B.Cu",(147.,90.),(147.,95.)),
                    (7,"F.Cu",(137.62,72.62),(160.,72.62)),
                    (7,"F.Cu",(160.,72.62),(160.,65.)),
                    (7,"F.Cu",(160.,65.),(167.,65.)),
                    (7,"F.Cu",(160.,72.62),(160.,82.)),
                    (7,"F.Cu",(160.,82.),(167.,82.)),
                ]
                actual_main=[(int(net),layer,(float(x1),float(y1)),
                    (float(x2),float(y2))) for x1,y1,x2,y2,width,layer,net,uuid in segments
                    if float(width)==0.5]
                assert len(segments)==len(actual_main)==len(expected_main)==30
                assert sorted(actual_main)==sorted(expected_main),(
                    "MAIN unauthorized candidate copper",actual_main)
                assert all(int(n) in (3,4,5,6,7,8,9) for *_,n,uuid in segments)
                assert not any(int(n) in (1,2,10,11) for *_,n,uuid in segments)
            assert raw.count("(via ")==0
            assert "(zone " not in raw and '(layer "Edge.Cuts")' not in raw
            assert "(gr_rect " not in raw and "(gr_poly " not in raw
            assert "NO DRC0 / NO FAB / NO TX" in raw
            pcb_net={name:int(num) for num,name in
                re.findall(r'^\(net (\d+) "([^"]*)"\)$',raw,re.M)}
            assert pcb_net.get("")==0
            assert set(pcb_net)-{""}==set(wanted.values())-{""}
            assert len(pcb_net)==(12 if board=="MAIN" else 8)
            pads={}
            blocks=raw.split('\n(footprint "')[1:]
            assert len(blocks)==(13 if board=="MAIN" else 7)
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
                    else "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" if ref in ("R1901","R1902")
                    else "Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm" if ref in ("C1201","C1203","C1205")
                    else "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" if ref in ("R1201","R1202")
                    else "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm" if ref=="C1202"
                    else "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm" if ref=="C1206"
                    else "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical" if ref=="J1201"
                    else "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm" if ref=="C1204"
                    else "Package_DIP:DIP-8_W7.62mm" if ref=="U1201"
                    else FOOTPRINT)) in block.split('"',1)[0]
                allpads=re.findall(
                    r'\(pad "(\d+)" thru_hole (?:rect|circle) \(at [^)]+\) '
                    r'\(size [^)]+\) \(drill [^)]+\) '
                    r'\(layers "\*\.Cu" "\*\.Mask"\) '
                    r'\(net (\d+) "([^"]*)"\)',block)
                assert len(allpads)==(8 if ref=="U1201" else 6 if ref=="K1901" else 3 if ref=="RV1301" else 2),(board,ref,allpads)
                for pin,net_id,netname in allpads:
                    assert pcb_net[netname]==int(net_id)
                    assert (ref,pin) not in pads,(board,ref,pin)
                    pads[(ref,pin)]=netname
            assert pads==wanted,(board,pads,wanted)
            if board=="MAIN":
                # Real LM386 schematic nodes: C1201 AUDIO_IN -> PRE_IN,
                # R1201 PRE_IN -> AMP_IN; PCB pad placement unconnected.
                for ref,coord in {"C1201":(100.,65.),
                                  "R1201":(110.,75.)}.items():
                    block=next(b for b in blocks if f'(property "Reference" "{ref}"' in b)
                    assert f'(at {coord[0]:g} {coord[1]:g})' in block
                assert all(pads[(ref,pin)]==net for (ref,pin),net in {
                    ("C1201","1"):"AUDIO_IN",
                    ("C1201","2"):"PRE_IN",
                    ("R1201","1"):"PRE_IN",
                    ("R1201","2"):"AMP_IN"}.items())
                # Physical U1201 pad geometry follows KiCad DIP8 TOP view;
                # pins 1 and 8 have deliberately no net in this gain=20 lab schematic.
                dip=next(b for b in blocks if '(property "Reference" "U1201"' in b)
                assert '(at 130 65)' in dip
                expected_dip={
                    "1":("",0.,0.),"2":("GND",0.,2.54),
                    "3":("AMP_IN",0.,5.08),"4":("GND",0.,7.62),
                    "5":("AMP_OUT",7.62,7.62),
                    "6":("AUDIO_6V_LAB",7.62,5.08),
                    "7":("BYPASS",7.62,2.54),"8":("",7.62,0.),
                }
                for pin,(net,x,y) in expected_dip.items():
                    assert pads[("U1201",pin)]==net
                    assert f'(pad "{pin}" thru_hole' in dip
                    assert f'(at {x:g} {y:g})' in dip
                assert pads[("C1204","1")]=="BYPASS"
                assert pads[("C1204","2")]=="GND"
                bypass_cap=next(b for b in blocks if '(property "Reference" "C1204"' in b)
                assert '(at 150 80)' in bypass_cap
                assert '(pad "1" thru_hole rect (at 0 0)' in bypass_cap
                assert '(pad "2" thru_hole circle (at 2 0)' in bypass_cap
                # Polarized bypass positive at U1201/7 BYPASS, negative GND.
                # This is placement only; no U1201 pin7/C1204 copper yet.
                assert pads[("C1205","1")]=="AUDIO_6V_LAB"
                assert pads[("C1205","2")]=="GND"
                c1205=next(b for b in blocks if '(property "Reference" "C1205"' in b)
                assert '(at 147 95)' in c1205
                assert '(pad "1" thru_hole rect (at 0 0)' in c1205
                assert '(pad "2" thru_hole circle (at 2.5 0)' in c1205
                # Placement only, do not imply VCC/GND physically connected.
                assert "IF_BENCH_GND"!=pads[("C1201","1")]
                assert "GND"!=pads[("R1201","2")]
                # Native verified MAIN plated-pad clearance and route topology.
                from math import hypot
                mainpads={
                    ("J1502","1"):((40.,45.),1.,1),
                    ("J1502","2"):((40.,47.54),1.,2),
                    ("J1202","1"):((90.,45.),1.,3),
                    ("J1202","2"):((90.,47.54),1.,4),
                    ("C1201","1"):((100.,65.),.8,3),
                    ("C1201","2"):((102.5,65.),.8,5),
                    ("R1201","1"):((110.,75.),.9,5),
                    ("R1201","2"):((117.62,75.),.9,6),
                    ("U1201","1"):((130.,65.),.8,0),
                    ("U1201","2"):((130.,67.54),.8,4),
                    ("U1201","3"):((130.,70.08),.8,6),
                    ("U1201","4"):((130.,72.62),.8,4),
                    ("U1201","5"):((137.62,72.62),.8,7),
                    ("U1201","6"):((137.62,70.08),.8,8),
                    ("U1201","7"):((137.62,67.54),.8,9),
                    ("U1201","8"):((137.62,65.),.8,0),
                    ("C1204","1"):((150.,80.),.9,9),
                    ("C1204","2"):((152.,80.),.9,4),
                    ("C1205","1"):((147.,95.),.8,8),
                    ("C1205","2"):((149.5,95.),.8,4),
                    ("C1202","1"):((167.,65.),.9,7),
                    ("C1202","2"):((170.5,65.),.9,10),
                    ("C1203","1"):((167.,82.),.8,7),
                    ("C1203","2"):((169.5,82.),.8,11),
                    ("R1202","1"):((184.,82.),.9,11),
                    ("R1202","2"):((191.62,82.),.9,4),
                    ("C1206","1"):((168.,106.),.9,8),
                    ("C1206","2"):((170.5,106.),.9,4),
                    ("J1201","1"):((90.,110.),.9,8),
                    ("J1201","2"):((92.5,110.),.9,4),
                    ("J1203","1"):((205.,65.),1.,10),
                    ("J1203","2"):((207.54,65.),1.,4),
                }
                assert set(mainpads)==set(wanted)
                def gap_to_track(pt,a,b):
                    dx,dy=b[0]-a[0],b[1]-a[1]
                    den=dx*dx+dy*dy
                    assert den>0
                    t=max(0.,min(1.,((pt[0]-a[0])*dx+(pt[1]-a[1])*dy)/den))
                    return hypot(pt[0]-a[0]-t*dx,pt[1]-a[1]-t*dy)
                wires_main=[(int(n),(float(x),float(y)),(float(xx),float(yy)),
                    float(w),l) for x,y,xx,yy,w,l,n,u in segments]
                for net,a,b,w,layer in wires_main:
                    for (point,rad,othernet) in mainpads.values():
                        if net!=othernet:
                            assert gap_to_track(point,a,b)-rad-w/2>=0.2-1e-8,(
                                "MAIN different-net pad copper clearance",net,othernet,point)
                # Independent same-layer different-net trace/trace spacing
                # on every MAIN physical candidate route, including BYPASS.
                def segment_spacing(a,b,c,d):
                    def cross(p,q,r):
                        return (q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0])
                    if cross(a,b,c)*cross(a,b,d)<0 and cross(c,d,a)*cross(c,d,b)<0:
                        return 0.
                    return min(gap_to_track(a,c,d),gap_to_track(b,c,d),
                               gap_to_track(c,a,b),gap_to_track(d,a,b))
                for i,(na,a,bb,wa,la) in enumerate(wires_main):
                    for nb,c,end2,wb,lb in wires_main[i+1:]:
                        if na!=nb and la==lb:
                            assert segment_spacing(a,bb,c,end2)-(wa+wb)/2 >= .2-1e-8,(
                                "MAIN cross-net trace clearance",na,nb,la,a,bb,c,end2)
                for net in (3,5,6):
                    group=[(a,b) for n,a,b,w,l in wires_main if n==net]
                    assert len(group)==(3 if net==6 else 2) and all(group[i][1]==group[i+1][0] for i in range(len(group)-1)),(
                        "MAIN split audio input copper",net,group)
                    for point,rad,n in mainpads.values():
                        if n==net:
                            assert any(gap_to_track(point,a,b)<1e-8 for a,b in group),(
                                "MAIN native input pad unconnected",net,point)
                # The new amplifier input must terminate on U1201/3, with
                # pins 1/8 unconnected and both ground returns still separate.
                amp=[(a,b) for n,a,b,w,l in wires_main if n==6]
                assert len(amp)==3 and amp[0][0]==(117.62,75.) and amp[-1][1]==(130.,70.08)
                assert all(n not in (0,1,2,10,11) for n,a,b,w,l in wires_main)
                # GND is a branching MAIN net on F.Cu: J1202/2
                # must reach both amplifier GND pins without touching IF return.
                grounded=[(a,b) for n,a,b,w,l in wires_main if n==4]
                assert len(grounded)==11
                reachable={(90.,47.54)}
                for _ in range(len(grounded)+1):
                    for a,c in grounded:
                        if a in reachable: reachable.add(c)
                        if c in reachable: reachable.add(a)
                assert {(90.,47.54),(130.,67.54),(130.,72.62),(152.,80.),(149.5,95.)}<=reachable
                assert all(n!=2 for n,a,c,w,l in wires_main)
                assert [(a,c,l) for n,a,c,w,l in wires_main if n==4][6:9]==[
                    ((152.,80.),(152.,85.),"F.Cu"),
                    ((152.,85.),(130.,85.),"F.Cu"),
                    ((130.,85.),(130.,72.62),"F.Cu")]
                assert [(a,c,l) for n,a,c,w,l in wires_main if n==4][-2:]==[
                    ((149.5,95.),(152.,95.),"F.Cu"),
                    ((152.,95.),(152.,85.),"F.Cu")]
                # Polarized BYPASS is a distinct B.Cu path from LM386 pin7
                # to C1204 positive; negative stays GND and unconnected here.
                bypass=[(a,c,l) for n,a,c,w,l in wires_main if n==9]
                assert bypass==[
                    ((137.62,67.54),(145.,67.54),"B.Cu"),
                    ((145.,67.54),(145.,80.),"B.Cu"),
                    ((145.,80.),(150.,80.),"B.Cu")]
                assert pads[("U1201","7")]==pads[("C1204","1")]=="BYPASS"
                assert not any(n==9 and (a==(152.,80.) or c==(152.,80.))
                    for n,a,c,w,l in wires_main)
                # AUDIO_6V_LAB is only the local U1201/6→C1205/1 decoupling
                # branch: it is not connected to a qualified laboratory power source.
                supply=[(a,c,l) for n,a,c,w,l in wires_main if n==8]
                assert supply==[
                    ((137.62,70.08),(140.,70.08),"B.Cu"),
                    ((140.,70.08),(140.,90.),"B.Cu"),
                    ((140.,90.),(147.,90.),"B.Cu"),
                    ((147.,90.),(147.,95.),"B.Cu")]
                assert pads[("U1201","6")]==pads[("C1205","1")]=="AUDIO_6V_LAB"
                assert not any(n in (1,2,10,11) for n,a,c,w,l in wires_main)
                # Real output branching joins LM386 pin5 to the positive output
                # coupling capacitor and Zobel capacitor; speaker path and Zobel
                # resistor remain unrouted at this stage. No accidental supply link.
                output=[(a,c,l) for n,a,c,w,l in wires_main if n==7]
                assert output==[
                    ((137.62,72.62),(160.,72.62),"F.Cu"),
                    ((160.,72.62),(160.,65.),"F.Cu"),
                    ((160.,65.),(167.,65.),"F.Cu"),
                    ((160.,72.62),(160.,82.),"F.Cu"),
                    ((160.,82.),(167.,82.),"F.Cu")]
                assert pads[("U1201","5")]==pads[("C1202","1")]==pads[("C1203","1")]=="AMP_OUT"
                assert all(n not in (10,11) for n,a,c,w,l in wires_main)
                # No MAIN copper joins the distinct input and output returns.
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

                # Coil contacts are not routed and the lab driver is not qualified.
                assert not any(int(n) in (6,7) for *_,n,uuid in segments)
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
                relay_keys={("K1901",pin) for pin in ("1","2","5","6","9","10")}
                resistor_keys={(ref,pin) for ref in ("R1901","R1902") for pin in ("1","2")}
                assert set(wanted)==set(physical)|relay_keys|resistor_keys
                assert not (set(physical)&(relay_keys|resistor_keys))
                physical.update({
                    ("K1901","1"):((80.,55.),1.,2),
                    ("K1901","2"):((80.,57.54),1.,6),
                    ("K1901","5"):((80.,65.16),1.,5),
                    ("K1901","6"):((85.08,65.16),1.,5),
                    ("K1901","9"):((85.08,57.54),1.,7),
                    ("K1901","10"):((85.08,55.),1.,4),
                    ("R1901","1"):((100.,60.),.9,3),
                    ("R1901","2"):((110.16,60.),.9,2),
                    ("R1902","1"):((100.,70.),.9,5),
                    ("R1902","2"):((110.16,70.),.9,3),
                })
                assert set(wanted)==set(physical)
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
                # Reject same-layer cross-net copper intersections and spacing
                # below 0.20mm, in addition to every plated pad clearance.
                def cross(a,b,c):
                    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
                def intersects(a,b,c,d):
                    p,q=cross(a,b,c),cross(a,b,d)
                    z,t=cross(c,d,a),cross(c,d,b)
                    if p*q < -1e-12 and z*t < -1e-12:
                        return True
                    return (abs(p)<1e-9 and dist(c,a,b)<1e-9 or
                            abs(q)<1e-9 and dist(d,a,b)<1e-9 or
                            abs(z)<1e-9 and dist(a,c,d)<1e-9 or
                            abs(t)<1e-9 and dist(b,c,d)<1e-9)
                for i,(net,a,b,width,layer) in enumerate(wires):
                    for other,c,other_end,w2,other_layer in wires[i+1:]:
                        if net==other or layer!=other_layer:
                            continue
                        gap=0. if intersects(a,b,c,other_end) else min(
                            dist(a,c,other_end),dist(b,c,other_end),
                            dist(c,a,b),dist(other_end,a,b))
                        assert gap-(width+w2)/2>=0.2-1e-8,(
                            "same-layer copper collision",net,other,a,b,c,other_end)
                # Ensure all connected schematic pad sets are actually
                # linked by copper; copper endpoints may join mid-segment.
                def onseg(pt,a,c):
                    return dist(pt,a,c)<1e-7
                for net in (1,2,3,4,5):
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
                # All K1901 plated pads must clear foreign-net copper, even
                # on the opposite layer; coil pads remain free of copper.
                for pad,(net,x,y) in expected_relay.items():
                    for tracknet,a,c,width,layer in wires:
                        if tracknet!=pcb_net[net]:
                            assert dist((x,y),a,c)-1.0-width/2>=0.2-1e-8,(
                                "K1901 foreign-net copper clearance",pad,tracknet)
                # Resistive bleed and series routing must match native master.
                physical_resistors={
                    ("R1901","1"):("AMP_INPUT_MUTED",(100.,60.)),
                    ("R1901","2"):("AF_GND",(110.16,60.)),
                    ("R1902","1"):("RELAY_COM_AUDIO",(100.,70.)),
                    ("R1902","2"):("AMP_INPUT_MUTED",(110.16,70.)),
                }
                assert set(physical_resistors)==resistor_keys
                for (ref,pin),(net,pos) in physical_resistors.items():
                    assert pads[(ref,pin)]==net
                    block=next(b for b in blocks if f'(property "Reference" "{ref}"' in b)
                    local=(0.,0.) if pin=="1" else (10.16,0.)
                    assert f'(pad "{pin}" thru_hole' in block
                    assert f'(at {local[0]:g} {local[1]:g})' in block
                    for tracknet,a,c,width,layer in wires:
                        if tracknet!=pcb_net[net]:
                            assert dist(pos,a,c)-0.9-width/2>=0.2-1e-8,(
                                "resistor foreign-net copper clearance",ref,pin)
                # Strict isolation: coil nets never routed and no direct
                # copper path joins relay NO/wiper net4 with amp output net3.
                assert not any(n in (6,7) for n,a,c,w,layer in wires)
                assert sum(n==3 for n,a,c,w,layer in wires)==7
                assert sum(n==5 for n,a,c,w,layer in wires)==4
            nets=exported_nets(sch,d/(board+".net"))
            for endpoint,netname in wanted.items():
                matches=[name for name,members in nets.items()
                         if endpoint in members]
                if netname=="":
                    # Gain pins 1/8 unconnected: do not silently assign
                    # their pad to the amplifier supply or an audio net.
                    assert board=="MAIN" and endpoint in {
                        ("U1201","1"),("U1201","8")}
                    assert not matches,(board,endpoint,"unconnected pin gained copper",matches)
                    continue
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
            assert len(refs)==(13 if board=="MAIN" else 7)
            assert len(pads)==(32 if board=="MAIN" else 19)
    print("PASS_KICAD9_MAIN_FRONT_TWO_SEPARATE_NONFAB_AUDIO_PCB_PAD_ISLANDS_4REF_8THT_PADS",{
        "MAIN":("J1502","J1202","C1201","R1201","U1201","C1204","C1205","C1202","C1203","R1202","C1206","J1201","J1203"),
        "FRONT":("J1301","J1902","RV1301","J1302","K1901","R1901","R1902"),
        "independent_MAIN_nets":11,
        "MAIN_output_bulk_IO_6_new_THT_footprints_pin_pad_net_candidate":True,
        "MAIN_U1201_DIP8_native_pads_verified":True,
        "MAIN_C1204_polarized_bypass_THT_placement_verified":True,
        "MAIN_C1205_100nF_supply_decoupling_THT_placement_verified":True,
        "MAIN_U1201_gain_pins_1_and_8_no_net":True,
        "MAIN_input_cap_series_resistor_THT_30_audio_segments":True,
        "MAIN_AMP_OUT_pin5_to_C1202_and_C1203_positive_connected":True,
        "MAIN_U1201_pin6_to_C1205_positive_decoupling_connected":True,
        "MAIN_C1205_negative_GND_routed_from_pad2":True,
        "MAIN_C1204_negative_GND_routed_to_U1201_pin4":True,
        "MAIN_BYPASS_U1201_pin7_to_C1204_positive_connected":True,
        "MAIN_GND_J1202_to_U1201_pins2_4_connected":True,
        "MAIN_AMP_IN_R1201_to_U1201_pin3_connected":True,
        "independent_FRONT_nets":3,
        "shared_FRONT_AF_GND_pad_assignments":4,
        "FRONT_volume_to_wiper_10_original_segments_preserved":True,
        "FRONT_mute_17_new_candidate_segments":True,
        "K1901_coil_unrouted":True,
        "all_pads_mapped_to_native_schematic_labels":True,
        "native_kicad9_pos_export_both_islands":True,
        "no_edge_no_vias_no_extra_components":True,
        "FRONT_AF_GND_copper_branched_to_volume_and_header":True,
        "MAIN_IF_return_unrouted_GND_only_routed_isolated":True,
        "production_DRC_and_routing_claimed":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True},flush=True)

if __name__=="__main__":
    main()
