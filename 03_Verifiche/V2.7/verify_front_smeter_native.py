#!/usr/bin/env python3
"""Native KiCad9 ERC and strict pins↔nets for isolated FRONT analog S-meter.

NOT a qualified meter, protection network, MAIN-FRONT cable or production PCB.
The two 100k series resistor candidates and 10k potentiometer are only schematic candidates:
full-scale meter current, coil resistance and MAIN drive are NOT specified.
"""
from pathlib import Path
import subprocess
import tempfile

from verify_interboard_audio_contract_native import exported_nets, require

ROOT=Path(__file__).resolve().parents[2]
SCH=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_SMETER/FRONT_SMETER_THT_V2_7_DRAFT.kicad_sch"

def main():
    text=SCH.read_text(encoding="utf-8")
    assert text.count("(symbol (lib_id ")==5
    assert all(text.count(f'(property "Reference" "{ref}"')==1
               for ref in ("J1801","J1802","RV1801","R1801","R1802"))
    assert "100k_0P25W_CANDIDATE_NO_FSD_QUAL" in text
    assert "100k_0P25W_REDUNDANT_CANDIDATE_NO_FSD_QUAL" in text
    assert "THT_DRAFT_PROVISIONAL" in text
    assert "TH_FRONT:Potentiometer_THT_3Pin_PROVISIONAL" in text
    assert "METER_DRIVE_CANDIDATE" in text and "METER_POS_LIMITED" in text
    footprint=SCH.parent/"TH_FRONT.pretty/Potentiometer_THT_3Pin_PROVISIONAL.kicad_mod"
    mod=footprint.read_text(encoding="utf-8")
    assert "DO NOT FAB" in mod and "PROVISIONAL" in mod
    assert mod.count(" thru_hole ")==3
    for pad in ("1","2","3"):
        assert f'(pad "{pad}" thru_hole ' in mod
    fp_table=(SCH.parent/"fp-lib-table").read_text(encoding="utf-8")
    assert 'TH_FRONT' in fp_table and 'TH_FRONT.pretty' in fp_table
    sym_table=(SCH.parent/"sym-lib-table").read_text(encoding="utf-8")
    assert 'TH_FRONT.kicad_sym' in sym_table and 'TH_SMETER.kicad_sym' in sym_table
    assert (SCH.parent/"FRONT_SMETER_THT_V2_7_DRAFT.kicad_pro").exists()
    frontend_symbols=(SCH.parent/"TH_FRONT.kicad_sym").read_text(encoding="utf-8")
    resistor_symbols=(SCH.parent/"TH_SMETER.kicad_sym").read_text(encoding="utf-8")
    assert '(symbol "POT_MONO_THT"' in frontend_symbols
    assert '(symbol "AUDIO_2PIN"' in frontend_symbols
    assert '(symbol "R"' in resistor_symbols
    with tempfile.TemporaryDirectory(prefix="tht_front_smeter_") as d:
        erc=Path(d)/"erc.rpt"
        process=subprocess.run(["kicad-cli","sch","erc","--exit-code-violations",
                                "-o",str(erc),str(SCH)],
                               cwd=ROOT,capture_output=True,text=True)
        print("SMETER_KICAD_ERC",process.stdout,process.stderr,flush=True)
        if erc.exists():
            print(erc.read_text(encoding="utf-8"),flush=True)
        process.check_returncode()
        nets=exported_nets(SCH,Path(d)/"smeter.net")
        require(nets,"METER_DRIVE_CANDIDATE",("J1801","1"),("RV1801","1"))
        require(nets,"METER_TRIM_OUTPUT",("RV1801","2"),("R1801","1"))
        require(nets,"METER_LIMIT_STAGE1",("R1801","2"),("R1802","1"))
        require(nets,"METER_POS_LIMITED",("R1802","2"),("J1802","1"))
        require(nets,"METER_RETURN",("J1801","2"),("RV1801","3"),("J1802","2"))
        # Ensure no unintended short around the resistor/trim and that
        # no local supply or TX pins were added to the isolated harness.
        relevant=("METER_DRIVE_CANDIDATE","METER_TRIM_OUTPUT",
                  "METER_LIMIT_STAGE1","METER_POS_LIMITED","METER_RETURN")
        assert len(set(relevant))==5
        for a in relevant:
            for b in relevant:
                if a!=b:
                    assert not (nets[a]&nets[b]),(a,b,nets[a]&nets[b])
        assert set.union(*(nets[x] for x in relevant))=={
            ("J1801","1"),("J1801","2"),("RV1801","1"),
            ("RV1801","2"),("RV1801","3"),("R1801","1"),
            ("R1801","2"),("R1802","1"),("R1802","2"),
            ("J1802","1"),("J1802","2")}
        print("FRONT_SMETER_NATIVE_PIN_CONTRACT",
              {k:sorted(nets[k]) for k in relevant},flush=True)
    print("PASS_KICAD9_FRONT_SMETER_ERC0_DUAL_SERIES_THT_LIMITERS_NETLIST_NO_FSD_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
