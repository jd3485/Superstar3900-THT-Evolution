#!/usr/bin/env python3
"""V0.9 ngspice: explicit UP/DOWN/HOLD tri-state source with real passive R/C.

Not ML145151 macro model; no VCO, PFD feedback, lock capture, phase margin or
RF phase noise. A green run is only an execution of this surrogate.
"""
from pathlib import Path
import json,re,subprocess
ROOT=Path(__file__).resolve().parents[2]
DECK=ROOT/"03_Verifiche/V0.9/PDOUT_TRISTATE_SURROGATE_V0.9.cir"
OUT=ROOT/"03_Verifiche/V0.9/ngspice_results"
RX=re.compile(r"^\s*(before_pulse|after_first|final_voltage|min_filter|max_filter)\s*=\s*([+-]?[0-9.]+(?:[Ee][+-]?[0-9]+)?)",re.I|re.M)
CASES=[("UP",1,0,10000),("DOWN",0,1,10000),("HOLD",0,0,10000),
       ("UP",1,0,47000),("DOWN",0,1,47000),("HOLD",0,0,47000)]
def measure(mode,up,dn,resistor):
    src=DECK.read_text()
    for old,new in ((".param UP_ACTIVE=1",f".param UP_ACTIVE={up}"),
                    (".param DN_ACTIVE=0",f".param DN_ACTIVE={dn}"),
                    (".param R_FILTER=10000",f".param R_FILTER={resistor}")):
        assert old in src
        src=src.replace(old,new)
    code=f"{mode.lower()}_r{resistor}"
    script=OUT/f"{code}.cir";log=OUT/f"{code}.log"
    script.write_text(src)
    run=subprocess.run(["ngspice","-b","-o",str(log),str(script)],cwd=ROOT,capture_output=True,text=True,timeout=60)
    output=log.read_text(errors="replace") if log.exists() else ""
    vals={k.lower():float(v) for k,v in RX.findall(output)}
    if run.returncode!=0 or len(vals)!=5:
        print("SPICE_ERROR",code,output[-3000:],flush=True)
        raise RuntimeError(f"SPICE incomplete for {code}")
    row={"mode":mode,"r_filter_ohm":resistor,
         "before_v":round(vals["before_pulse"],7),
         "after_first_v":round(vals["after_first"],7),
         "final_v":round(vals["final_voltage"],7),
         "min_v":round(vals["min_filter"],7),"max_v":round(vals["max_filter"],7),
         "high_impedance_in_hold":mode=="HOLD",
         "vendor_PFD_model":False,"closed_loop_pll":False}
    print("PFD_SURROGATE",json.dumps(row,sort_keys=True),flush=True)
    return row
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    results=[measure(*case) for case in CASES]
    lookup={(r["mode"],r["r_filter_ohm"]):r for r in results}
    for ohms in (10000,47000):
        up=lookup["UP",ohms];down=lookup["DOWN",ohms];hold=lookup["HOLD",ohms]
        if not (up["after_first_v"]>up["before_v"] and
                down["after_first_v"]<down["before_v"] and
                abs(hold["after_first_v"]-hold["before_v"])<0.002):
            raise RuntimeError("PFD three-state charge response differs from intended sign/hold")
    payload={"status":"SURROGATE_ONLY","measures":results,
             "actual_phase_detector_implemented":False,
             "PLL_loop_stability_verified":False,"phase_noise_verified":False,
             "fabrication_authorized":False,"tx_authorized":False}
    (OUT/"tristate_results.json").write_text(json.dumps(payload,indent=2)+"\n")
    print("PFD_TRISTATE_SURROGATE_COMPLETE",len(results),"ngspice cases",flush=True)
if __name__=="__main__":main()
