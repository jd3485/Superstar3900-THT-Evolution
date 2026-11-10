#!/usr/bin/env python3
"""Supply-ramp-only RF tuning study; no artificial UIC initial conditions.
16 L/C combinations x five VTUNE points = 80 real ngspice transients.
This is a model exploration, not hardware qualification.
"""
from pathlib import Path
import tempfile,json
import run_operating_window_v06 as w
SOURCE=w.SRC.read_text()
L_NH=(160,162,164,165,166,167,168,170)
CBLOCK_PF=(330,470)
BIASES=(8.,9.,10.,12.,15.)
def main():
    w.OUT.mkdir(parents=True,exist_ok=True)
    out=[]
    with tempfile.TemporaryDirectory() as tmp:
        for L in L_NH:
            for C in CBLOCK_PF:
                deck=Path(tmp)/f"l{L}_cb{C}.cir"
                text=SOURCE.replace("L501 V9 TANK 168n",f"L501 V9 TANK {L}n")
                text=text.replace("C504 TANK VAR_A 470p",f"C504 TANK VAR_A {C}p")
                assert text!=SOURCE or (L==168 and C==470)
                deck.write_text(text)
                w.SRC=deck
                rows=[w.execute(v,True) for v in BIASES]
                exists=all(x["oscillates_with_measurable_period_in_model"] for x in rows)
                fs=[x["freq_mhz"] for x in rows]
                safe=exists and all(x["diode_kept_reverse"] for x in rows)
                covers=exists and fs[0]<=36.310 and fs[-1]>=39.0
                monotonic=exists and all(a<b for a,b in zip(fs,fs[1:]))
                choice=dict(L_nh=L,Cblock_pf=C,biases=rows,
                            startup="supply_ramp_from_zero",
                            reverse_all=safe,covers_target_in_window=covers,
                            monotonic=monotonic,model_only=True,
                            usable_study_candidate=safe and covers and monotonic)
                choice["score"]=round(abs(fs[0]-36.2)+abs(fs[-1]-39.2)+
                    (30 if not safe else 0)+(20 if not covers else 0),4) if exists else 1000
                out.append(choice)
    out.sort(key=lambda x:x["score"])
    (w.OUT/"power_ramp_param_v06.json").write_text(json.dumps({
        "models_not_vendor_verified":True,"NO_FAB":True,"NO_TX":True,
        "number_of_candidates":len(out),"number_of_ngspice_transients":len(out)*len(BIASES),
        "results":out},indent=2)+"\n")
    for i,x in enumerate(out[:8]):
        print("RAMP_CANDIDATE_RANK",i+1,json.dumps(x,sort_keys=True),flush=True)
    print("RAMP_SCAN_SUMMARY",json.dumps({
        "n_variants":len(out),"n_simulations":len(out)*len(BIASES),
        "safe_and_cover":sum(x["usable_study_candidate"] for x in out)},sort_keys=True),flush=True)
if __name__=="__main__":main()
