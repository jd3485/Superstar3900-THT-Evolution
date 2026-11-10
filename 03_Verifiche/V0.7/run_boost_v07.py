#!/usr/bin/env python3
"""Execute REAL ngspice on a BEHAVIORAL BOOST ONLY (not an MC34063 SPICE macro-model).

The script reports bias, swing and limitations. A green CI proves simulator
execution/observations, not the suitability of the boost nor VCO RF noise.
"""
from pathlib import Path
import subprocess,re,json
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"03_Verifiche/V0.7/BOOST_THT_BEHAVIORAL_V0.7.cir"
OUT=ROOT/"03_Verifiche/V0.7/ngspice_results"
RX=re.compile(r"^\s*(avg_boost|min_boost|max_boost|avg_input)\s*=\s*([+-]?[0-9.]+(?:[Ee][+-]?[0-9]+)?)",re.M|re.I)
def simulate(v):
    src=SRC.read_text()
    assert src.count(".param V_SOURCE=11.0")==1
    src=src.replace(".param V_SOURCE=11.0",f".param V_SOURCE={v}")
    key=str(v).replace(".","p")
    deck=OUT/f"boost_vin_{key}.cir";log=OUT/f"boost_vin_{key}.log"
    deck.write_text(src)
    p=subprocess.run(["ngspice","-b","-o",str(log),str(deck)],cwd=ROOT,capture_output=True,text=True,timeout=90)
    output=log.read_text(errors="replace") if log.exists() else ""
    vals={k.lower():float(z) for k,z in RX.findall(output)}
    good=p.returncode==0 and len(vals)==4
    row={"vin_set_v":v,"ngspice_returncode":p.returncode,
         "data_complete":good,"avg_boost_v":round(vals.get("avg_boost",0),4) if good else None,
         "min_boost_v":round(vals.get("min_boost",0),4) if good else None,
         "max_boost_v":round(vals.get("max_boost",0),4) if good else None,
         "avg_input_v":round(vals.get("avg_input",0),4) if good else None,
         "real_mc34063_device_model":False,"real_lm317_model":False,"noise_qualified":False}
    print("BOOST_BEHAVIORAL",json.dumps(row,sort_keys=True),flush=True)
    if not good:
        print("NGSPICE_DIAGNOSTICS",output[-4500:],flush=True)
        raise RuntimeError("ngspice not executed or measures incomplete")
    return row
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    rows=[simulate(v) for v in (11.,13.8,15.5)]
    evidence={"model":"ideal switch and feedback, NOT IC macro-model", "software":"ngspice",
              "observations":rows,"all_executed":True,
              "output_regulation_authorized":False,"rf_noise_qualified":False,
              "tx_enabled":False,"fabrication_authorized":False}
    (OUT/"boost_behavioral_summary.json").write_text(json.dumps(evidence,indent=2)+"\n")
    print("BOOST_SUMMARY",json.dumps({k:v for k,v in evidence.items() if k!="observations"},sort_keys=True),flush=True)
if __name__=="__main__":main()
