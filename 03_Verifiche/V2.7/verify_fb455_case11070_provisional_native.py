#!/usr/bin/env python3
"""Manufacturer graphic-derived FB455 Case 11070 pin-to-pad guard.

This runs KiCad9 native footprint SVG export but does NOT approve any
manufacturing orientation, drill, plating, mold tolerance or pin fit.
The proposed footprint is deliberately unassigned to any schematic.
"""
from pathlib import Path
import math
import re
import subprocess
import tempfile
from verify_interboard_audio_contract_native import exported_nets, require

ROOT=Path(__file__).resolve().parents[2]
FP=ROOT/"04_KiCad/V2.7_DRAFT/FILTER_IF455_NEXTGEN_CANDIDATE/FB455_CANDIDATE.pretty/FB455_11070_UNQUALIFIED.kicad_mod"
IF455=ROOT/"04_KiCad/V2.7_DRAFT/IF455_TANK/IF455_TANK_THT_V2_7_DRAFT.kicad_sch"
PAD=re.compile(r'\(pad "(\d+)" thru_hole (circle|rect) \(at ([-.\d]+) ([-.\d]+)\) \(size ([\d.]+) ([\d.]+)\) \(drill ([\d.]+)\) \(layers "\*\.Cu" "\*\.Mask"\)\)')
# OEM 2024-10-10 FB series PDF p3 BOTTOM drawing: 4/3/2/1 upper row
# moving right; pin5 below pin4, offset 0.8mm in bottom view.
# X-mirrored TOP candidate only; no OEM top pin1 index shown.
OEM_BOTTOM={
    "4":(0.0,-2.15),"3":(2.9,-2.15),"2":(5.8,-2.15),
    "1":(8.4,-2.15),"5":(0.8,2.15)}
EXPECTED={pin:(-x,y) for pin,(x,y) in OEM_BOTTOM.items()}
PORTS={1:"INPUT",2:"GROUND",3:"GROUND",4:"GROUND",5:"OUTPUT"}
def main():
    assert len(EXPECTED)==5 and len(set(EXPECTED.values()))==5
    assert len(PORTS)==5 and {p for p,net in PORTS.items() if net=="GROUND"}=={2,3,4}
    text=FP.read_text(encoding="utf-8")
    assert text.startswith('(footprint "FB455_11070_UNQUALIFIED"')
    assert '(attr through_hole)' in text
    assert 'NO FAB - VERIFY TOP MARK' in text
    pads=PAD.findall(text)
    assert len(pads)==5,(len(pads),pads)
    actual={}
    for pin,shape,x,y,dx,dy,drill in pads:
        assert pin not in actual
        actual[pin]=(float(x),float(y))
        assert shape==("rect" if pin=="1" else "circle")
        # DRAFT dimensions, not an approved OEM finished hole.
        assert (float(dx),float(dy),float(drill))==(1.5,1.5,0.8)
    assert actual==EXPECTED,(actual,EXPECTED)
    assert text.count('(pad "')==5
    assert math.isclose(abs(actual["1"][0]-actual["2"][0]),2.6)
    assert math.isclose(abs(actual["2"][0]-actual["3"][0]),2.9)
    assert math.isclose(abs(actual["3"][0]-actual["4"][0]),2.9)
    assert math.isclose(abs(actual["4"][0]-actual["5"][0]),0.8)
    assert math.isclose(abs(actual["4"][1]-actual["5"][1]),4.3)
    assert abs(actual["4"][0]-actual["5"][0])>0, "Pin5 is offset; never grid-align it"
    # Safeguard against falsely dropping the existing 10pF IF input.
    sch=IF455.read_text(encoding="utf-8")
    assert "FB455_11070_UNQUALIFIED" not in sch
    assert 'property "Reference" "C1601"' in sch
    with tempfile.TemporaryDirectory(prefix="tht_fb455_native_") as temp:
        t=Path(temp)
        nets=exported_nets(IF455,t/"tank.net")
        require(nets,"IF455_SOURCE",("J1601","1"),("C1601","1"))
        require(nets,"IF455_TANK",("C1601","2"),("L1601","1"))
        cmd=["kicad-cli","fp","export","svg","--output",str(t),
             "--footprint","FB455_11070_UNQUALIFIED",str(FP.parent)]
        p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
        assert p.returncode==0,(cmd,p.stdout,p.stderr)
        svg=list(t.rglob("*.svg"))
        assert svg and all(f.stat().st_size>500 for f in svg)
        print("FB455_NATIVE_KICAD9_FOOTPRINT_SVG",[(f.name,f.stat().st_size) for f in svg],flush=True)
    print("FB455_OEM_BOTTOM_VIEW_MM",OEM_BOTTOM,flush=True)
    print("FB455_PROVISIONAL_PCB_TOP_PADS_MM",actual,flush=True)
    print("FB455_PIN_FUNCTIONS",PORTS,flush=True)
    print("FB455_ACTIVE_455K_CANDIDATES_REQUIRE_2000OHM_INTERFACE_NOT_ASSIGNED",flush=True)
    print("PASS_NATIVE_KICAD9_FB455_5PIN_CASE11070_PROVISIONAL_PINPAD_GROUND_CONTRACT_NO_OEM_TOP_DRILL_QUALIFICATION_NO_FAB_NO_TX",flush=True)
if __name__=="__main__":
    main()
