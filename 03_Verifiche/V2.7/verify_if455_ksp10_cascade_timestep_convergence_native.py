#!/usr/bin/env python3
"""Native ngspice time-resolution convergence audit of generic IF455/KSP10/AM455.
Does not call a BJT or diode OEM model, does not qualify receiver noise or SNR.
"""
from pathlib import Path
import math
import re
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
DECK=ROOT/"03_Verifiche/V2.7/spice/if455_ksp10_am455_combined_generic_transient.cir"
STEPS=(("50ns","0.05u"),("25ns","0.025u"),("12p5ns","0.0125u"))
AMPS=(0.5,2.0)
ANCHOR=".tran 0.05u 12m 0 0.05u"

def value(log,label):
    match=re.search(r"(?im)^\s*"+re.escape(label)+
                    r"\s*=\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)",log)
    assert match,("Missing .meas",label,log[-1400:])
    num=float(match.group(1))
    assert math.isfinite(num),(label,num)
    return num

def main():
    source=DECK.read_text(encoding="utf-8")
    assert source.count(ANCHOR)==1
    assert source.count("amp=2 rail=6 gain=80")==1
    assert "D1501B bufferout envelope_b DGENERIC" in source
    assert "Q1701 vcc base_b emitter_b QGEN" in source
    results=[]
    with tempfile.TemporaryDirectory(prefix="tht_if455_cascade_tstep_") as tmp:
        root=Path(tmp)
        for amp in AMPS:
            samples=[]
            for label,step in STEPS:
                name=str(amp).replace(".","p")+"_"+label
                folder=root/name
                folder.mkdir()
                modified=source.replace(ANCHOR,f".tran {step} 12m 0 {step}")
                modified=modified.replace("amp=2 rail=6 gain=80",
                                          f"amp={amp} rail=6 gain=80")
                assert modified!=source or (amp==2 and label=="50ns")
                deck=folder/"cascade.cir"
                logpath=folder/"cascade.log"
                deck.write_text(modified,encoding="utf-8")
                run=subprocess.run(["ngspice","-b","-o",str(logpath),str(deck)],
                                   cwd=folder,capture_output=True,text=True)
                log=logpath.read_text(encoding="utf-8",errors="replace") if logpath.exists() else ""
                run.check_returncode()
                assert "Error:" not in log and "fatal" not in log.lower(),log[-1000:]
                straight=value(log,"direct_max")-value(log,"direct_min")
                follower=value(log,"buffered_max")-value(log,"buffered_min")
                rf_d=value(log,"direct_tank_max")
                rf_b=value(log,"buffered_tank_max")
                assert straight>0 and follower>0 and rf_d>0 and rf_b>0
                record={"input_peak_V":amp,"max_timestep":label,
                        "direct_AFpp_V":straight,"buffered_AFpp_V":follower,
                        "direct_tank_positive_peak_V":rf_d,
                        "buffered_tank_positive_peak_V":rf_b,
                        "buffer_to_direct_ratio":follower/straight}
                samples.append(record)
                print("IF455_KSP10_GENERIC_TIMESTEP_CASE",
                      {k:round(v,9) if isinstance(v,float) else v
                       for k,v in record.items()},flush=True)
            if amp==2:
                assert abs(samples[0]["direct_AFpp_V"]-0.21432405)/0.21432405<0.01
                assert abs(samples[0]["buffered_AFpp_V"]-0.014614407)/0.014614407<0.01
            for i in range(1,len(samples)):
                prev,curr=samples[i-1],samples[i]
                for field in ("direct_AFpp_V","buffered_AFpp_V",
                              "direct_tank_positive_peak_V",
                              "buffered_tank_positive_peak_V"):
                    delta=abs(curr[field]-prev[field])/max(abs(curr[field]),1e-12)
                    print("IF455_KSP10_GENERIC_NUMERIC_DELTA",
                          {"input_peak_V":amp,"from":prev["max_timestep"],
                           "to":curr["max_timestep"],"measurement":field,
                           "relative_change":round(delta,7),
                           "below_two_percent":delta<0.02},flush=True)
                    assert math.isfinite(delta) and delta>=0
                    if i==len(samples)-1:
                        assert delta<0.02,("Final 25ns->12.5ns model step not converged at 2%",amp,field,delta)
            results.extend(samples)
    assert len(results)==len(AMPS)*len(STEPS)
    print("PASS_NGSPICE_IF455_KSP10_AM455_6_TIMESTEP_AUDITS_NOT_OEM_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
