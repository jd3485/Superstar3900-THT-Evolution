#!/usr/bin/env python3
"""Inspect the ACTUAL KiCad-exported netlist: no PDF/CSV connectivity guesses.

This validates only the V1.0 isolated THT LM358N driver and tri-state RC sheet.
No simulation of PLL lock, PCB DRC or physical pin inspection is implied.
"""
import json,re,sys
from pathlib import Path

PAT=re.compile(r'"(?:\\.|[^"\\])*"|[()]|[^()\s]+')
def parse_expr(tokens,position=0):
    if position>=len(tokens) or tokens[position]!="(":
        raise ValueError("Expected opening bracket")
    result=[];i=position+1
    while i<len(tokens):
        t=tokens[i]
        if t==")":return result,i+1
        if t=="(":
            sub,i=parse_expr(tokens,i);result.append(sub);continue
        if t.startswith('"'):
            try: result.append(json.loads(t))
            except json.JSONDecodeError:result.append(t.strip('"'))
        else:result.append(t)
        i+=1
    raise ValueError("S-expression unclosed")

def child(node,key):
    for item in node[1:]:
        if isinstance(item,list) and item and item[0]==key:return item
    raise ValueError(f"Missing {key} in {node[0] if node else 'empty'}")

def optional_child(node,key):
    for item in node[1:]:
        if isinstance(item,list) and item and item[0]==key:return item
    return None

def read_nets(path:Path):
    source=path.read_text(encoding="utf8")
    tokens=PAT.findall(source)
    root,end=parse_expr(tokens)
    if end!=len(tokens) or root[0]!="export":
        raise ValueError("Not KiCad CLI netlist")
    result={}
    for net in child(root,"nets")[1:]:
        if not isinstance(net,list) or not net or net[0]!="net":continue
        # KiCad 9 qualifies root-sheet net names as /NET; strip only that leading root slash.
        name=str(child(net,"name")[1]).removeprefix("/")
        nodes=set()
        for n in net[1:]:
            if isinstance(n,list) and n and n[0]=="node":
                nodes.add((str(child(n,"ref")[1]),str(child(n,"pin")[1])))
        if name in result:raise AssertionError(f"Duplicate net {name}")
        result[name]=nodes
    return result

REQUIRED={
 "PLL_PDOUT_3STATE":{("J901","1"),("R901","1")},
 "PD_FILTER":{("R901","2"),("C901","1"),("U803","3")},
 "OPA_OUT_A":{("U803","1"),("R803","1"),("R805","1")},
 "OPA_FB_A":{("U803","2"),("R803","2"),("R804","1")},
 "OPA_OUT_B":{("U803","6"),("U803","7")},
 "VANA20_FILT":{("U803","8"),("J902","1"),("C803","1")},
 "GND":{("U803","4"),("U803","5"),("J901","2"),("J902","2"),("J903","2"),("C901","2"),("R804","2"),("C803","2")},
 "VTUNE_RAIL":{("J903","1"),("R805","2")}
}
def verify(nets):
    errors=[]
    for name,required in REQUIRED.items():
        actual=nets.get(name,set())
        if not required.issubset(actual):
            errors.append(f"{name}: missing {sorted(required-actual)}, actual={sorted(actual)}")
    # Reject any short between independently named positive/ground/reference nodes
    allpins={}
    for net,pins in nets.items():
        for pin in pins:
            if pin in allpins and allpins[pin]!=net:
                errors.append(f"Pin {pin} occurs on both {net} and {allpins[pin]}")
            allpins[pin]=net
    if errors:
        raise AssertionError("KiCad NETLIST CONNECTIVITY FAIL:\n"+"\n".join(errors))
    return {"status":"PASS_NETLIST_PARTIAL_ONLY","net_count":len(nets),
            "validated_nets":{name:sorted(map(list,nets[name])) for name in REQUIRED},
            "supply_and_PDout_external":True,
            "full_PLL_validated":False,"pcb_DRC":"NOT_RUN",
            "physical_RF_verified":False,"tx_authorized":False,"fab_authorized":False}

def main():
    path=Path(sys.argv[1]) if len(sys.argv)>1 else Path(
      "03_Verifiche/V1.0/kicad_results/pll_filter.net")
    nets=read_nets(path);result=verify(nets)
    destination=path.parent/"netlist_connectivity.json"
    destination.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    print(json.dumps({k:v for k,v in result.items() if k!="validated_nets"},sort_keys=True))
if __name__=="__main__":
    main()
