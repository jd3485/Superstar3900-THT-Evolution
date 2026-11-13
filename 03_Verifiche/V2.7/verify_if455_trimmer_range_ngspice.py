#!/usr/bin/env python3
"""Check real ngspice 10–50pF *candidate* trimmer coverage at 455kHz.

A PASS proves only a simulated adjustable range straddles 455kHz for modeled
inductance ±5% and nominal SRF-derived parasitic cases, NOT RF performance.
"""
from pathlib import Path
import subprocess
import tempfile
import math

ROOT=Path(__file__).resolve().parents[2]
NET=ROOT/"03_Verifiche/V2.7/spice/if455_trimmer_gkg50015_tuning_envelope.cir"
SCH=ROOT/"04_KiCad/V2.7_DRAFT/IF455_TANK/IF455_TANK_THT_V2_7_DRAFT.kicad_sch"
CORNERS=("LMIN","LNOM","LMAX","LPAR")


def rows(path):
    result=[]
    for raw in path.read_text(encoding="utf-8").splitlines():
        try: record=tuple(float(v) for v in raw.split())
        except ValueError:continue
        if not record:continue
        assert len(record)==9,("Expected 1 frequency + 8 magnitudes",record)
        assert all(math.isfinite(v) for v in record)
        result.append(record)
    return result


def main():
    s=SCH.read_text(encoding="utf-8")
    text=NET.read_text(encoding="utf-8")
    for needle in ("EW_GKG50015_10to50pF_THT_CANDIDATE_TRIM",
                   "82pF_C0G_THT",
                   "TH_TANK:Trimmer_EW_GKG50015_P5.00mm_OEM_DRAFT"):
        assert needle in s,("Actual KiCad draft not the simulated topology",needle)
    for needle in ("NO FAB","C1602_LMIN_MIN tank_LMIN_MIN 0 82p",
                   "CTRIM_LMIN_MIN tank_LMIN_MIN 0 10p",
                   "CTRIM_LMIN_MAX tank_LMIN_MAX 0 50p",
                   "L_LMIN_MIN tank_LMIN_MIN loss_LMIN_MIN 0.95m",
                   "L_LMAX_MAX tank_LMAX_MAX loss_LMAX_MAX 1.05m",
                   "CPAR_LPAR_MAX tank_LPAR_MAX 0 3.23p",
                   "RLOSS_LNOM_MAX loss_LNOM_MAX 0 16.5",
                   "ac lin 1201 390k 550k",
                   "wrdata if455_trimmer_envelope_ac.dat"):
        assert needle in text,("Model expectation changed",needle)
    with tempfile.TemporaryDirectory(prefix="tht_if455_adjustable_") as temp:
        tmp=Path(temp)
        log=tmp/"spice.log"
        cp=subprocess.run(["ngspice","-b","-o",str(log),str(NET)],
                          cwd=tmp,capture_output=True,text=True)
        logs=log.read_text(encoding="utf-8",errors="replace") if log.exists() else ""
        print("IF455_TRIM_NGSPICE_STDERR",cp.stderr[-800:],flush=True)
        print("IF455_TRIM_NGSPICE_LOG",logs[-1300:],flush=True)
        cp.check_returncode()
        assert "Error:" not in logs and "fatal" not in logs.lower()
        tab=tmp/"if455_trimmer_envelope_ac.dat"
        assert tab.exists(),("No native ngspice results",logs[-1300:])
        table=rows(tab)
    assert len(table)==1201,len(table)
    assert abs(table[0][0]-390000)<1 and abs(table[-1][0]-550000)<1
    measurements={}
    for i,corner in enumerate(CORNERS):
        colmin=1+2*i
        colmax=colmin+1
        f_at_C10=max(table,key=lambda x:x[colmin])[0]
        f_at_C50=max(table,key=lambda x:x[colmax])[0]
        # Opposite trimmer endpoints straddle 455 kHz in *this* simplistic
        # RF model, so a tuning solution is plausible (not certified).
        assert f_at_C10>455000+3000,(corner,f_at_C10,f_at_C50)
        assert f_at_C50<455000-3000,(corner,f_at_C10,f_at_C50)
        measurements[corner]=(f_at_C10,f_at_C50)
    assert measurements["LMIN"][0]>measurements["LNOM"][0]>measurements["LMAX"][0]
    assert measurements["LPAR"][0]<measurements["LNOM"][0]
    print("IF455_GKG50015_THT_TRIM_RANGE_PEAKS_HZ",measurements,flush=True)
    print("PASS_NGSPICE_IF455_VARIABLE_10TO50P_TUNING_RANGE_ONLY_NOT_RF_QUALIFIED_NO_FAB",flush=True)


if __name__=="__main__":
    main()
