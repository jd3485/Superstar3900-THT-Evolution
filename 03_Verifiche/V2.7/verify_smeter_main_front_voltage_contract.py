#!/usr/bin/env python3
"""Explicit no-connection MAIN/FRONT S-meter voltage-versus-current contract.

Both current designs are isolated KiCad9 bench schematics. This proves only
that the MCP6002 follower's 5V lab source cannot be assumed to deliver the
required unknown moving-coil FSD through the two provisional FRONT 100k
series resistors. It does NOT connect these boards or authorize build.
"""
from pathlib import Path
from verify_front_smeter_fsd_fault_screen import screen
from verify_smeter_mcp6002_highz_native import EXPECTED as SOURCE_NETS

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "04_KiCad/V2.7_DRAFT/SMETER_MCP6002_HIGHZ_BENCH/SMETER_MCP6002_HIGHZ_BENCH_V2_7_DRAFT.kicad_sch"
FRONT = ROOT / "04_KiCad/V2.7_DRAFT/FRONT_SMETER/FRONT_SMETER_THT_V2_7_DRAFT.kicad_sch"


def verify():
    src = SOURCE.read_text(encoding="utf-8")
    dst = FRONT.read_text(encoding="utf-8")
    # The pre-existing native KiCad tests independently ERC/netlist-check
    # these exact connectors; this test checks a NON-BINDING contract.
    assert ("J1902", "1") in SOURCE_NETS["SMBUF_VOUT_BENCH"]
    assert ("J1902", "2") in SOURCE_NETS["SMBUF_BENCH_GND"]
    assert "SMBUF_VOUT_BENCH" in src and "VLAB5_BUFFER" in src
    assert "METER_DRIVE_CANDIDATE" in dst and "METER_RETURN" in dst
    assert 'UNQUALIFIED_S_METER_DRIVE_FROM_MAIN' in dst
    assert "NO MAIN AGC/FSD" in src
    assert "100k_0P25W_CANDIDATE_NO_FSD_QUAL" in dst
    assert "100k_0P25W_REDUNDANT_CANDIDATE_NO_FSD_QUAL" in dst
    # 5V is an optimistic upper source *voltage* for this simplistic
    # calculation: opamp swing limitations would reduce current.
    # Actual driver may have an entirely different architecture.
    optimistic_v = 5.0
    two = screen(optimistic_v)
    single_short = screen(optimistic_v, shorted_resistors=1)
    assert 0.0 < two["coil_current_upper_bound_A_ideal"] < 27e-6
    assert 0.0 < single_short["coil_current_upper_bound_A_ideal"] < 53e-6
    assert screen(optimistic_v, fsd_a=50e-6)["possible_FSD_exceedance_model"] is False
    assert screen(optimistic_v, fsd_a=20e-6)["possible_FSD_exceedance_model"] is True
    # To reach an assumed 50uA full scale in the ideal load-free 2x100k
    # chain needs at least 9.5V on 5%-low resistor corner; nominal 10V.
    fsd_example = 50e-6
    min_v = fsd_example * (2*100000*(1-0.05))
    nominal_v = fsd_example * 2*100000
    assert min_v > optimistic_v and nominal_v == 10.0
    # This is neither a meter choice nor a direct interface definition:
    # FSD and coil Ohms unselected, interboard cable unqualified.
    print("SMETER_MAIN_FRONT_BENCH_VOLTAGE_DRIVE_UNQUALIFIED", {
        "source": "MCP6002 lab-only J1902 OUT 5V supply",
        "front": "J1801 + RV1801 + 2x100k + J1802 coil",
        "max_drive_5V_ideal_upper_current_uA": round(two["coil_current_upper_bound_A_ideal"]*1e6, 6),
        "hypothetical_FSD_50uA_required_min_voltage_V": round(min_v, 3),
        "hypothetical_FSD_50uA_required_nominal_voltage_V": nominal_v,
        "actual_output_swing_measured": False,
        "coil_FSD_and_resistance_qualified": False,
        "MAIN_AGC_real_source_present": False,
        "interboard_cable_and_return_qualified": False,
        "direct_connection_authorized": False,
        "NO_FAB_NO_TX": True,
    }, flush=True)


if __name__ == "__main__":
    verify()
