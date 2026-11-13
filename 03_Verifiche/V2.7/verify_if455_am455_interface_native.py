#!/usr/bin/env python3
"""Native KiCad9 IF455 tank ↔ AM455 detector *proposed* two-wire interface.

Checks BOTH independent schematic exports. No physical harness exists yet,
no impedance qualification, no mixer/IF sensitivity, no FM/SSB, NO FAB.
"""
from pathlib import Path
import tempfile
from verify_interboard_audio_contract_native import exported_nets,require

ROOT=Path(__file__).resolve().parents[2]
IF455=ROOT/"04_KiCad/V2.7_DRAFT/IF455_TANK/IF455_TANK_THT_V2_7_DRAFT.kicad_sch"
AM455=ROOT/"04_KiCad/V2.7_DRAFT/AM455_ENVELOPE/AM455_ENVELOPE_THT_V2_7_DRAFT.kicad_sch"
HARNESS={("J1602","1"):("J1501","1"),("J1602","2"):("J1501","2")}


def main():
    with tempfile.TemporaryDirectory(prefix="tht_if455_am455_contract_") as folder:
        target=Path(folder)
        source=exported_nets(IF455,target/"if455.net")
        receiver=exported_nets(AM455,target/"am455.net")
    assert len(source)==4 and len(receiver)==4,("Unexpected pilot nets",source,receiver)
    require(source,"IF455_FILTER_OUT",("J1602","1"),("R1602","1"),("C1604","2"))
    require(source,"IF_BENCH_GND",("J1602","2"),("R1602","2"),
            ("C1603","2"),("L1601","2"))
    require(receiver,"IF455_BENCH_IN",("J1501","1"),("D1501","2"))
    require(receiver,"IF_BENCH_GND",("J1501","2"),("R1501","2"),
            ("C1501","2"),("J1502","2"))
    require(receiver,"AM_RECTIFIED_ENV",("D1501","1"),("R1501","1"),
            ("C1501","1"),("C1502","1"))
    require(receiver,"AM_DEMOD_AF_BENCH",("C1502","2"),("J1502","1"))
    assert len(HARNESS)==2 and len(set(HARNESS.values()))==2
    all_output={v for nodes in source.values() for v in nodes}
    all_input={v for nodes in receiver.values() for v in nodes}
    assert ("J1602","1") in all_output and ("J1602","2") in all_output
    assert ("J1501","1") in all_input and ("J1501","2") in all_input
    for _from,_to in HARNESS.items():
        assert _from in all_output and _to in all_input,(_from,_to)
    # These isolated source/destination schematics must NEVER be tied
    # to any of the audio amplifier, PLL, TX power rails.
    forbidden=("AUDIO_6V_LAB","PLL_5V","VCC","13V8","TX_ENABLE","ANTENNA")
    assert not any(any(bad in name for bad in forbidden) for name in source),source
    assert not any(any(bad in name for bad in forbidden) for name in receiver),receiver
    print("IF455_TANK_TO_AM455_ENVELOPE_PIN_MAP_BENCH_ONLY",HARNESS,flush=True)
    print("IF455_DETECTOR_LOADING_UNMODELLED_UNTIL_END_TO_END_SPICE_AND_MEASUREMENTS",flush=True)
    print("PASS_KICAD9_NATIVE_IF455_AM455_2WIRE_IF_CONTRACT_NO_FAB_NO_TX",flush=True)


if __name__=="__main__":
    main()
