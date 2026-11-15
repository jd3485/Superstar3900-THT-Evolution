#!/usr/bin/env python3
"""Native ngspice AM455 generic diode plus real passive FRONT / LM386 input loading.

Compare duplicate 455kHz tank+non-OEM diode paths: existing standalone
100k AF termination vs 100k in parallel with 10k FRONT pot and the LM386
50k-TYPICAL input preceded by 100nF and 10k series components.
No OEM diode, gain, IF transistors, cable/ground, PCB, SINAD or THD proof.
"""
from pathlib import Path
import math
import subprocess
import tempfile
from verify_if455_am455_input_level_sweep_native import number
from verify_am455_front_lm386_loaded_ac_native import check_actual_cad

ROOT=Path(__file__).resolve().parents[2]
DECK=ROOT/"03_Verifiche/V2.7/spice/if455_am455_front_lm386_loaded_generic_diode.cir"
REFERENCE=ROOT/"03_Verifiche/V2.7/spice/if455_am455_nonlinear_transient_generic.cir"
LEVELS=(0.5,1.0,2.0)
WIPERS=(0.1,0.5,0.9)
PARAM=".param fc=455k fa=1k depth=0.5 amp=2 wiper=0.5"

def main():
    check_actual_cad()
    raw=DECK.read_text(encoding="utf-8")
    base=REFERENCE.read_text(encoding="utf-8")
    assert raw.count(PARAM)==1
    assert ".model DGENERIC D(Is=2.5n N=1.9 Rs=0.6 Cjo=4p Vj=0.75 Tt=4n)" in raw
    assert ".model DGENERIC D(Is=2.5n N=1.9 Rs=0.6 Cjo=4p Vj=0.75 Tt=4n)" in base
    # No changes to the existing tank/diode/RC branch are permitted. The
    # independently excited loaded branch must reproduce identical cards.
    cards=[line for line in base.splitlines()
           if line.startswith(("BIF ","RGEN ","C1601 ","L1601 ","RCOIL ",
                               "C1602 ","C1603 ","R1601 ","C1604 ","R1602 ",
                               "D1501 ","R1501 ","C1501 ","C1502 ","R1502 "))]
    assert len(cards)==15
    for line in cards:
        assert line in raw,("Reference branch was silently changed",line)
    for line in (
        "RVP_TOP af_l wiper_l {10000*(1-wiper)}",
        "RVP_BOT wiper_l 0 {10000*wiper}",
        "C1201L wiper_l pre_l 100n",
        "R1201L pre_l ampin_l 10k",
        "RLM386_INPUT ampin_l 0 50k",
        "D1501L out_l envelope_l DGENERIC",
        ".tran 0.2u 12m 0 0.2u",
    ):
        assert line in raw,line
    results=[]
    with tempfile.TemporaryDirectory(prefix="tht_if455_loaded_diode_") as tmp:
        folder=Path(tmp)
        for amp in LEVELS:
            for wiper in WIPERS:
                settings=PARAM.replace("amp=2",f"amp={amp}").replace(
                    "wiper=0.5",f"wiper={wiper}")
                assert settings!=PARAM
                f=folder/f"level_{amp}_wiper_{wiper}.cir"
                logpath=f.with_suffix(".log")
                f.write_text(raw.replace(PARAM,settings),encoding="utf-8")
                result=subprocess.run(["ngspice","-b","-o",str(logpath),str(f)],
                                      cwd=folder,capture_output=True,text=True,timeout=180)
                log=logpath.read_text(encoding="utf-8",errors="replace") if logpath.exists() else ""
                result.check_returncode()
                assert "Error:" not in log and "fatal" not in log.lower(),log[-1600:]
                unloaded=number(log,"coupled_max")-number(log,"coupled_min")
                loaded=number(log,"loaded_input_max")-number(log,"loaded_input_min")
                af=number(log,"loaded_af_max")-number(log,"loaded_af_min")
                peak=number(log,"loaded_rf_peak")
                assert all(math.isfinite(v) and v>0 for v in (unloaded,loaded,af,peak)),(
                    amp,wiper,unloaded,loaded,af,peak)
                assert loaded < af,("Passive volume/input chain amplified",amp,wiper,loaded,af)
                results.append((amp,wiper,unloaded,af,loaded,loaded/unloaded))
                print("IF455_AM455_FRONT_LM386_GENERIC_DIODE_LOADED",{
                    "source_peak_V":amp,"wiper_fraction":wiper,
                    "100k_alone_af_pp_V":round(unloaded,9),
                    "loaded_detector_af_pp_V":round(af,9),
                    "lm386_pin3_pp_V":round(loaded,9),
                    "loaded_to_unloaded_ratio_model_only":round(loaded/unloaded,7),
                    "diode_OEM_qualified":False,
                    "AF_gain_included":False},flush=True)
    assert len(results)==9
    # Same wiper, greater generator excursion should give greater recovered
    # AF in THIS model; not a physical minimum receiver sensitivity claim.
    for w in WIPERS:
        values=[r[4] for r in results if r[1]==w]
        assert all(x<y for x,y in zip(values,values[1:])),(w,values)
    for amp in LEVELS:
        values=[r[4] for r in results if r[0]==amp]
        assert all(x<y for x,y in zip(values,values[1:])),(amp,values)
    print("PASS_NGSPICE_9_GENERIC_DIODE_IF455_AM455_LOADED_FRONT_LM386_TRANSIENT_CASES_NOT_OEM_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
