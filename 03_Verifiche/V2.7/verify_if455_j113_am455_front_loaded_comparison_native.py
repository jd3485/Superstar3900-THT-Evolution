#!/usr/bin/env python3
"""6 native ngspice IF455 direct vs J113 follower generic AM diode transients
with actual FRONT 10k and passive LM386 100n/10k/50k input. OEM unqualified.
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
ORIGINAL=ROOT/"03_Verifiche/V2.7/spice/if455_j113_am455_generic_jfet_transient.cir"
DECK=ROOT/"03_Verifiche/V2.7/spice/if455_j113_am455_front_lm386_loaded_generic_comparison.cir"
PARAM=".param fc=455k fa=1k depth=0.5 amp=2 rail=6 wiper=0.5"
LEVELS=(0.5,2.0)
POSITIONS=(0.1,0.5,0.9)

def main():
    check_actual_cad()
    source=DECK.read_text(encoding="utf-8")
    original=ORIGINAL.read_text(encoding="utf-8")
    assert source.count(PARAM)==1
    assert source.count("RVP_TOP_")==source.count("RVP_BOT_")==2
    assert ".tran 0.025u 12m 0 0.025u" in source
    for line in original.splitlines():
        if line.startswith(("BIFD ","BIFB ","RGEN","C160","L160","RCOIL",
                            "D1501","R1501","C1501","C1502","R1502",
                            "VLAB ","C180","R180","JQ1801 ","EGS ",".model ")):
            assert line in source,("Noncomparable original path",line)
    with tempfile.TemporaryDirectory(prefix="tht_j113_af_loaded_") as td:
        folder=Path(td)
        nets=exported_nets(SCH,folder/"j113.net")
        # Actual schematic pin-net names are asserted by native related gate;
        # this comparison refuses to drift from the existing J113 candidate.
        parts=set(ref for pins in nets.values() for ref,pin in pins)
        assert parts=={"J1801","J1802","J1803","C1801","R1801",
                      "Q1801","R1802","C1802","R1803"},parts
        require(nets,"IF455_TANK_OUT",("J1801","1"),("C1801","1"))
        require(nets,"JFET_GATE",("C1801","2"),("Q1801","3"))
        require(nets,"JFET_AC_OUT",("C1802","2"),("J1802","1"))
        require(nets,"VLAB6_JFET_ONLY",("Q1801","1"),("J1803","1"))
        for drive in LEVELS:
            rows=[]
            for pos in POSITIONS:
                settings=PARAM.replace("amp=2",f"amp={drive}").replace("wiper=0.5",f"wiper={pos}")
                deck=folder/f"a{drive}_w{pos}.cir"
                logpath=deck.with_suffix(".log")
                deck.write_text(source.replace(PARAM,settings),encoding="utf-8")
                run=subprocess.run(["ngspice","-b","-o",str(logpath),str(deck)],
                                    cwd=folder,capture_output=True,text=True,timeout=180)
                log=logpath.read_text(encoding="utf-8",errors="replace") if logpath.exists() else ""
                run.check_returncode()
                assert "Error:" not in log and "fatal" not in log.lower(),log[-1400:]
                direct=metric(log,"loaded_direct_af_max")-metric(log,"loaded_direct_af_min")
                buffered=metric(log,"loaded_buffered_af_max")-metric(log,"loaded_buffered_af_min")
                af_d=metric(log,"direct_max")-metric(log,"direct_min")
                af_b=metric(log,"buffered_max")-metric(log,"buffered_min")
                assert all(math.isfinite(x) and x>0 for x in (direct,buffered,af_d,af_b)),(drive,pos)
                assert direct<af_d and buffered<af_b,(drive,pos,direct,buffered)
                rows.append((pos,direct,buffered))
                print("J113_IF455_AM455_LOADED_COMPARE_GENERIC",{
                    "source_peak_V":drive,"wiper":pos,
                    "direct_LM386_pin3_Vpp":round(direct,9),
                    "J113_LM386_pin3_Vpp":round(buffered,9),
                    "J113_to_direct_ratio":round(buffered/direct,6),
                    "BJT_or_JFET_vendor_model":False,"diode_vendor_model":False},flush=True)
            assert len(rows)==3
            assert all(x[1]<y[1] and x[2]<y[2] for x,y in zip(rows,rows[1:])),(drive,rows)
    print("PASS_NGSPICE_6_IF455_J113_AM455_FRONT_LM386_GENERIC_LOADED_COMPARISONS_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
