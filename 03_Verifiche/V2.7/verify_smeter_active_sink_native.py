#!/usr/bin/env python3
"""KiCad 9 native ERC + exact pin/net for isolated ACTIVE S-meter current sink.

This bench uses MCP6002 PDIP8 and onsemi-style TO-92 E1 B2 C3 candidate;
it is not connected to MAIN nor FRONT and has no current/FSD safety approval.
"""
from pathlib import Path
import subprocess
import tempfile

from verify_interboard_audio_contract_native import exported_nets, require

ROOT=Path(__file__).resolve().parents[2]
SCH=ROOT/"04_KiCad/V2.7_DRAFT/SMETER_ACTIVE_SINK_BENCH/SMETER_ACTIVE_SINK_BENCH_V2_7_DRAFT.kicad_sch"
NETS={
    "VLAB5":{("J2101","1"),("J2103","1"),("U2101","8")},
    "GND":{("J2101","2"),("J2102","2"),("U2101","4"),("U2101","5"),("R2101","2"),("R2103","2")},
    "VSET_LAB":{("J2102","1"),("U2101","3")},
    "SENSE":{("U2101","2"),("Q2101","1"),("R2101","1")},
    "OPAMP_DRIVE":{("U2101","1"),("R2102","1")},
    "BASE":{("R2102","2"),("Q2101","2"),("R2103","1")},
    "COIL_LOW":{("J2103","2"),("Q2101","3")},
    "IDLE_B":{("U2101","6"),("U2101","7")},
}

def main():
    sch=SCH.read_text(encoding="utf-8")
    lib=(SCH.parent/"TH_SMETERDRIVE.kicad_sym").read_text(encoding="utf-8")
    table=(SCH.parent/"sym-lib-table").read_text(encoding="utf-8")
    assert (SCH.parent/"SMETER_ACTIVE_SINK_BENCH_V2_7_DRAFT.kicad_pro").is_file()
    assert "TH_SMETERDRIVE.kicad_sym" in table
    assert sch.count('(symbol (lib_id "TH_SMETERDRIVE:') == 8
    assert "NO FAB NO TX" in sch
    assert "Package_TO_SOT_THT:TO-92_Inline" in sch
    assert "Package_DIP:DIP-8_W7.62mm" in sch
    for reference in ("Q2101","U2101","J2101","J2102","J2103","R2101","R2102","R2103"):
        assert sch.count('(property "Reference" "'+reference+'"') == 1,reference
    for name,pin in (("E","1"),("B","2"),("C","3")):
        token='(name "'+name+'" (effects (font (size 1 1)))) (number "'+pin+'"'
        assert token in sch and token in lib,token
    for pin in "123":
        assert '(pin "'+pin+'"' in sch
    with tempfile.TemporaryDirectory(prefix="tht_smeter_active_sink_") as d:
        erc=Path(d)/"erc.rpt"
        cp=subprocess.run(["kicad-cli","sch","erc","--exit-code-violations",
                           "-o",str(erc),str(SCH)],cwd=ROOT,
                          capture_output=True,text=True,timeout=120)
        print("ACTIVE_SINK_ERC_STDOUT",cp.stdout,cp.stderr,flush=True)
        if erc.exists():
            print("ACTIVE_SINK_ERC_REPORT",erc.read_text(encoding="utf-8"),flush=True)
        cp.check_returncode()
        nets=exported_nets(SCH,Path(d)/"active_sink.net")
    assert set(nets)==set(NETS),(nets.keys(),NETS.keys())
    for label,members in NETS.items():
        require(nets,label,*sorted(members))
        assert set(nets[label])==members,(label,nets[label],members)
    assert sum(len(m) for m in nets.values())==23
    print("ACTIVE_SINK_KICAD_NATIVE",{"refs":8,"nets":8,"pins":23,
           "Q2101_footprint":"TO-92_Inline 1E 2B 3C candidate",
           "coil_FSD_and_driver_stability_qualified":False,
           "no_main_front_physical_connection":True,
           "NO_FAB_NO_TX":True},flush=True)
    print("PASS_KICAD9_ACTIVE_SMETER_SINK_ERC0_NETS8_PINS23_LAB_ONLY_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
