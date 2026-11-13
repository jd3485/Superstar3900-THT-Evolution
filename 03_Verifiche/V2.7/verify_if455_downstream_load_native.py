#!/usr/bin/env python3
"""Native ngspice AC 455k tank output loading — resistive surrogates only.

No diode small-signal model or AM receiver sensitivity conclusions are allowed.
"""
from pathlib import Path
import math
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
DECK=ROOT/"03_Verifiche/V2.7/spice/if455_downstream_input_load_ac.cir"
TANK=ROOT/"04_KiCad/V2.7_DRAFT/IF455_TANK/IF455_TANK_THT_V2_7_DRAFT.kicad_sch"

def main():
    net=DECK.read_text(encoding="utf-8")
    sch=TANK.read_text(encoding="utf-8")
    for label in ("82pF_C0G_THT","EW_GKG50015_10to50pF_THT_CANDIDATE_TRIM"):
        assert label in sch
    for term in ("NOT the nonlinear 1N4148","UNKNOWN. NO FAB",
                 "C1602_UNLOADED tank_UNLOADED 0 82p",
                 "CTRIM_UNLOADED tank_UNLOADED 0 30p",
                 "C1604_UNLOADED tank_UNLOADED out_UNLOADED 10p",
                 "R1602_UNLOADED out_UNLOADED 0 100k",
                 "R_DOWNSTREAM_R10K out_R10K 0 10000",
                 "R_DOWNSTREAM_R1K out_R1K 0 1000",
                 "ac lin 101 450k 460k",
                 "wrdata if455_downstream_loading_ac.dat"):
        assert term in net,("Model contract changed",term)
    with tempfile.TemporaryDirectory(prefix="tht_if455_load_") as t:
        folder=Path(t)
        logpath=folder/"native.log"
        result=subprocess.run(["ngspice","-b","-o",str(logpath),str(DECK)],
                              cwd=folder,capture_output=True,text=True)
        log=logpath.read_text(encoding="utf-8",errors="replace") if logpath.exists() else ""
        print("IF455_LOAD_NGSPICE_STDERR",result.stderr[-600:],flush=True)
        print("IF455_LOAD_NGSPICE_LOG",log[-1600:],flush=True)
        result.check_returncode()
        assert "Error:" not in log and "fatal" not in log.lower()
        data=folder/"if455_downstream_loading_ac.dat"
        assert data.is_file(),("No native output",log[-1200:])
        rows=[]
        for line in data.read_text(encoding="utf-8").splitlines():
            try:nums=tuple(float(x) for x in line.split())
            except ValueError:continue
            if nums:rows.append(nums)
    assert len(rows)==101,("Unexpected data length",len(rows))
    assert all(len(r)==4 and all(math.isfinite(x) for x in r) for r in rows)
    assert abs(rows[0][0]-450000)<1 and abs(rows[-1][0]-460000)<1
    sample=rows[50]
    assert abs(sample[0]-455000)<1,sample
    _,no_extra_load,load10k,load1k=sample
    assert 0<load1k<load10k<no_extra_load,("Not load sensitive",sample)
    assert load1k<0.2*no_extra_load,("1k load unexpectedly negligible",sample)
    assert load10k<0.75*no_extra_load,("10k load unexpectedly negligible",sample)
    print("IF455_DOWNSTREAM_455KHZ_TRANSFER_MAGNITUDES",
          {"baseline_100k":round(no_extra_load,6),
           "plus_10k_shunt":round(load10k,6),
           "plus_1k_shunt":round(load1k,6)},flush=True)
    print("PASS_NGSPICE_IF455_DETECTOR_LOAD_SENSITIVITY_SURROGATES_NOT_DIODE_NO_FAB",flush=True)

if __name__=="__main__":
    main()
