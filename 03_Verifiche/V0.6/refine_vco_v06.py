#!/usr/bin/env python3
"""Fine L sweep using same real ngspice transient equations as coarse V0.6 study."""
import tempfile,json
from pathlib import Path
import explore_vco_v06 as coarse
L_VALUES=(165.,167.,168.,169.,170.,172.)
def main():
    with tempfile.TemporaryDirectory() as td:
        out=[coarse.analyze((5.,1200,470.,l),Path(td),i) for i,l in enumerate(L_VALUES)]
    dest=coarse.OUTPUT/"inductance_refinement_v06.json"
    dest.write_text(json.dumps({"results":out,"note":"Not hardware and no vendor RF models"},indent=2)+"\n")
    for x in out:print("INDUCTANCE_REFINEMENT",json.dumps(x,sort_keys=True),flush=True)
if __name__=="__main__":main()
