#!/usr/bin/env python3
"""Native worst-case generic J113 source follower coupling/source-resistor screen.
JGEN is NOT an OEM macro-model; no RF noise, hardware or production sign-off.
"""
from pathlib import Path
import math
import re
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
DECK=ROOT/"03_Verifiche/V2.7/spice/if455_j113_am455_generic_jfet_transient.cir"
SOURCE_RESISTORS=("680","1k","2.2k")
GATE_COUPLING=("10p","47p","100p")
LEVELS=(0.5,2.0)
OLD_MODEL=".model JGEN NJF(BETA=0.00088888889 VTO=-1.5 LAMBDA=0.02 CGS=5p CGD=2p RD=20 RS=20)"
WORST_MODEL=".model JGEN NJF(BETA=0.00022222222 VTO=-3 LAMBDA=0.02 CGS=5p CGD=2p RD=20 RS=20)"
REFERENCES={0.5:0.023924896,2.0:0.21630616}
JFET_BASELINE={0.5:0.005823876,2.0:0.29403445}

def val(text,label):
    m=re.search(r"(?im)^\s*"+re.escape(label)+r"\s*=\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)",text)
    assert m,("Missing ngspice native .meas",label,text[-1100:])
    v=float(m.group(1))
    assert math.isfinite(v),(label,v)
    return v

def main():
    initial=DECK.read_text(encoding="utf-8")
    for anchor in (OLD_MODEL,"C1801 out_b gate_j 10p",
                   "R1802 source_j 0 2.2k",
                   "EGS gs_monitor 0 gate_j source_j 1",
                   "JQ1801 vcc gate_j source_j JGEN",
                   ".tran 0.025u 12m 0 0.025u",
                   "amp=2 rail=6"):
        assert initial.count(anchor)==1,("Changed benchmark",anchor)
    outputs=[]
    with tempfile.TemporaryDirectory(prefix="tht_if455_j113_loading_") as tmp:
        for amp in LEVELS:
            for cap in GATE_COUPLING:
                for rs in SOURCE_RESISTORS:
                    sample=initial.replace(OLD_MODEL,WORST_MODEL)
                    sample=sample.replace("C1801 out_b gate_j 10p",f"C1801 out_b gate_j {cap}")
                    sample=sample.replace("R1802 source_j 0 2.2k",f"R1802 source_j 0 {rs}")
                    sample=sample.replace("amp=2 rail=6",f"amp={amp} rail=6")
                    folder=Path(tmp)/(f"source_{amp}_cap_{cap}_rs_{rs}".replace(".","p"))
                    folder.mkdir()
                    deck=folder/"case.cir"
                    logpath=folder/"result.log"
                    deck.write_text(sample,encoding="utf-8")
                    run=subprocess.run(["ngspice","-b","-o",str(logpath),str(deck)],
                                       cwd=folder,capture_output=True,text=True)
                    log=logpath.read_text(encoding="utf-8",errors="replace") if logpath.exists() else ""
                    run.check_returncode()
                    assert "Error:" not in log and "fatal" not in log.lower(),log[-1100:]
                    direct=val(log,"direct_max")-val(log,"direct_min")
                    follower=val(log,"buffered_max")-val(log,"buffered_min")
                    rf_d=val(log,"direct_tank_max")
                    rf_j=val(log,"buffered_tank_max")
                    vgsmax=val(log,"gate_source_max")
                    src_min=val(log,"buffered_source_min")
                    src_max=val(log,"buffered_source_max")
                    assert direct>0 and follower>=0 and rf_d>0 and rf_j>0
                    assert src_min<src_max
                    ref=REFERENCES[amp]
                    assert abs(direct-ref)/ref<0.03,(amp,direct,ref)
                    if cap=="10p" and rs=="2.2k":
                        base=JFET_BASELINE[amp]
                        assert abs(follower-base)/base<0.03,("PR105 worst corner reference drift",amp,base,follower)
                    row={"level_peak_V":amp,"input_C_pF":cap,"source_R_ohms":rs,
                         "VTO_model_V":-3.0,"IDSS_model_mA":2.0,
                         "AFpp_direct_V":round(direct,9),
                         "AFpp_JFET_V":round(follower,9),
                         "AFpp_JFET_to_direct":round(follower/direct,6),
                         "tank_positive_ratio":round(rf_j/rf_d,6),
                         "source_min_V":round(src_min,6),
                         "source_max_V":round(src_max,6),
                         "Vgs_max_V":round(vgsmax,6),
                         "gate_forward_in_model":vgsmax>0}
                    print("IF455_J113_GENERIC_WORST_CORNER_COUPLING_SOURCE",row,flush=True)
                    outputs.append(row)
    assert len(outputs)==len(LEVELS)*len(GATE_COUPLING)*len(SOURCE_RESISTORS)
    for amp in LEVELS:
        ranked=sorted([r for r in outputs if r["level_peak_V"]==amp],
                      key=lambda r:r["AFpp_JFET_to_direct"],reverse=True)
        assert len(ranked)==9
        print("IF455_J113_GENERIC_WORST_CASE_RANKED_AFPP_ONLY",{
            "amp":amp,"best_model_cap":ranked[0]["input_C_pF"],
            "best_model_source_R":ranked[0]["source_R_ohms"],
            "best_ratio":ranked[0]["AFpp_JFET_to_direct"],
            "warning":"NOT OEM/low-noise/linear RF qualification"},flush=True)
    print("PASS_NGSPICE_IF455_J113_GENERIC_18_WORSTCORNER_CAP_SOURCE_NO_OEM_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
