#!/usr/bin/env python3
"""Actual KiCad9 ERC/netlist audit of independent 455kHz THT LC bench resonator.
No selectivity, measured Q, OEM coil, mixer, IF gain, AGC or PCB qualification.
"""
from pathlib import Path
import math
import subprocess
import tempfile
from verify_interboard_audio_contract_native import exported_nets,require
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"04_KiCad/V2.7_DRAFT/IF455_TANK"
SCH=BASE/"IF455_TANK_THT_V2_7_DRAFT.kicad_sch"
FP=BASE/"TH_TANK.pretty/L_1mH_Axial_THT_PROVISIONAL.kicad_mod"
PARTS={"J1601","C1601","L1601","C1602","C1603","R1601","C1604","R1602","J1602"}
def main():
    frequency=1/(2*math.pi*math.sqrt(1e-3*112.2e-12))
    assert 473000<frequency<478000,frequency
    sch=SCH.read_text(encoding="utf-8")
    fp=FP.read_text(encoding="utf-8")
    assert sch.count("(symbol (lib_id ")==9
    assert "IF455 BENCH PASSIVE LC ONLY" in sch
    assert "NOT RF QUALIFIED" in sch and "NO FAB" in sch
    assert "L_1mH_Axial_THT_PROVISIONAL" in sch
    assert fp.count(' thru_hole ')==2, "Provisional coil MUST have exactly two THT pads"
    assert '(pad "1" thru_hole circle (at 0 0)' in fp
    assert '(pad "2" thru_hole circle (at 15.24 0)' in fp
    for part in sch.split('(symbol (lib_id ')[1:]:
        section=part.split('(instances ',1)[0]
        footprint=section.split('(property "Footprint" "',1)[1].split('"',1)[0]
        assert footprint.startswith(("Connector_PinHeader_2.54mm:",
                                     "Capacitor_THT:","Resistor_THT:","TH_TANK:")),footprint
    with tempfile.TemporaryDirectory(prefix="tht_if455_tank_") as directory:
        directory=Path(directory)
        rpt=directory/"erc.rpt"
        run=subprocess.run(["kicad-cli","sch","erc","--exit-code-violations",
                           "-o",str(rpt),str(SCH)],
                           cwd=ROOT,capture_output=True,text=True)
        print("IF455_TANK_KICAD9_ERC_STDOUT",run.stdout,run.stderr,flush=True)
        if rpt.exists(): print("IF455_TANK_ERC_REPORT",rpt.read_text(encoding="utf-8"),flush=True)
        run.check_returncode()
        nets=exported_nets(SCH,directory/"tank.net")
        found={ref for nodes in nets.values() for (ref,_pin) in nodes}
        assert PARTS==found,("Missing/extra physical parts",PARTS-found,found-PARTS)
        require(nets,"IF455_SOURCE",("J1601","1"),("C1601","1"))
        require(nets,"IF455_TANK",("C1601","2"),("L1601","1"),
                ("C1602","1"),("C1603","1"),("R1601","1"),("C1604","1"))
        require(nets,"IF455_FILTER_OUT",("C1604","2"),("R1602","1"),
                ("J1602","1"))
        require(nets,"IF_BENCH_GND",("J1601","2"),("J1602","2"),
                ("L1601","2"),("C1602","2"),("C1603","2"),
                ("R1601","2"),("R1602","2"))
        assert len(nets)==4,sorted(nets)
    print("IF455_UNLOADED_LC_IDEAL_RESONANCE_HZ",round(frequency,2),flush=True)
    print("PASS_KICAD9_IF455_THT9_ERC0_1MH_112P2_UNLOADED_PROVISIONAL_NO_FAB",flush=True)
if __name__=="__main__":main()
