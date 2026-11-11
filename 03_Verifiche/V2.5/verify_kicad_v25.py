#!/usr/bin/env python3
"""Native KiCad 9 seven-sheet netlist comparison V2.4 to V2.5, no synthetic nets."""
from pathlib import Path
import json,runpy,sys
root=Path(__file__).resolve().parents[2]
h=runpy.run_path(str(root/"03_Verifiche/V1.0/verify_kicad_netlist_v10.py"))
old=h["read_nets"](Path(sys.argv[1]));new=h["read_nets"](Path(sys.argv[2]))
assert len(old)==73,len(old)
# One pre-existing isolated NC pin7 net joins CMP_OUT; new UVLO_SENSE net is created.
assert len(new)==73,(len(new),"Unexpected actual V2.5 net count")
moved={("U801","5"),("U801","7")}
added={("R1012","1"),("R1012","2"),("R1013","1"),("R1013","2")}
def canon(nets,exclude):
    return {frozenset(net-exclude) for net in nets.values() if net-exclude}
assert canon(old,moved)==canon(new,moved|added),"Undocumented old pin partition change"
def net_of(nets,pin):
    match=[name for name,pins in nets.items() if pin in pins]
    assert len(match)==1,(pin,match)
    return match[0]
def same(a,b):
    assert net_of(new,a)==net_of(new,b),(a,b)
same(("R1012","1"),("R1002","1"))
same(("R1012","2"),("R1013","1"))
same(("R1012","2"),("U801","5"))
same(("R1013","2"),("U801","4"))
same(("U801","6"),("U802","1"))
same(("U801","7"),("U801","1"))
same(("U801","7"),("R1007","1"))
assert net_of(new,("U801","5"))!=net_of(new,("U801","6"))
tokens=h["PAT"].findall(Path(sys.argv[2]).read_text())
tree,end=h["parse_expr"](tokens);assert end==len(tokens) and tree[0]=="export"
parts={};values={}
for comp in h["child"](tree,"components")[1:]:
    if not isinstance(comp,list) or not comp or comp[0]!="comp":continue
    ref=str(h["child"](comp,"ref")[1]);assert ref not in parts,ref
    fp=h["optional_child"](comp,"footprint")
    parts[ref]=str(fp[1]) if fp and len(fp)>1 else ""
    values[ref]=str(h["child"](comp,"value")[1])
assert len(parts)==133,len(parts)
assert all(parts.values()),[r for r,fp in parts.items() if not fp]
for ref in ("R1012","R1013"):
    assert parts[ref]=="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal"
assert "1K8" in values["R1001"],values["R1001"]
assert "36K" in values["R1012"] and "10K" in values["R1013"]
assert parts["D806"]=="Diode_THT:D_DO-201_P15.24mm_Horizontal"
assert parts["R1011"]=="Resistor_THT:R_Axial_DIN0617_L17.0mm_D6.0mm_P25.40mm_Horizontal"
assert all("SMD" not in fp for fp in parts.values())
report={"gate":"PASS_V25_NATIVE_UVLO_LM393_OC_WINDOW_TOPOLOGY_ONLY",
"old_nets":len(old),"new_nets":len(new),"component_count":len(parts),
"footprint_fields":len(parts),"moved_pins":["U801/5","U801/7"],
"old_pin_partitions_preserved_except_moved":True,
"fault_tolerant_qualified":False,"PCB_DRC":"NOT_RUN_NO_PCB",
"NO_FAB":True,"NO_TX":True}
Path(sys.argv[2]).parent.joinpath("v25_native_audit.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,sort_keys=True))
