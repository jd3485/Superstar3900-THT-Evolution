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
# Exact KiCad9 2.50mm two-position, TH-header footprint (JST XH).
JST_XH_FP="Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical"
JST_XH_OLD="Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical"


def check_header_footprints():
    psu_src=PSU.read_text(encoding="utf-8")
    amp_src=AMP.read_text(encoding="utf-8")
    psu_lib=(PSU.parent/"TH_PSU.kicad_sym").read_text(encoding="utf-8")
    amp_lib=(AMP.parent/"TH_AUDIO.kicad_sym").read_text(encoding="utf-8")
    for content, ref in ((psu_src,"J1402"),(amp_src,"J1201")):
        # KiCad reference and footprint must agree at instance level.
        i=content.index('(property "Reference" "'+ref+'"')
        j=content.index("(instances ",i)
        instance=content[i:j]
        assert '(property "Footprint" "'+JST_XH_FP+'"' in instance,(ref,"wrong instance footprint")
    for content,symbol in ((psu_src,"TH_PSU:AUDIO_OUT"),
                           (amp_src,"TH_AUDIO:BENCH_6V_CONN"),
                           (psu_lib,"AUDIO_OUT"),
                           (amp_lib,"BENCH_6V_CONN")):
        i=content.index('(symbol "'+symbol+'"')
        j=content.index("(symbol \"",i+10)
        top=content[i:j]
        assert '(property "Footprint" "'+JST_XH_FP+'"' in top,(symbol,"wrong symbol footprint")
    # Verify the *installed* KiCad9 original footprint file, not an
    # assumed pitch or a hand-copied substitute. No phantom PCB DRC.
    possible=[Path("/usr/share/kicad/footprints"),Path("/usr/local/share/kicad/footprints")]
    fp_name="JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical.kicad_mod"
    matching=[p/"Connector_JST.pretty"/fp_name for p in possible
              if (p/"Connector_JST.pretty"/fp_name).is_file()]
    assert matching,("Official KiCad9 JST XH footprint unavailable",possible)
    footprint=matching[0].read_text(encoding="utf-8")
    # Read only the exact two THT pad declarations, without assuming that
    # KiCad footprint generator line wrapping is stable across KiCad9.
    pads=[]
    for pin_number in ("1","2"):
        signature='(pad "'+pin_number+'" thru_hole '
        assert footprint.count(signature)==1,("Missing or duplicated THT pad",pin_number)
        section=footprint.split(signature,1)[1][:240]
        assert "(at " in section,("Missing pad coordinate",pin_number)
        coords=section.split("(at ",1)[1].split(")",1)[0].split()
        assert len(coords)>=2,("Malformed KiCad footprint pad coordinate",coords)
        pads.append((pin_number,float(coords[0]),float(coords[1])))
    assert sorted(pads)==[("1",0.0,0.0),("2",2.5,0.0)],("Pad1/pad2 or pitch mismatch",pads)
    assert footprint.count("(pad \"")==2, "Unexpected pad count"
    assert "Connector_JST" in JST_XH_FP and JST_XH_OLD!=JST_XH_FP
    print("PASS_KICAD9_JST_XH_2P50_TH_HEADER_PAD1_PAD2_PITCH_BOTH_MODULES",flush=True)


HARNESS = {("J1402", "1"): ("J1201", "1"),
           ("J1402", "2"): ("J1201", "2")}


def main():
    check_header_footprints()
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
