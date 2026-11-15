#!/usr/bin/env python3
"""KiCad9 Bourns PTV09A4 provisional 5.0mm THT terminal-pitch candidate.

Manufacturer datasheet https://www.bourns.com/docs/product-datasheets/ptv09.pdf
PTV09A-4 drawings: three terminals span 5.0mm, 1-2-3 electrical notation.
HOLE diameter, body/courtyard, shaft axis, chassis and board locks here are
NOT a finished MPN footprint. Product PCB must retain the 2.54mm prototype
and is forbidden from silently substituting this candidate.
"""
from pathlib import Path
import re
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_PLACEMENT"
NAME="Potentiometer_Bourns_PTV09A4_5mm_THT_CANDIDATE_NOT_FOR_FAB"
LIB=BASE/"TH_FRONT_OEM_CANDIDATES.pretty"
FP=LIB/(NAME+".kicad_mod")
BOARD=BASE/"FRONT_CONTROL_13REFS_PLACEMENT_NONFAB.kicad_pcb"
MANUFACTURER="https://www.bourns.com/docs/product-datasheets/ptv09.pdf"
def main():
    text=FP.read_text(encoding="utf-8")
    assert text.startswith('(footprint "'+NAME+'"')
    assert "BOURNS PTV09A-4" in text
    assert "NOT QUALIFIED" in text and "DO NOT FAB" in text
    assert MANUFACTURER.startswith("https://www.bourns.com/")
    assert '(attr through_hole)' in text
    assert "smd" not in text.lower()
    pads=re.findall(r'\(pad "(\d+)" thru_hole (rect|circle) '
        r'\(at (-?[\d.]+) (-?[\d.]+)\) '
        r'\(size ([\d.]+) ([\d.]+)\) '
        r'\(drill ([\d.]+)\) \(layers "\*\.Cu" "\*\.Mask"\)\)',text)
    assert len(pads)==3,pads
    actual={p[0]:(float(p[2]),float(p[3]),float(p[6])) for p in pads}
    assert actual=={"1":(-2.5,0.,1.),"2":(0.,0.,1.),"3":(2.5,0.,1.)},actual
    assert abs(actual["1"][0]-actual["3"][0])==5.
    assert abs(actual["1"][0]-actual["2"][0])==2.5
    assert abs(actual["3"][0]-actual["2"][0])==2.5
    assert len(set(p[0] for p in pads))==3
    # Board-level manufacturability SCREEN ONLY (not a fab clearance rule).
    # Each 1.8 mm circular copper pad around a provisional 1.0 mm finished
    # drill has 0.4 mm radial annular ring. At 2.5 mm adjacent pitch, the
    # mathematical pad-to-pad copper gap is 0.7 mm; mask/web, tolerance and
    # OEM lead fit still require independent qualification.
    xy={}
    for pin,shape,x,y,sx,sy,drill in pads:
        x,y,sx,sy,drill=map(float,(x,y,sx,sy,drill))
        assert sx==sy==1.8 and drill==1.0,(pin,sx,sy,drill)
        assert (sx-drill)/2 >= 0.4-1e-9,(pin,"annular ring")
        xy[pin]=(x,y,sx,sy)
    import math
    for ia,a in enumerate(("1","2","3")):
        for b in ("1","2","3")[ia+1:]:
            xa,ya,wa,ha=xy[a]
            xb,yb,wb,hb=xy[b]
            # Conservative enclosing-radius check for circular copper pads.
            center=math.hypot(xa-xb,ya-yb)
            gap=center-(wa+wb)/2
            assert gap>=0.5-1e-9,(a,b,gap)
    assert abs(xy["1"][0]-xy["2"][0])-1.8==0.7
    assert abs(xy["3"][0]-xy["2"][0])-1.8==0.7
    assert all(p[1] in ("rect","circle") for p in pads)
    board=BOARD.read_text(encoding="utf-8")
    assert board.count('(footprint "TH_FRONT:Potentiometer_THT_3Pin_PROVISIONAL"')==2
    assert NAME not in board
    assert board.count('(segment ')==35
    assert '(layer "Edge.Cuts")' not in board
    # KiCad9 native export actually parses the standalone candidate module.
    with tempfile.TemporaryDirectory(prefix="tht_bourns_candidate_") as tmp:
        out=Path(tmp)/"rendered"
        out.mkdir()
        run=subprocess.run(["kicad-cli","fp","export","svg",
                            "--footprint",NAME,"--output",str(out),str(LIB)],
                           capture_output=True,text=True,cwd=ROOT,timeout=120)
        print("BOURNS_PTV09A4_KICAD9_NATIVE_SVG_EXPORT",run.stdout,run.stderr,flush=True)
        run.check_returncode()
        files=list(out.glob("*.svg"))
        assert files,("No KiCad9 footprint SVG emitted",str(out))
        for file in files:
            assert "<svg" in file.read_text(encoding="utf-8",errors="replace")[:10000]
    print("PASS_KICAD9_BOURNS_PTV09A4_3THT_PINS_5MM_CANDIDATE_SVG_NO_PRODUCT_SWAP_NO_FAB",{
        "terminal_span_mm":5.,
        "THT_electrical_pins":3,
        "provisional_drill_diameter_mm":1.,
        "provisional_annular_ring_radial_mm":0.4,
        "nominal_adjacent_pad_copper_gap_mm":0.7,
        "copper_geometry_screen_only_not_fab_drc":True,
        "board_replaced":False,
        "panel_mount_geometry_qualified":False,
        "OEM_in_production_confirmed_by_manufacturer":False,
        "PTV09A4_ambient_limit_C":[-10,50],
        "NO_FAB_NO_TX":True
    },flush=True)
if __name__=="__main__":main()
