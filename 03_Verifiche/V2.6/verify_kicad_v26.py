#!/usr/bin/env python3
"""V2.5->V2.6 real native KiCad 9 netlist audit. Candidate only."""
from pathlib import Path
import json,runpy,sys
root=Path(__file__).resolve().parents[2]
h=runpy.run_path(str(root/"03_Verifiche/V1.0/verify_kicad_netlist_v10.py"))
old=h["read_nets"](Path(sys.argv[1]));new=h["read_nets"](Path(sys.argv[2]))
assert len(old)==73,(len(old),"v25 baseline")
assert len(new)==76,(len(new),"v26 expected native nets")
moved={("U801","7"),("Q802","1")}
added={(r,str(i)) for r in ("R1014","R1015","R1016","R1017") for i in (1,2)}
added|={("Q803",str(i)) for i in (1,2,3)}
def canon(nets,excluded):return {frozenset(p-excluded) for p in nets.values() if p-excluded}
assert canon(old,moved)==canon(new,moved|added),"Undocumented legacy pin partition migration"
def get(p):
    a=[name for name,members in new.items() if p in members]
    assert len(a)==1,(p,a)
    return a[0]
def same(a,b):assert get(a)==get(b),(a,b,get(a),get(b))
for a,b in [
(("U801","7"),("R1014","2")),(("U801","7"),("R1015","1")),
(("U801","7"),("R1016","1")),(("R1014","1"),("U801","6")),
(("R1015","2"),("U801","5")),(("R1016","2"),("Q803","2")),
(("R1017","1"),("Q803","2")),(("R1017","2"),("Q803","1")),
(("Q802","1"),("Q803","3")),(("Q802","3"),("R1009","2")),
(("U801","1"),("R1007","1"))]:same(a,b)
assert get(("U801","7"))!=get(("U801","1"))
assert get(("Q803","1"))!=get(("Q803","3"))
assert get(("Q803","2"))!=get(("Q803","3"))
tokens=h["PAT"].findall(Path(sys.argv[2]).read_text())
tree,end=h["parse_expr"](tokens);assert end==len(tokens) and tree[0]=="export"
parts={};values={}
for comp in h["child"](tree,"components")[1:]:
    if not isinstance(comp,list) or not comp or comp[0]!="comp":continue
    ref=str(h["child"](comp,"ref")[1]);assert ref not in parts,ref
    fp=h["optional_child"](comp,"footprint")
    parts[ref]=str(fp[1]) if fp and len(fp)>1 else ""
    values[ref]=str(h["child"](comp,"value")[1])
assert len(parts)==138,len(parts)
assert all(parts.values())
for ref in ("R1014","R1015","R1016","R1017"):
    assert parts[ref]=="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal"
assert parts["Q803"]=="Package_TO_SOT_THT:TO-92_Inline"
assert "2N3904" in values["Q803"]
assert all("SMD" not in x for x in parts.values())
result={"gate":"PASS_V26_NATIVE_OVP_UVLO_SEPARATE_GATE_CANDIDATE_ONLY",
"old_net_groups":len(old),"new_net_groups":len(new),
"parts":len(parts),"footprints":len(parts),
"moved":["U801/7","Q802/1"],"added":["Q803","R1014","R1015","R1016","R1017"],
"legacy_partitions_preserved":True,"hardware_qualified":False,
"PCB_DRC":"NOT_RUN_NO_PCB","NO_FAB":True,"NO_TX":True}
Path(sys.argv[2]).parent.joinpath("v26_native_audit.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,sort_keys=True))
