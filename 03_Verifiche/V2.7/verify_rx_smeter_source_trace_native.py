#!/usr/bin/env python3
"""Trace candidate RX level across REAL KiCad9 nets, fail closed on false AGC.

A lab AM envelope detector exposes a rectified IF node internally, whereas
its J1502 connector carries AC-coupled AF. Neither is a qualified
AM/FM/SSB S-meter drive or part of the V2.6 MAIN receiver.
"""
import math
import re
import tempfile
from pathlib import Path
from verify_interboard_audio_contract_native import exported_nets, require

ROOT=Path(__file__).resolve().parents[2]
V26=ROOT/"04_KiCad/V2.6"
MAIN=V26/"PLL_RX_HIERARCHICAL_MASTER_V2.6.kicad_sch"
AM=ROOT/"04_KiCad/V2.7_DRAFT/AM455_ENVELOPE/AM455_ENVELOPE_THT_V2_7_DRAFT.kicad_sch"
METER=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_SMETER/FRONT_SMETER_THT_V2_7_DRAFT.kicad_sch"
EXPECTED_V26_CHILDREN={
    "INPUT_FUSE_REVERSE_TVS_OVP_V2.6.kicad_sch",
    "PD_FILTER_DRIVER_V2.6.kicad_sch",
    "PLL_CORE_DIGITAL_V2.6.kicad_sch",
    "POWER20_VTUNE_BOOST_LDO_V2.6.kicad_sch",
    "POWER5_DISTRIBUTION_V2.6.kicad_sch",
    "VCO_RX_AND_LOBUF_V2.6.kicad_sch",
}
FORBIDDEN_SOURCE=re.compile(r"(AGC|S[_ -]?METER|SMETER|RSSI|RX[_ -]?LEVEL)",re.I)

def main():
    master=MAIN.read_text(encoding="utf-8")
    filenames=set(re.findall(r'\(property "Sheetfile" "([^"]+)"',master))
    assert filenames==EXPECTED_V26_CHILDREN,("Review new MAIN sheets",sorted(filenames))
    # Forbid claiming any master net as the meter source without a
    # reviewed source/driver. Any future AGC addition MUST revise this gate.
    for path in [MAIN]+[V26/name for name in sorted(filenames)]:
        content=path.read_text(encoding="utf-8")
        source_labels=re.findall(
            r'\((?:label|global_label|hierarchical_label) "([^"]+)"',
            content)
        suspect=[name for name in source_labels if FORBIDDEN_SOURCE.search(name)]
        assert not suspect,("New potential source requires explicit engineering review",str(path),suspect)

    with tempfile.TemporaryDirectory(prefix="tht_agc_source_trace_") as d:
        temp=Path(d)
        am=exported_nets(AM,temp/"am.net")
        meter=exported_nets(METER,temp/"meter.net")
    require(am,"AM_RECTIFIED_ENV",("D1501","1"),("R1501","1"),
            ("C1501","1"),("C1502","1"))
    require(am,"AM_DEMOD_AF_BENCH",("C1502","2"),("J1502","1"))
    require(am,"IF_BENCH_GND",("J1502","2"),("R1501","2"))
    assert ("J1502","1") not in am["AM_RECTIFIED_ENV"]
    assert not any(ref.startswith("J15") for ref,pad in
                   am["AM_RECTIFIED_ENV"])
    # Only the opposite C1502 pin (through a DC-blocking 100nF capacitor)
    # reaches the audio output connector; not a valid DC level source.
    assert AM.read_text(encoding="utf-8").count(
        '(property "Value" "100nF_50V_FILM"')==1
    require(meter,"METER_DRIVE_CANDIDATE",("J1801","1"),("RV1801","1"))
    require(meter,"METER_RETURN",("J1801","2"),("RV1801","3"))
    assert not any(n in meter for n in am)
    assert not any("AGC" in n or "RSSI" in n for n in meter)

    # If someone wires the lab AM detector envelope DIRECTLY across 10k
    # trim, it loads the 47k//1nF detector. Idealized small-signal RC
    # comparison only, not a diode/IF noise/fault qualification.
    rdet=47000.0
    rtrim=10000.0
    cfilter=1e-9
    rparallel=rdet*rtrim/(rdet+rtrim)
    bare_fc=1/(2*math.pi*rdet*cfilter)
    loaded_fc=1/(2*math.pi*rparallel*cfilter)
    assert math.isclose(rparallel,8245.61403508772,rel_tol=1e-10)
    assert loaded_fc>5*bare_fc
    print("RX_METER_SOURCE_TRACE_NATIVE_KICAD9",{
        "v26_master_children":len(filenames),
        "lab_am_rectified_node":"AM_RECTIFIED_ENV",
        "lab_am_out":"AM_DEMOD_AF_BENCH (AC-coupled C1502)",
        "MAIN_AGC_RSSI_source_qualified":False,
        "FRONT_meter_input_connected_to_MAIN":False,
        "47k_detector_parallel_10k_trim_ohm":round(rparallel,2),
        "unloaded_filter_fc_hz":round(bare_fc,2),
        "direct_trim_load_filter_fc_hz":round(loaded_fc,2)},flush=True)
    print("PASS_NATIVE_RX_SOURCE_TRACE_AM_ENVELOPE_NOT_DC_AGC_NOT_MAIN_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
