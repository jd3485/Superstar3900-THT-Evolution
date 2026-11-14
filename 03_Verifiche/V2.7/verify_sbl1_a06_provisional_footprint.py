#!/usr/bin/env python3
"""Check provisional A06 KiCad9 native footprint PAD GEOMETRY, not OEM sign-off.
FAIL closed if MX1701 is assigned this UNQUALIFIED footprint in the bench.
"""
from pathlib import Path
import re
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[2]
DIR=ROOT/"04_KiCad/V2.7_DRAFT/MIXER_SBL1_CANDIDATE"
FP=DIR/"SBL1_A06_CANDIDATE.pretty/SBL1_A06_UNQUALIFIED.kicad_mod"
SCH=DIR/"MIXER_SBL1_BENCH_THT_V2_7_DRAFT.kicad_sch"
PAD=re.compile(r'\(pad "(\d+)" thru_hole (circle|rect) \(at ([\-\d.]+) ([\-\d.]+)\) \(size ([\d.]+) ([\d.]+)\) \(drill ([\d.]+)\) \(layers "\*\.Cu" "\*\.Mask"\)\)')
# OEM SBL-1+ PDF REV B page1 top M-over-pin2 + OEM bottom view.\n# Bottom-only mirrored-X assumption was contradicted by the actual TOP marker.
# Reading convention is not a substitute for inspection of the drawing image.
OEM_BOTTOM_TOP_ROW=("1","3","5","7")
OEM_BOTTOM_BOTTOM_ROW=("2","4","6","8")
PITCH=5.08
def expected_top_view():
    # OEM *graphic* SBL-1+ datasheet: "M" over pin 2 at TOP-LEFT.
    # The BOTTOM VIEW shows pin 2 at BOTTOM-LEFT. Reflect the Y axis
    # (flip upper/lower), NOT X (left/right), to preserve that mark.
    # This is intentionally an image-anchored mechanical *candidate*,
    # still not an assembly/drill tolerance qualification.
    columns=(-1.5*PITCH,-0.5*PITCH,0.5*PITCH,1.5*PITCH)
    result={}
    for row,y in ((OEM_BOTTOM_TOP_ROW,-PITCH/2),
                  (OEM_BOTTOM_BOTTOM_ROW,PITCH/2)):
        for x,pin in zip(columns,row):
            result[pin]=(x,-y)
    return result
EXPECTED=expected_top_view()
def main():
    src=FP.read_text(encoding="utf-8")
    sch=SCH.read_text(encoding="utf-8")
    table=(DIR/"fp-lib-table").read_text(encoding="utf-8")
    assert '(name "SBL1_A06_CANDIDATE")' in table
    assert '${KIPRJMOD}/SBL1_A06_CANDIDATE.pretty' in table
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
    # Geometric acceptance limits for THIS CANDIDATE only, not a fab signoff.
    assert len({x for x,y in seen.values()})==4
    assert len({y for x,y in seen.values()})==2
    xs=sorted({x for x,y in seen.values()})
    ys=sorted({y for x,y in seen.values()})
    assert all(abs((xs[i+1]-xs[i])-PITCH)<1e-8 for i in range(3))
    assert abs((ys[1]-ys[0])-PITCH)<1e-8
    assert seen["1"]==(-7.62,2.54),"OEM top marker: pin1 lower left"
    assert seen["2"]==(-7.62,-2.54),"OEM top M-over-pin2 must align upper left"
    assert "(fp_circle (center -8.0 4.0)" in src,"Pin 1 silkscreen marker missing"
    assert src.count('(pad "')==8,"Unexpected extra pad"
    # 0.031in diameter + .005in tolerance => 0.9144mm maximum pin diameter.
    # 1.10mm nominal plated finished drill proposal leaves only 0.1856mm
    # diametral clearance before plating and meniscus constraints are qualified.
    max_pin_diameter_mm=(0.031+0.005)*25.4
    assert max_pin_diameter_mm<1.10
    min_annular_ring_mm=(2.00-1.10)/2
    assert min_annular_ring_mm>=0.45-1e-9
    assert (PITCH-2.00)>3.0,"Insufficient adjacent pad copper separation"
    assert "MX1701" in sch
    mix=sch.split('(lib_id "MCL_SBL1_CANDIDATE:SBL-1_PLUS")',1)[1].split("(instances ",1)[0]
    assert '(property "Footprint" ""' in mix,"NO FAB: footprint must stay unassigned before OEM graphic review"
    assert all(f'(pin "{i}"' in mix for i in range(1,9))
    # Native KiCad9 parse/export of the real .pretty module: this is not PCB DRC.
    # SVG proves the footprint can be loaded by KiCad; it does not certify the
    # manufacturer's drawing or drill/plating mechanical fit.
    with tempfile.TemporaryDirectory(prefix="tht_sbl1_a06_native_fp_") as tmp:
        cmd=["kicad-cli","fp","export","svg","--output",tmp,
             "--footprint","SBL1_A06_UNQUALIFIED",str(FP.parent)]
        run=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
        print("NATIVE_KICAD9_A06_FOOTPRINT_SVG",run.stdout,run.stderr,flush=True)
        run.check_returncode()
        svgs=list(Path(tmp).rglob("*.svg"))
        assert svgs,("KiCad9 generated no SVG for A06 candidate",cmd)
        assert all(p.stat().st_size>500 for p in svgs),svgs
        print("NATIVE_KICAD9_A06_SVG_SIZE",[(p.name,p.stat().st_size) for p in svgs],flush=True)
    print("PASS_NATIVE_KICAD9_FP_EXPORT_A06_TOP_M_OVER_PIN2_Y_FLIP_THT_8_PADS_UNQUALIFIED_NOT_ASSIGNED_NO_FAB_NO_TX")
if __name__=="__main__": main()
