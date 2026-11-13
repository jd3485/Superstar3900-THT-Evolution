#!/usr/bin/env python3
"""Native KiCad9 cross-module IF455 tank -> AM455 detector BENCH cable contract.

Each independent schematic is exported through kicad-cli. A matching label
name is NOT required across designs; this checks physical connector pins and
each internal node without claiming a built/mated cable or master integration.
"""
from pathlib import Path
import subprocess
import tempfile
from verify_interboard_audio_contract_native import exported_nets, require

ROOT=Path(__file__).resolve().parents[2]
TANK=ROOT/"04_KiCad/V2.7_DRAFT/IF455_TANK/IF455_TANK_THT_V2_7_DRAFT.kicad_sch"
DETECTOR=ROOT/"04_KiCad/V2.7_DRAFT/AM455_ENVELOPE/AM455_ENVELOPE_THT_V2_7_DRAFT.kicad_sch"

# Two independent THT 2x1 pin-header boundaries. No actual cable specified.
HARNESS={
    ("J1602","1"):("J1501","1"),
    ("J1602","2"):("J1501","2"),
}

def main():
    for schematic, required in (
            (TANK,("J1602","IF455_FILTER_OUT","IF_BENCH_GND")),
            (DETECTOR,("J1501","IF455_BENCH_IN","IF_BENCH_GND"))):
        content=schematic.read_text(encoding="utf-8")
        for item in required:
            assert item in content,(schematic,item)
        assert "NO FAB" in content,(schematic,"fabrication warning absent")
    assert len(HARNESS)==2 and len(set(HARNESS.values()))==2
    assert HARNESS[("J1602","1")]==("J1501","1")
    assert HARNESS[("J1602","2")]==("J1501","2")
    with tempfile.TemporaryDirectory(prefix="tht_if_am_native_") as temp:
        d=Path(temp)
        filtered=exported_nets(TANK,d/"tank.net")
        detected=exported_nets(DETECTOR,d/"am.net")
    # Coil & AC coupling are separate; check OUTPUT reference and RF ground.
    require(filtered,"IF455_FILTER_OUT",("C1604","2"),("R1602","1"),
            ("J1602","1"))
    require(filtered,"IF_BENCH_GND",("J1602","2"),("L1601","2"),
            ("C1602","2"),("C1603","2"),("R1601","2"),("R1602","2"))
    require(filtered,"IF455_TANK",("C1604","1"),("L1601","1"),
            ("C1602","1"),("C1603","1"),("R1601","1"))
    # The AM diode ANODE is pin2, not a swapped cathode:
    require(detected,"IF455_BENCH_IN",("J1501","1"),("D1501","2"))
    require(detected,"AM_RECTIFIED_ENV",("D1501","1"),("R1501","1"),
            ("C1501","1"),("C1502","1"))
    require(detected,"IF_BENCH_GND",("J1501","2"),("R1501","2"),
            ("C1501","2"),("R1502","2"),("J1502","2"))
    assert "IF455_FILTER_OUT" not in detected
    assert "IF455_BENCH_IN" not in filtered
    assert len(filtered)==4 and len(detected)==4
    # Supply or transmitter nets must NOT be routed onto this lab IF cable.
    blocked=("AUDIO_6V_LAB","PLL_5V","13V8","TX","PTT","VCC")
    for forbidden in blocked:
        assert forbidden not in filtered and forbidden not in detected,forbidden
    print("IF455_AM455_DRAFT_2WIRE_PIN_MAP",sorted(HARNESS.items()),flush=True)
    print("PASS_KICAD9_IF455_AM455_J1602_J1501_PIN_NET_DIODE_ANODE_BENCH_NO_FAB",flush=True)

if __name__=="__main__":
    main()
