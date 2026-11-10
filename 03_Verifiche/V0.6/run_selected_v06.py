#!/usr/bin/env python3
"""ngspice test of selected V0.6 candidate B, with realistic VCC ramp.
Produces traceable measured frequency, RF swing and varactor voltage limits.
This is a SIMULATION, not vendor/device proof, not KiCad validation nor PCB release.
"""
import re,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DECK=ROOT/"03_Verifiche/V0.6/VCO_COLPITTS_CANDIDATE_B_V0.6.cir"
OUT=ROOT/"03_Verifiche/V0.6/ngspice_results"
BIASES=(8.,9.,10.,12.,15.)
MEAS="""
.measure tran t50 WHEN v(TANK)=5 RISE=50 TD=25u
.measure tran t250 WHEN v(TANK)=5 RISE=250 TD=25u
.measure tran max_vara MAX v(VAR_A) FROM=25u TO=40u
.measure tran min_vara MIN v(VAR_A) FROM=25u TO=40u
"""
RX=re.compile(r"^\s*(max_tank|min_tank|max_out|min_out|max_vara|min_vara|t50|t250)\s*=\s*([+-]?[0-9.]+(?:[Ee][+-]?[0-9]+)?)",re.I|re.M)
def run(v):
    src=DECK.read_text()
    assert src.count(".param VCTRL=8.0")==1 and "uic" not in src.lower() and ".ic " not in src
    assert "PWL(0 0 100n 5)" in src
    src=src.replace(".param VCTRL=8.0",f".param VCTRL={v}")
    src=src.rstrip()[:-4]+MEAS+"\n.end\n"
    key=str(v).replace(".","p")
    deck=OUT/f"candidate_b_v{key}.cir";log=OUT/f"candidate_b_v{key}.log"
    deck.write_text(src)
    r=subprocess.run(["ngspice","-b","-o",str(log),str(deck)],capture_output=True,text=True,timeout=90)
    output=log.read_text(errors="replace") if log.exists() else ""
    val={name.lower():float(z) for name,z in RX.findall(output)}
    if r.returncode or not all(n in val for n in ("t50","t250","max_tank","min_tank","max_out","min_out","max_vara","min_vara")):
        print("SPICE_DIAGNOSTICS",v,output[-2500:])
        raise RuntimeError(f"ngspice failed or did not oscillate at VTUNE {v}")
    f=200/(val["t250"]-val["t50"])/1e6
    maxforward=val["max_vara"]-v
    maxreverse=v-val["min_vara"]
    return {"vtune_v":v,"frequency_mhz":round(f,5),"tank_vpp":round(val["max_tank"]-val["min_tank"],4),
            "output_vpp":round(val["max_out"]-val["min_out"],4),
            "max_forward_voltage_v":round(maxforward,5),
            "max_reverse_voltage_v":round(maxreverse,5),
            "reverse_bias_maintained_model":maxforward<=0,
            "varicap_under_30v_reverse_model":maxreverse<30,
            "model_only":True,"tx_enabled":False}
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    res=[run(v) for v in BIASES]
    for x in res:print("SELECTED_V06",json.dumps(x,sort_keys=True),flush=True)
    f=[x["frequency_mhz"] for x in res]
    result={"variant":"CANDIDATE_B_L166nH_Cblock470p_Remit1200_VCC5",
            "simulation_version":"ngspice on runner",
            "supply_ramp":True,"artificial_IC":False,
            "covers_target_band_in_sampled_model":f[0]<36.310 and f[-1]>39.000,
            "reverse_bias_all_samples":all(x["reverse_bias_maintained_model"] for x in res),
            "under_30v_reverse_all_samples":all(x["varicap_under_30v_reverse_model"] for x in res),
            "frequency_monotonic_samples":all(a<b for a,b in zip(f,f[1:])),
            "vendor_model_qualified":False,"hardware_qualified":False,
            "tx_enabled":False,"pcb_release":False,
            "observations":res}
    print("SELECTED_V06_RESULT",json.dumps({k:v for k,v in result.items() if k!="observations"},sort_keys=True),flush=True)
    (OUT/"candidate_b_summary.json").write_text(json.dumps(result,indent=2)+"\n")
if __name__=="__main__":main()
