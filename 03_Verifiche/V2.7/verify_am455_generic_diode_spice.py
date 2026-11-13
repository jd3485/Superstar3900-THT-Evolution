#!/usr/bin/env python3
"""Run real ngspice AM455 THT envelope bench using NON-VENDOR diode model.

Tests that 455kHz/1kHz AM causes measurable AF output but an unmodulated
455kHz carrier does not. Not a guarantee of sensitivity, distortion,
selectivity, matching, FM/SSB demodulation, PCB routing or safety.
"""
from pathlib import Path
import math
import re
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
DECK=ROOT/"03_Verifiche/V2.7/spice/am455_envelope_1khz_generic_diode_bench.cir"
MEAS=("am_max","am_min","unmod_max","unmod_min")


def parse(stdout):
    measured={}
    for key in MEAS:
        match=re.search(r"(?im)^\s*"+key+r"\s*=\s*([-+]?\d+\.?\d*(?:[eE][-+]?\d+)?)",stdout)
        assert match,("Missing native ngspice .meas",key,stdout[-2400:])
        v=float(match.group(1))
        assert math.isfinite(v),(key,v)
        measured[key]=v
    return measured


def main():
    text=DECK.read_text(encoding="utf-8")
    required=("455kHz AM ONLY","NO FAB","DGENERIC",
              "R1501_AM env_am 0 47k","C1501_AM env_am 0 1n",
              "C1502_AM env_am af_am 100n","R1502_AM af_am 0 100k",
              "R1501_UN env_unmod 0 47k","C1501_UN env_unmod 0 1n",
              "C1502_UN env_unmod af_unmod 100n","R1502_UN af_unmod 0 100k",
              ".param fc=455k fa=1k mag=0.50 amp=2.0",
              ".model DGENERIC D(")
    for item in required:
        assert item in text,("Simulation no longer mirrors bench topology",item)
    assert "TI vendor model" not in text
    with tempfile.TemporaryDirectory(prefix="tht_am455_spice_") as folder:
        logfile=Path(folder)/"ngspice.log"
        run=subprocess.run(["ngspice","-b","-o",str(logfile),str(DECK)],
                           cwd=ROOT,capture_output=True,text=True)
        log=logfile.read_text(encoding="utf-8",errors="replace") if logfile.exists() else ""
        print("AM455_NGSPICE_STDERR",run.stderr[-1500:],flush=True)
        print("AM455_NGSPICE_LOG",log[-2500:],flush=True)
        run.check_returncode()
        assert not re.search(r"(?im)^\s*(?:error|fatal):",log),"ngspice errors"
        values=parse(log)
    am_pp=values["am_max"]-values["am_min"]
    unmod_pp=values["unmod_max"]-values["unmod_min"]
    assert values["am_max"]>values["am_min"]
    assert values["unmod_max"]>=values["unmod_min"]
    # Broad detection check, NOT an audio quality or absolute gain threshold.
    assert 0.12<am_pp<4.5,("No convincing bench 1kHz envelope recovery",values,am_pp)
    assert 0<=unmod_pp<0.15,("Unmodulated carrier leaking too much into audio",values,unmod_pp)
    assert am_pp>3*unmod_pp,("Demodulation not distinguishable from carrier ripple",values)
    print("AM455_SPICE_BENCH_AM_P2P_V",round(am_pp,4),
          "UNMOD_P2P_V",round(unmod_pp,4),flush=True)
    print("PASS_NGSPICE_AM455_GENERIC_DIODE_AM_VS_UNMOD_BENCH_NO_FAB_NO_SSB_FM",flush=True)


if __name__=="__main__":
    main()
