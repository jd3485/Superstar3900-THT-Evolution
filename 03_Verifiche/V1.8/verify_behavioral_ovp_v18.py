#!/usr/bin/env python3
"""Check idealized analog ngspice sample measurements; never claim vendor/hardware OVP qualification."""
import re,sys,json
from pathlib import Path
log=Path(sys.argv[1]).read_text()
def sample(name):
 match=re.search(r"(?mi)^"+name+r"\s*=\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[-+]?\d+)?)",log)
 if not match:raise AssertionError(f"Missing ngspice {name}; log tail: {log[-1200:]}")
 return float(match.group(1))
v={name:sample(name) for name in ("normal_v","ovp_v","hysteresis_hold_v","rearm_v")}
if not (12<v["normal_v"]<14.5):raise AssertionError("Did not turn ON at normal 13.8V")
if not (0<=v["ovp_v"]<0.02):raise AssertionError("Ideal high-side switch not disconnected at sustained 19V")
if not (0<=v["hysteresis_hold_v"]<0.02):raise AssertionError("Ideal hysteresis failed to hold off at 15.5V")
if not (13<v["rearm_v"]<14.5):raise AssertionError("Ideal switch failed to rearm when VIN returned to 14V")
obj={"status":"PASS_IDEAL_BEHAVIORAL_NGSPICE_OVP_ONLY",
"input_schedule":"13.8V normal -> 19V continuous fault -> 15.5V hysteresis hold -> 14.0V re-arm",
"measured_switch_node_v":v,"TI_LM393_vendor_model_used":False,"TL431_vendor_model_used":False,
"Infineon_IRF9540_vendor_model_used":False,"startup_and_inrush":"NOT_SIMULATED",
"safe_for_vehicle":False,"fab_authorized":False,"tx_authorized":False}
Path(sys.argv[1]).parent.joinpath("v18_behavioral_results.json").write_text(json.dumps(obj,indent=2)+"\n")
print(json.dumps(obj))
