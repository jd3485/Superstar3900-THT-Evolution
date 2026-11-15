#!/usr/bin/env python3
"""Native KiCad9 validation of FRONT 13-reference THT PLACEMENT-ONLY board.

No Edge.Cuts, vias, ground tie, mechanical drawing or approved MPN.
Only the four isolated 5V LAB LED nets may carry copper segments.
This is a real physical footprint/pad/net and partial lab-LED routing artifact, NOT a complete PCB and
NEVER a DRC0 or product manufacturability claim.
"""
from pathlib import Path
import re
import subprocess
import tempfile
from verify_front_partial_hierarchy_native import PARTITIONS

ROOT=Path(__file__).resolve().parents[2]
BOARD=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_PLACEMENT/FRONT_CONTROL_13REFS_PLACEMENT_NONFAB.kicad_pcb"
EXPECTED_REFS={
    "J1301","RV1301","J1302",
    "J2201","R2201","D2201","R2202","D2202",
    "J1801","RV1801","R1801","R1802","J1802"
}
EXPECTED_PINS={
    (ref,pin):name
    for name,refs in PARTITIONS.items()
    for ref,pin in refs
}

def verify():
    raw=BOARD.read_text(encoding="utf-8")
    assert BOARD.with_suffix(".kicad_pro").exists()
    assert raw.startswith("(kicad_pcb (version 20241229)")
    assert "(paper \"A3\")" in raw
    assert "LED NETS ONLY ROUTED" in raw
    assert "NO APPROVED PANEL GEOMETRY" in raw
    assert "NOT PRODUCTION PCB" in raw
    assert "(gr_rect " not in raw and "(gr_poly " not in raw
    assert "(layer \"Edge.Cuts\")" not in raw
    assert "(via " not in raw and "(zone " not in raw
    assert "(filled_polygon " not in raw
    assert 'TH_FRONT:Potentiometer_THT_3Pin_PROVISIONAL' in raw
    assert raw.count('(footprint "')==13
    assert len(EXPECTED_PINS)==28
    assert len(PARTITIONS)==12
    nets=re.findall(r'^\(net (\d+) "([^"]*)"\)$',raw,re.M)
    assert len(nets)==13,(nets,len(nets))
    numbers={name:int(num) for num,name in nets}
    assert numbers[""]==0
    assert set(numbers)-{""}==set(PARTITIONS),(set(numbers),set(PARTITIONS))
    blocks=raw.split('\n(footprint "')[1:]
    refs=set()
    actual={}
    zones={}
    for block in blocks:
        value=block.split('"',1)[0]
        ref_match=re.search(r'\(property "Reference" "([^"]+)"',block)
        assert ref_match,(value,block[:400])
        ref=ref_match.group(1)
        assert ref not in refs,ref
        refs.add(ref)
        assert "(attr through_hole)" in block,ref
        assert "smd" not in block.lower(),ref
        assert "(layer \"F.Cu\")" in block,ref
        coord=re.search(r'^\(footprint ".*?" \(layer "F.Cu"\) \(at ([\d.]+) ([\d.]+)\)',"(footprint \""+block,re.M)
        assert coord,ref
        x=float(coord.group(1))
        zones[ref]=x
        if ref in ("RV1301","RV1801"):
            assert value=="TH_FRONT:Potentiometer_THT_3Pin_PROVISIONAL",(ref,value)
        found=re.findall(
            r'\(pad "(\d+)" thru_hole (?:rect|circle) \(at [^)]*\) '
            r'\(size [^)]*\) \(drill [^)]*\) '
            r'\(layers "\*\.Cu" "\*\.Mask"\) '
            r'\(net (\d+) "([^"]+)"\)',
            block)
        assert len(found) in (2,3),(ref,found)
        for pin,n,net in found:
            assert (ref,pin) not in actual,(ref,pin)
            assert numbers[net]==int(n),(ref,pin,net,n)
            actual[(ref,pin)]=net
    assert refs==EXPECTED_REFS,(refs,EXPECTED_REFS)
    assert actual==EXPECTED_PINS,(actual,EXPECTED_PINS)
    # The three zones may be placed apart, but have no PANEL dimensions.
    assert all(zones[x]<110 for x in ("J1301","RV1301","J1302"))
    assert all(120<zones[x]<190 for x in ("J2201","R2201","D2201","R2202","D2202"))
    assert all(zones[x]>200 for x in ("J1801","RV1801","R1801","R1802","J1802"))
    # ONLY four LED laboratory nets have copper. Full geometric topology is
    # fail-closed, including layer, all 13 segment endpoints, and 0.5mm width.
    # No audio/SMETER/power-to-MAIN nets, copper zones, vias or outline permitted.
    expected_route_defs=[
      (4,"F.Cu",(130,35),(140,35)),
      (4,"F.Cu",(140,35),(140,25)),
      (4,"F.Cu",(140,25),(150,25)),
      (4,"F.Cu",(140,35),(140,48)),
      (4,"F.Cu",(140,48),(150,48)),
      (6,"F.Cu",(157.62,25),(175,25)),
      (7,"F.Cu",(157.62,48),(175,48)),
      (5,"B.Cu",(130,37.54),(130,60)),
      (5,"B.Cu",(130,60),(190,60)),
      (5,"B.Cu",(190,60),(190,48)),
      (5,"B.Cu",(190,48),(190,25)),
      (5,"B.Cu",(190,25),(177.54,25)),
      (5,"B.Cu",(190,48),(177.54,48)),
    ]
    from collections import Counter
    def key(t):
        net,layer,a,b=t
        return (net,layer,tuple(sorted((a,b))))
    expected_routes=Counter(map(key,expected_route_defs))
    pattern=(r'\(segment \(start ([\d.]+) ([\d.]+)\) '
             r'\(end ([\d.]+) ([\d.]+)\) '
             r'\(width ([\d.]+)\) \(layer "([^"]+)"\) '
             r'\(net (\d+)\) \(uuid "([^"]+)"\)\)')
    matches=re.findall(pattern,raw)
    assert len(matches)==13,("Expected exactly 13 LED-only segments",len(matches))
    parsed=[]
    for x1,y1,x2,y2,width,layer,net,uuid in matches:
        assert float(width)==0.5 and layer in ("F.Cu","B.Cu")
        assert int(net) in (4,5,6,7),("Unexpected copper outside lab",net)
        pts=((float(x1),float(y1)),(float(x2),float(y2)))
        assert all(125<=x<=195 and 20<=y<=65 for x,y in pts)
        assert pts[0]!=pts[1]
        parsed.append((int(net),layer,*pts))
    assert Counter(map(key,parsed))==expected_routes,(
        "PCB copper changed from verified LED-only topology",
        Counter(map(key,parsed))-expected_routes,
        expected_routes-Counter(map(key,parsed)))
    # Each complete LED subnet is connected through real physical pad centers.
    # The copper net partition remains disjoint from AUDIO / SMETER.
    pads_by_net={
        4:{(130,35),(150,25),(150,48)},
        5:{(130,37.54),(177.54,25),(177.54,48)},
        6:{(157.62,25),(175,25)},
        7:{(157.62,48),(175,48)}
    }
    for n,pads in pads_by_net.items():
        pairs=[(a,b) for net,ly,a,b in parsed if net==n]
        assert pairs
        graph={}
        for a,b in pairs:
            graph.setdefault(a,set()).add(b)
            graph.setdefault(b,set()).add(a)
        visited=set()
        todo=[next(iter(pads))]
        while todo:
            node=todo.pop()
            if node in visited: continue
            visited.add(node)
            todo.extend(graph.get(node,()))
        assert pads.issubset(visited),(n,pads-visited)
        assert set(graph)==visited,(n,"Disconnected dangling LED track",set(graph)-visited)
    assert all(n not in (1,2,3,8,9,10,11,12) for n,ly,a,b in parsed)
    with tempfile.TemporaryDirectory(prefix="tht_front_13place_") as td:
        pos=Path(td)/"front_13tht.pos"
        cp=subprocess.run(["kicad-cli","pcb","export","pos",
                           "--format","ascii","--side","front",
                           "-o",str(pos),str(BOARD)],
                          capture_output=True,text=True,cwd=ROOT,timeout=120)
        print("FRONT_13PLACEMENT_NATIVE_POS_STDOUT",cp.stdout,cp.stderr,flush=True)
        cp.check_returncode()
        content=pos.read_text(encoding="utf-8")
        for ref in EXPECTED_REFS:
            assert re.search(r'(?m)^\s*'+re.escape(ref)+r'\s',content),(ref,content[:2000])
    print("PASS_KICAD9_FRONT_13THT_28PADS_12NETS_4_LED_LAB_NETS_ROUTED_13_SEGMENTS_AUDIO_SMETER_UNROUTED_NO_OUTLINE_NO_FAB",{
        "THT_footprints":len(refs),
        "real_pad_net_assignments":len(actual),
        "isolated_nets":len(PARTITIONS),
        "native_component_pos_export":True,
        "LED_LAB_routed_nets":4,
        "LED_LAB_copper_segments":len(matches),
        "product_BOARD_outline_exists":False,
        "fully_routed":False,
        "AUDIO_SMETER_routed":False,
        "DRC_claimed":False,
        "OEM_footprints_qualified":False,
        "NO_FAB_NO_TX":True
    },flush=True)

if __name__=="__main__":
    verify()
