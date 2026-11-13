#!/usr/bin/env python3
"""Genuine ngspice AC check: candidate Delevan 2500-28J 455kHz ±5% corners.

PASS means the *risk is detected*, NOT that a fixed tank is approved.
Uses DCR 16.5ohm and a 2.8MHz-SRF-equivalent capacitor as illustrative
parameters; Q at 455kHz and real parasitics have NOT been measured.
"""
from pathlib import Path
import math
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
NET=ROOT/"03_Verifiche/V2.7/spice/if455_delevan_2500_28j_tolerance_ac.cir"
SCHEMATIC=ROOT/"04_KiCad/V2.7_DRAFT/IF455_TANK/IF455_TANK_THT_V2_7_DRAFT.kicad_sch"


def rows_from_ngspice(path):
    data=[]
    for line in path.read_text(encoding="utf-8").splitlines():
        try: vals=tuple(float(i) for i in line.split())
        except ValueError: continue
        if not vals:continue
        assert len(vals)==5,("Expected frequency and four amplitude columns",vals)
        assert all(math.isfinite(x) for x in vals)
        data.append(vals)
    return data


def main():
    sch=SCHEMATIC.read_text(encoding="utf-8")
    net=NET.read_text(encoding="utf-8")
    assert "110pF_C0G_THT" in sch
    assert "1mH_DELEVAN_2500-28J_CANDIDATE_NOT_QUALIFIED" in sch
    assert "L_1mH_Axial_THT_PROVISIONAL" in sch
    for required in ("NO FAB NO TX","L_L_MINUS5 tank_L_MINUS5 loss_L_MINUS5 0.95m",
                     "L_L_NOM tank_L_NOM loss_L_NOM 1m",
                     "L_L_PLUS5 tank_L_PLUS5 loss_L_PLUS5 1.05m",
                     "RLOSS_L_NOM loss_L_NOM 0 16.5",
                     "CPAR_L_NOM_CPAR tank_L_NOM_CPAR 0 3.23p",
                     "ac lin 2001 400k 510k",
                     "wrdata if455_delevan_corners.dat"):
        assert required in net,("Scope/model assumption changed",required)
    parasitic=1/((2*math.pi*2.8e6)**2*1e-3)
    assert 3.20e-12<parasitic<3.26e-12
    with tempfile.TemporaryDirectory(prefix="tht_if455_delevan_") as location:
        folder=Path(location)
        logfile=folder/"run.log"
        cp=subprocess.run(["ngspice","-b","-o",str(logfile),str(NET)],
                          cwd=folder,capture_output=True,text=True)
        log=logfile.read_text(encoding="utf-8",errors="replace") if logfile.exists() else ""
        print("IF455_CORNERS_NGSPICE_STDERR",cp.stderr[-1000:],flush=True)
        print("IF455_CORNERS_NGSPICE_LOG",log[-1800:],flush=True)
        cp.check_returncode()
        assert "Error:" not in log and "fatal" not in log.lower()
        output=folder/"if455_delevan_corners.dat"
        assert output.is_file(),("Missing actual ngspice AC data",log[-1000:])
        data=rows_from_ngspice(output)
    assert len(data)==2001,("AC sweep rows",len(data))
    assert abs(data[0][0]-400000)<1 and abs(data[-1][0]-510000)<1
    freqs=[]
    for column in (1,2,3,4):
        i=max(range(len(data)),key=lambda j:data[j][column])
        freqs.append(data[i][0])
    f_lowL,f_nom,f_highL,f_parasitic=freqs
    assert 445000<f_nom<465000,("Nominal case not near historical model",freqs)
    assert f_lowL>f_nom+7000,("Minus 5% inductance not changing center enough",freqs)
    assert f_highL<f_nom-7000,("Plus 5% inductance not changing center enough",freqs)
    assert f_parasitic<f_nom-2500,("Nominal SRF-equivalent stray capacitance not detuning",freqs)
    # Acceptance threshold 455 kHz +/-5kHz is illustrative, not a CB
    # passband/sensitivity/adjacent-channel or commercial specification.
    assert max(abs(f_lowL-455000),abs(f_highL-455000))>8000, (
        "Unexpected robust center: remove rejection only after RF review",freqs)
    print("IF455_DELEVAN_2500_28J_GENERIC_CORNER_PEAKS_HZ",dict(zip(
        ("L_minus5pct","L_nominal","L_plus5pct","L_nominal_plus_3p23_pF"),freqs)),flush=True)
    print("REJECT_FIXED_110PF_IF455_TANK_WITH_5PCT_COIL_UNTIL_TRIM_AND_RF_MEASUREMENTS",flush=True)
    print("PASS_NGSPICE_IF455_OEM_CANDIDATE_TOLERANCE_RISK_DETECTED_NOT_FOR_FAB",flush=True)


if __name__=="__main__":
    main()
