#!/usr/bin/env python3
"""KiCad9 native Q804/Q805 common-source + Q806 onsemi KSP42BU 300V THT high-voltage sink.
Not an independent OVP/UVLO supervisor, vendor simulation or hardware approval.
"""
from pathlib import Path
import itertools
import math
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_interboard_audio_contract_native import exported_nets, require

SCH = ROOT / "04_KiCad/V2.7_DRAFT/MAIN_SECONDARY_OVP_Q804_Q805_Q806_DRIVER/MAIN_SECONDARY_OVP_Q804_Q805_Q806_NPN_LAB_V2_7_DRAFT.kicad_sch"
EXPECTED = {
    "PRIMARY_IN_DRAIN_LAB": {("J2101","1"), ("Q804","2")},
    "FLOATING_COMMON_SOURCE_LAB": {("Q804","3"), ("Q805","3"),
                                    ("D2101","1"), ("R2101","1")},
    "COMMON_GATE_LAB": {("Q804","1"), ("Q805","1"),
                         ("D2101","2"), ("R2101","2"), ("R2102","2")},
    "SECONDARY_OUT_DRAIN_LAB": {("Q805","2"), ("J2102","1")},
    "DRIVER_SINK_LAB": {("R2102","1"), ("Q806","3")},
    "ENABLE_LOGIC_5V_LAB": {("J2103","1"), ("R2103","1")},
    "Q806_BASE_LAB": {("R2103","2"), ("R2104","1"), ("Q806","2")},
    "LAB_RETURN_ONLY": {("J2101","2"), ("J2102","2"), ("J2103","2"),
                         ("Q806","1"), ("R2104","2")},
}


def has_path(edges, src, dst):
    seen = {src}
    queue = [src]
    while queue:
        node = queue.pop()
        if node == dst:
            return True
        for a,b in edges:
            if a == node and b not in seen:
                seen.add(b)
                queue.append(b)
    return False


def main():
    schematic = SCH.read_text(encoding="utf-8")
    assert schematic.count('(symbol (lib_id "LAB_OVP:') == 11
    assert "KSP42BU_NPN_CANDIDATE" in schematic
    assert "NO FAB / NO TX / NO BATTERIA / NO VEICOLO" in schematic
    with tempfile.TemporaryDirectory(prefix="q806_native_nonfab_") as d:
        tmp = Path(d)
        report = tmp / "q806.erc"
        out = subprocess.run(
            ["kicad-cli","sch","erc","--exit-code-violations",
             "-o",str(report),str(SCH)],
            cwd=ROOT, capture_output=True, text=True)
        print("Q806_NATIVE_ERC", out.stdout, out.stderr, flush=True)
        if report.exists():
            print(report.read_text(encoding="utf-8"), flush=True)
        out.check_returncode()
        nets = exported_nets(SCH, tmp / "q806.net")
    assert len(nets) == len(EXPECTED) == 8, sorted(nets)
    assert set(nets) == set(EXPECTED)
    for name,pins in EXPECTED.items():
        require(nets,name,*pins)
        assert nets[name] == pins, (name, sorted(nets[name]),sorted(pins))
    all_pins = [p for members in nets.values() for p in members]
    assert len(all_pins) == len(set(all_pins)) == 25
    # Pinout per onsemi KSP43/D (KSP42), January 2025 Rev.4: E1/B2/C3. Neither
    # transistor emitter nor control return may short the floating source.
    assert ("Q806","1") in nets["LAB_RETURN_ONLY"]
    assert ("Q806","2") in nets["Q806_BASE_LAB"]
    assert ("Q806","3") in nets["DRIVER_SINK_LAB"]
    assert not (nets["FLOATING_COMMON_SOURCE_LAB"] & nets["LAB_RETURN_ONLY"])
    assert ("J2103","1") not in nets["DRIVER_SINK_LAB"]

    diodes = {
        ("PRIMARY_IN_DRAIN_LAB","FLOATING_COMMON_SOURCE_LAB"),
        ("SECONDARY_OUT_DRAIN_LAB","FLOATING_COMMON_SOURCE_LAB"),
    }
    assert not has_path(diodes,"PRIMARY_IN_DRAIN_LAB","SECONDARY_OUT_DRAIN_LAB")
    assert not has_path(diodes,"SECONDARY_OUT_DRAIN_LAB","PRIMARY_IN_DRAIN_LAB")
    # A D-S short of either transistor (or TO220 metal tab short)
    # removes one switching barrier. It is not a qualified single-fault design.
    assert has_path(diodes | {("FLOATING_COMMON_SOURCE_LAB","PRIMARY_IN_DRAIN_LAB")},
                    "SECONDARY_OUT_DRAIN_LAB","PRIMARY_IN_DRAIN_LAB")
    assert has_path(diodes | {("FLOATING_COMMON_SOURCE_LAB","SECONDARY_OUT_DRAIN_LAB")},
                    "PRIMARY_IN_DRAIN_LAB","SECONDARY_OUT_DRAIN_LAB")

    # Mathematical screening only, no OEM BJT saturation/leakage/SPICE.
    # Hypothetical 5V ENABLE high and VBE=0.65..0.95V at R 5% corners.
    ib_min = float("inf")
    ib_max = 0.0
    over_20_vgs_cases = 0
    over_40_bjt_off_baseline_cases = 0
    over_300_ksp42_off_cases = 0
    cases = 0
    for vin,vbe,rbase,rpul,rgs,rgate,vf in itertools.product(
        (0.,5.,8.,12.,13.8,16.,20.,24.,36.,48.),
        (.65,.8,.95),
        (4465.,4700.,4935.),
        (95000.,100000.,105000.),
        (44650.,47000.,49350.),
        (9500.,10000.,10500.),
        (.2,.5,.9)
    ):
        # BJT ON hypothesis: Ibase=(VENABLE-VBE)/R2103 - VBE/R2104
        ib = max(0., (5.-vbe)/rbase-vbe/rpul)
        ib_min=min(ib_min,ib)
        ib_max=max(ib_max,ib)
        # Zener D2101 OPEN under hard sink: divider across R2101/R2102,
        # not an allowed operating voltage.
        vgs_open = vin*rgs/(rgs+rgate)
        if vgs_open > 20.:
            over_20_vgs_cases += 1
        # BJT OFF source can rise via input->source body diode:
        # VCE(off) ≈ max(0, VIN-VF), assuming source unloaded.
        if max(0.,vin-vf)>40.:
            over_40_bjt_off_baseline_cases += 1
        if max(0.,vin-vf)>300.:
            over_300_ksp42_off_cases += 1
        cases+=1
    assert cases == 10*3**6 == 7290
    assert 0.0007 < ib_min < ib_max < 0.0011
    assert over_20_vgs_cases > 0 and over_40_bjt_off_baseline_cases > 0
    assert over_300_ksp42_off_cases == 0
    # 5V logic condition is NOT an independent fail-closed qualifier.
    print("Q806_NATIVE_PINNET_AND_MODEL_SCREEN", {
        "native_nets":len(nets),"physical_pins":len(all_pins),
        "analytic_cases":cases,
        "ideal_enabled_base_current_mA":(round(ib_min*1000,5),round(ib_max*1000,5)),
        "D2101_OPEN_over_PFET_20V_VGS_cases":over_20_vgs_cases,
        "rejected_2N3904_OFF_over_40V_VCEO_cases":over_40_bjt_off_baseline_cases,
        "candidate_KSP42BU_OFF_over_300V_VCEO_cases":over_300_ksp42_off_cases,
        "BJT_base_drive_5V_independent_supervisor_exists":False,
        "Q806_actual_saturation_and_hot_leakage_verified":False,
        "OEM_dynamic_zener_verified":False,
        "input_48V_permitted":False,
        "NO_FAB_NO_TX_NO_BATTERY_NO_VEHICLE":True
    },flush=True)
    print("PASS_NATIVE_KICAD9_THT_Q806_KSP42BU_25PINS_8NETS_7290_MODEL_CASES_NONFAB",flush=True)

if __name__ == "__main__":
    main()
