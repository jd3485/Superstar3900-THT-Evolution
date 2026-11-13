#!/usr/bin/env python3
"""Native ngspice IF455->generic diode AM455 input-level transient sweep.
Not a real IF gain/source model, OEM 1N4148 model, or sensitivity claim.
"""
from pathlib import Path
import math
import re
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"03_Verifiche/V2.7/spice/if455_am455_nonlinear_transient_generic.cir"
LEVELS=(0.2,0.5,1.0,2.0)
PARAM=".param fc=455k fa=1k depth=0.5 amp=2"

def number(log,label):
    match=re.search(r"(?im)^\s*"+re.escape(label)+r"\s*=\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)",log)
    assert match,("Missing native measurement",label,log[-1700:])
    value=float(match.group(1))
    assert math.isfinite(value),label
    return value

def main():
    base=BASE.read_text(encoding="utf-8")
    assert base.count(PARAM)==1,"Source amplitude not uniquely controlled"
    assert ".model DGENERIC" in base and "D1501 out envelope DGENERIC" in base
    results=[]
    with tempfile.TemporaryDirectory(prefix="tht_if455_level_sweep_") as tmp:
        folder=Path(tmp)
        for idx,level in enumerate(LEVELS):
            modified=base.replace(PARAM, PARAM.replace("amp=2","amp="+str(level)))
            deck=folder/f"level_{idx}.cir"
            logfile=folder/f"level_{idx}.log"
            deck.write_text(modified,encoding="utf-8")
            run=subprocess.run(["ngspice","-b","-o",str(logfile),str(deck)],
                               cwd=folder,capture_output=True,text=True)
            log=logfile.read_text(encoding="utf-8",errors="replace") if logfile.exists() else ""
            run.check_returncode()
            assert "Error:" not in log and "fatal" not in log.lower(),log[-1000:]
            coupled=number(log,"coupled_max")-number(log,"coupled_min")
            direct=number(log,"direct_max")-number(log,"direct_min")
            assert coupled>0 and direct>0,("Nonpositive AF pp",level,coupled,direct)
            results.append((level,coupled,direct,coupled/direct))
    # Detector is non-linear: amplitude recovery must be tested explicitly;
    # do not assume small-signal AC gain and do not infer receiver sensitivity.
    assert all(results[i][1]<results[i+1][1] for i in range(len(results)-1)),results
    print("IF455_GENERIC_DIODE_AMP_SWEEP_SOURCE_PEAK_V_COUPLED_AFPP_DIRECT_AFPP_RATIO")
    for row in results:
        print("GENERIC_NONLINEAR_LEVEL",{"source_peak_V":row[0],
          "tank_diode_AFpp_V":round(row[1],9),
          "direct_reference_AFpp_V":round(row[2],9),
          "ratio_of_model_only":round(row[3],7)},flush=True)
    print("PASS_NGSPICE_IF455_AM455_GENERIC_DIODE_INPUT_LEVEL_SWEEP_NOT_OEM_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
