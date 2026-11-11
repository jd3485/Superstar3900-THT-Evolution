#!/usr/bin/env node
/* Reproducible native KiCad V2.2 seven-sheet migration from V2.1: ONLY L920 footprint metadata. NO FAB / NO TX. */
"use strict";
const fs=require("fs"),path=require("path"),assert=require("assert");
const repo=path.resolve(__dirname,"../..");
const names=["PLL_RX_HIERARCHICAL_MASTER","PLL_CORE_DIGITAL","PD_FILTER_DRIVER","VCO_RX_AND_LOBUF","POWER5_DISTRIBUTION","INPUT_FUSE_REVERSE_TVS_OVP","POWER20_VTUNE_BOOST_LDO"];
const old='(property "Footprint" "" (at 120.65 201.93 0)';
const replacement='(property "Footprint" "THT_V22:Inductor_Bourns_RLB0914_681KL_P5.00mm" (at 120.65 201.93 0)';
function transform(source,index) {
  let text=source.replaceAll('(project "PLL_RX_HIERARCHICAL_MASTER_V2.1"','(project "PLL_RX_HIERARCHICAL_MASTER_V2.2"');
  if(index===0) text=text.replaceAll('_V2.1.kicad_sch','_V2.2.kicad_sch');
  if(index===6) {
    assert.strictEqual(text.split(old).length,2,'expected exactly one empty footprint at L920');
    text=text.replace(old,replacement);
  }
  return text;
}
function radialFootprint(){
return `(footprint "Inductor_Bourns_RLB0914_681KL_P5.00mm" (version 20241229) (generator "pcbnew") (layer "F.Cu")
 (descr "Bourns RLB0914-681KL THT 680uH, body max D9.2 H13.0mm, leads D0.65 pitch 5.0 +/-0.8mm; mechanical candidate NO FAB")
 (tags "THT radial inductor Bourns RLB0914 unshielded unqualified NO_FAB")
 (attr through_hole)
 (fp_text reference "REF**" (at 0 -6.6) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))
 (fp_text value "Inductor_Bourns_RLB0914_681KL_P5.00mm" (at 0 6.6) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))
 (fp_arc (start -3.25 -3.25) (mid 0 -4.6) (end 3.25 -3.25) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
 (fp_arc (start 3.25 3.25) (mid 0 4.6) (end -3.25 3.25) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
 (fp_circle (center 0 0) (end 4.6 0) (stroke (width 0.10) (type solid)) (fill none) (layer "F.Fab"))
 (fp_circle (center 0 0) (end 5.2 0) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd"))
 (pad "1" thru_hole circle (at -2.5 0) (size 2 2) (drill 1.0) (layers "*.Cu" "*.Mask"))
 (pad "2" thru_hole circle (at 2.5 0) (size 2 2) (drill 1.0) (layers "*.Cu" "*.Mask"))
)\n`;
}
const fpTable=`(fp_lib_table
 (lib (name "THT_V21") (type "KiCad") (uri "\${KIPRJMOD}/../V2.1/THT_V21.pretty") (options "") (descr "V2.1 axial F701 and D702 candidate footprints"))
 (lib (name "THT_V22") (type "KiCad") (uri "\${KIPRJMOD}/THT_V22.pretty") (options "") (descr "V2.2 Bourns RLB0914 radial L920 mechanical candidate"))
)
`;
const entries=names.map((name,i)=>[
  path.join(__dirname,name+'_V2.2.kicad_sch'),
  transform(fs.readFileSync(path.join(repo,'04_KiCad/V2.1',name+'_V2.1.kicad_sch'),'utf8'),i)
]);
entries.push([path.join(__dirname,'sym-lib-table'),fs.readFileSync(path.join(repo,'04_KiCad/V2.1/sym-lib-table'),'utf8')]);
entries.push([path.join(__dirname,'fp-lib-table'),fpTable]);
entries.push([path.join(__dirname,'THT_V22.pretty/Inductor_Bourns_RLB0914_681KL_P5.00mm.kicad_mod'),radialFootprint()]);
const check=process.argv.includes('--check'),write=process.argv.includes('--write');
assert(check!==write,'choose --check OR --write');
for(const [p,content] of entries){
  if(check) assert.strictEqual(fs.readFileSync(p,'utf8'),content,'not reproducible: '+p);
  else fs.writeFileSync(p,content);
}
console.log(JSON.stringify({gate:'PASS_V22_GENERATOR_REPRODUCIBLE',files:entries.length,seven_sheets:true,base:'V2.1',only_L920_footprint_changed:true,pcb_fab:false,tx:false}));
