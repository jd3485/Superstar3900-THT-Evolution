#!/usr/bin/env python3
"""Verify actual ngspice AC sweep of coupling-loaded IF455 THT laboratory LC tank.

30-ohm coil ESR, capacitors and source impedances are ASSUMED scenarios:
not Coilcraft/vendor RF model, not receiver filter selectivity certification.
"""
from pathlib import Path
import math
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
NET=ROOT/"03_Verifiche/V2.7/spice/if455_loaded_tank_ac_comparison.cir"
SCH=ROOT/"04_KiCad/V2.7_DRAFT/IF455_TANK/IF455_TANK_THT_V2_7_DRAFT.kicad_sch"

def data_rows(path):
    rows=[]
    for line in path.read_text(encoding="utf-8").splitlines():
        parts=line.split()
        if not parts or parts[0].startswith("*"):continue
        try: numeric=tuple(float(x) for x in parts)
        except ValueError:continue
        assert len(numeric)==3,("ngspice wr_singlescale expected frequency/new/old",numeric)
        assert all(math.isfinite(x) for x in numeric),numeric
        rows.append(numeric)
    return rows

def main():
    sch=SCH.read_text(encoding="utf-8")
    spice=NET.read_text(encoding="utf-8")
    assert '"110pF_C0G_THT"' in sch
    assert '"2p2_C0G_THT"' in sch
    for required in ("NO FAB/NO TX","C1602_NEW tank_new 0 110p",
                     "C1602_OLD tank_old 0 120p",
                     "C1603_NEW tank_new 0 2.2p","C1604_NEW tank_new out_new 10p",
                     "R_LOSS_NEW loss_new 0 30","RGEN_NEW src_new gen_new 50",
                     "ac lin 1001 350k 600k","wrdata if455_tank_ac_sweep.dat"):
        assert required in spice,("Changed RF test assumptions",required)
    with tempfile.TemporaryDirectory(prefix="tht_if455_ac_") as root:
        d=Path(root)
        log=d/"ngspice.log"
        run=subprocess.run(["ngspice","-b","-o",str(log),str(NET)],
                           cwd=d,capture_output=True,text=True)
        logs=log.read_text(encoding="utf-8",errors="replace") if log.exists() else ""
        print("IF455_AC_NGSPICE_STDERR",run.stderr[-1600:],flush=True)
        print("IF455_AC_NGSPICE_LOG",logs[-2500:],flush=True)
        run.check_returncode()
        assert "Error:" not in logs and "fatal" not in logs.lower()
        output=d/"if455_tank_ac_sweep.dat"
        assert output.exists(),("Missing actual native ngspice AC wrdata",logs[-1500:])
        rows=data_rows(output)
    assert len(rows)==1001,("Missing AC sweep data",len(rows))
    freqs=[x[0] for x in rows]
    assert abs(freqs[0]-350000)<1 and abs(freqs[-1]-600000)<1
    assert all(x<y for x,y in zip(freqs,freqs[1:]))
    idx_new=max(range(len(rows)),key=lambda i:rows[i][1])
    idx_old=max(range(len(rows)),key=lambda i:rows[i][2])
    fnew=rows[idx_new][0]
    fold=rows[idx_old][0]
    assert 445000<fnew<465000,("Unexpected coupled new peak",fnew)
    assert 425000<fold<449000,("Unexpected original 122pF loaded peak",fold)
    assert abs(fnew-455000)<abs(fold-455000)/2,("Retuning did not improve loaded center",fnew,fold)
    assert rows[idx_new][1]>2.5*rows[0][1] and rows[idx_new][1]>2.5*rows[-1][1], "No selective resonance in illustrative model"
    ideal_unloaded=1/(2*math.pi*math.sqrt(1e-3*112.2e-12))
    assert 473000<ideal_unloaded<478000,ideal_unloaded
    print("IF455_AC_NGSPICE_LOADED_PEAKS_HZ",
          {"updated":round(fnew,2),"old":round(fold,2),
           "unloaded_new_LC_formula":round(ideal_unloaded,2),
           "new_gain_peak":round(rows[idx_new][1],5)},flush=True)
    print("PASS_NGSPICE_IF455_LOADED_RESONANCE_RETUNE_GENERIC_RLC_NOT_OEM_NO_FAB",flush=True)

if __name__=="__main__":main()
