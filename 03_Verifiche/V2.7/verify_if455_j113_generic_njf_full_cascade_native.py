#!/usr/bin/env python3
"""12 native ngspice generic onsemi J113-candidate JFET source follower corners.
OEM J113 pin1 D pin2 S pin3 G is verified separately by native KiCad9 gate.
SPICE model is exploratory: no OEM transistor/noise/real IF reception claim.
"""
from pathlib import Path
import math
import re
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
DECK=ROOT/"03_Verifiche/V2.7/spice/if455_j113_am455_generic_jfet_transient.cir"
SCH=ROOT/"04_KiCad/V2.7_DRAFT/IF455_J113_SOURCE_FOLLOWER/IF455_J113_SOURCE_FOLLOWER_THT_V2_7_DRAFT.kicad_sch"
LEVELS=(0.5,2.0)
CUTOFFS=(0.5,1.5,3.0) # |VTO| in V; illustrative ends of onsemi J113 VGS(off) rating
IDSS_AMPS=(0.002,0.010) # nominal stand-ins (min OEM Idss 2mA, NO certified upper)
MODEL=".model JGEN NJF(BETA=0.00088888889 VTO=-1.5 LAMBDA=0.02 CGS=5p CGD=2p RD=20 RS=20)"

def metric(log,label):
    pattern=r"(?im)^\s*"+re.escape(label)+r"\s*=\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)"
    m=re.search(pattern,log)
    assert m,("ngspice native .meas absent",label,log[-1400:])
    v=float(m.group(1))
    assert math.isfinite(v),(label,v)
    return v

def main():
    base=DECK.read_text(encoding="utf-8")
    sch=SCH.read_text(encoding="utf-8")
    assert base.count(MODEL)==1
    assert base.count("amp=2 rail=6")==1
    assert base.count("C1801 out_b gate_j 10p")==1
    assert base.count("R1801 gate_j 0 1Meg")==1
    assert base.count("JQ1801 vcc gate_j source_j JGEN")==1
    assert base.count("R1802 source_j 0 2.2k")==1
    assert base.count("C1802 source_j bufferout 10n")==1
    assert base.count("R1803 bufferout 0 100k")==1
    assert base.count("EGS gs_monitor 0 gate_j source_j 1")==1
    assert base.count(".meas tran gate_source_max MAX v(gs_monitor)")==1
    assert base.count(".meas tran gate_source_min MIN v(gs_monitor)")==1
    assert base.count(".tran 0.025u 12m 0 0.025u")==1
    for item in ("10pF_C0G_RF_INPUT_PROVISIONAL","1Meg_GATE_DC_RETURN_PROVISIONAL",
                 "2k2_SOURCE_SELF_BIAS_DRAFT","ONSEMI_J113_TO92_1D_2S_3G_ONLY_CANDIDATE"):
        assert item in sch,item
    rows=[]
    with tempfile.TemporaryDirectory(prefix="tht_j113_njf_corners_") as tmp:
        for amp in LEVELS:
            for cutoff in CUTOFFS:
                for idss in IDSS_AMPS:
                    label=f"amp_{amp}_cut_{cutoff}_idss_{idss}".replace(".","p")
                    wd=Path(tmp)/label
                    wd.mkdir()
                    beta=idss/(cutoff*cutoff)
                    model=f".model JGEN NJF(BETA={beta:.10g} VTO={-cutoff:.10g} LAMBDA=0.02 CGS=5p CGD=2p RD=20 RS=20)"
                    case=base.replace(MODEL,model).replace("amp=2 rail=6",f"amp={amp} rail=6")
                    path=wd/"model.cir"
                    logfile=wd/"model.log"
                    path.write_text(case,encoding="utf-8")
                    result=subprocess.run(["ngspice","-b","-o",str(logfile),str(path)],
                                          cwd=wd,capture_output=True,text=True)
                    log=logfile.read_text(encoding="utf-8",errors="replace") if logfile.exists() else ""
                    result.check_returncode()
                    assert "Error:" not in log and "fatal" not in log.lower(),log[-1200:]
                    direct=metric(log,"direct_max")-metric(log,"direct_min")
                    buffered=metric(log,"buffered_max")-metric(log,"buffered_min")
                    rf_direct=metric(log,"direct_tank_max")
                    rf_buffer=metric(log,"buffered_tank_max")
                    source_min=metric(log,"buffered_source_min")
                    source_max=metric(log,"buffered_source_max")
                    vgsmax=metric(log,"gate_source_max")
                    vgsmin=metric(log,"gate_source_min")
                    assert direct>0 and buffered>=0 and rf_direct>0 and rf_buffer>0
                    assert source_max>source_min and math.isfinite(buffered/direct)
                    ref=0.023924605 if amp==0.5 else 0.216298180
                    assert abs(direct-ref)/ref<0.03,(
                        "Changed direct reference path or timestep",amp,direct,ref)
                    row={"input_peak_V":amp,"cutoff_model_V":cutoff,
                         "idss_model_mA":round(idss*1000,3),
                         "BETA_model_A_per_V2":round(beta,8),
                         "AFpp_direct_V":round(direct,9),
                         "AFpp_JFET_V":round(buffered,9),
                         "AFpp_JFET_to_direct":round(buffered/direct,6),
                         "tank_RF_positive_JFET_to_direct":round(rf_buffer/rf_direct,6),
                         "source_min_V":round(source_min,6),
                         "source_max_V":round(source_max,6),
                         "Vgs_forward_peak_V":round(vgsmax,6),
                         "Vgs_negative_peak_V":round(vgsmin,6)}
                    rows.append(row)
                    print("IF455_ONSEMI_J113_GENERIC_NJF_CASCADE_CASE",row,flush=True)
    assert len(rows)==12
    for amp in LEVELS:
        ranked=sorted([v for v in rows if v["input_peak_V"]==amp],
                      key=lambda r:r["AFpp_JFET_to_direct"],reverse=True)
        assert len(ranked)==6
        print("IF455_J113_GENERIC_NJF_BEST_AFPP_ONLY_NOT_APPROVED",
              {"amp":amp,"case":ranked[0],"interpretation":"No noise/stability/THD/OEM gate"},flush=True)
    print("PASS_NGSPICE_IF455_ONSEMI_J113_GENERIC_NJF_12_CORNERS_NOT_OEM_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
