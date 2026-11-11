#!/usr/bin/env python3
"""Native KiCad9 7 sheet electrical migration V2.3->V2.4, no synthetic netlist.
Only D804/1 and R1002/1 move; add R1011 + D806. CAD-only evidence."""
from pathlib import Path
import json,runpy,sys
root=Path(__file__).resolve().parents[2]
h=runpy.run_path(str(root/"03_Verifiche/V1.0/verify_kicad_netlist_v10.py"))
old=h["read_nets"](Path(sys.argv[1]));new=h["read_nets"](Path(sys.argv[2]))
assert len(old)==72,len(old)
assert len(new)==73,len(new)
move={("D804","1"),("R1002","1")}
addition={("R1011","1"),("R1011","2"),("D806","1"),("D806","2")}
def canon(net,exclude):
 return {frozenset(n-exclude) for n in net.values() if n-exclude}
assert canon(old,move)==canon(new,move|addition),"NON-MIGRATED PIN CONNECTIVITY CHANGED"
def net_of(net,pin):
 matches=[(label,p) for label,p in net.items() if pin in p]
 assert len(matches)==1,(pin,matches)
 return matches[0]
def same(a,b):
 assert net_of(new,a)[0]==net_of(new,b)[0],(a,b)
same(("D804","1"),("R1011","1"))
same(("R1011","2"),("U801","8"))
same(("D806","1"),("U801","8"))
same(("D806","2"),("U801","4"))
same(("R1002","1"),("D804","2"))
assert net_of(new,("D804","1"))[0]!=net_of(new,("U801","8"))[0]
assert net_of(new,("R1002","1"))[0]!=net_of(new,("U801","8"))[0]
tokens=h["PAT"].findall(Path(sys.argv[2]).read_text())
tree,end=h["parse_expr"](tokens)
assert end==len(tokens) and tree[0]=="export"
parts={}
for comp in h["child"](tree,"components")[1:]:
 if not isinstance(comp,list) or not comp or comp[0]!="comp":continue
 ref=str(h["child"](comp,"ref")[1])
 fp=h["optional_child"](comp,"footprint")
 assert ref not in parts,ref
 parts[ref]=str(fp[1]) if fp and len(fp)>1 else ""
assert len(parts)==131,len(parts)
assert all(parts.values()),[k for k,v in parts.items() if not v]
assert parts["D806"]=="Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal"
assert parts["R1011"]=="Resistor_THT:R_Axial_DIN0411_L11.9mm_D4.5mm_P15.24mm_Horizontal"
assert parts["L501"].startswith("THT_V23:") and parts["L920"].startswith("THT_V22:")
assert all("SMD" not in f for f in parts.values())
report={"gate":"PASS_V24_NATIVE_73_PINNET_MIGRATION","old_nets":len(old),"new_nets":len(new),"unchanged_partitions_exact_except_documented_pins":True,"component_fields":len(parts),"assigned_footprint_fields":sum(bool(f) for f in parts.values()),"R1011_D806_THT_metadata_candidate":True,"LAB_AND_HARDWARE_QUALIFIED":False,"NO_FAB":True,"NO_TX":True,"PCB_DRC":"NOT_APPLICABLE_NO_PCB"}
Path(sys.argv[2]).parent.joinpath("v24_native_audit.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,sort_keys=True))
