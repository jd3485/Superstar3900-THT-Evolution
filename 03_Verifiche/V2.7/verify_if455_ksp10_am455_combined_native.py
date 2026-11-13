#!/usr/bin/env python3
"""ngspice nonlinear generic IF455 tank -> KSP10 candidate -> AM455 diode comparison.

The 1N4148 and BJT are GENERIC models; do not infer hardware sensitivity, noise,
RF selectivity or approve the buffer for manufacture based on these checks.
"""
from pathlib import Path
import math
import re
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
DECK=ROOT/"03_Verifiche/V2.7/spice/if455_ksp10_am455_combined_generic_transient.cir"
PRIOR=ROOT/"03_Verifiche/V2.7/spice/if455_am455_nonlinear_transient_generic.cir"
KICAD=ROOT/"04_KiCad/V2.7_DRAFT/IF455_KSP10_FOLLOWER/IF455_KSP10_FOLLOWER_THT_V2_7_DRAFT.kicad_sch"
AMPS=(0.5,2.0)

def metric(log,name):
    regex=r"(?im)^\s*"+re.escape(name)+r"\s*=\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)"
    match=re.search(regex,log)
    assert match, ("Missing native ngspice .meas",name,log[-1500:])
    result=float(match.group(1))
    assert math.isfinite(result),(name,result)
    return result

def main():
    original=DECK.read_text(encoding="utf-8")
    prior=PRIOR.read_text(encoding="utf-8")
    kicad=KICAD.read_text(encoding="utf-8")
    assert original.count(".param fc=455k fa=1k depth=0.5 amp=2 rail=6 gain=80")==1
    for token in ("R1701 vcc base_b 22k","R1702 base_b 0 10k",
                  "R1703 emitter_b 0 2.2k","C1701 out_b base_b 10n",
                  "C1702 emitter_b bufferout 10n","Q1701 vcc base_b emitter_b QGEN",
                  ".model DGENERIC", ".model QGEN", "D1501B bufferout envelope_b DGENERIC",
                  "R1601B tank_b 0 47k","R1602B out_b 0 100k",
                  "C1604B tank_b out_b 10p", "RCOILB ltail_b 0 16.5"):
        assert token in original, ("Altered combined path",token)
    for token in ("22k_TOP_BIAS_DRAFT","10k_BOTTOM_BIAS_DRAFT",
                  "2k2_EMITTER_SET_DRAFT","ONSEMI_KSP10BU_TO92_CANDIDATE"):
        assert token in kicad, ("KiCad mismatch",token)
    # Compare actual generic parameters against the previously verified model.
    assert ".model DGENERIC D(Is=2.5n N=1.9 Rs=0.6 Cjo=4p Vj=0.75 Tt=4n)" in prior
    assert ".model DGENERIC D(Is=2.5n N=1.9 Rs=0.6 Cjo=4p Vj=0.75 Tt=4n)" in original
    for old,new in (("RCOIL ltail 0 16.5","RCOILD ltail_d 0 16.5"),
                    ("C1604 tank out 10p","C1604D tank_d out_d 10p"),
                    ("R1501 envelope 0 47k","R1501D envelope_d 0 47k")):
        assert old in prior and new in original,("Prior model reference drift",old,new)
    outcomes=[]
    with tempfile.TemporaryDirectory(prefix="tht_if455_full_cascade_") as temp:
        for amplitude in AMPS:
            folder=Path(temp)/str(amplitude).replace(".","p")
            folder.mkdir()
            model=original.replace("amp=2 rail=6 gain=80",
                                   "amp="+str(amplitude)+" rail=6 gain=80")
            path=folder/"cascade.cir"
            logfile=folder/"cascade.log"
            path.write_text(model,encoding="utf-8")
            proc=subprocess.run(["ngspice","-b","-o",str(logfile),str(path)],
                                cwd=folder,capture_output=True,text=True)
            log=logfile.read_text(encoding="utf-8",errors="replace") if logfile.exists() else ""
            proc.check_returncode()
            assert "Error:" not in log and "fatal" not in log.lower(),log[-1600:]
            direct=metric(log,"direct_max")-metric(log,"direct_min")
            buffered=metric(log,"buffered_max")-metric(log,"buffered_min")
            tank_d=metric(log,"direct_tank_max")
            tank_b=metric(log,"buffered_tank_max")
            emax=metric(log,"buffered_emitter_max")
            emin=metric(log,"buffered_emitter_min")
            assert direct>0 and buffered>0,(amplitude,direct,buffered)
            assert tank_d>0 and tank_b>0,(amplitude,tank_d,tank_b)
            assert emax>emin and emax<6.6,(amplitude,emin,emax)
            ratio=buffered/direct
            assert math.isfinite(ratio) and ratio>0
            if amplitude==2.0:
                # Independent prior native deck delivered 0.17444891 Vpp at 2 Vpeak.
                # This ensures direct reference was not silently redesigned.
                assert abs(direct-0.17444891)<0.005,(
                    "Reference drift versus PR #94/#95",direct)
            result={"input_peak_V":amplitude,"direct_AFpp_V":round(direct,9),
                    "buffered_AFpp_V":round(buffered,9),"buffer_to_direct_AFpp":round(ratio,6),
                    "direct_tank_positive_peak_V":round(tank_d,9),
                    "buffered_tank_positive_peak_V":round(tank_b,9),
                    "buffer_emitter_min_V":round(emin,6),
                    "buffer_emitter_max_V":round(emax,6)}
            outcomes.append(result)
            print("IF455_KSP10_AM455_FULL_CASCADE_GENERIC",result,flush=True)
    assert outcomes[0]["input_peak_V"]<outcomes[1]["input_peak_V"]
    print("PASS_NGSPICE_IF455_KSP10_AM455_GENERIC_NONLINEAR_CASCADE_NOT_OEM_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
