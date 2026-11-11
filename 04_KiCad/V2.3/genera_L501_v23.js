#!/usr/bin/env node
/* THT V2.3 generator: KiCad9 seven sheet V2.2 => V2.3; only L501 value+footprint CAD metadata. NO FAB / NO TX */
"use strict";
const fs=require("fs"),path=require("path"),assert=require("assert");
const repo=path.resolve(__dirname,"../..");
const names=["PLL_RX_HIERARCHICAL_MASTER","PLL_CORE_DIGITAL","PD_FILTER_DRIVER","VCO_RX_AND_LOBUF","POWER5_DISTRIBUTION","INPUT_FUSE_REVERSE_TVS_OVP","POWER20_VTUNE_BOOST_LDO"];
const oldVal="(property \"Value\" \"166nH_MODEL\" (at 482.6 72.39 0)",newVal="(property \"Value\" \"165nH_150-05J08L_CAND\" (at 482.6 72.39 0)";
const oldFp="(property \"Footprint\" \"\" (at 482.6 55.88 0)",newFp="(property \"Footprint\" \"THT_V23:Inductor_Coilcraft_150-05J08L_Uni7_Tunable_THT\" (at 482.6 55.88 0)";
function convert(src,index){
 let txt=src.replaceAll('(project "PLL_RX_HIERARCHICAL_MASTER_V2.2"','(project "PLL_RX_HIERARCHICAL_MASTER_V2.3"');
 if(index===0)txt=txt.replaceAll('_V2.2.kicad_sch','_V2.3.kicad_sch');
 if(index===3){
  assert.strictEqual(txt.split(oldVal).length,2,'L501 value must occur once');
  assert.strictEqual(txt.split(oldFp).length,2,'L501 footprint must be empty once');
  txt=txt.replace(oldVal,newVal).replace(oldFp,newFp);
 }
 return txt;
}
const footprint="(footprint \"Inductor_Coilcraft_150-05J08L_Uni7_Tunable_THT\" (version 20241229) (generator \"pcbnew\") (layer \"F.Cu\")\n (descr \"Coilcraft 150-05J08L Uni7 unshielded THT tunable RF inductor; 165nH nom, 137..193nH adjust. 4.5x4.5 lead centers, 0.51+/-0.05mm dia; NO FAB\")\n (tags \"THT Coilcraft RF tunable VCO prototype unshielded 150-05J08L NOT_RF_QUALIFIED NO_FAB\")\n (attr through_hole)\n (fp_text reference \"REF**\" (at 0 -5.4) (layer \"F.SilkS\") (effects (font (size 1 1) (thickness 0.15))))\n (fp_text value \"Inductor_Coilcraft_150-05J08L_Uni7_Tunable_THT\" (at 0 5.4) (layer \"F.Fab\") (effects (font (size 1 1) (thickness 0.15))))\n (fp_rect (start -3.47 -3.47) (end 3.47 3.47) (stroke (width 0.12) (type solid)) (fill none) (layer \"F.SilkS\"))\n (fp_rect (start -3.47 -3.47) (end 3.47 3.47) (stroke (width 0.10) (type solid)) (fill none) (layer \"F.Fab\"))\n (fp_rect (start -4.25 -4.25) (end 4.25 4.25) (stroke (width 0.05) (type solid)) (fill none) (layer \"F.CrtYd\"))\n (pad \"1\" thru_hole circle (at -2.25 -2.25) (size 1.8 1.8) (drill 0.8) (layers \"*.Cu\" \"*.Mask\"))\n (pad \"2\" thru_hole circle (at 2.25 2.25) (size 1.8 1.8) (drill 0.8) (layers \"*.Cu\" \"*.Mask\"))\n)\n";
const fpTable="(fp_lib_table\n (lib (name \"THT_V21\") (type \"KiCad\") (uri \"${KIPRJMOD}/../V2.1/THT_V21.pretty\") (options \"\") (descr \"V2.1 F701 D702 axial THT\"))\n (lib (name \"THT_V22\") (type \"KiCad\") (uri \"${KIPRJMOD}/../V2.2/THT_V22.pretty\") (options \"\") (descr \"V2.2 L920 Bourns radial THT\"))\n (lib (name \"THT_V23\") (type \"KiCad\") (uri \"${KIPRJMOD}/THT_V23.pretty\") (options \"\") (descr \"V2.3 L501 Coilcraft Uni7 tunable THT candidate\"))\n)\n";
const files=names.map((n,i)=>[path.join(__dirname,n+'_V2.3.kicad_sch'),convert(fs.readFileSync(path.join(repo,'04_KiCad/V2.2',n+'_V2.2.kicad_sch'),'utf8'),i)]);
files.push([path.join(__dirname,'sym-lib-table'),fs.readFileSync(path.join(repo,'04_KiCad/V2.2/sym-lib-table'),'utf8')]);
files.push([path.join(__dirname,'fp-lib-table'),fpTable]);
files.push([path.join(__dirname,'THT_V23.pretty/Inductor_Coilcraft_150-05J08L_Uni7_Tunable_THT.kicad_mod'),footprint]);
const check=process.argv.includes('--check'),write=process.argv.includes('--write');
assert(check!==write,'pass exactly --check or --write');
for(const [p,c] of files){if(check)assert.strictEqual(fs.readFileSync(p,'utf8'),c,'not reproducible: '+p);else fs.writeFileSync(p,c)}
console.log(JSON.stringify({gate:'PASS_V23_NATIVE_7SHEET_REPRODUCIBLE',files:files.length,only_L501_value_and_footprint_changed:true,qualification:'NONE',no_fab:true,no_tx:true}));
