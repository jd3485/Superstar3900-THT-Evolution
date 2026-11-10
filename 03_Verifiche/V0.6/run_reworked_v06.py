#!/usr/bin/env python3
"""Verify V0.6 reworked schematic at 7 VTUNE points using real ngspice transients.
Pass for execution does NOT imply full-band, physical stability or regulatory qualification.
"""
from pathlib import Path
import re,subprocess,json,math
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"03_Verifiche/V0.6/VCO_COLPITTS_REWORKED_V0.6.cir"
OUT=ROOT/"03_Verifiche/V0.6/ngspice_results"
BIASES=(3.5,4.0,5.0,7.0,9.0,11.0,12.0,13.0)
RX=re.compile(r"^\s*(t50|t250|max_tank|min_tank|max_out|min_out|max_vara|min_vara)\s*=\s*([+-]?[0-9.]+(?:[Ee][+-]?[0-9]+)?)",re.I|re.M)
MEAS="""
.measure tran t50 WHEN v(TANK)=5 RISE=50 TD=15u
.measure tran t250 WHEN v(TANK)=5 RISE=250 TD=15u
.measure tran max_vara MAX v(VAR_A) FROM=15u TO=25u
.measure tran min_vara MIN v(VAR_A) FROM=15u TO=25u
"""
def run(v):
    src=SOURCE.read_text()
    assert src.count(".param VCTRL=5.0")==1
    src=src.replace(".param VCTRL=5.0",f".param VCTRL={v}")
    src=src.rstrip()[:-4]+MEAS+"\n.end\n"
    key=str(v).replace(".","p")
    deck=OUT/f"v06_reworked_v{key}.cir";log=OUT/f"v06_reworked_v{key}.log"
    deck.write_text(src)
    run=subprocess.run(["ngspice","-b","-o",str(log),str(deck)],capture_output=True,text=True,timeout=90)
    output=log.read_text(errors="replace") if log.exists() else ""
    val={k.lower():float(z) for k,z in RX.findall(output)}
    complete=all(k in val for k in ("t50","t250","max_tank","min_tank","max_out","min_out","max_vara","min_vara"))
    if not complete or run.returncode!=0:
        print("INCOMPLETE",v,output[-2300:])
        raise RuntimeError("SPICE simulation incomplete or cross threshold not found")
    f=200/(val["t250"]-val["t50"])/1e6
    row={"vtune_v":v,"frequency_mhz_measured":round(f,5),
         "tank_vpp":round(val["max_tank"]-val["min_tank"],4),
         "out_vpp":round(val["max_out"]-val["min_out"],4),
         "max_forward_diode_v":round(val["max_vara"]-v,5),
         "reverse_bias_maintained_in_model":val["max_vara"]-v<=0.05,
         "model_qualified":False,"rx_only":True}
    print("REWORKED",json.dumps(row,sort_keys=True),flush=True)
    return row
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    results=[run(v) for v in BIASES]
    freqs=[x["frequency_mhz_measured"] for x in results]
    safe=all(x["reverse_bias_maintained_in_model"] for x in results)
    cover=min(freqs)<=36.31 and max(freqs)>=39.0
    mon=all(a<b for a,b in zip(freqs,freqs[1:]))
    summary={"results":results,"frequency_coverage_target_model":cover,
             "all_points_reverse_bias_model":safe,
             "frequency_monotonic_in_model":mon,
             "report_RF_gate":"NOT_QUALIFIED_WITHOUT_VENDOR_MODELS_AND_LAB",
             "kicad_erc":"NOT_RUN","tx_enabled":False,"fabrication_authorized":False}
    (OUT/"reworked_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print("REWORKED_SUMMARY",json.dumps({k:v for k,v in summary.items() if k!="results"},sort_keys=True),flush=True)
if __name__=="__main__":main()
