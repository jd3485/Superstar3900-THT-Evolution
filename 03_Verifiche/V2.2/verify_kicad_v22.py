#!/usr/bin/env python3
"""KiCad9 native V2.1=>V2.2 exact pin/net equivalence and Bourns L920 footprint metadata gate.
NOT a substitute for RF / mechanical / automotive safety qualification.
"""
from pathlib import Path
import json,runpy,sys
repo=Path(__file__).resolve().parents[2]
helper=runpy.run_path(str(repo/"03_Verifiche/V1.0/verify_kicad_netlist_v10.py"))
read_nets=helper["read_nets"]
before=read_nets(Path(sys.argv[1]))
after=read_nets(Path(sys.argv[2]))
assert len(before)==len(after)==72,(len(before),len(after))
def parts(nets):
    items={}
    for net,pins in nets.items():
        for pin in pins:
            assert pin not in items,("duplicate pin",pin)
            items[pin]=net
    return items
old,new=parts(before),parts(after)
assert set(old)==set(new),("pin list changed",set(old)^set(new))
partitions_old={frozenset(pins) for pins in before.values()}
partitions_new={frozenset(pins) for pins in after.values()}
assert partitions_old==partitions_new,("electrical partitions changed",partitions_old^partitions_new)
for ref,pin in [("L920","1"),("L920","2"),("F701","1"),("F701","2"),("D702","1"),("D702","2"),("U803","8"),("U911","1"),("U912","2")]:
    assert (ref,pin) in new,(ref,pin)
tokens=helper["PAT"].findall(Path(sys.argv[2]).read_text())
ast,end=helper["parse_expr"](tokens)
assert end==len(tokens) and ast[0]=="export"
seen={}
for c in helper["child"](ast,"components")[1:]:
    if not isinstance(c,list) or not c or c[0]!="comp":continue
    ref=str(helper["child"](c,"ref")[1])
    fp=helper["optional_child"](c,"footprint")
    assert ref not in seen,("duplicate ref",ref)
    seen[ref]=str(fp[1]) if fp and len(fp)>1 else ""
assert seen["L920"]=="THT_V22:Inductor_Bourns_RLB0914_681KL_P5.00mm",seen["L920"]
assert seen["F701"].startswith("THT_V21:Fuse_Littelfuse_"),seen["F701"]
assert seen["D702"].startswith("THT_V21:TVS_ST_"),seen["D702"]
missing=sorted(ref for ref,fp in seen.items() if not fp)
assert missing==["L501"],missing
assert len(seen)>=100,len(seen)
assert not {r:p for r,p in seen.items() if any(x in p for x in ("_SMD","Package_QFN","Package_DFN","Package_BGA","Package_SOIC","Package_SOT-23"))}
footprint=repo/"04_KiCad/V2.2/THT_V22.pretty/Inductor_Bourns_RLB0914_681KL_P5.00mm.kicad_mod"
s=footprint.read_text()
assert s.count('(pad "')==2
for x,n in (("-2.5","1"),("2.5","2")):
    assert f'(pad "{n}" thru_hole circle (at {x} 0) (size 2 2) (drill 1.0)' in s,n
assert '(fp_circle (center 0 0) (end 4.6 0)' in s
assert '(fp_circle (center 0 0) (end 5.2 0)' in s
assert '(attr through_hole)' in s
assert 1.0-0.65>=0.30 and (2.0-1.0)/2>=0.45
assert (5.0+0.8)-(5.0-0.8)==1.6
report={"gate":"PASS_V22_NATIVE_PIN_NET_AND_THROUGH_HOLE_FOOTPRINT_METADATA",
        "nets_V21":len(before),"nets_V22":len(after),"all_pin_net_partitions_equal":True,
        "physical_references":len(seen),"footprints_assigned":sum(bool(p) for p in seen.values()),
        "remaining_unqualified_unassigned_footprints":missing,
        "L920_pitch_vendor_nominal_mm":5.0,"L920_pitch_vendor_tolerance_mm":0.8,
        "L920_drill_candidate_mm":1.0,"L920_pad_candidate_mm":2.0,
        "L920_mechanical_assembly_qualified":False,"L920_boost_thermal_EMI_RF_qualified":False,
        "PCB_DRC":"NOT_APPLICABLE_NO_PCB","fab_authorized":False,"tx_authorized":False}
out=Path(sys.argv[2]).parent/"v22_audit_native.json"
out.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,sort_keys=True))
