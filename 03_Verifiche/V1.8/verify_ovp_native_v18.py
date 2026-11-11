#!/usr/bin/env python3
"""V1.8 native KiCad9: exact old pin partitions + only D701/2 re-routed through Q801.
Never conflate ERC/continuity with functional OVP, fault energy or production authorization.
"""
import json,runpy,sys
from pathlib import Path
repo=Path(__file__).resolve().parents[2]
read=runpy.run_path(str(repo/"03_Verifiche/V1.0/verify_kicad_netlist_v10.py"))["read_nets"]
old=read(Path(sys.argv[1]));new=read(Path(sys.argv[2]))
if len(old)!=54:raise AssertionError(f"V1.7 baseline expected 54 native nets: {len(old)}")
if len(new)!=62:raise AssertionError(f"V1.8 expected 62 native nets: {len(new)}")
where={}
for net,members in new.items():
 for pin in members:
  if pin in where:raise AssertionError(f"Duplicate component pin {pin}")
  where[pin]=net
def group(name,*pins):
 matches={where.get(x) for x in pins}
 if len(matches)!=1 or None in matches:raise AssertionError(f"{name}: {pins}: {matches}")
 return next(iter(matches))
preserved={}
for prior,members in old.items():
 members=members-{("D701","2")} # sole intentional partition change, now after high-side PFET
 if not members:raise AssertionError(f"Unexpected empty legacy net after D701 split: {prior}")
 nets={where.get(p) for p in members}
 if len(nets)!=1 or None in nets:raise AssertionError(f"Legacy V1.7 net split/lost: {prior} -> {nets}")
 now=next(iter(nets))
 if now in preserved:raise AssertionError(f"Two original nets shorted: {prior} and {preserved[now]}")
 preserved[now]=prior
raw=group("13.8V raw",("J701","1"),("F701","1"))
fused=group("Pre-switch fused raw and sensed supply",("F701","2"),("D702","1"),("Q801","3"),
   ("U801","8"),("R1001","1"),("R1002","1"),("R1008","1"),("D803","1"))
sw=group("P-channel drain to D701 anode",("Q801","2"),("D701","2"))
prot=group("D701 cathode to original 7805 input",("D701","1"),("U601","1"),("C600","1"))
gnd=group("GND",("D702","2"),("Q802","1"),("U801","4"),("U801","5"),("U802","2"),
    ("R1003","2"),("R1010","2"),("U601","2"),("U401","2"))
sense=group("Comparator divider node",("R1002","2"),("R1003","1"),("U801","2"))
vref=group("TL431BCLP TO92 K1 REF3",("U802","1"),("U802","3"),("R1001","2"),
    ("R1004","1"),("R1006","1"),("U801","6"))
positive=group("LM393 + input feedback node",("R1004","2"),("R1005","2"),("U801","3"))
cmpout=group("LM393 A open collector output",("R1005","1"),("R1006","2"),("R1007","1"),("U801","1"))
qbase=group("2N3904 base",("Q802","2"),("R1007","2"),("R1010","1"))
gateSink=group("Q802 collector",("Q802","3"),("R1009","2"))
gate=group("IRF9540 gate to 12V zener anode",("Q801","1"),("D803","2"),("R1008","2"),("R1009","1"))
five=group("5V regulated prior",("U601","3"),("R611","1"),("R612","1"),("R613","1"))
pll=group("PLL 5V branch",("R611","2"),("U401","3"))
vco=group("VCO 5V branch",("R612","2"),("L501","1"))
lo=group("LO buffer 5V branch",("R613","2"),("U520","14"))
allgroups={raw,fused,sw,prot,gnd,sense,vref,positive,cmpout,qbase,gateSink,gate,five,pll,vco,lo}
if len(allgroups)!=16:raise AssertionError("Unexpected OVP/reverse/shunt rail short")
if ("U801","7") in where:raise AssertionError("Unused LM393 channel B output must be NC")
group("Legacy VTUNE unaffected",("R805","2"),("D501","2"))
group("Legacy LO buffered clock unaffected",("U402","3"),("R513","2"))
oldrefs={p[0] for m in old.values() for p in m}
newrefs={"Q801","Q802","U801","U802","D803"}|{f"R{n}" for n in range(1001,1011)}
if newrefs & oldrefs:raise AssertionError("V1.8 duplicate refdes: "+repr(sorted(newrefs&oldrefs)))
for ref,num in [("Q801",3),("Q802",3),("U801",7),("U802",3),("D803",2)]+[(f"R{n}",2) for n in range(1001,1011)]:
 count=sum(x[0]==ref for x in where)
 if count!=num:raise AssertionError(f"{ref} expected {num} connected pins, got {count}")
evidence={"status":"PASS_V18_REAL_KICAD9_OVP_CAD_TOPOLOGY_ONLY",
"previous_54_net_groups":len(old),"new_62_net_groups":len(new),
"legacy_pin_groups_preserved_except_D701_anode2":True,"no_refdes_collision":True,
"IRF9540N_PINMAP":"Q801 gate1 drain2 source3","TL431BCLP_PINMAP":"U802 cathode1 anode2 REF3",
"LM393N_PINMAP":"U801 OUT_A1 IN-A2 IN+A3 GND4 IN+B5 IN-B6 OUT_B7_NC VCC8",
"ZENER":"D803 cathode1 on FUSED_RAW and anode2 on PMOS gate",
"high_side_isolation":"Q801 D2 -> D701 A2 on OVP_SWITCHED",
"continuous_ovp_status":"CIRCUIT_TOPOLOGY_CANDIDATE_ONLY","VREF_startup":"NOT_VALIDATED",
"fuse_source_energy":"NOT_QUALIFIED","surge_automotive":"NOT_TESTED",
"upstream_LM393_36V_max":"EXPOSED_TO_RAW_OVERVOLTAGE",
"powergood_mute":"NOT_DESIGNED","PCB_DRC":"NOT_RUN","fab_authorized":False,"tx_authorized":False}
Path(sys.argv[2]).parent.joinpath("v18_native_net_evidence.json").write_text(json.dumps(evidence,indent=2)+"\n")
print(json.dumps(evidence,sort_keys=True))
