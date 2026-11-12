#!/usr/bin/env python3
"""Native KiCad9 test of a *standalone laboratory-only* 6V THT audio supply.

This is not a safety qualification. Never use for a battery or vehicle supply
and never use the thermal *illustration* as proof of device junction limits.
"""
from pathlib import Path
import math
import subprocess
import tempfile
from verify_interboard_audio_contract_native import exported_nets, require

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "04_KiCad/V2.7_DRAFT/AUDIO_PSU_6V"
SCH = BASE / "AUDIO_PSU_LM317_6V_LAB_DRAFT.kicad_sch"
LIB = BASE / "TH_PSU.kicad_sym"
PARTS = {"U1401", "R1401", "R1402", "C1401", "C1402",
         "C1403", "D1401", "D1402", "J1401", "J1402"}


def nominal_vout(vref=1.25, iadj=50e-6, rtop=110.0, rbottom=412.0):
    """First-order TI equation; use typical, not worst-case parameters."""
    return vref * (1 + rbottom / rtop) + iadj * rbottom


def estimated_tj(vin, vout, iout, ambient=60.0, assumed_theta_ja=50.0):
    """Illustrative thermal budget; not a guaranteed datasheet limit."""
    assert vin >= vout > 0 and iout >= 0
    return ambient + (vin - vout) * iout * assumed_theta_ja


def budget_checks():
    assert abs(nominal_vout() - 5.95241818) < 0.002
    assert 5.8 < nominal_vout() < 6.3
    assert 1.20 / (110 * 1.01) >= 0.010, "Regulator divider must support worst-case 10mA minimum load"
    # Conservative illustrative 50 C/W, 60 C ambient. These are not
    # approval for even 9V operation; thermal + PVT review still pending.
    assert estimated_tj(9.0, 6.0, 0.20) == 90.0
    assert estimated_tj(10.0, 6.0, 0.20) == 100.0
    assert estimated_tj(13.8, 6.0, 0.20) > 125.0, "Automotive 13.8V is unsafe in example"
    assert estimated_tj(10.0, 6.0, 0.35) > 125.0, "35% A high-current example violates budget"
    # This circuit is not suitable for an unprotected vehicular environment.
    print("PASS_LM317_6V_DESIGN_EQUATION_AND_NONVEHICULAR_THERMAL_RED_FLAGS", flush=True)


def main():
    budget_checks()
    text = SCH.read_text(encoding="utf-8")
    library = LIB.read_text(encoding="utf-8")
    assert text.count("(symbol (lib_id ") == 10
    assert "LM317T/NOPB" in text and "Package_TO_SOT_THT:TO-220-3_Vertical" in text
    for pin, label in ((1, "ADJ"), (2, "OUT"), (3, "VIN")):
        assert f'(number "{pin}"' in text and f'(name "{label}"' in text
        assert f'(number "{pin}"' in library and f'(name "{label}"' in library
    assert "AUDIO_5V" not in text, "Must not tie into RF/PLL 5V"
    assert "BENCH_ISOLATED_9TO10V" in text and "NO VEHICLE INPUT" in text

    with tempfile.TemporaryDirectory(prefix="tht_audio_psu_") as temp:
        directory = Path(temp)
        report = directory / "erc.rpt"
        check = subprocess.run(
            ["kicad-cli", "sch", "erc", "--exit-code-violations",
             "-o", str(report), str(SCH)],
            cwd=ROOT, capture_output=True, text=True)
        print("PSU_NATIVE_KICAD_ERC:", check.stdout, check.stderr, flush=True)
        if report.exists():
            print("PSU_NATIVE_ERC_REPORT:\\n" + report.read_text(encoding="utf-8"), flush=True)
        check.check_returncode()
        nets = exported_nets(SCH, directory / "psu.net")
        found = {ref for members in nets.values() for (ref, _pin) in members}
        assert PARTS == found, ("Unexpected or missing parts in native netlist",
                                sorted(PARTS - found), sorted(found - PARTS))

        require(nets, "LAB_VIN_9TO10V", ("J1401", "1"), ("U1401", "3"),
                ("C1401", "1"), ("D1401", "2"))
        require(nets, "AUDIO_6V_LAB", ("U1401", "2"), ("J1402", "1"),
                ("R1401", "1"), ("C1402", "1"),
                ("D1401", "1"), ("D1402", "2"))
        require(nets, "AUDIO_ADJ", ("U1401", "1"), ("R1401", "2"),
                ("R1402", "1"), ("C1403", "1"), ("D1402", "1"))
        require(nets, "AUDIO_GND", ("J1401", "2"), ("J1402", "2"),
                ("R1402", "2"), ("C1401", "2"), ("C1402", "2"),
                ("C1403", "2"))
        print("PASS_KICAD9_AUDIO_6V_LM317_PSU_ERC0_THT10_PINNET_NO_FAB", flush=True)


if __name__ == "__main__":
    main()
