#!/usr/bin/env python3
"""Check provisional A06 KiCad9 native footprint PAD GEOMETRY, not OEM sign-off.
FAIL closed if MX1701 is assigned this UNQUALIFIED footprint in the bench.
"""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[2]
DIR=ROOT/"04_KiCad/V2.7_DRAFT/MIXER_SBL1_CANDIDATE"
FP=DIR/"SBL1_A06_CANDIDATE.pretty/SBL1_A06_UNQUALIFIED.kicad_mod"
SCH=DIR/"MIXER_SBL1_BENCH_THT_V2_7_DRAFT.kicad_sch"
PAD=re.compile(r'\(pad "(\d+)" thru_hole (circle|rect) \(at ([\-\d.]+) ([\-\d.]+)\) \(size ([\d.]+) ([\d.]+)\) \(drill ([\d.]+)\) \(layers "\*\.Cu" "\*\.Mask"\)\)')
EXPECTED={"7":(-7.62,-2.54),"5":(-2.54,-2.54),"3":(2.54,-2.54),"1":(7.62,-2.54),
          "8":(-7.62,2.54),"6":(-2.54,2.54),"4":(2.54,2.54),"2":(7.62,2.54)}
def main():
    src=FP.read_text(encoding="utf-8")
    sch=SCH.read_text(encoding="utf-8")
    assert src.startswith('(footprint "SBL1_A06_UNQUALIFIED"')
    assert "NO FAB - CHECK OEM BOTTOM VIEW" in src
    assert "(attr through_hole)" in src
    pads=PAD.findall(src)
    assert len(pads)==8,("Expected eight THT pads",pads)
    seen={}
    for num,shape,x,y,dx,dy,drill in pads:
        assert num not in seen,("duplicate pad",num)
        seen[num]=(float(x),float(y))
        assert shape==("rect" if num=="1" else "circle"),(num,shape)
        assert (float(dx),float(dy),float(drill))==(2.0,2.0,1.1),(num,dx,dy,drill)
    assert seen==EXPECTED,(seen,EXPECTED)
    assert "MX1701" in sch
    mix=sch.split('(lib_id "MCL_SBL1_CANDIDATE:SBL-1_PLUS")',1)[1].split("(instances ",1)[0]
    assert '(property "Footprint" ""' in mix,"NO FAB: footprint must stay unassigned before OEM graphic review"
    assert all(f'(pin "{i}"' in mix for i in range(1,9))
    print("PASS_A06_PROVISIONAL_THT_8_PADS_MIRROR_CONSISTENT_FOOTPRINT_NOT_ASSIGNED_NO_FAB_NO_TX")
if __name__=="__main__": main()
