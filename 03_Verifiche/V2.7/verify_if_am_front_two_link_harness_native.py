#!/usr/bin/env python3
"""Native KiCad9 bench signal pin map: IF455->AM455->FRONT.

Separate IF and AF signal/return pairs; NOT a proven electrical cascade.
No power transfer, no production cable/PCB, no fabrication, no TX.
"""
from pathlib import Path
import subprocess
import tempfile
from verify_interboard_audio_contract_native import exported_nets, require

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"04_KiCad/V2.7_DRAFT"
HARNESS=BASE/"IF_AM_FRONT_TWO_LINK_HARNESS_V2_7_DRAFT.kicad_sch"
IF455=BASE/"IF455_TANK/IF455_TANK_THT_V2_7_DRAFT.kicad_sch"
AM455=BASE/"AM455_ENVELOPE/AM455_ENVELOPE_THT_V2_7_DRAFT.kicad_sch"
FRONT=BASE/"FRONT_VOLUME/FRONT_VOLUME_THT_V2_7_DRAFT.kicad_sch"

EXPECTED={
    "IF455_TO_AM455_SIGNAL":{("J2501","1"),("J2502","1")},
    "IF455_TO_AM455_RETURN":{("J2501","2"),("J2502","2")},
    "AM455_TO_FRONT_AF":{("J2503","1"),("J2504","1")},
    "AM455_TO_FRONT_RETURN":{("J2503","2"),("J2504","2")},
}
INTERFACES={
    ("J2501","1"):("J1602","1"),
    ("J2501","2"):("J1602","2"),
    ("J2502","1"):("J1501","1"),
    ("J2502","2"):("J1501","2"),
    ("J2503","1"):("J1502","1"),
    ("J2503","2"):("J1502","2"),
    ("J2504","1"):("J1301","1"),
    ("J2504","2"):("J1301","2"),
}

def main():
    design=HARNESS.read_text(encoding="utf-8")
    assert HARNESS.with_suffix(".kicad_pro").exists()
    assert design.count('(symbol (lib_id "TH_FRONT:AUDIO_2PIN")')==4
    assert design.count("(wire (pts")==4
    assert "(global_label" not in design and "(power" not in design
    assert "NO TX, NO FAB" in design
    for ref in ("J2501","J2502","J2503","J2504"):
        assert design.count('(property "Reference" "'+ref+'"')==1
    with tempfile.TemporaryDirectory(prefix="tht_if_am_front_harness_") as td:
        d=Path(td)
        report=d/"erc.rpt"
        erc=subprocess.run(["kicad-cli","sch","erc","--exit-code-violations",
            "-o",str(report),str(HARNESS)],cwd=ROOT,
            capture_output=True,text=True,timeout=120)
        print("IF_AM_FRONT_HARNESS_ERC_STDOUT",erc.stdout,erc.stderr,flush=True)
        if report.exists():
            print("IF_AM_FRONT_HARNESS_ERC_REPORT",report.read_text(encoding="utf-8"),flush=True)
        erc.check_returncode()
        nets=exported_nets(HARNESS,d/"harness.net")
        ifnets=exported_nets(IF455,d/"if.net")
        amnets=exported_nets(AM455,d/"am.net")
        frontnets=exported_nets(FRONT,d/"front.net")
    assert set(nets)==set(EXPECTED),(nets,EXPECTED)
    for name,members in EXPECTED.items():
        assert nets[name]==members,(name,nets[name],members)
    assert len(set.union(*nets.values()))==8
    assert len(INTERFACES)==8 and len(set(INTERFACES.values()))==8
    require(ifnets,"IF455_FILTER_OUT",("J1602","1"),("C1604","2"))
    require(ifnets,"IF_BENCH_GND",("J1602","2"),("R1602","2"))
    require(amnets,"IF455_BENCH_IN",("J1501","1"),("D1501","2"))
    require(amnets,"IF_BENCH_GND",("J1501","2"),("J1502","2"))
    require(amnets,"AM_DEMOD_AF_BENCH",("J1502","1"),("C1502","2"))
    require(frontnets,"DEMOD_AUDIO",("J1301","1"),("RV1301","1"))
    require(frontnets,"AF_GND",("J1301","2"),("RV1301","3"))
    targets={
        "J1602":ifnets,"J1501":amnets,
        "J1502":amnets,"J1301":frontnets}
    for harness_pin,endpoint in INTERFACES.items():
        name,pin=endpoint
        assert any((name,pin) in pins for pins in targets[name].values()),endpoint
        assert harness_pin in set.union(*nets.values()),harness_pin
    forbidden=("AUDIO_6V_LAB","PLL_5V","13V8","TX_ENABLE","ANTENNA")
    assert not any(any(token in name for token in forbidden) for name in nets)
    print("IF_AM_FRONT_PIN_MAP",INTERFACES,flush=True)
    print("PASS_KICAD9_IF_AM_FRONT_4NETS_8PINS_ERC0_BENCH_PIN_CONTRACT_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
