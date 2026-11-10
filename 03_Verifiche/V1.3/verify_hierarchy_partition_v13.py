#!/usr/bin/env python3
"""KiCad 9 exhaustive partition equivalence of EVERY component pin V1.2 -> V1.3."""
import json,runpy,sys
from pathlib import Path
repo=Path(__file__).resolve().parents[2]
lib=runpy.run_path(str(repo/"03_Verifiche/V1.0/verify_kicad_netlist_v10.py"))
old=lib["read_nets"](Path(sys.argv[1]));new=lib["read_nets"](Path(sys.argv[2]))
part=lambda n:{frozenset(v) for v in n.values() if v}
if len(old)!=33 or len(new)!=33 or part(old)!=part(new):
    lost=part(old)-part(new);gain=part(new)-part(old)
    raise AssertionError("NON-EQUIVALENT FULL PIN NETLIST "+repr((len(old),len(new)))+
      " lost="+repr([sorted(x) for x in lost])+" gained="+repr([sorted(x) for x in gain]))
p={pin:net for net,pins in new.items() for pin in pins}
def joined(*pins):
    n={p.get(i) for i in pins}
    if len(n)!=1 or None in n:raise AssertionError("Pins not connected: "+repr(pins)+" => "+repr(n))
joined(("U401","4"),("R901","1"),("J401","1"),("J901","1"))
joined(("R901","2"),("C901","1"),("U803","3"))
joined(("U401","2"),("U402","7"),("U803","4"),("J901","2"))
for a,b in [(("U401","4"),("U803","3")),(("U401","3"),("U803","8")),(("U803","4"),("U803","8"))]:
    if p.get(a)==p.get(b):raise AssertionError("Short: "+repr((a,b)))
for ref,n in (("U401",28),("U402",14),("U803",8)):
    if len([i for i in p if i[0]==ref])!=n:raise AssertionError("Missing KiCad pins "+ref)
source=Path(sys.argv[2]).read_text()
ast,pos=lib["parse_expr"](lib["PAT"].findall(source))
sheetpaths={}
for comp in lib["child"](ast,"components")[1:]:
    if not isinstance(comp,list) or not comp or comp[0]!="comp":continue
    sp=lib["optional_child"](comp,"sheetpath")
    if sp is None:continue
    names=lib["optional_child"](sp,"names")
    sheetpaths[str(lib["child"](comp,"ref")[1])]=str(names[1]) if names is not None else str(sp)
if not sheetpaths.get("U401") or not sheetpaths.get("U803") or sheetpaths["U401"]==sheetpaths["U803"]:
    raise AssertionError("Not 2 distinct native KiCad child sheetpaths: "+repr(sheetpaths))
result={"status":"PASS_ALL_PIN_HIERARCHICAL_EQUIVALENCE","old_nets":len(old),"new_nets":len(new),
        "all_pin_groups_unchanged":True,"different_child_sheetpaths":True,
        "U401_pin4_to_R901_pin1":True,"ground_cross_sheet":True,
        "VCO":"NOT_INTEGRATED","PCB_DRC":"NOT_RUN","RF_lab":"NOT_RUN","fab_authorized":False,"tx_authorized":False}
Path(sys.argv[2]).parent.joinpath("hierarchy_evidence.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,sort_keys=True))
