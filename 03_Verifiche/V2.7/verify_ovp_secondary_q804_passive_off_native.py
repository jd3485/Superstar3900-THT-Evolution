#!/usr/bin/env python3
"""Native KiCad9 Q804 THT passive-off lab topology. NOT a safety qualification."""
from pathlib import Path
import subprocess,tempfile,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"V2.7"))
from verify_interboard_audio_contract_native import exported_nets,require
ROOT=Path(__file__).resolve().parents[2]
SCH=ROOT/"04_KiCad/V2.7_DRAFT/MAIN_SECONDARY_OVP_Q804_PASSIVE_OFF/MAIN_SECONDARY_OVP_Q804_PASSIVE_OFF_LAB_V2_7_DRAFT.kicad_sch"

def main():
    assert SCH.is_file()
    schematic=SCH.read_text(encoding="utf-8")
    assert schematic.count('(symbol (lib_id "LAB_OVP:')==6
    assert "NO FAB / NO TX / NO BATTERIA / NO VEICOLO" in schematic
    assert "IRF9540NPBF" in schematic and "1N4742A" in schematic
    with tempfile.TemporaryDirectory(prefix="q804_ovp_off_native_") as temp:
        t=Path(temp)
        erc=t/"q804.erc"
        check=subprocess.run(["kicad-cli","sch","erc","--exit-code-violations",
                              "-o",str(erc),str(SCH)],cwd=ROOT,capture_output=True,text=True)
        print("Q804_PASSIVE_OFF_NATIVE_ERC",check.stdout,check.stderr,flush=True)
        if erc.exists():print(erc.read_text(encoding="utf-8"),flush=True)
        check.check_returncode()
        nets=exported_nets(SCH,t/"q804.net")
    require(nets,"PRIMARY_PREPROTECTED_LAB",("J2101","1"),("Q804","3"),("R2101","1"),("D2101","1"))
    require(nets,"SECONDARY_GATE_SINK_LAB",("Q804","1"),("R2101","2"),("D2101","2"),("J2103","1"))
    require(nets,"SECONDARY_OUTPUT_LAB",("Q804","2"),("J2102","1"))
    require(nets,"LAB_RETURN_ONLY",("J2101","2"),("J2102","2"),("J2103","2"))
    assert len(nets)==4,sorted(nets)
    # Never silently short source, gate, drain or power return.
    assert all(not (nets[x]&nets[y]) for i,x in enumerate(nets) for y in list(nets)[i+1:])
    assert set.union(*nets.values())=={
        ("J2101","1"),("J2101","2"),("J2102","1"),("J2102","2"),
        ("J2103","1"),("J2103","2"),("Q804","1"),("Q804","2"),
        ("Q804","3"),("R2101","1"),("R2101","2"),("D2101","1"),("D2101","2")}
    print("Q804_PASSIVE_OFF_NATIVE_PIN_NETS",{x:sorted(v) for x,v in nets.items()},flush=True)
    print("PASS_NATIVE_KICAD9_Q804_THT_PASSIVE_OFF_LAB_ERC_NETS_NONFAB",flush=True)

if __name__=="__main__":main()
