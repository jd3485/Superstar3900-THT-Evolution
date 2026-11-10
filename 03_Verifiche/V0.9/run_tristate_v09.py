#!/usr/bin/env python3
"""Actually execute SPICE models of a THREE-STATE phase-detector *abstraction*.
DO NOT treat these pulses as closed-loop phase lock or verified device leakage.
"""
from pathlib import Path
import subprocess,json,re
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"03_Verifiche/V0.9/PLL_TRISTATE_HOLD_V0.9.cir"
OUT=ROOT/"03_Verifiche/V0.9/tristate_results"
PAT=re.compile(r"^\s*(before_up|after_up|hold_start|hold_end|after_down|vtune_hold_start|vtune_hold_end)\s*=\s*([+-]?[0-9.]+(?:[Ee][+-]?[0-9]+)?)",re.I|re.M)
CURRENTS=(0.,20e-9,100e-9)
def run(i):
    src=SOURCE.read_text()
    assert src.count(".param I_BIAS=20n")==1
    src=src.replace(".param I_BIAS=20n",f".param I_BIAS={i}")
    name=f"bias_{i:.9g}".replace(".","p").replace("-","n")
    deck=OUT/f"{name}.cir";log=OUT/f"{name}.log"
    deck.write_text(src)
    proc=subprocess.run(["ngspice","-b","-o",str(log),str(deck)],cwd=ROOT,capture_output=True,text=True,timeout=70)
    s=log.read_text(errors="replace") if log.exists() else ""
    d={k.lower():float(v) for k,v in PAT.findall(s)}
    if proc.returncode!=0 or len(d)!=7:
        print("MODEL_FAILURE",i,s[-3800:],flush=True)
        raise RuntimeError("ngspice failed or missing measures")
    row={"bias_leakage_assumed_a":i,"before_up_v":d["before_up"],
         "after_up_v":d["after_up"],"hold_start_v":d["hold_start"],"hold_end_v":d["hold_end"],
         "hold_pd_filter_drift_v":d["hold_end"]-d["hold_start"],
         "vtune_hold_start_v":d["vtune_hold_start"],"vtune_hold_end_v":d["vtune_hold_end"],
         "vtune_drift_v":d["vtune_hold_end"]-d["vtune_hold_start"],
         "after_down_v":d["after_down"],
         "is_physical_PLL":False,"vendor_model_used":False}
    print("TRISTATE_MEASUREMENT",json.dumps(row,sort_keys=True),flush=True)
    if not (row["after_up_v"]>row["before_up_v"] and row["after_down_v"]<row["after_up_v"]):
        raise RuntimeError("tri-state pulse model did not respond to both signs")
    return row
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    rows=[run(x) for x in CURRENTS]
    out={"ngspice_executed":True,"tri_state_switches_ideal":True,
         "vco_closed_loop":False,"model_vendor_leakage":False,"hardware_qualified":False,
         "rows":rows,"fabrication_authorized":False,"tx_enabled":False}
    (OUT/"summary.json").write_text(json.dumps(out,indent=2)+"\n")
    print("TRISTATE_SIMULATIONS_DONE",len(rows),flush=True)
if __name__=="__main__":main()
