#!/usr/bin/env python3
"""Native KiCad9 cross-schematic mixer IF -> IF455 tank boundary contract.

Uses two exported REAL native netlists, not label-search as proof. Computes
only input coupling reactance and port boundaries, not vendor mixer Zout
or conversion gain. Two stand-alone pilot schematics remain unconnected.
NO FAB / NO TX / NO BATTERY / NO VEHICLE.
"""
from pathlib import Path
import math
import tempfile
from verify_interboard_audio_contract_native import exported_nets,require

ROOT=Path(__file__).resolve().parents[2]
MIXER=ROOT/"04_KiCad/V2.7_DRAFT/MIXER_SBL1_CANDIDATE/MIXER_SBL1_BENCH_THT_V2_7_DRAFT.kicad_sch"
IF455=ROOT/"04_KiCad/V2.7_DRAFT/IF455_TANK/IF455_TANK_THT_V2_7_DRAFT.kicad_sch"
# Proposed bench-only cable map, NOT an actual harness or layout.
HARNESS={
    ("J1703","1"):("J1601","1"),
    ("J1703","2"):("J1601","2"),
}
IF_HZ=455000.0
C_INPUT_F=10.0e-12

def main():
    with tempfile.TemporaryDirectory(prefix="tht_mixer_to_if455_") as tmp:
        folder=Path(tmp)
        mixer=exported_nets(MIXER,folder/"sbl1_mixer.net")
        tank=exported_nets(IF455,folder/"if455_tank.net")
    assert len(mixer)==4,sorted(mixer)
    assert len(tank)==4,sorted(tank)
    require(mixer,"IF455_MIXER_IF",("MX1701","3"),("MX1701","4"),
            ("J1703","1"))
    require(mixer,"IF_BENCH_GND",("MX1701","2"),("MX1701","5"),
            ("MX1701","6"),("MX1701","7"),("J1703","2"))
    require(mixer,"RF_27MHZ_INPUT_PENDING",("MX1701","1"),("J1701","1"))
    require(mixer,"LO_27MHZ_OFFSET_PENDING",("MX1701","8"),("J1702","1"))
    require(tank,"IF455_SOURCE",("J1601","1"),("C1601","1"))
    require(tank,"IF_BENCH_GND",("J1601","2"),("J1602","2"),
            ("L1601","2"),("C1603","2"))
    require(tank,"IF455_TANK",("C1601","2"),("L1601","1"),
            ("C1602","1"),("R1601","1"))
    require(tank,"IF455_FILTER_OUT",("J1602","1"),("C1604","2"),
            ("R1602","1"))
    assert set(HARNESS.keys())=={("J1703","1"),("J1703","2")}
    assert len(set(HARNESS.values()))==2
    mix_nodes={node for members in mixer.values() for node in members}
    tank_nodes={node for members in tank.values() for node in members}
    for source,dest in HARNESS.items():
        assert source in mix_nodes and dest in tank_nodes,(source,dest)
    assert ("MX1701","3") not in mixer["IF_BENCH_GND"]
    assert ("MX1701","4") not in mixer["IF_BENCH_GND"]
    for name in ( "RF_27MHZ_INPUT_PENDING","LO_27MHZ_OFFSET_PENDING"):
        assert not any(ref=="J1703" for ref,pin in mixer[name])
    # Guard no power or TX rail accidentally crosses these two bench interfaces.
    forbidden=("TX_ENABLE","BATTERY","13V8","AUDIO_6V","POWER20")
    assert not any(any(token in n for token in forbidden) for n in (*mixer,*tank))
    # First pole is nominal 10pF coupling, NOT a 50-ohm port termination.
    sch=IF455.read_text(encoding="utf-8")
    assert '(property "Reference" "C1601"' in sch
    assert '(property "Value" "10pF_C0G_INPUT_COUPLING"' in sch
    x_c=1/(2*math.pi*IF_HZ*C_INPUT_F)
    assert 34900<x_c<35100,x_c
    # Compared to hypothetical resistive source scenarios, input coupling
    # reactance cannot be treated as zero or an ideal 50-ohm match.
    assert x_c>100*50.0
    print("MIXER_IF455_NATIVE_BOUNDARY_CABLE_DRAFT",HARNESS,flush=True)
    print("MIXER_IF455_C1601_INPUT_SERIES_REACTANCE_AT_455KHZ_OHM",
          round(x_c,3),"component_nominal_10pF_only",flush=True)
    print("MIXER_IF455_SOURCE_ZOUT_UNCHARACTERIZED_NO_GAIN_OR_MATCH_CLAIM",flush=True)
    print("PASS_NATIVE_KICAD9_MIXER_TO_IF455_TWO_PIN_IF3_IF4_TIED_C1601_REACTANCE_NO_MATCH_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":main()
