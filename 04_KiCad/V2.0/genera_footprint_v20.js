#!/usr/bin/env node
/* V2.0 KiCad9 deterministic F701 D702 dimensional footprint selection. NO PCB/no fab. */
const fs=require("fs"),path=require("path"),assert=require("assert");
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
function makeV20(files,fuse,tvs){
 const previous="PLL_RX_HIERARCHICAL_MASTER_V1.9",current="PLL_RX_HIERARCHICAL_MASTER_V2.0";
 const rename=x=>x.replaceAll(`(project "${previous}"`,`(project "${current}"`);
 let input=files[5];
 for(const [a,b] of [
 ['(property "Footprint" "" (at 104.14 66.04 0)',`(property "Footprint" "THT_V20:Fuse_Littelfuse_PICOII_0251_500MXL_P12.70mm" (at 104.14 66.04 0)`],
 ['(property "Footprint" "" (at 132.08 111.76 0)',`(property "Footprint" "THT_V20:TVS_ST_P6KE20CA_DO15_P12.70mm" (at 132.08 111.76 0)`]
 ]){if(input.split(a).length!==2)throw Error("Missing unique footprint target");input=input.replace(a,b)}
 input=rename(input);
 const root=rename(files[0]).replaceAll("_V1.9.kicad_sch","_V2.0.kicad_sch");
 if(!root.includes("INPUT_FUSE_REVERSE_TVS_OVP_V2.0.kicad_sch"))throw Error("Root incomplete");
 return {root,core:rename(files[1]),filter:rename(files[2]),vco:rename(files[3]),power:rename(files[4]),input,table:files[6],fptable:'(fp_lib_table\n (lib (name "THT_V20") (type "KiCad") (uri "${KIPRJMOD}/THT_V20.pretty") (options "") (descr "THT axial candidate footprints F701 D702"))\n)\n',fuse,tvs};
}
const repo=path.resolve(__dirname,"../..");
const src=["04_KiCad/V1.9/PLL_RX_HIERARCHICAL_MASTER_V1.9.kicad_sch","04_KiCad/V1.9/PLL_CORE_DIGITAL_V1.9.kicad_sch","04_KiCad/V1.9/PD_FILTER_DRIVER_V1.9.kicad_sch","04_KiCad/V1.9/VCO_RX_AND_LOBUF_V1.9.kicad_sch","04_KiCad/V1.9/POWER5_DISTRIBUTION_V1.9.kicad_sch","04_KiCad/V1.9/INPUT_FUSE_REVERSE_TVS_OVP_V1.9.kicad_sch","04_KiCad/V1.9/sym-lib-table"].map(p=>fs.readFileSync(path.join(repo,p),"utf8"));
const f=footprint("Fuse_Littelfuse_PICOII_0251_500MXL_P12.70mm",7.11,2.8,.9,"Littelfuse 0251.500MXL axial 0.5A 125V lead max 0.64mm");
const t=footprint("TVS_ST_P6KE20CA_DO15_P12.70mm",6.75,3.53,1.1,"ST P6KE20CA DO15 bidirectional TVS lead max 0.88mm");
const x=makeV20(src,f,t);
const o={"PLL_RX_HIERARCHICAL_MASTER_V2.0.kicad_sch":x.root,"PLL_CORE_DIGITAL_V2.0.kicad_sch":x.core,"PD_FILTER_DRIVER_V2.0.kicad_sch":x.filter,"VCO_RX_AND_LOBUF_V2.0.kicad_sch":x.vco,"POWER5_DISTRIBUTION_V2.0.kicad_sch":x.power,"INPUT_FUSE_REVERSE_TVS_OVP_V2.0.kicad_sch":x.input,"sym-lib-table":x.table,"fp-lib-table":x.fptable,"THT_V20.pretty/Fuse_Littelfuse_PICOII_0251_500MXL_P12.70mm.kicad_mod":x.fuse,"THT_V20.pretty/TVS_ST_P6KE20CA_DO15_P12.70mm.kicad_mod":x.tvs};
for(const [n,content] of Object.entries(o)){const target=path.join(__dirname,n);if(process.argv.includes("--check"))assert.strictEqual(fs.readFileSync(target,"utf8"),content,n+" not deterministic");else if(process.argv.includes("--write")){fs.mkdirSync(path.dirname(target),{recursive:true});fs.writeFileSync(target,content)}else throw Error("Use --check or --write")}
console.log(JSON.stringify({status:"PASS_V20_DETERMINISTIC_NATIVE_CAD",files:Object.keys(o).length,full_board:false,fab_authorized:false,tx_authorized:false}));
