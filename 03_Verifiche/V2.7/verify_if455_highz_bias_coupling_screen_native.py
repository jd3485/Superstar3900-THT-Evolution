#!/usr/bin/env python3
"""Native ngspice screen of IF455 follower bias impedance × RF coupling.
The circuit is a generic BJT/diode BENCH model, NOT KSP10BU OEM qualification.
Keep both independent and identical direct/loaded LC tank paths.
"""
from pathlib import Path
import math
import re
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"03_Verifiche/V2.7/spice/if455_ksp10_am455_combined_generic_transient.cir"
# Values in ohms and farads are SPICE engineering suffixes.
# Case selection is exploratory: no candidate is assumed to beat direct diode.
CASES=(
    ("legacy_10n_lowbias","10n","22k","10k"),
    ("10n_highbias","10n","220k","100k"),
    ("10n_veryhighbias","10n","470k","220k"),
    ("47p_highbias","47p","220k","100k"),
    ("10p_highbias","10p","220k","100k"),
    ("2p2_highbias","2.2p","220k","100k"),
    ("47p_veryhighbias","47p","470k","220k"),
    ("10p_veryhighbias","10p","470k","220k"),
)
LEVELS=(0.5,2.0)
REFERENCE={
    0.5:(0.023924605,0.000752869),
    2.0:(0.216298180,0.015565562),
}

def metric(log, name):
    m=re.search(r"(?im)^\s*"+re.escape(name)+r"\s*=\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)",log)
    assert m,("ngspice native measurement missing",name,log[-1300:])
    v=float(m.group(1))
    assert math.isfinite(v),(name,v)
    return v

def main():
    deck=SOURCE.read_text(encoding="utf-8")
    for anchor in ("C1701 out_b base_b 10n","R1701 vcc base_b 22k",
                   "R1702 base_b 0 10k", ".tran 0.05u 12m 0 0.05u",
                   "amp=2 rail=6 gain=80", "Q1701 vcc base_b emitter_b QGEN",
                   "D1501B bufferout envelope_b DGENERIC",
                   "C1604B tank_b out_b 10p"):
        assert deck.count(anchor)==1,("Baseline unexpectedly changed",anchor)
    results=[]
    with tempfile.TemporaryDirectory(prefix="tht_if455_bjt_zscreen_") as d:
        for amp in LEVELS:
            for label,cap,rtop,rbot in CASES:
                c=deck.replace("C1701 out_b base_b 10n",f"C1701 out_b base_b {cap}")
                c=c.replace("R1701 vcc base_b 22k",f"R1701 vcc base_b {rtop}")
                c=c.replace("R1702 base_b 0 10k",f"R1702 base_b 0 {rbot}")
                c=c.replace(".tran 0.05u 12m 0 0.05u",".tran 0.025u 12m 0 0.025u")
                c=c.replace("amp=2 rail=6 gain=80",f"amp={amp} rail=6 gain=80")
                folder=Path(d)/(str(amp).replace(".","p")+"_"+label)
                folder.mkdir()
                circuit=folder/"cascade.cir"
                logpath=folder/"native.log"
                circuit.write_text(c,encoding="utf-8")
                cmd=subprocess.run(["ngspice","-b","-o",str(logpath),str(circuit)],
                                   cwd=folder,capture_output=True,text=True)
                log=logpath.read_text(encoding="utf-8",errors="replace") if logpath.exists() else ""
                cmd.check_returncode()
                assert "Error:" not in log and "fatal" not in log.lower(),log[-1300:]
                direct=metric(log,"direct_max")-metric(log,"direct_min")
                buffered=metric(log,"buffered_max")-metric(log,"buffered_min")
                tank=metric(log,"buffered_tank_max")
                directtank=metric(log,"direct_tank_max")
                emit_min=metric(log,"buffered_emitter_min")
                emit_max=metric(log,"buffered_emitter_max")
                assert direct>0 and buffered>=0 and directtank>0 and tank>0,(
                    amp,label,direct,buffered,tank)
                assert emit_min<emit_max and -1<emit_min<7 and 0<emit_max<7,(
                    amp,label,emit_min,emit_max)
                result={"level_peak_V":amp,"case":label,
                        "C1701":cap,"R1701":rtop,"R1702":rbot,
                        "AFpp_direct_V":round(direct,9),
                        "AFpp_buffered_V":round(buffered,9),
                        "AFpp_buffered_to_direct":round(buffered/direct,7),
                        "tank_positive_ratio":round(tank/directtank,7),
                        "emitter_min_V":round(emit_min,6),
                        "emitter_max_V":round(emit_max,6)}
                results.append(result)
                print("IF455_HIGHZ_BIAS_COUPLING_CORNER",result,flush=True)
                if label=="legacy_10n_lowbias":
                    prior_direct,prior_buffer=REFERENCE[amp]
                    assert abs(direct-prior_direct)/prior_direct<0.025
                    assert abs(buffered-prior_buffer)/prior_buffer<0.025
    assert len(results)==len(CASES)*len(LEVELS)
    for amp in LEVELS:
        subset=[r for r in results if r["level_peak_V"]==amp]
        assert len(subset)==len(CASES)
        rank=sorted(subset,key=lambda x:x["AFpp_buffered_V"],reverse=True)
        print("IF455_HIGHZ_SCREEN_RANKED_BY_AFPP_GENERIC",{
            "level_peak_V":amp,"highest_model_AFpp_case":rank[0]["case"],
            "highest_AFpp_V":rank[0]["AFpp_buffered_V"],
            "best_to_direct_ratio":rank[0]["AFpp_buffered_to_direct"],
            "note":"No SNR/noise/receiver or OEM qualification"},flush=True)
    print("PASS_NGSPICE_IF455_GENERIC_BJT_16_BIAS_COUPLING_CORNERS_NO_OEM_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
