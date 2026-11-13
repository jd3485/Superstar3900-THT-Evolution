#!/usr/bin/env python3
"""Native KiCad9 ERC + netlist for standalone SBL-1+ THT candidate.
Requires IF pins 3 and 4 *wired together*, four grounded device pads,
separate RF/LO input connectors and IF output. Does NOT qualify A06 footprint.
"""
from pathlib import Path
import subprocess
import tempfile
from verify_interboard_audio_contract_native import exported_nets, require

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"04_KiCad/V2.7_DRAFT/MIXER_SBL1_CANDIDATE"
PROJECT="MIXER_SBL1_BENCH_THT_V2_7_DRAFT"
SCH=BASE/(PROJECT+".kicad_sch")
EXPECTED={"MX1701","J1701","J1702","J1703"}

def main():
    schematic=SCH.read_text(encoding="utf-8")
    lib=(BASE/"SBL1_MIXER_OEM_PINOUT.kicad_sym").read_text(encoding="utf-8")
    assert (BASE/(PROJECT+".kicad_pro")).is_file()
    assert schematic.count("(symbol (lib_id ")==4
    assert '(symbol "MCL_SBL1_CANDIDATE:SBL-1_PLUS"' in schematic
    assert '(symbol "SBL-1_PLUS"' in lib
    assert '(lib_id "MCL_SBL1_CANDIDATE:SBL-1_PLUS")' in schematic
    for name in ("IF455_MIXER_IF","RF_27MHZ_INPUT_PENDING",
                 "LO_27MHZ_OFFSET_PENDING","IF_BENCH_GND"):
        assert f'(label "{name}"' in schematic,name
    mix=schematic.split('(lib_id "MCL_SBL1_CANDIDATE:SBL-1_PLUS")',1)[1]
    mix=mix.split("(instances ",1)[0]
    assert '(property "Reference" "MX1701"' in mix
    assert '(property "Footprint" ""' in mix,("A06 footprint not qualified",mix)
    assert all(f'(pin "{i}"' in mix for i in range(1,9))
    assert "NO FAB / NO TX" in schematic
    with tempfile.TemporaryDirectory(prefix="tht_mcl_sbl1_bench_cad_") as td:
        folder=Path(td)
        erc=folder/"sbl1_erc.rpt"
        run=subprocess.run(["kicad-cli","sch","erc","--exit-code-violations",
                            "-o",str(erc),str(SCH)],cwd=ROOT,
                           capture_output=True,text=True)
        print("SBL1_STANDALONE_NATIVE_KICAD9_ERC",run.stdout,run.stderr,flush=True)
        if erc.is_file():
            print("SBL1_STANDALONE_NATIVE_ERC_REPORT",
                  erc.read_text(encoding="utf-8"),flush=True)
        run.check_returncode()
        nets=exported_nets(SCH,folder/"mixer.net")
        observed={ref for members in nets.values() for ref,pin in members}
        assert observed==EXPECTED,("Unexpected native CAD refs",observed,EXPECTED)
        require(nets,"IF455_MIXER_IF",("MX1701","3"),("MX1701","4"),
                ("J1703","1"))
        require(nets,"RF_27MHZ_INPUT_PENDING",("MX1701","1"),("J1701","1"))
        require(nets,"LO_27MHZ_OFFSET_PENDING",("MX1701","8"),("J1702","1"))
        require(nets,"IF_BENCH_GND",("MX1701","2"),("MX1701","5"),
                ("MX1701","6"),("MX1701","7"),("J1701","2"),
                ("J1702","2"),("J1703","2"))
        assert len(nets)==4,sorted(nets)
        for name,members in nets.items():
            print("SBL1_KICAD9_NATIVE_NET",name,sorted(members),flush=True)
    print("PASS_NATIVE_KICAD9_SBL1_4REF_4NETS_ERC0_OEM_IF3_IF4_SHORT_A06_FOOTPRINT_NOT_QUALIFIED_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":main()
