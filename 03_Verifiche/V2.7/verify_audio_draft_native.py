#!/usr/bin/env python3
"""Check *real* KiCad9 native ERC + netlist for isolated 100% THT RX audio pilot.

Only a draft module, not part of the seven-sheet MAIN V2.6. Test must fail on
ERC errors and cannot be used as a production release or speaker-power proof.
"""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "04_KiCad/V2.7_DRAFT/AUDIO_RX_MONO_LM386_V2_7_DRAFT.kicad_sch"
REQUIRED = {
    "U1201", "R1201", "R1202", "C1201", "C1202",
    "C1203", "C1204", "C1205", "C1206", "J1201", "J1202", "J1203",
}
NETS = {"AUDIO_IN", "PRE_IN", "AMP_IN", "AMP_OUT", "AUDIO_5V",
        "SPK_HOT", "ZOBEL", "BYPASS", "GND"}


def main():
    source = SOURCE.read_text(encoding="utf-8")
    assert source.count("(symbol (lib_id ") == 12
    assert source.count("(in_bom yes)") >= 12
    assert "(footprint" not in source.lower() or "Footprint" in source
    assert "Package_DIP:DIP-8_W7.62mm" in source
    assert "LM386N-1/NOPB" in source
    assert source.count("(no_connect (at ") == 2, "Gain pins intentionally floating"
    with tempfile.TemporaryDirectory(prefix="tht_audio_native_") as folder:
        folder = Path(folder)
        erc = folder / "erc_audio.rpt"
        netfile = folder / "audio.net"
        completed = subprocess.run(
            ["kicad-cli", "sch", "erc", "--exit-code-violations",
             "-o", str(erc), str(SOURCE)],
            cwd=ROOT, text=True, capture_output=True)
        print("KiCad CLI ERC STDOUT:", completed.stdout, flush=True)
        print("KiCad CLI ERC STDERR:", completed.stderr, flush=True)
        if erc.exists():
            print("KiCad9 AUDIO PILOT ERC REPORT:\\n" + erc.read_text(encoding="utf-8"), flush=True)
        completed.check_returncode()
        subprocess.run(
            ["kicad-cli", "sch", "export", "netlist", "-o", str(netfile),
             str(SOURCE)],
            cwd=ROOT, text=True, check=True)
        netlist = netfile.read_text(encoding="utf-8")
        missing = {ref for ref in REQUIRED if f'(ref "{ref}")' not in netlist}
        assert not missing, f"Missing from native netlist: {sorted(missing)}"
        for name in NETS:
            assert name in netlist, f"Missing required native net: {name}"
        print("PASS_KICAD9_AUDIO_DRAFT_ERC0_NETLIST_12_THT", flush=True)


if __name__ == "__main__":
    main()
