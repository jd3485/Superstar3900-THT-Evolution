#!/usr/bin/env python3
"""Pin-to-footprint-pad proof for all four actual THT MAIN/FRONT audio headers.

Native KiCad9 exported netlists supply component references, symbol pins
and assigned footprints. The installed KiCad footprint source supplies
physical pad numbers and through-hole technology. No assembled cable,
board placement, tracks, gender/polarization or DRC is implied.
"""
from pathlib import Path
import os
import re
import subprocess
import tempfile
from verify_interboard_audio_contract_native import exported_nets
from verify_main_front_dual_af_harness_native import MAIN,FRONT,HARNESS,LINKS,EXPECTED

ROOT=Path(__file__).resolve().parents[2]
FOOTPRINT="Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical"
BOARDS={"MAIN":MAIN,"FRONT":FRONT}
HEADERS={
    "MAIN":{"J1502","J1202"},
    "FRONT":{"J1301","J1902"},
}

def components(netlist):
    block=netlist.split("(components",1)[1].split("(libparts",1)[0]
    refs=list(re.finditer(r'\(comp\s+\(ref\s+"([^"]+)"\)',block))
    assert refs
    result={}
    for i,match in enumerate(refs):
        name=match.group(1)
        assert name not in result,name
        segment=block[match.start():refs[i+1].start() if i+1<len(refs) else len(block)]
        fp=re.search(r'\(footprint\s+"([^"]+)"\)',segment)
        result[name]=fp.group(1) if fp else None
    return result

def main():
    locations=[
        Path(os.environ["KICAD9_FOOTPRINT_DIR"]) if "KICAD9_FOOTPRINT_DIR" in os.environ
            else Path("/usr/share/kicad/footprints"),
        Path("/usr/local/share/kicad/footprints"),
    ]
    libfile=next((root/"Connector_PinHeader_2.54mm.pretty"/
                  "PinHeader_1x02_P2.54mm_Vertical.kicad_mod"
                  for root in locations
                  if (root/"Connector_PinHeader_2.54mm.pretty"/
                     "PinHeader_1x02_P2.54mm_Vertical.kicad_mod").is_file()),None)
    assert libfile is not None,("Missing real KiCad9 footprint source",locations)
    raw=libfile.read_text(encoding="utf8")
    assert "(footprint " in raw or "(module " in raw
    pad_types=re.findall(r'\(pad\s+"([^"]+)"\s+(thru_hole|smd|np_thru_hole)\b',raw)
    assert pad_types==[("1","thru_hole"),("2","thru_hole")],pad_types
    assert "(drill " in raw and "(layers \"*.Cu\" \"*.Mask\")" in raw
    assert "2.54" in raw
    assert len(pad_types)==2
    assert set(LINKS.values())=={
        ("MAIN","J1502","1"),("MAIN","J1502","2"),
        ("FRONT","J1301","1"),("FRONT","J1301","2"),
        ("FRONT","J1902","1"),("FRONT","J1902","2"),
        ("MAIN","J1202","1"),("MAIN","J1202","2"),
    }
    with tempfile.TemporaryDirectory(prefix="tht_af_4hdr_") as td:
        d=Path(td)
        netlists={}
        parts={}
        native={}
        for board,sch in [*BOARDS.items(),("HARNESS",HARNESS)]:
            out=d/(board+".net")
            cp=subprocess.run(["kicad-cli","sch","export","netlist","-o",str(out),str(sch)],
                cwd=ROOT,capture_output=True,text=True,timeout=180)
            cp.check_returncode()
            txt=out.read_text(encoding="utf8")
            netlists[board]=txt
            parts[board]=components(txt)
            native[board]=exported_nets(sch,d/(board+"_nets.net"))
    assert native["HARNESS"]==EXPECTED
    for board,refs in HEADERS.items():
        assert refs.issubset(parts[board]),(board,refs-parts[board].keys())
        for ref in refs:
            assert parts[board][ref]==FOOTPRINT,(board,ref,parts[board][ref])
            actual_pins={pin for pins in native[board].values()
                         for comp,pin in pins if comp==ref}
            assert actual_pins=={"1","2"},(board,ref,actual_pins)
            for pin in actual_pins:
                assert (board,ref,pin) in LINKS.values()
                assert (pin,"thru_hole") in pad_types
    for ref in ("J2701","J2702","J2703","J2704"):
        assert parts["HARNESS"][ref]==FOOTPRINT,ref
        assert {pin for pins in native["HARNESS"].values()
                for comp,pin in pins if comp==ref}=={"1","2"}
    # Both actual PCB connectors and abstract mating ends are headers of
    # the SAME male-type footprint. The cable ends are NOT female cable
    # assemblies simply because KiCad symbol references are J270x.
    assert len(HEADERS["MAIN"]|HEADERS["FRONT"])==4
    print("PASS_KICAD9_MAIN_FRONT_FOUR_PHYSICAL_AUDIO_HEADERS_8_THT_PADS_NATIVE_NETLIST",{
        "actual_board_THT_connector_headers":4,
        "actual_pin_to_physical_pad_numbers_checked":8,
        "cable_abstraction_THT_header_symbols":4,
        "harness_4_nets_8_pins":True,
        "mating_cable_gender_specified":False,
        "pin1_orientation_and_polarization_qualified":False,
        "on_board_pad_coordinates_and_routes_qualified":False,
        "ESD_EMC_shield_and_mechanical_qualified":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True},flush=True)

if __name__=="__main__":
    main()
