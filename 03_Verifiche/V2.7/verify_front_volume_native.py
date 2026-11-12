#!/usr/bin/env python3
"""Strict native KiCad9 ERC and netlist checks for isolated FRONT THT volume pilot.

Not a production approval: the potentiometer pad pattern is explicitly
provisional and must not be fabricated without a qualified OEM replacement.
"""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "04_KiCad/V2.7_DRAFT/FRONT_VOLUME"
SCH = BASE / "FRONT_VOLUME_THT_V2_7_DRAFT.kicad_sch"
MOD = BASE / "TH_FRONT.pretty/Potentiometer_THT_3Pin_PROVISIONAL.kicad_mod"
EXPECTED = {"RV1301", "J1301", "J1302"}
NETS = {"DEMOD_AUDIO", "VOL_WIPER_TO_AMP", "AF_GND"}


def main():
    sch = SCH.read_text(encoding="utf-8")
    assert sch.count("(symbol (lib_id ") == 3
    assert "TH_FRONT:Potentiometer_THT_3Pin_PROVISIONAL" in sch
    assert all(sch.count(f'(property "Reference" "{ref}"') == 1 for ref in EXPECTED)
    assert "(hierarchical_label " not in sch
    mod = MOD.read_text(encoding="utf-8")
    assert all(f'(pad "{p}" thru_hole ' in mod for p in ("1", "2", "3"))
    assert mod.count(" thru_hole ") == 3
    assert "PROVISIONAL" in mod and "DO NOT FAB" in mod
    with tempfile.TemporaryDirectory(prefix="tht_front_volume_") as directory:
        erc = Path(directory) / "front_erc.rpt"
        netfile = Path(directory) / "front.net"
        checked = subprocess.run(
            ["kicad-cli", "sch", "erc", "--exit-code-violations",
             "-o", str(erc), str(SCH)],
            cwd=ROOT, capture_output=True, text=True)
        print(checked.stdout, checked.stderr, flush=True)
        if erc.exists():
            print("FRONT_VOLUME_ERC_REPORT\n" + erc.read_text(encoding="utf-8"), flush=True)
        checked.check_returncode()
        subprocess.run(
            ["kicad-cli", "sch", "export", "netlist", "-o", str(netfile), str(SCH)],
            cwd=ROOT, check=True)
        netlist = netfile.read_text(encoding="utf-8")
        for ref in EXPECTED:
            assert f'(ref "{ref}")' in netlist, ("Missing ref from native netlist", ref)
        for net in NETS:
            assert f'(name "{net}")' in netlist, ("Missing named net", net)
        assert "TH_FRONT:Potentiometer_THT_3Pin_PROVISIONAL" in netlist
        print("PASS_KICAD9_FRONT_VOLUME_ERC0_THREE_COMPONENT_THT_NETLIST_NOT_FOR_FAB", flush=True)


if __name__ == "__main__":
    main()
