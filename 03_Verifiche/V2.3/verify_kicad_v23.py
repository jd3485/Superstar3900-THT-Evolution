#!/usr/bin/env python3
"""V2.3 KiCad9 seven-sheet native PIN->NET regression: only L501 metadata changed.
This asserts internal CAD integrity, NOT phase noise, lock, thermal or RF qualification.
"""
from pathlib import Path
import json,runpy,sys,math
root=Path(__file__).resolve().parents[2]
h=runpy.run_path(str(root/"03_Verifiche/V1.0/verify_kicad_netlist_v10.py"))
old=h["read_nets"](Path(sys.argv[1]));new=h["read_nets"](Path(sys.argv[2]))
assert len(old)==len(new)==72,(len(old),len(new))
assert {frozenset(p) for p in old.values()}=={frozenset(p) for p in new.values()},"PIN-NET PARTITIONS CHANGED"
def pins(nets):
 out=set()
 for entries in nets.values():
  for x in entries:
   assert x not in out,x
   out.add(x)
 return out
assert pins(old)==pins(new)
tokens=h["PAT"].findall(Path(sys.argv[2]).read_text())
tree,end=h["parse_expr"](tokens)
assert end==len(tokens) and tree[0]=="export"
parts={}
for comp in h["child"](tree,"components")[1:]:
 if not isinstance(comp,list) or not comp or comp[0]!="comp":continue
 ref=str(h["child"](comp,"ref")[1])
 assert ref not in parts,ref
 fp=h["optional_child"](comp,"footprint")
 parts[ref]=str(fp[1]) if fp and len(fp)>1 else ""
assert len(parts)==129,len(parts)
assert all(parts.values()),[r for r,p in parts.items() if not p]
assert parts["L501"]=="THT_V23:Inductor_Coilcraft_150-05J08L_Uni7_Tunable_THT"
assert parts["L920"].startswith("THT_V22:Inductor_Bourns_")
assert parts["F701"].startswith("THT_V21:Fuse_")
assert parts["D702"].startswith("THT_V21:TVS_")
assert not any(any(y in f for y in ("_SMD","Package_QFN","Package_BGA","Package_DFN","Package_SOIC","Package_SOT-23")) for f in parts.values())
fname=root/"04_KiCad/V2.3/THT_V23.pretty/Inductor_Coilcraft_150-05J08L_Uni7_Tunable_THT.kicad_mod"
s=fname.read_text()
assert '(attr through_hole)' in s and s.count('(pad "')==2
assert '(pad "1" thru_hole circle (at -2.25 -2.25) (size 1.8 1.8) (drill 0.8)' in s
assert '(pad "2" thru_hole circle (at 2.25 2.25) (size 1.8 1.8) (drill 0.8)' in s
assert '(fp_rect (start -3.47 -3.47) (end 3.47 3.47)' in s
# vendor max lead Ø0.56 mm vs candidate drill Ø0.8 mm; annular ring 0.5 mm
assert 0.8-0.56>=0.20 and (1.8-0.8)/2>=0.45
report={"gate":"PASS_V23_NATIVE_PINNET_AND_BOM_129_OF_129_FOOTPRINT_FIELDS",
 "nets_before":72,"nets_after":72,"preserved_all_pin_net_partitions":True,
 "real_references":len(parts),"footprint_fields_assigned":sum(bool(x) for x in parts.values()),
 "Coilcraft_L501_footprint_candidate_only":True,
 "L501_min_adjust_nH":137,"L501_nom_adjust_nH":165,"L501_max_adjust_nH":193,
 "L501_Qmin_50MHz":114,"L501_SRF_min_MHz":650,
 "PCB_exists":False,"PCB_DRC":"NOT_RUN",
 "RF_phase_noise_lock_PVT_hardware_qualified":False,"no_fab":True,"no_tx":True}
Path(sys.argv[2]).parent.joinpath("v23_native_audit.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,sort_keys=True))
