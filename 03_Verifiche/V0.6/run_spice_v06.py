#!/usr/bin/env python3
"""ngspice V0.6 sweep of the *unchanged* historical V0.5 candidate.

It executes a circuit-level transient for each VTUNE bias and records measured
node excursions and oscillation frequency from 200 rising threshold crossings.
Results are provisional: all vendor transistor/varactor models are approximate.
It does NOT prove a stable PLL, RF specifications or suitability for fabrication.
"""
from pathlib import Path
import json, os, re, subprocess, sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "03_Verifiche/V0.5/VCO_COLPITTS_CANDIDATE_V0.5.cir"
OUT = ROOT / "03_Verifiche/V0.6/ngspice_results"
BIASES=(3.2,5.0,7.5)
MEASURES = """
.measure tran t50 WHEN v(TANK)=9 RISE=50 TD=15u
.measure tran t250 WHEN v(TANK)=9 RISE=250 TD=15u
.measure tran max_vara MAX v(VAR_A) FROM=15u TO=25u
.measure tran min_vara MIN v(VAR_A) FROM=15u TO=25u
"""
RX = re.compile(r"^\s*(max_tank|min_tank|max_out|min_out|t50|t250|max_vara|min_vara)\s*=\s*([+-]?[0-9.]+(?:[Ee][+-]?[0-9]+)?)",re.M|re.I)
def simulate(v):
    orig = SOURCE.read_text(encoding="utf-8")
    assert orig.count(".param VCTRL=5.0")==1 and orig.rstrip().endswith(".end")
    text = orig.replace(".param VCTRL=5.0",f".param VCTRL={v}")
    text=text.rstrip()[:-4]+MEASURES+"\n.end\n"
    deck=OUT/f"v05_vtune_{str(v).replace('.','p')}.cir"
    log=OUT/f"v05_vtune_{str(v).replace('.','p')}.log"
    deck.write_text(text,encoding="utf-8")
    result=subprocess.run(["ngspice","-b","-o",str(log),str(deck)],cwd=ROOT,capture_output=True,text=True,timeout=90)
    data=log.read_text(errors="replace") if log.exists() else ""
    vals={k.lower():float(z) for k,z in RX.findall(data)}
    crosses=vals.get("t250",0)>vals.get("t50",0)>0
    freq_mhz=200/(vals["t250"]-vals["t50"])/1e6 if crosses else None
    observed_all=all(k in vals for k in ("max_tank","min_tank","max_out","min_out","max_vara","min_vara"))
    row={"vtune_v":v,"ngspice_exit":result.returncode,
         "frequency_mhz_measured":round(freq_mhz,5) if freq_mhz else None,
         "tank_vpp":round(vals["max_tank"]-vals["min_tank"],5) if observed_all else None,
         "buffer_vpp":round(vals["max_out"]-vals["min_out"],5) if observed_all else None,
         "max_diode_forward_v":round(vals["max_vara"]-v,5) if "max_vara" in vals else None,
         "min_diode_reverse_v":round(vals["min_vara"]-v,5) if "min_vara" in vals else None,
         "simulation_metrics_complete":observed_all and crosses,
         "model_qualified":False,
         "electrical_RF_gate": ("FAIL_VARACTOR_FORWARD_IN_MODEL" if vals.get("max_vara",float("-inf")) -v>0.3 else "NOT_QUALIFIED")}
    print("BENCH",json.dumps(row,sort_keys=True),flush=True)
    if result.returncode or not observed_all:
        print("NGSPICE OUTPUT",data[-5000:],flush=True)
        raise RuntimeError("ngspice execution/measurement error")
    return row
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    info=subprocess.run(["ngspice","--version"],capture_output=True,text=True)
    rows=[simulate(v) for v in BIASES]
    summary={"source_commit_baseline":"V0.5","ngspice_version":(info.stdout+info.stderr).strip().splitlines()[:3],
             "observations":rows,"source":"historical candidate model, not vendor models",
             "kicad_erc":"NOT_RUN","lab_measurements":"NOT_RUN","tx_enabled":False,
             "fabrication_authorized":False}
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("SIMULATION_COMPLETE",len(rows),"V0.5 original test biases",flush=True)
if __name__=="__main__":
    main()
