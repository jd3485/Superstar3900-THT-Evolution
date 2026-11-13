#!/usr/bin/env python3
"""Actual ngspice low-level AM carrier screening on the historic IF455 tank path.

NO hardware sensitivity, noise floor, SINAD or OEM J113/diode model is inferred.
Carrier generator level is NOT an antenna input: unknown preceding RF/IF gain.
"""
from pathlib import Path
import math
import re
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
DECK=ROOT/"03_Verifiche/V2.7/spice/if455_j113_am455_generic_jfet_transient.cir"
LEVELS=(0.0001,0.001,0.01,0.1,0.5)
CORNERS=(
    ("vto_m0p5_idss_2mA",0.5),
    ("vto_m3_idss_2mA",3.0),
)
ANCHOR=".model JGEN NJF(BETA=0.00088888889 VTO=-1.5 LAMBDA=0.02 CGS=5p CGD=2p RD=20 RS=20)"
AM_ANCHOR=".param fc=455k fa=1k depth=0.5 amp=2 rail=6"
BASELINE_500UV=(0.023925459,0.025212924)
BASELINE_500UV_WORST=(0.023924896,0.005823876)

def measure(log,name):
    rx=r"(?im)^\\s*"+re.escape(name)+r"\\s*=\\s*([+-]?(?:\\d+(?:\\.\\d*)?|\\.\\d+)(?:[eE][+-]?\\d+)?)"
    m=re.search(rx,log)
    assert m,("Missing ngspice transient measurement",name,log[-1600:])
    v=float(m.group(1))
    assert math.isfinite(v),(name,v)
    return v

def main():
    original=DECK.read_text(encoding="utf-8")
    assert original.count(ANCHOR)==1 and original.count(AM_ANCHOR)==1
    assert ".tran 0.025u 12m 0 0.025u" in original
    assert "D1501D out_d envelope_d DGENERIC" in original
    assert "D1501B bufferout envelope_b DGENERIC" in original
    assert "C1801 out_b gate_j 10p" in original
    assert "JQ1801 vcc gate_j source_j JGEN" in original
    rows=[]
    with tempfile.TemporaryDirectory(prefix="tht_if455_lowlevel_") as tmp:
        root=Path(tmp)
        for label,cutoff in CORNERS:
            # Generic square-law parameterization: IDSS=2mA, VTO=-cutoff.
            beta=.002/(cutoff*cutoff)
            model=f".model JGEN NJF(BETA={beta:.11g} VTO={-cutoff:g} LAMBDA=0.02 CGS=5p CGD=2p RD=20 RS=20)"
            for amplitude in LEVELS:
                source=original.replace(ANCHOR,model).replace(
                    AM_ANCHOR,
                    f".param fc=455k fa=1k depth=0.5 amp={amplitude:g} rail=6")
                folder=root/(label+"_"+str(amplitude).replace(".","p"))
                folder.mkdir()
                circuit=folder/"level.cir"
                logfile=folder/"native.log"
                circuit.write_text(source,encoding="utf-8")
                run=subprocess.run(
                    ["ngspice","-b","-o",str(logfile),str(circuit)],
                    cwd=folder,capture_output=True,text=True)
                log=logfile.read_text(encoding="utf-8",errors="replace") if logfile.exists() else ""
                run.check_returncode()
                assert "Error:" not in log and "fatal" not in log.lower(),log[-1200:]
                direct=measure(log,"direct_max")-measure(log,"direct_min")
                jfet=measure(log,"buffered_max")-measure(log,"buffered_min")
                ref_rf=measure(log,"direct_tank_max")
                jfet_rf=measure(log,"buffered_tank_max")
                assert direct>=0 and jfet>=0 and ref_rf>0 and jfet_rf>0,(
                    cutoff,amplitude,direct,jfet,ref_rf,jfet_rf)
                if amplitude==0.5:
                    old=(BASELINE_500UV if cutoff==0.5 else BASELINE_500UV_WORST)
                    assert abs(direct-old[0])/old[0]<0.03,(
                        "Direct path baseline drift",label,direct,old[0])
                    assert abs(jfet-old[1])/old[1]<0.03,(
                        "JFET path baseline drift",label,jfet,old[1])
                record={
                    "generator_carrier_peak_V":amplitude,
                    "generic_JFET_cutoff_model_V":-cutoff,
                    "generic_JFET_IDSS_model_mA":2.0,
                    "direct_detector_AFpp_V":round(direct,12),
                    "JFET_detector_AFpp_V":round(jfet,12),
                    "direct_tank_RF_positive_peak_V":round(ref_rf,12),
                    "JFET_tank_RF_positive_peak_V":round(jfet_rf,12),
                    "JFET_to_direct_AFpp_ratio":round(jfet/direct,6) if direct>1e-15 else None,
                    "note":"Ideal noise-free ngspice model only; output does not establish detectable SNR"}
                rows.append(record)
                print("IF455_GENERIC_LOWLEVEL_ENVELOPE_CASE",record,flush=True)
    assert len(rows)==len(LEVELS)*len(CORNERS)
    print("PASS_NGSPICE_IF455_10_LOWLEVEL_GENERIC_DIODE_J113_CASES_NO_SENSITIVITY_CLAIM_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
