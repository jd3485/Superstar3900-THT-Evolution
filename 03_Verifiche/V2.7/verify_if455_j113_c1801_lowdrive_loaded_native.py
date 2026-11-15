#!/usr/bin/env python3
"""Native IF455 10p-J113 low-drive experiment: coupling C1801 sweep.

Comparative *generic* NJF+DGENERIC nonlinear AM demod, 455 kHz, final
FRONT/LM386 passive load. C1801=2.2/4.7/10/22pF: only 10pF exists in
actual draft KiCad; all other values are SPICE-only hypotheses.
An AFpp enhancement does NOT qualify noise, sensitivity, selectivity,
VGS stress, source impedance, OEM silicon or actual RF performance.
"""
from pathlib import Path
import math
import subprocess
import tempfile
from verify_if455_j113_generic_njf_full_cascade_native import metric
from verify_am455_front_lm386_loaded_ac_native import check_actual_cad
from verify_interboard_audio_contract_native import exported_nets,require

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"04_KiCad/V2.7_DRAFT"
SOURCE=ROOT/"03_Verifiche/V2.7/spice/if455_j113_am455_front_lm386_loaded_generic_comparison.cir"
SCH=BASE/"IF455_J113_SOURCE_FOLLOWER/IF455_J113_SOURCE_FOLLOWER_THT_V2_7_DRAFT.kicad_sch"
PARAM=".param fc=455k fa=1k depth=0.5 amp=2 rail=6 wiper=0.5"
LEVELS=(0.10,0.25,0.50)
COUPLING=("2.2p","4.7p","10p","22p")
CURRENT="C1801 out_b gate_j 10p"
WIPER="0.9"

def main():
    check_actual_cad()
    src=SOURCE.read_text(encoding="utf-8")
    assert src.count(PARAM)==1
    assert src.count(CURRENT)==1
    assert src.count("RVP_TOP_")==src.count("RVP_BOT_")==2
    assert ".tran 0.025u 12m 0 0.025u" in src
    assert "Q1801" in SCH.read_text(encoding="utf-8")
    assert '"Value" "10pF_C0G_RF_INPUT_PROVISIONAL"' in SCH.read_text(encoding="utf-8")
    results=[]
    with tempfile.TemporaryDirectory(prefix="tht_if455_j113_lowdrive_") as td:
        folder=Path(td)
        nets=exported_nets(SCH,folder/"j113.net")
        require(nets,"IF455_TANK_OUT",("J1801","1"),("C1801","1"))
        require(nets,"JFET_GATE",("C1801","2"),("Q1801","3"),("R1801","1"))
        require(nets,"VLAB6_JFET_ONLY",("Q1801","1"),("J1803","1"))
        require(nets,"JFET_AC_OUT",("C1802","2"),("J1802","1"))
        for level in LEVELS:
            direct_reference=None
            for cap in COUPLING:
                settings=PARAM.replace("amp=2",f"amp={level}").replace("wiper=0.5",f"wiper={WIPER}")
                candidate=src.replace(PARAM,settings).replace(CURRENT,f"C1801 out_b gate_j {cap}")
                assert candidate!=src
                filepath=folder/f"c{cap}_a{level}.cir"
                logfile=filepath.with_suffix(".log")
                filepath.write_text(candidate,encoding="utf-8")
                run=subprocess.run(["ngspice","-b","-o",str(logfile),str(filepath)],
                                   cwd=folder,capture_output=True,text=True,timeout=180)
                log=logfile.read_text(encoding="utf-8",errors="replace") if logfile.exists() else ""
                run.check_returncode()
                assert "Error:" not in log and "fatal" not in log.lower(),(level,cap,log[-1600:])
                direct=metric(log,"loaded_direct_af_max")-metric(log,"loaded_direct_af_min")
                j113=metric(log,"loaded_buffered_af_max")-metric(log,"loaded_buffered_af_min")
                tank=metric(log,"buffered_tank_max")
                emitter_hi=metric(log,"buffered_source_max")
                emitter_lo=metric(log,"buffered_source_min")
                vgs_hi=metric(log,"gate_source_max")
                vgs_lo=metric(log,"gate_source_min")
                assert all(math.isfinite(z) for z in
                           (direct,j113,tank,emitter_hi,emitter_lo,vgs_hi,vgs_lo))
                assert direct>0 and j113>=0 and tank>0
                assert emitter_hi>emitter_lo and 0<emitter_hi<6.6
                if direct_reference is None: direct_reference=direct
                else:
                    # Independent coupled branch changes adaptive integration meshes despite\n                    # invariant direct cards. Permit <=0.01% numerical Vpp drift;\n                    # circuit-card invariance is already a separate fail-closed check.\n                    assert abs(direct-direct_reference)/direct_reference<1e-4,(
                        "Direct path changed during coupling-only experiment",level,cap,direct,direct_reference)
                row={"source_peak_V":level,"C1801_SPICE_only":cap,
                     "direct_LM386_pin3_pp_V":round(direct,10),
                     "J113_LM386_pin3_pp_V":round(j113,10),
                     "J113_to_direct_ratio":round(j113/direct,7),
                     "J113_tank_positive_peak_V":round(tank,8),
                     "emitter_range_V":(round(emitter_lo,6),round(emitter_hi,6)),
                     "Vgs_range_V":(round(vgs_lo,6),round(vgs_hi,6)),
                     "actual_KiCad_C1801":cap=="10p",
                     "OEM_models":False}
                results.append(row)
                print("IF455_J113_C1801_LOWDRIVE_NATIVE_CASE",row,flush=True)
    assert len(results)==len(LEVELS)*len(COUPLING)==12
    for level in LEVELS:
        subset=[r for r in results if r["source_peak_V"]==level]
        assert len(subset)==4
        best=max(subset,key=lambda x:x["J113_LM386_pin3_pp_V"])
        baseline=next(x for x in subset if x["actual_KiCad_C1801"])
        print("IF455_J113_C1801_LOWDRIVE_GENERIC_LEVEL_SUMMARY",{
            "source_peak_V":level,
            "best_SPICE_cap":best["C1801_SPICE_only"],
            "best_AFpp_V":best["J113_LM386_pin3_pp_V"],
            "actual_draft_10p_AFpp_V":baseline["J113_LM386_pin3_pp_V"],
            "direct_AFpp_V":baseline["direct_LM386_pin3_pp_V"],
            "physical_cap_change_approved":False},flush=True)
    print("PASS_NGSPICE_12_J113_C1801_LOW_IF_LEVEL_COUPLING_GENERIC_NONLINEAR_CASES_NO_OEM_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
