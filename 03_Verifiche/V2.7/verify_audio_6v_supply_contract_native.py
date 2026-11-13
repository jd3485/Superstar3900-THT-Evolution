#!/usr/bin/env python3
"""Native KiCad9 connector contract between isolated THT 6V PSU and LM386.

Not a connected PCB or cable test; both draft schematics remain standalone.
"""
from pathlib import Path
import tempfile
from verify_interboard_audio_contract_native import exported_nets, require
from verify_audio_psu_lm317_native import vout_pvt_endpoints

ROOT = Path(__file__).resolve().parents[2]
PSU = ROOT / "04_KiCad/V2.7_DRAFT/AUDIO_PSU_6V/AUDIO_PSU_LM317_6V_LAB_DRAFT.kicad_sch"
AMP = ROOT / "04_KiCad/V2.7_DRAFT/AUDIO_RX_MONO_LM386_V2_7_DRAFT.kicad_sch"
HARNESS = {("J1402", "1"): ("J1201", "1"),
           ("J1402", "2"): ("J1201", "2")}


def main():
    with tempfile.TemporaryDirectory(prefix="tht_audio_6v_contract_") as tmp:
        tmp = Path(tmp)
        a = exported_nets(PSU, tmp / "psu.net")
        b = exported_nets(AMP, tmp / "amp.net")
    require(a, "AUDIO_6V_LAB", ("U1401", "2"), ("J1402", "1"),
            ("C1402", "1"))
    require(a, "AUDIO_GND", ("J1402", "2"), ("C1402", "2"))
    require(b, "AUDIO_6V_LAB", ("J1201", "1"), ("U1201", "6"),
            ("C1206", "1"), ("C1205", "1"))
    require(b, "GND", ("J1201", "2"), ("U1201", "4"),
            ("C1206", "2"), ("C1205", "2"))
    # Never accidentally attach the audio rail to the PLL or boost.
    assert not {"AUDIO_5V", "+5V_PLL", "VTUNE20", "VIN_13V8"}.intersection(a)
    assert not {"AUDIO_5V", "+5V_PLL", "VTUNE20", "VIN_13V8"}.intersection(b)
    assert len(HARNESS) == 2 and len(set(HARNESS.values())) == 2
    vmin, vtyp, vmax = vout_pvt_endpoints()
    assert 4.0 <= vmin < vtyp < vmax <= 12.0, "LM386N-1 must remain inside 4–12V nominal range"
    print("AUDIO_6V_PSU_TO_LM386_HARNESS_DRAFT", HARNESS,
          "REFERENCE_ONLY_OUTPUT_RANGE", tuple(round(x,4) for x in (vmin,vtyp,vmax)), flush=True)
    print("PASS_NATIVE_6V_PSU_LM386_PIN_CONTRACT_NO_FAB_NO_BATTERY", flush=True)


if __name__ == "__main__":
    main()
