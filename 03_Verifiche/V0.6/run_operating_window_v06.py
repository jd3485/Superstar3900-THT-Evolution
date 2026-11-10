#!/usr/bin/env python3
"""V0.6 SPICE RX VCO operating window, comparing artificially seeded and real supply ramp startup.
Models are generic; no PCB/TX or measured hardware validation.
"""
from pathlib import Path
import re,subprocess,json
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"03_Verifiche/V0.6/VCO_COLPITTS_REWORKED_V0.6.cir"
OUT=ROOT/"03_Verifiche/V0.6/ngspice_results"
BIASES=(6.0,6.5,7.0,12.0,13.0,14.0,15.0)
RX=re.compile(r"^\s*(t50|t250|max_tank|min_tank|max_out|min_out|max_vara|min_vara)\s*=\s*([+-]?[0-9.]+(?:[Ee][+-]?[0-9]+)?)",re.M|re.I)
def execute(bias,ramped):
    source=SRC.read_text(encoding="utf-8")
    assert source.count(".param VCTRL=5.0")==1
    source=source.replace(".param VCTRL=5.0",f".param VCTRL={bias}")
    if ramped:
        assert source.count("VCC V9 0 DC 5")==1
        source=source.replace("VCC V9 0 DC 5","VCC V9 0 PWL(0 0 100n 5)")
        source="\n".join(line for line in source.splitlines() if not line.startswith(".ic "))
        source=source.replace(".tran 0.5n 25u 0 0.5n uic",".tran 0.5n 40u 0 0.5n")
        measure_start,measure_end="25u","40u"
    else:
        measure_start,measure_end="15u","25u"
    meas=f"""
.measure tran t50 WHEN v(TANK)=5 RISE=50 TD={measure_start}
.measure tran t250 WHEN v(TANK)=5 RISE=250 TD={measure_start}
.measure tran max_tank MAX v(TANK) FROM={measure_start} TO={measure_end}
.measure tran min_tank MIN v(TANK) FROM={measure_start} TO={measure_end}
.measure tran max_out MAX v(LO1_ANALOG_OUT) FROM={measure_start} TO={measure_end}
.measure tran min_out MIN v(LO1_ANALOG_OUT) FROM={measure_start} TO={measure_end}
.measure tran max_vara MAX v(VAR_A) FROM={measure_start} TO={measure_end}
.measure tran min_vara MIN v(VAR_A) FROM={measure_start} TO={measure_end}
"""
    source=source.rstrip()[:-4]+meas+"\n.end\n"
    key=("ramp" if ramped else "seeded")+"_bias"+str(bias).replace(".","p")
    deck=OUT/f"window_{key}.cir";log=OUT/f"window_{key}.log"
    deck.write_text(source)
    run=subprocess.run(["ngspice","-b","-o",str(log),str(deck)],cwd=ROOT,capture_output=True,text=True,timeout=90)
    vals={k.lower():float(v) for k,v in RX.findall(log.read_text(errors="replace"))} if log.exists() else {}
    complete=all(k in vals for k in ("t50","t250","max_tank","min_tank","max_out","min_out","max_vara","min_vara")) and vals.get("t250",0)>vals.get("t50",0)
    row={"startup":("supply_ramp_from_zero" if ramped else "seeded_uic"),"bias_v":bias,
         "ngspice_exit":run.returncode,
         "oscillates_with_measurable_period_in_model":complete,
         "freq_mhz":round(200/(vals["t250"]-vals["t50"])/1e6,5) if complete else None,
         "tank_vpp":round(vals["max_tank"]-vals["min_tank"],4) if complete else None,
         "out_vpp":round(vals["max_out"]-vals["min_out"],4) if complete else None,
         "max_varactor_forward_v":round(vals["max_vara"]-bias,4) if complete else None,
         "diode_kept_reverse":(vals["max_vara"]-bias<=0.05) if complete else False,
         "vendor_model_verified":False,"real_hardware_qualified":False}
    if run.returncode!=0:raise RuntimeError(f"ngspice failed at {key}")
    print("WINDOW",json.dumps(row,sort_keys=True),flush=True)
    return row
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    rows=[execute(v,mode) for mode in (False,True) for v in BIASES]
    summary={"results":rows,
             "note":"Model uses simplified BJTs and varactor; field results and production unqualified",
             "tx_enabled":False,"fab_authorized":False}
    (OUT/"startup_comparison_v06.json").write_text(json.dumps(summary,indent=2)+"\n")
    for mode in ("seeded_uic","supply_ramp_from_zero"):
        selected=[r for r in rows if r["startup"]==mode]
        print("WINDOW_SUMMARY",json.dumps({"startup":mode,
            "periods_found":sum(r["oscillates_with_measurable_period_in_model"] for r in selected),
            "diode_reverse":sum(r["diode_kept_reverse"] for r in selected)},sort_keys=True),flush=True)
if __name__=="__main__": main()
