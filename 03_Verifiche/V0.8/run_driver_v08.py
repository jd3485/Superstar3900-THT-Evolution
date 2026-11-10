#!/usr/bin/env python3
"""Actual ngspice executions of a deliberately simplified high-rail opamp model.

Green process != LM358N hardware validation, PLL lock, stability or acceptable
phase noise. Uses synthetic DC filtered phase-detector values, not U401.
"""
from pathlib import Path
import subprocess,json,re
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"03_Verifiche/V0.8/VTUNE_DRIVER_BEHAVIORAL_V0.8.cir"
OUT=ROOT/"03_Verifiche/V0.8/ngspice_results"
PAT=re.compile(r"^\s*(av_vtune|min_vtune|max_vtune|av_filtered)\s*=\s*([+-]?[0-9.]+(?:[Ee][+-]?[0-9]+)?)",re.I|re.M)
CASES=((2.0,19.05,3.0),(2.5,19.05,3.0),(3.75,19.05,3.0),
       (3.75,20.02225,3.0),(4.30,19.05,3.0),(3.75,19.05,4.3))
def execute(pd,rail,headroom):
    s=SOURCE.read_text()
    assert s.count(".param V_CONTROL=2.0")==1 and s.count(".param V_RAIL=20.0")==1
    s=s.replace(".param V_CONTROL=2.0",f".param V_CONTROL={pd}")
    s=s.replace(".param V_RAIL=20.0",f".param V_RAIL={rail}")
    s=s.replace(".param V_HEADROOM=3.0",f".param V_HEADROOM={headroom}")
    key=f"pd{pd}_rail{rail}_room{headroom}".replace(".","p")
    deck=OUT/f"{key}.cir";log=OUT/f"{key}.log"
    deck.write_text(s)
    r=subprocess.run(["ngspice","-b","-o",str(log),str(deck)],capture_output=True,text=True,timeout=60)
    raw=log.read_text(errors="replace") if log.exists() else ""
    vals={k.lower():float(v) for k,v in PAT.findall(raw)}
    ok=r.returncode==0 and len(vals)==4
    row={"pd_filter_dc_v":pd,"rail_v":rail,"headroom_assumption_v":headroom,
         "ngspice_executed":ok,"vtune_avg_v":round(vals.get("av_vtune",0),5) if ok else None,
         "vtune_min_v":round(vals.get("min_vtune",0),5) if ok else None,
         "vtune_max_v":round(vals.get("max_vtune",0),5) if ok else None,
         "model_has_real_LM358N":False,"model_has_real_phase_detector":False,
         "phase_margin_verified":False}
    print("VTUNE_DRIVER_CASE",json.dumps(row,sort_keys=True),flush=True)
    if not ok:
        print("NGSPICE_DIAGNOSTIC",raw[-3500:],flush=True)
        raise RuntimeError("SPICE execution or measures not complete")
    return row
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    rows=[execute(*x) for x in CASES]
    (OUT/"driver_behavioral_summary.json").write_text(json.dumps({
        "notes":"No physical op amp model, no PLL loop, no actual VCO loaded",
        "rows":rows,"tx_authorized":False,"fab_authorized":False},indent=2)+"\n")
    print("DRIVER_SWEEP_COMPLETE",len(rows),"simulation cases, no hardware pass",flush=True)
if __name__=="__main__":
    main()
