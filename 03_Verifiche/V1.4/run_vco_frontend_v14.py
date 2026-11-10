#!/usr/bin/env python3
"""Execute actual ngspice loaded VCO candidate at 8,10,12,15V (not vendor/hardware qualification).
Do not infer phase noise, AC14 logic function, guaranteed lock, fabrication or transmission.
"""
from pathlib import Path
import json,re,subprocess,sys
base=Path(__file__).with_name("VCO_B_LOBUF_INPUT_LOAD_V1.4.cir")
raw=base.read_text()
if ".param VCTRL=8.0" not in raw:raise ValueError("Unexpected V0.6 model parameter baseline")
dest=Path(sys.argv[1]) if len(sys.argv)>1 else Path("03_Verifiche/V1.4/ngspice_results")
dest.mkdir(parents=True,exist_ok=True)
wanted=("v14_buf_high","v14_buf_low","v14_varactor_a_minus_k_max","v14_analog_lo_high","v14_analog_lo_low")
rows=[]
for tune in (8,10,12,15):
    deck=dest/f"vco_v14_{tune}V.cir"
    deck.write_text(raw.replace(".param VCTRL=8.0",f".param VCTRL={tune}.0"))
    logfile=dest/f"vco_v14_{tune}V.log"
    result=subprocess.run(["ngspice","-b","-o",str(logfile),str(deck)],capture_output=True,text=True,timeout=115)
    if result.returncode:
        raise RuntimeError(f"ngspice failed {tune}V: {result.stderr[-2000:]} ; log {logfile.read_text()[-2000:]}")
    log=logfile.read_text()
    vals={}
    for key in wanted:
        match=re.search(r"(?im)^\s*"+re.escape(key)+r"\s*=\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?)",log)
        if not match:raise RuntimeError(f"Missing ngspice measurement {key} at {tune}V: {log[-2200:]}")
        vals[key]=float(match.group(1))
    if vals["v14_buf_high"]<=vals["v14_buf_low"] or vals["v14_analog_lo_high"]<=vals["v14_analog_lo_low"]:
        raise RuntimeError(f"Invalid measured waveform extrema: {vals}")
    rows.append({"vtune_v":tune,**vals,
                 "varactor_reverse_polarity_in_model":vals["v14_varactor_a_minus_k_max"]<0,
                 "ac14_input_not_guaranteed":True})
screen=all(r["varactor_reverse_polarity_in_model"] for r in rows)
proof={"status":"SPICE_LOADED_VCO_CANDIDATE_EXECUTED",
       "ngspice_electrical_screening_all_tested_varactors_in_reverse":screen,
       "candidate_scope":"V0.6 Colpitts plus *assumed* AC14 analog input load, NOT a logic device model",
       "measured_points":rows,"phase_noise":"NOT_RUN","buffer_digital_39MHz":"NOT_SIMULATED",
       "pll_lock":"NOT_RUN","pcb_drc":"NOT_RUN","vendor_model":"NOT_USED",
       "fab_authorized":False,"tx_authorized":False}
(dest/"v14_frontend_load_evidence.json").write_text(json.dumps(proof,indent=2)+"\n")
print(json.dumps({k:v for k,v in proof.items() if k!="measured_points"}))
