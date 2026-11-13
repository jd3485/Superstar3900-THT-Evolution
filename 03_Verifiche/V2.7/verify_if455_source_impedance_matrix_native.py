#!/usr/bin/env python3
"""Native ngspice input source impedance × AM input-level matrix.
Generic nonlinear diode and assumed tank losses; NOT OEM, RF acceptance, or sensitivity.
"""
from pathlib import Path
import math
import re
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"03_Verifiche/V2.7/spice/if455_am455_nonlinear_transient_generic.cir"
AMPLITUDES=(0.5,2.0)
SOURCE_OHMS=(50,500,5000)
SOURCE_LINE="RGEN src_if gen 50"
REF_LINE="RREF src_ref direct 50"
PARAM_LINE=".param fc=455k fa=1k depth=0.5 amp=2"

def measure(log, key):
    pattern=r"(?im)^\s*"+re.escape(key)+r"\s*=\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)"
    found=re.search(pattern,log)
    assert found, ("Missing ngspice native .meas",key,log[-1200:])
    value=float(found.group(1))
    assert math.isfinite(value), (key,value)
    return value

def main():
    baseline=BASE.read_text(encoding="utf-8")
    for token in (SOURCE_LINE,REF_LINE,PARAM_LINE,
                  "D1501 out envelope DGENERIC",".model DGENERIC",
                  "C1602 tank 0 82p","C1603 tank 0 30p"):
        assert baseline.count(token)==1, ("Changed baseline contract",token)
    matrix=[]
    with tempfile.TemporaryDirectory(prefix="tht_if455_zsrc_") as tmp:
        folder=Path(tmp)
        for resistance in SOURCE_OHMS:
            for amplitude in AMPLITUDES:
                deck=baseline.replace(SOURCE_LINE,
                         "RGEN src_if gen "+str(resistance))
                deck=deck.replace(REF_LINE,
                         "RREF src_ref direct "+str(resistance))
                deck=deck.replace(PARAM_LINE,
                         PARAM_LINE.replace("amp=2","amp="+str(amplitude)))
                assert deck!=baseline or (resistance==50 and amplitude==2)
                path=folder/f"src_{resistance}_amp_{str(amplitude).replace('.','p')}.cir"
                log_path=path.with_suffix(".log")
                path.write_text(deck,encoding="utf-8")
                result=subprocess.run(["ngspice","-b","-o",str(log_path),str(path)],
                                      cwd=folder,text=True,capture_output=True)
                log=log_path.read_text(encoding="utf-8",errors="replace") if log_path.exists() else ""
                result.check_returncode()
                assert "Error:" not in log and "fatal" not in log.lower(),log[-1500:]
                af_coupled=measure(log,"coupled_max")-measure(log,"coupled_min")
                af_reference=measure(log,"direct_max")-measure(log,"direct_min")
                rf_peak=measure(log,"rf_out_peak")
                assert af_coupled>0 and af_reference>0 and rf_peak>0, (
                    "Nonpositive model amplitude",resistance,amplitude)
                matrix.append((resistance,amplitude,af_coupled,af_reference,rf_peak))
    assert len(matrix)==len(AMPLITUDES)*len(SOURCE_OHMS)
    for amplitude in AMPLITUDES:
        sample=[row for row in matrix if row[1]==amplitude]
        assert len(sample)==len(SOURCE_OHMS)
        assert max(row[2] for row in sample)-min(row[2] for row in sample)>1e-8, (
            "No observable source impedance dependence",amplitude,sample)
    for resistance in SOURCE_OHMS:
        low,high=[row for row in matrix if row[0]==resistance]
        assert low[1]<high[1] and low[2]<high[2], (
            "Unexpected detector level ordering in simplified model",resistance,low,high)
    for r,a,af,ref,rf in matrix:
        print("IF455_GENERIC_ZSOURCE_MATRIX",
              {"source_ohm":r,"source_peak_V":a,"coupled_AFpp_V":round(af,9),
               "direct_AFpp_V":round(ref,9),"coupled_to_direct_ratio":round(af/ref,7),
               "tank_RF_positive_peak_V":round(rf,9)},flush=True)
    print("PASS_NGSPICE_IF455_SOURCE_IMPEDANCE_LEVEL_MATRIX_GENERIC_ONLY_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
