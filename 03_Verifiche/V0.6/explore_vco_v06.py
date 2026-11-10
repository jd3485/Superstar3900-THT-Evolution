#!/usr/bin/env python3
"""EXPLORATORY SPICE parameter sweep for VCO variants; not an approved circuit.

Parametric guesses DO NOT constitute a BOM or validated electrical design.
Uses actual ngspice transient executions with *approximate* transistor/diode models.
"""
import itertools,json,re,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"03_Verifiche/V0.5/VCO_COLPITTS_CANDIDATE_V0.5.cir"
OUTPUT=ROOT/"03_Verifiche/V0.6/ngspice_results"
OUTPUT.mkdir(parents=True,exist_ok=True)
ORIGINAL=SOURCE.read_text(encoding="utf-8")
BIASES=(3.5,7.0,12.0)
RX=re.compile(r"^\s*(max_tank|min_tank|max_vara|min_vara|t50|t250)\s*=\s*([+-]?[0-9.]+(?:[Ee][+-]?[0-9]+)?)",re.M|re.I)
MES="""
.measure tran t50 WHEN v(TANK)={LEVEL} RISE=50 TD=15u
.measure tran t250 WHEN v(TANK)={LEVEL} RISE=250 TD=15u
.measure tran max_vara MAX v(VAR_A) FROM=15u TO=25u
.measure tran min_vara MIN v(VAR_A) FROM=15u TO=25u
"""
def run(deck_src, supply, bias, tmp, ident):
    text=deck_src.replace(".param VCTRL=5.0",f".param VCTRL={bias}")
    text=text.rstrip()[:-4]+MES.replace("{LEVEL}",str(supply))+"\n.end\n"
    deck=tmp/f"vco_{ident}.cir";log=tmp/f"vco_{ident}.log"
    deck.write_text(text)
    p=subprocess.run(["ngspice","-b","-o",str(log),str(deck)],cwd=ROOT,capture_output=True,text=True,timeout=60)
    c=log.read_text(errors="replace") if log.exists() else ""
    vals={k.lower():float(v) for k,v in RX.findall(c)}
    freq=200/(vals["t250"]-vals["t50"])/1e6 if vals.get("t250",0)>vals.get("t50",0)>0 else None
    p2p=vals["max_tank"]-vals["min_tank"] if "max_tank" in vals and "min_tank" in vals else None
    fwd=vals["max_vara"]-bias if "max_vara" in vals else None
    return {"bias":bias,"freq_mhz":round(freq,5) if freq else None,
            "tank_vpp":round(p2p,4) if p2p is not None else None,
            "diode_forward_v":round(fwd,4) if fwd is not None else None,
            "sim_ok":p.returncode==0 and freq is not None}
def analyze(params,tmp,index):
    supply,emitter,block,lval=params
    src=ORIGINAL
    replacements={
       "VCC V9 0 DC 9":f"VCC V9 0 DC {supply}",
       "R503 EMIT1 0 330":f"R503 EMIT1 0 {emitter}",
       "C504 TANK VAR_A 1n":f"C504 TANK VAR_A {block}p",
       "L501 V9 TANK 150n":f"L501 V9 TANK {lval}n",
    }
    for old,new in replacements.items():
        if src.count(old)!=1:raise ValueError(f"patch missing {old}")
        src=src.replace(old,new)
    rows=[run(src,supply,bias,tmp,f"{index}_{i}") for i,bias in enumerate(BIASES)]
    freqs=[x["freq_mhz"] for x in rows]
    fwd=[x["diode_forward_v"] for x in rows]
    all_ok=all(x["sim_ok"] for x in rows)
    span=freqs[-1]-freqs[0] if all_ok else None
    safe=all_ok and all(x<=0.05 for x in fwd)
    covers=all_ok and min(freqs)<=36.31 and max(freqs)>=39.0
    score=(max(0.,max((x for x in fwd if x is not None),default=1.0)-0.05)*10
           + (abs(freqs[0]-36.31)+abs(freqs[-1]-39.) if all_ok else 100)
           + (2 if not safe else 0)
           + (2 if all_ok and span<0.3 else 0))
    return {"supply_v":supply,"emitter_ohm":emitter,"block_pf":block,"inductor_nh":lval,
            "observations":rows,"frequency_span_mhz":round(span,4) if span else None,
            "reverse_bias_no_forward_in_model":safe,"covers_target_in_model":covers,
            "score_for_ranking":round(score,4),"hardware_qualified":False}
def main():
    # 2*2*3*3 = 36 candidate combinations; 108 true transient simulations.
    combos=list(itertools.product([5.,7.],[680,1200],[100.,220.,470.],[150.,180.,220.]))
    with tempfile.TemporaryDirectory() as td:
        tmp=Path(td)
        results=[analyze(par,tmp,i) for i,par in enumerate(combos)]
    results.sort(key=lambda x:x["score_for_ranking"])
    (OUTPUT/"parameter_exploration_v06.json").write_text(json.dumps(
         {"note":"Exploratory numerical device models; NOT a component approval, NO FAB, NO TX",
          "n_candidates":len(results),"n_transients":3*len(results),
          "results":results},indent=2)+"\n")
    for i,item in enumerate(results[:12]):
        print("CANDIDATE_RANK",i+1,json.dumps(item,sort_keys=True),flush=True)
    print("PARAMETER_EXPLORATION_COMPLETE",len(results),"candidates,",
          3*len(results),"transient simulations, safe_variants",
          sum(r["reverse_bias_no_forward_in_model"] for r in results),flush=True)
if __name__=="__main__":main()
