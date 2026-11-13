#!/usr/bin/env python3
"""Native KiCad9 ERC/netlist proof of an onsemi-only J113 (1D,2S,3G) TO92
isolated high-impedance IF455 source follower draft. No PCB or hardware gate.
"""
from pathlib import Path
import subprocess
import tempfile
from verify_interboard_audio_contract_native import exported_nets, require

ROOT=Path(__file__).resolve().parents[2]
PROJECT="IF455_J113_SOURCE_FOLLOWER_THT_V2_7_DRAFT"
BASE=ROOT/"04_KiCad/V2.7_DRAFT/IF455_J113_SOURCE_FOLLOWER"
SCH=BASE/(PROJECT+".kicad_sch")
EXPECTED={"J1801","J1802","J1803","C1801","R1801",
          "Q1801","R1802","C1802","R1803"}

def main():
    schematic=SCH.read_text(encoding="utf-8")
    lib=(BASE/"TH_J113.kicad_sym").read_text(encoding="utf-8")
    table=(BASE/"sym-lib-table").read_text(encoding="utf-8")
    assert (BASE/(PROJECT+".kicad_pro")).is_file()
    assert 'TH_J113' in table
    assert schematic.count("(symbol (lib_id ")==9
    for expected in ("ONSEMI_J113_TO92_1D_2S_3G_ONLY_CANDIDATE",
                     "ONLY onsemi J113: PIN1 DRAIN / PIN2 SOURCE / PIN3 GATE",
                     "C0G_RF_INPUT_PROVISIONAL", "1Meg_GATE_DC_RETURN_PROVISIONAL",
                     "2k2_SOURCE_SELF_BIAS_DRAFT","NO FAB / NO TX"):
        assert expected in schematic,expected
    assert '(symbol "TH_J113:JFET"' in schematic
    assert '(symbol "JFET"' in lib
    for number,name in (("1","D"),("2","S"),("3","G")):
        assert '(number "'+number+'" ' in schematic,number
        assert '(number "'+number+'" ' in lib,number
        assert '(name "'+name+'" ' in lib,name
    for part in schematic.split("(symbol (lib_id ")[1:]:
        block=part.split("(instances ",1)[0]
        fp=block.split('(property "Footprint" "',1)[1].split('"',1)[0]
        assert fp.startswith(("Connector_PinHeader_2.54mm:","Resistor_THT:",
                              "Capacitor_THT:","Package_TO_SOT_THT:TO-92_Inline")),fp
    with tempfile.TemporaryDirectory(prefix="tht_if455_j113_kicad9_") as d:
        folder=Path(d)
        erc=folder/"erc.rpt"
        run=subprocess.run(["kicad-cli","sch","erc","--exit-code-violations","-o",
                            str(erc),str(SCH)],cwd=ROOT,capture_output=True,text=True)
        print("IF455_J113_KICAD9_ERC_OUTPUT",run.stdout,run.stderr,flush=True)
        if erc.is_file():print("IF455_J113_NATIVE_ERC_REPORT",
                               erc.read_text(encoding="utf-8"),flush=True)
        run.check_returncode()
        nets=exported_nets(SCH,folder/"jfetsch.net")
        observed={ref for connections in nets.values() for ref,pin in connections}
        assert observed==EXPECTED,(EXPECTED-observed,observed-EXPECTED)
        require(nets,"IF455_TANK_OUT",("J1801","1"),("C1801","1"))
        require(nets,"JFET_GATE",("C1801","2"),("R1801","1"),("Q1801","3"))
        require(nets,"VLAB6_JFET_ONLY",("J1803","1"),("Q1801","1"))
        require(nets,"JFET_SOURCE",("Q1801","2"),("R1802","1"),("C1802","1"))
        require(nets,"JFET_AC_OUT",("C1802","2"),("R1803","1"),("J1802","1"))
        require(nets,"IF_BENCH_GND",("J1801","2"),("J1802","2"),
                ("J1803","2"),("R1801","2"),("R1802","2"),("R1803","2"))
        assert len(nets)==6,sorted(nets)
    print("PASS_NATIVE_KICAD9_ONSEMI_J113_TO92_9THT_6NETS_ERC0_PIN1D_2S_3G_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
