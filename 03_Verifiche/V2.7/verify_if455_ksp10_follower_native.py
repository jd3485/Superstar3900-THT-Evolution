#!/usr/bin/env python3
"""Native KiCad9 KSP10BU 455kHz bench emitter follower pin/net/ERC audit.
Prototype schematic only. No RF, thermal, PVT, OEM production or fab approval.
"""
from pathlib import Path
import subprocess
import tempfile
from verify_interboard_audio_contract_native import exported_nets, require

ROOT=Path(__file__).resolve().parents[2]
PROJECT="IF455_KSP10_FOLLOWER_THT_V2_7_DRAFT"
SCH=ROOT/"04_KiCad/V2.7_DRAFT/IF455_KSP10_FOLLOWER"/(PROJECT+".kicad_sch")
PARTS={"J1701","J1702","J1703","C1701","C1702",
       "R1701","R1702","R1703","R1704","Q1701"}

def main():
    s=SCH.read_text(encoding="utf-8")
    assert s.count("(symbol (lib_id ")==len(PARTS)
    assert "ONSEMI_KSP10BU_TO92_CANDIDATE" in s
    assert 'Package_TO_SOT_THT:TO-92_Inline' in s
    assert "(pin \"1\" (uuid" in s
    for term in ('(number "1"', '(number "2"', '(number "3"',
                 "PIN1 BASE / PIN2 EMITTER / PIN3 COLLECTOR",
                 "NO FAB / NO TX", "6V BENCH ONLY"):
        assert term in s, term
    assert "Footprint" in s
    base=SCH.parent
    assert (base/"TH_IFBUF.kicad_sym").is_file()
    assert (base/"sym-lib-table").is_file()
    assert (base/(PROJECT+".kicad_pro")).is_file()
    assert "TH_IFBUF" in (base/"sym-lib-table").read_text(encoding="utf-8")
    # Refuse SMD footprints in every placed physical component.
    for block in s.split("(symbol (lib_id ")[1:]:
        section=block.split("(instances ",1)[0]
        fp=section.split('(property "Footprint" "',1)[1].split('"',1)[0]
        assert fp.startswith(("Connector_PinHeader_2.54mm:","Resistor_THT:",
                              "Capacitor_THT:","Package_TO_SOT_THT:TO-92_Inline")),fp
    with tempfile.TemporaryDirectory(prefix="tht_ksp10_if455_") as tmp:
        folder=Path(tmp)
        report=folder/"erc.rpt"
        cmd=["kicad-cli","sch","erc","--exit-code-violations",
             "-o",str(report),str(SCH)]
        run=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
        print("KSP10_IF455_NATIVE_ERC_STDOUT",run.stdout,run.stderr,flush=True)
        if report.exists():
            print("KSP10_IF455_NATIVE_ERC_REPORT",
                  report.read_text(encoding="utf-8"),flush=True)
        run.check_returncode()
        nets=exported_nets(SCH,folder/"ifbuf.net")
        refs={r for pins in nets.values() for r,p in pins}
        assert refs==PARTS, (PARTS-refs,refs-PARTS)
        require(nets,"IF455_TANK_OUT",("J1701","1"),("C1701","1"))
        require(nets,"IFBUF_BASE_BIAS",("C1701","2"),("R1701","2"),
                ("R1702","1"),("Q1701","1"))
        require(nets,"VLAB6_IFBUF_ONLY",("J1703","1"),("R1701","1"),
                ("Q1701","3"))
        require(nets,"IFBUF_EMITTER",("Q1701","2"),("R1703","1"),
                ("C1702","1"))
        require(nets,"IFBUF_AC_OUT",("C1702","2"),("R1704","1"),
                ("J1702","1"))
        require(nets,"IF_BENCH_GND",("J1701","2"),("J1702","2"),
                ("J1703","2"),("R1702","2"),("R1703","2"),("R1704","2"))
        assert len(nets)==6,sorted(nets)
    print("PASS_NATIVE_KICAD9_IF455_KSP10BU_BENCH_THT10_PINPAD_NET_ERC0_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
