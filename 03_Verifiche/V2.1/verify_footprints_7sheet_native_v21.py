#!/usr/bin/env python3
"""KiCad9 V2.1: seven-sheet native netlist PIN->NET equivalence to main V2.0 VTUNE20.
Only 2 footprint metadata additions F701/D702 are allowed; NO electrical net changes.
"""
from pathlib import Path
import json,runpy,sys,re
repo=Path(__file__).resolve().parents[2]
r=runpy.run_path(str(repo/"03_Verifiche/V1.0/verify_kicad_netlist_v10.py"))["read_nets"]
before=r(Path(sys.argv[1]));after=r(Path(sys.argv[2]))
assert len(before)==72 and len(after)==72,(len(before),len(after))
pre={};post={}
for name,members in before.items():
 for pin in members:
  assert pin not in pre,pin
  pre[pin]=name
for name,members in after.items():
 for pin in members:
  assert pin not in post,pin
  post[pin]=name
assert set(pre)==set(post),{"lost":sorted(set(pre)-set(post)),"unexpected":sorted(set(post)-set(pre))}
mapped={}
for net,members in before.items():
 dest={post[p] for p in members}
 assert len(dest)==1,(net,dest)
 new=next(iter(dest))
 assert new not in mapped,(net,mapped[new])
 mapped[new]=net
assert len(mapped)==72
def net(name,*pins):
 targets={post.get(p) for p in pins}
 assert len(targets)==1 and None not in targets,(name,pins,targets)
 return next(iter(targets))
raw=net("external raw",("J701","1"),("F701","1"))
fused=net("fused raw to TVS and MOSFET",("F701","2"),("D702","1"),("Q801","3"),("D804","2"))
gnd=net("TVS to ground",("D702","2"),("U601","2"),("U911","2"),("J701","2"))
controller=net("OVP supervised supply",("D804","1"),("U801","8"),("R1001","1"),("R1002","1"))
protected=net("protected supply from OVP",("D701","1"),("U601","1"),("U911","6"))
boost=net("boost rail -> LM317 input",("D920","1"),("U912","3"))
ldo=net("LM317 output pin2",("U912","2"),("R926","1"))
vtune=net("20V supply actual link to PLL driver",("R926","2"),("U803","8"),("C929","1"))
pll=net("PLL5",("R611","2"),("U401","3"))
vco=net("VCO5",("R612","2"),("L501","1"))
lo=net("LOBUF5",("R613","2"),("U520","14"))
assert len({raw,fused,gnd,controller,protected,boost,ldo,vtune,pll,vco,lo})==11
sch=(repo/"04_KiCad/V2.1/INPUT_FUSE_REVERSE_TVS_OVP_V2.1.kicad_sch").read_text()
footprints={"F701":("104.14","66.04","THT_V21:Fuse_Littelfuse_PICOII_0251_500MXL_P12.70mm"),
"D702":("132.08","111.76","THT_V21:TVS_ST_P6KE20CA_DO15_P12.70mm")}
for ref,(x,y,fp) in footprints.items():
 assert f'(property "Footprint" "{fp}" (at {x} {y} 0)' in sch,(ref,fp)
 assert sch.count(f'(property "Reference" "{ref}"')==1,ref
for f,l,d,lead,drill,pad in [
 ("Fuse_Littelfuse_PICOII_0251_500MXL_P12.70mm",7.11,2.8,.64,.9,2.10),
 ("TVS_ST_P6KE20CA_DO15_P12.70mm",6.75,3.53,.88,1.1,2.30)
]:
 file=repo/"04_KiCad/V2.1/THT_V21.pretty"/(f+".kicad_mod")
 text=file.read_text()
 assert text.count('(pad "')==2,(f,"pad count")
 for p,x in [("1","-6.35"),("2","6.35")]:
  assert f'(pad "{p}" thru_hole circle (at {x} 0)' in text,(f,p)
 assert f'(drill {drill})' in text,f
 assert f'(size {pad:.2f} {pad:.2f})' in text,f
 assert pad-drill>=1.1 and drill-lead>=.2 and 12.7-l>=4.5,f
 assert '(attr through_hole)' in text and 'SMD' not in text,f
report={"status":"PASS_V21_SEVEN_SHEET_NATIVE_KICAD9_FOOTPRINTS_AND_ALL_72_NETS",
 "baseline_v20_seven_sheet_nets":len(before),"v21_seven_sheet_nets":len(after),
 "all_pin_net_partitions_100percent_preserved":True,
 "VANA20_FILT_real_native_hierarchical_rail_preserved":True,
 "F701_and_D702_new_footprint_fields":list(footprints.values()),
 "mechanical_tolerances_screened_against_vendor_package_max":True,
 "lead_form_pitch_12p70_hardware_qualified":False,
 "fuse_TVS_fault_energy_qualified":False,
 "PCB_full_radio":"NOT_STARTED",
 "fab_authorized":False,"tx_authorized":False}
Path(sys.argv[2]).parent.joinpath("v21_native_evidence.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({k:v for k,v in report.items() if k!="F701_and_D702_new_footprint_fields"},sort_keys=True))
