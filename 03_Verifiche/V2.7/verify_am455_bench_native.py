#!/usr/bin/env python3
"""Native KiCad9 455kHz AM-only bench envelope detector pin-net/footprint gate.

This does NOT implement 3900 AM/FM/SSB RX, does not model diode at low RF
level, validate sensitivity/selectivity, or authorize PCB/TX.
"""
from pathlib import Path
import subprocess
import tempfile
from verify_interboard_audio_contract_native import exported_nets, require

ROOT=Path(__file__).resolve().parents[2]
DIRECTORY=ROOT/"04_KiCad/V2.7_DRAFT/AM455_ENVELOPE"
SOURCE=DIRECTORY/"AM455_ENVELOPE_THT_V2_7_DRAFT.kicad_sch"
LIB=DIRECTORY/"TH_DEMOD.kicad_sym"
REFERENCES={"J1501","J1502","D1501","R1501","R1502","C1501","C1502"}
THT_NAMES=("Connector_PinHeader_2.54mm:",
           "Diode_THT:", "Resistor_THT:", "Capacitor_THT:")


def main():
    s=SOURCE.read_text(encoding="utf-8")
    library=LIB.read_text(encoding="utf-8")
    assert s.count("(symbol (lib_id ") == len(REFERENCES)
    assert s.count("(property \"Footprint\"") >= len(REFERENCES)
    for ref in REFERENCES:
        assert '(property "Reference" "'+ref+'"' in s,("Missing reference",ref)
    assert "AM ENVELOPE ONLY" in s and "NOT FM/SSB" in s
    assert "1N4148" in s and "1N4148" not in library
    for mark in ("D4148","J2","R","C"):
        assert '(symbol "TH_DEMOD:'+mark+'"' in s
        assert '(symbol "'+mark+'"' in library
    # Strictly verify seven actual instance footprints are all THT.
    for part in s.split('(symbol (lib_id ')[1:]:
        unit=part.split("(instances ",1)[0]
        fp=unit.split('(property "Footprint" "',1)[1].split('"',1)[0]
        assert fp.startswith(THT_NAMES),("Not through-hole",fp)
    assert "Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal" in s
    assert '("D1501"' not in s  # don't assume any special SPICE mapping
    with tempfile.TemporaryDirectory(prefix="am455_native_kicad9_") as temporary:
        d=Path(temporary)
        report=d/"erc.rpt"
        cp=subprocess.run(
            ["kicad-cli","sch","erc","--exit-code-violations",
             "-o",str(report),str(SOURCE)],
            cwd=ROOT,capture_output=True,text=True)
        print("AM455_ERC_STDOUT",cp.stdout,cp.stderr,flush=True)
        if report.exists():
            print("AM455_ERC_REPORT",report.read_text(encoding="utf-8"),flush=True)
        cp.check_returncode()
        nets=exported_nets(SOURCE,d/"am455.net")
        found={ref for members in nets.values() for (ref,_pin) in members}
        assert REFERENCES==found,("Unconnected or unexpected part",REFERENCES-found,found-REFERENCES)
        # 1N4148 DO-35: pin2 anode toward lab IF, pin1 cathode to envelope RC.
        require(nets,"IF455_BENCH_IN",("J1501","1"),("D1501","2"))
        require(nets,"AM_RECTIFIED_ENV",("D1501","1"),("R1501","1"),
                ("C1501","1"),("C1502","1"))
        require(nets,"AM_DEMOD_AF_BENCH",("C1502","2"),
                ("R1502","1"),("J1502","1"))
        require(nets,"IF_BENCH_GND",("J1501","2"),("R1501","2"),
                ("C1501","2"),("R1502","2"),("J1502","2"))
        assert len(nets)==4,("Unexpected IF power/ground or disconnected nets",sorted(nets))
    print("PASS_KICAD9_AM455_THT7_ERC0_DIODE_CATHODE_NETS_BENCH_ONLY_NO_FAB",flush=True)


if __name__=="__main__":
    main()
