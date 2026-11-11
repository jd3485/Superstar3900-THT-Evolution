#!/usr/bin/env python3
"""V2.0 KiCad9 native net equivalence and two manufacturer-dimensioned THT footprints.
This PRE-PCB gate explicitly CANNOT establish fab readiness or board DRC.
"""
import json,re,runpy,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
read=runpy.run_path(str(root/"03_Verifiche/V1.0/verify_kicad_netlist_v10.py"))["read_nets"]
prior=read(Path(sys.argv[1]));new=read(Path(sys.argv[2]))
assert len(prior)==64 and len(new)==64,(len(prior),len(new))
pinmap=lambda nets:{p:net for net,group in nets.items() for p in group}
before=pinmap(prior);after=pinmap(new)
assert set(before)==set(after),"Native KiCad pin set changed unexpectedly"
mapping={}
for n,pins in prior.items():
 destinations={after[p] for p in pins}
 assert len(destinations)==1,(n,pins,destinations)
 target=next(iter(destinations))
 assert target not in mapping,(n,mapping[target])
 mapping[target]=n
assert len(mapping)==64
def same(label,*pins):
 x={after.get(p) for p in pins}
 assert len(x)==1 and None not in x,(label,x)
 return next(iter(x))
raw=same("Raw fused",("J701","1"),("F701","1"))
fused=same("fused output and TVS",("F701","2"),("D702","1"),("D804","2"),("Q801","3"))
ground=same("TVS to common ground",("D702","2"),("U601","2"),("J701","2"))
ctrl=same("guarded controller power",("D804","1"),("U801","8"),("R1001","1"),("R1002","1"))
switched=same("PMOS drain to reverse diode anode",("Q801","2"),("D701","2"))
five=same("5V",("U601","3"),("R611","1"),("R612","1"),("R613","1"))
assert len({raw,fused,ground,ctrl,switched,five})==6
same("VTUNE unchanged",("D501","2"),("R805","2"))
same("LO clock unchanged",("U402","3"),("R513","2"))
input=(root/"04_KiCad/V2.0/INPUT_FUSE_REVERSE_TVS_OVP_V2.0.kicad_sch").read_text()
pairs={
 "F701":("104.14","66.04","THT_V20:Fuse_Littelfuse_PICOII_0251_500MXL_P12.70mm"),
 "D702":("132.08","111.76","THT_V20:TVS_ST_P6KE20CA_DO15_P12.70mm")
}
for ref,(x,y,fp) in pairs.items():
 assert f'(property "Footprint" "{fp}" (at {x} {y} 0)' in input,(ref,fp)
 assert input.count(f'(property "Reference" "{ref}"')==1,ref
fpdata=[
 ("Fuse_Littelfuse_PICOII_0251_500MXL_P12.70mm",7.11,2.8,0.9,0.64,2.10),
 ("TVS_ST_P6KE20CA_DO15_P12.70mm",6.75,3.53,1.1,0.88,2.30),
]
r=[]
for name,length,diameter,drill,wire,pad_diameter in fpdata:
 path=root/"04_KiCad/V2.0/THT_V20.pretty"/(name+".kicad_mod")
 content=path.read_text()
 assert content.count('(pad "')==2,("exactly two THT pads",name)
 for pin,x in ((1,-6.35),(2,6.35)):
  assert re.search(r'\(pad "'+str(pin)+r'" thru_hole circle \(at '+str(x)+r' 0\)',content),(pin,name)
 assert f'(size {pad_diameter:.2f} {pad_diameter:.2f})' in content,name
 assert f'(drill {drill})' in content,name
 assert pad_diameter-drill>=1.1,(name,"annular diameter margin")
 assert drill-wire>=.2,(name,"lead/drill insertion margin")
 assert 12.7-length>=4.5,(name,"formed lead extension too short")
 assert 'SMD' not in content and '(attr through_hole)' in content,name
 r.append({"component":name,"body_max_mm":[length,diameter],"lead_max_mm":wire,
           "pitch_mm":12.7,"drill_mm":drill,"pad_diameter_mm":pad_diameter,
           "minimum_annular_ring_mm":round((pad_diameter-drill)/2,3),
           "minimum_diameter_allowance_mm":round(drill-wire,3),
           "mechanical_vendor_tolerance_qualified":False})
# Some inherited RF/component footprints are genuinely missing; NEVER override their release blocker.
missing=[]
for src in sorted((root/"04_KiCad/V2.0").glob("*_V2.0.kicad_sch")):
 txt=src.read_text()
 for m in re.finditer(r'\(property "Reference" "([A-Z]+\d+)"',txt):
  ref=m.group(1)
  if ref.startswith("PWR"):continue
  start=m.start()
  nextref=re.search(r'\(property "Reference" "([A-Z]+\d+)"',txt[m.end():])
  tail=txt[start:start+500]
  f=re.search(r'\(property "Footprint" "([^"]*)"',tail)
  if f is not None and not f.group(1):missing.append({"sheet":src.name,"reference":ref})
# Reject release regardless of whether this conservative scan finds all missing footprints.
out={"status":"PASS_NATIVE_KICAD9_64_NET_PARTITIONS_AND_2_THOLE_FOOTPRINTS_ONLY",
 "v19_net_groups":len(prior),"v20_net_groups":len(new),"all_previous_pin_net_partitions_unchanged":True,
 "footprint_datasheet_geometric_screen":r,
 "unassigned_footprint_instances_found_by_conservative_scan":missing,
 "footprint_fit_in_real_board":"NOT_TESTED",
 "full_radio_schematic":"INCOMPLETE","complete_radio_pcb_file":False,
 "PCB_DRC":"NOT_RUN_NO_COMPLETE_BOARD",
 "fuse_fault_source_I2t":"UNKNOWN",
 "TVS_transient_protection":"UNQUALIFIED",
 "F701_and_D702_axial_bend_assembly":"NOT_VALIDATED",
 "fab_authorized":False,"tx_authorized":False}
Path(sys.argv[2]).parent.joinpath("v20_prepcb_net_footprint_evidence.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps({"status":out["status"],"nets":len(new),"footprints":len(r),
 "unassigned_footprints_scanned":len(missing),"pcb_drc":out["PCB_DRC"],
 "fab_authorized":False}))
