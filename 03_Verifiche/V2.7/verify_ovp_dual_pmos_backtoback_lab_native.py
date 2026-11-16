#!/usr/bin/env python3
"""Native KiCad9 isolated THT back-to-back PMOS pin-net and ideal fault screen.
NO safety qualification: independent gate controller absent; never energize.
"""
from pathlib import Path
import math
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets, require

SCH = ROOT / "04_KiCad/V2.7_DRAFT/MAIN_SECONDARY_OVP_Q804_Q805_ANTISERIES/MAIN_SECONDARY_OVP_Q804_Q805_B2B_LAB_V2_7_DRAFT.kicad_sch"
EXPECTED = {
    "PRIMARY_IN_DRAIN_LAB": {("J2101", "1"), ("Q804", "2")},
    "FLOATING_COMMON_SOURCE_LAB": {("Q804", "3"), ("Q805", "3"),
                                   ("D2101", "1"), ("R2101", "1")},
    "COMMON_GATE_LAB": {("Q804", "1"), ("Q805", "1"),
                        ("D2101", "2"), ("R2101", "2"), ("R2102", "2")},
    "SECONDARY_OUT_DRAIN_LAB": {("Q805", "2"), ("J2102", "1")},
    "DRIVER_SINK_LAB": {("J2103", "1"), ("R2102", "1")},
    "LAB_RETURN_ONLY": {("J2101", "2"), ("J2102", "2"), ("J2103", "2")},
}

def reachable(edges, start, finish):
    seen = {start}
    stack = [start]
    while stack:
        node = stack.pop()
        if node == finish:
            return True
        for a, b in edges:
            if a == node and b not in seen:
                seen.add(b)
                stack.append(b)
    return False


def main():
    s = SCH.read_text(encoding="utf-8")
    assert s.count('(symbol (lib_id "LAB_OVP:') == 8
    assert "NO FAB / NO TX / NO BATTERIA / NO VEICOLO" in s
    assert "IRF9540NPBF" in s and "10k_GATE_DRIVER_SERIES_UNQUALIFIED" in s
    with tempfile.TemporaryDirectory(prefix="tht_dual_pfet_nonfab_") as tmp:
        output = Path(tmp)
        report = output / "dual_pfet.erc"
        cmd = ["kicad-cli", "sch", "erc", "--exit-code-violations",
               "-o", str(report), str(SCH)]
        checked = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        print("DUAL_PFET_NATIVE_ERC:", checked.stdout, checked.stderr, flush=True)
        if report.exists():
            print(report.read_text(encoding="utf-8"), flush=True)
        checked.check_returncode()
        nets = exported_nets(SCH, output / "dual_pfet.net")
    assert len(nets) == 6, sorted(nets)
    assert set(nets) == set(EXPECTED), sorted(nets)
    for name, pins in EXPECTED.items():
        require(nets, name, *pins)
        assert nets[name] == pins, (name, sorted(nets[name]), sorted(pins))
    all_pins = [pin for pins in nets.values() for pin in pins]
    assert len(all_pins) == 18 and len(set(all_pins)) == 18
    assert sum(map(len, EXPECTED.values())) == 18

    # OEM IRF9540N P-channel body diodes conduct from D to S only.
    # Common-source outward-drain geometry forbids either input->output
    # or output->input path in the ideal OFF/body-diode-only graph.
    intrinsic = {
        ("PRIMARY_IN_DRAIN_LAB", "FLOATING_COMMON_SOURCE_LAB"),
        ("SECONDARY_OUT_DRAIN_LAB", "FLOATING_COMMON_SOURCE_LAB"),
    }
    assert not reachable(intrinsic, "PRIMARY_IN_DRAIN_LAB", "SECONDARY_OUT_DRAIN_LAB")
    assert not reachable(intrinsic, "SECONDARY_OUT_DRAIN_LAB", "PRIMARY_IN_DRAIN_LAB")
    # Real TO-220 tab = DRAIN: an uninsulated shared heatsink bypasses.
    assert reachable(intrinsic | {("PRIMARY_IN_DRAIN_LAB",
                                  "SECONDARY_OUT_DRAIN_LAB")},
                     "PRIMARY_IN_DRAIN_LAB", "SECONDARY_OUT_DRAIN_LAB")

    # Hypothetical HARD GATE SINK at J2103 and ideal 12V Zener.
    # Only mathematical static divider/ideal clamp; not vendor SPICE.
    r_gs = 47_000.0
    r_sink = 10_000.0
    vz = 12.0
    max_series_w = 0.0
    for vin in (0.0, 5.0, 8.0, 10.0, 12.0, 13.8, 16.0, 20.0, 24.0, 36.0, 48.0):
        vgs_abs = min(vin * r_gs / (r_gs + r_sink), vz)
        assert vgs_abs <= vz + 1e-12
        if vin * r_gs / (r_gs + r_sink) > vz:
            series_i = (vin - vz) / r_sink
            zener_i = series_i - vz / r_gs
            assert zener_i > 0
            series_w = series_i ** 2 * r_sink
            zener_w = vz * zener_i
            assert series_w >= 0 and zener_w >= 0
            max_series_w = max(max_series_w, series_w)
        else:
            series_i = vin / (r_gs + r_sink)
            assert series_i >= 0
    assert math.isclose(max_series_w, 0.1296, abs_tol=1e-9)
    open_zener_vgs_48 = 48.0 * r_gs / (r_gs + r_sink)
    assert open_zener_vgs_48 > 20.0  # PMOS absolute max exceeded in this assumed fault!
    print("DUAL_PFET_IDEAL_FAULT_SCREEN", {
        "nets": len(nets),
        "physical_pins": len(all_pins),
        "intrinsic_diodes_bidirectional_off_isolation_ideal_only": True,
        "uninsulated_common_tab_drain_short_bypasses": True,
        "nominal_13v8_hard_sink_VGS_abs_V": round(13.8 * r_gs / (r_gs + r_sink), 5),
        "ideal_48V_closed_zener_R2102_peak_W": max_series_w,
        "48V_zener_open_VGS_abs_V": round(open_zener_vgs_48, 5),
        "Q804_Q805_source_current_limits_vendor_qualified": False,
        "D2101_dynamic_clamp_qualified": False,
        "independent_supervisor_present": False,
        "physical_thermal_review_complete": False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE": True
    }, flush=True)
    print("PASS_NATIVE_KICAD9_THT_DUAL_PMOS_BACKTOBACK_18PINS_6NETS_IDEAL_SCREEN_NONFAB", flush=True)

if __name__ == "__main__":
    main()
