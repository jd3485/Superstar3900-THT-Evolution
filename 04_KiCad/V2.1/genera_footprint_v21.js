#!/usr/bin/env node
function footprint(n,l,d,drill,mpn){
 const w=l/2,h=d/2,p=6.35,ps=(drill+1.2).toFixed(2);
 return `(footprint "${n}" (version 20241229) (generator "pcbnew") (layer "F.Cu")
 (descr "${mpn}, max body ${l}x${d}mm; P12.70 candidate; NO FAB")
 (tags "THT axial lab prototype unqualified")
 (attr through_hole)
 (fp_text reference "REF**" (at 0 ${(-h-2.4).toFixed(3)}) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))
 (fp_text value "${n}" (at 0 ${(h+2.4).toFixed(3)}) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))
 (fp_rect (start ${-w} ${-h}) (end ${w} ${h}) (stroke (width 0.12) (type solid)) (fill none) (layer "F.SilkS"))
 (fp_rect (start ${-w} ${-h}) (end ${w} ${h}) (stroke (width 0.10) (type solid)) (fill none) (layer "F.Fab"))
 (fp_rect (start ${(-w-.5).toFixed(3)} ${(-h-.5).toFixed(3)}) (end ${(w+.5).toFixed(3)} ${(h+.5).toFixed(3)}) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd"))
 (pad "1" thru_hole circle (at -6.35 0) (size ${ps} ${ps}) (drill ${drill}) (layers "*.Cu" "*.Mask"))
 (pad "2" thru_hole circle (at 6.35 0) (size ${ps} ${ps}) (drill ${drill}) (layers "*.Cu" "*.Mask"))
)\n`;
}
/* Seven-sheet VTUNE20 V2.0 preserved. Integrate F701/D702 physical THT footprints in V2.1. NO FAB / NO TX. */
const fs=require("fs"),path=require("path"),assert=require("assert");
function makeV21(src){
 const OLD="PLL_RX_HIERARCHICAL_MASTER_V2.0",NEW="PLL_RX_HIERARCHICAL_MASTER_V2.1";
 const change=s=>s.replaceAll(`(project "${OLD}"`,`(project "${NEW}"`);
 const sheets=src.slice(0,7).map((s,i)=>i===0?change(s).replaceAll("_V2.0.kicad_sch","_V2.1.kicad_sch"):change(s));
 let input=sheets[5];
 for(const [a,b] of [
 ['(property "Footprint" "" (at 104.14 66.04 0)',`(property "Footprint" "THT_V21:Fuse_Littelfuse_PICOII_0251_500MXL_P12.70mm" (at 104.14 66.04 0)`],
 ['(property "Footprint" "" (at 132.08 111.76 0)',`(property "Footprint" "THT_V21:TVS_ST_P6KE20CA_DO15_P12.70mm" (at 132.08 111.76 0)`]
 ]){if(input.split(a).length!==2)throw Error("Exactly one old footprint value required: "+a);input=input.replace(a,b)}
 sheets[5]=input;
 if(sheets[0].match(/\(property "Sheetfile"/g).length!==6)throw Error("NOT SEVEN SHEET ROOT");
 if(!sheets[0].includes("POWER20_VTUNE_BOOST_LDO_V2.1.kicad_sch"))throw Error("VTUNE20 seven-sheet root lost");
 const symbols=src[7].replace('${KIPRJMOD}/THT_V20.kicad_sym','${KIPRJMOD}/../V2.0/THT_V20.kicad_sym');
 if(symbols.includes('${KIPRJMOD}/THT_V20.kicad_sym'))throw Error("THT V20 library relocation failed");
 const fpTable='(fp_lib_table\n (lib (name "THT_V21") (type "KiCad") (uri "${KIPRJMOD}/THT_V21.pretty") (options "") (descr "F701 PICO II and D702 ST DO15 axial THT mechanics candidate"))\n)\n';
 return {sheets,symbols,fpTable,fuse:src[8],tvs:src[9]};
}
const repo=path.resolve(__dirname,"../..");
const sources=["04_KiCad/V2.0/PLL_RX_HIERARCHICAL_MASTER_V2.0.kicad_sch","04_KiCad/V2.0/PLL_CORE_DIGITAL_V2.0.kicad_sch","04_KiCad/V2.0/PD_FILTER_DRIVER_V2.0.kicad_sch","04_KiCad/V2.0/VCO_RX_AND_LOBUF_V2.0.kicad_sch","04_KiCad/V2.0/POWER5_DISTRIBUTION_V2.0.kicad_sch","04_KiCad/V2.0/INPUT_FUSE_REVERSE_TVS_OVP_V2.0.kicad_sch","04_KiCad/V2.0/POWER20_VTUNE_BOOST_LDO_V2.0.kicad_sch","04_KiCad/V2.0/sym-lib-table"].map(f=>fs.readFileSync(path.join(repo,f),"utf8"));
const f1=footprint("Fuse_Littelfuse_PICOII_0251_500MXL_P12.70mm",7.11,2.8,.9,"Littelfuse 0251.500MXL axial 0.5A 125V lead max 0.64mm");
const f2=footprint("TVS_ST_P6KE20CA_DO15_P12.70mm",6.75,3.53,1.1,"ST P6KE20CA DO15 bidirectional TVS lead max 0.88mm");
const out=makeV21(sources.concat(f1,f2));
const paths=["PLL_RX_HIERARCHICAL_MASTER","PLL_CORE_DIGITAL","PD_FILTER_DRIVER","VCO_RX_AND_LOBUF","POWER5_DISTRIBUTION","INPUT_FUSE_REVERSE_TVS_OVP","POWER20_VTUNE_BOOST_LDO"].map((s,i)=>[s+"_V2.1.kicad_sch",out.sheets[i]]);
paths.push(["sym-lib-table",out.symbols],["fp-lib-table",out.fpTable],["THT_V21.pretty/Fuse_Littelfuse_PICOII_0251_500MXL_P12.70mm.kicad_mod",out.fuse],["THT_V21.pretty/TVS_ST_P6KE20CA_DO15_P12.70mm.kicad_mod",out.tvs]);
for(const [name,content] of paths){const target=path.join(__dirname,name);if(process.argv.includes("--check"))assert.strictEqual(fs.readFileSync(target,"utf8"),content,name+" not reproducible");else if(process.argv.includes("--write"))fs.writeFileSync(target,content);else throw Error("Use --check or --write")}
console.log(JSON.stringify({status:"PASS_V21_NATIVE_7_SHEET_REPRODUCIBLE",files:paths.length,base_V20_VTUNE20_preserved:true,fab_authorized:false,tx_authorized:false}));
