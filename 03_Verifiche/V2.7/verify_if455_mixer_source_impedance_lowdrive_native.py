#!/usr/bin/env python3
"""Isolated 455kHz candidate direct vs J113 envelope sensitivity to unknown mixer impedance.

Uses existing non-OEM dual-path IF455 tank/JGEN/DGENERIC loaded FRONT/LM386
ngspice model, alters ONLY source resistances of both drives and generator
peak. 6 experiments; no inference of real receiver microvolt sensitivity,
noise, gain, IF transformer loading or OEM PVT.
"""
from pathlib import Path
import math
import subprocess
import tempfile
from verify_if455_j113_generic_njf_full_cascade_native import metric
from verify_interboard_audio_contract_native import exported_nets,require
from verify_am455_front_lm386_loaded_ac_native import check_actual_cad

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"04_KiCad/V2.7_DRAFT"
SCH=BASE/"IF455_J113_SOURCE_FOLLOWER/IF455_J113_SOURCE_FOLLOWER_THT_V2_7_DRAFT.kicad_sch"
DECK=ROOT/"03_Verifiche/V2.7/spice/if455_j113_am455_front_lm386_loaded_generic_comparison.cir"
LEVELS=(0.01,0.10)
RSOURCE=(50,1000,10000)
PARAM=".param fc=455k fa=1k depth=0.5 amp=2 rail=6 wiper=0.5"
OLD_DIRECT="RGEND src_d gen_d 50"
OLD_BUFFER="RGENB src_b gen_b 50"

def main():
    check_actual_cad()
    source=DECK.read_text(encoding="utf-8")
    assert source.count(PARAM)==1 and source.count(OLD_DIRECT)==1
    assert source.count(OLD_BUFFER)==1
    assert source.count("RVP_TOP_")==source.count("RVP_BOT_")==2
    assert ".tran 0.025u 12m 0 0.025u" in source
    assert ".model JGEN NJF(" in source and ".model DGENERIC D(" in source
    with tempfile.TemporaryDirectory(prefix="tht_if455_source_impedance_") as td:
        folder=Path(td)
        nets=exported_nets(SCH,folder/"j113.net")
        require(nets,"IF455_TANK_OUT",("J1801","1"),("C1801","1"))
        require(nets,"JFET_GATE",("C1801","2"),("Q1801","3"))
        require(nets,"JFET_AC_OUT",("C1802","2"),("J1802","1"))
        results=[]
        for level in LEVELS:
            for rs in RSOURCE:
                params=PARAM.replace("amp=2",f"amp={level}").replace("wiper=0.5","wiper=0.9")
                deck=source.replace(PARAM,params).replace(OLD_DIRECT,
                    f"RGEND src_d gen_d {rs}").replace(OLD_BUFFER,
                    f"RGENB src_b gen_b {rs}")
                assert deck!=source and "RGEND src_d gen_d 50" not in deck if rs!=50 else deck!=source
                filename=folder/f"input{level}_rs{rs}.cir"
                logfile=filename.with_suffix(".log")
                filename.write_text(deck,encoding="utf-8")
                run=subprocess.run(["ngspice","-b","-o",str(logfile),str(filename)],
                                   cwd=folder,capture_output=True,text=True,timeout=180)
                log=logfile.read_text(encoding="utf-8",errors="replace") if logfile.exists() else ""
                run.check_returncode()
                assert "Error:" not in log and "fatal" not in log.lower(),(level,rs,log[-1800:])
                direct=metric(log,"loaded_direct_af_max")-metric(log,"loaded_direct_af_min")
                jfet=metric(log,"loaded_buffered_af_max")-metric(log,"loaded_buffered_af_min")
                ref_d=metric(log,"direct_max")-metric(log,"direct_min")
                ref_j=metric(log,"buffered_max")-metric(log,"buffered_min")
                tank_d=metric(log,"direct_tank_max")
                tank_j=metric(log,"buffered_tank_max")
                assert all(math.isfinite(v) and v>0 for v in
                           (direct,jfet,ref_d,ref_j,tank_d,tank_j)),(
                           level,rs,direct,jfet,ref_d,ref_j,tank_d,tank_j)
                assert direct<ref_d and jfet<ref_j,("Passive AF input should attenuate",level,rs)
                row={
                  "ideal_source_peak_V":level,
                  "source_ohm_each_path":rs,
                  "direct_LM386_pin3_Vpp":round(direct,11),
                  "J113_LM386_pin3_Vpp":round(jfet,11),
                  "J113_direct_ratio":round(jfet/direct,7),
                  "direct_tank_positive_peak_V":round(tank_d,9),
                  "J113_tank_positive_peak_V":round(tank_j,9),
                  "mixer_equivalent_circuit_qualified":False,
                  "OEM_models":False
                }
                results.append(row)
                print("IF455_UNKNOWN_MIXER_SOURCE_IMPEDANCE_GENERIC",row,flush=True)
    assert len(results)==6
    for rs in RSOURCE:
        a,b=[row for row in results if row["source_ohm_each_path"]==rs]
        assert a["ideal_source_peak_V"]<b["ideal_source_peak_V"]
        assert a["direct_LM386_pin3_Vpp"]<b["direct_LM386_pin3_Vpp"]
        assert a["J113_LM386_pin3_Vpp"]<b["J113_LM386_pin3_Vpp"]
    print("PASS_NGSPICE_6_IF455_UNKNOWN_MIXER_SOURCE_IMPEDANCE_LOWDRIVE_DIRECT_J113_CASES_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
