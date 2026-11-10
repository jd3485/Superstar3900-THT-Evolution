#!/usr/bin/env node
/* Real KiCad9 V1.6 native five-sheet THT RX PLL + independent 5V supply from unchanged previous source CAD.
   Input protection, thermal, RF, PLL lock and physical PCB are NOT approved. NO FAB / NO TX. */
const fs=require("fs"),path=require("path");
function integrate(v){
 const [master,core,filter,vco,supply]=v,ROOT="7b14bcd1-faae-4e37-bf14-000000000001",
 POWER="8d16bcd1-faae-4e37-bf16-000000000005",OLDPOWER="8c15bcd1-faae-4e37-bf15-000000000001",
 NAME="PLL_RX_HIERARCHICAL_MASTER_V1.6",OLDNAME="PLL_RX_HIERARCHICAL_MASTER_V1.4";
 let counter=50;const uid=()=>`8d16bcd1-faae-4e37-bf16-${String(++counter).padStart(12,"0")}`;
 function forms(src){let o=[],start=0,level=0,q=false,esc=false;for(let i=0;i<src.length;i++){const c=src[i];if(q){if(esc)esc=false;else if(c==="\\")esc=true;else if(c==='"')q=false;continue}if(c==='"'){q=true;continue}if(c==="("){if(!level)start=i;level++}if(c===")"){level--;if(level<0)throw Error("Stray )");if(!level)o.push(src.slice(start,i+1))}}if(level||q)throw Error("Unclosed S-expression");return o}
 const childForms=s=>{const t=s.trim();if(!t.startsWith("(kicad_sch")||!t.endsWith(")"))throw Error("Not KiCad schematic");return forms(t.slice("(kicad_sch".length,-1))};
 const pin=(n,x,y,rot)=>`(pin "${n}" passive (at ${x} ${y} ${rot}) (uuid "${uid()}") (effects (font (size 1.27 1.27)) (justify ${rot===180?"left":"right"})))`;
 const wire=(a,b,c,d)=>`(wire (pts (xy ${a} ${b}) (xy ${c} ${d})) (stroke (width 0) (type default)) (uuid "${uid()}"))`;
 const lbl=(n,x,y)=>`(label "${n}" (at ${x} ${y} 0) (effects (font (size 1.27 1.27))) (uuid "${uid()}"))`;
 const root=childForms(master).map(s=>{
  s=s.replaceAll(`(project "${OLDNAME}"`,`(project "${NAME}"`);
  if(s.startsWith("(sheet ")){
   if(s.includes('(property "Sheetname" "PLL_CORE_DIGITAL"')){
    s=s.replace('"PLL_CORE_DIGITAL_V1.4.kicad_sch"','"PLL_CORE_DIGITAL_V1.6.kicad_sch"').replace("(instances ",pin("+5V_PLL",43.18,96.52,180)+"\n(instances ");
   }else if(s.includes('(property "Sheetname" "PD_FILTER_DRIVER"')){
    s=s.replace('"PD_FILTER_DRIVER_V1.4.kicad_sch"','"PD_FILTER_DRIVER_V1.6.kicad_sch"');
   }else if(s.includes('(property "Sheetname" "RX_VCO_AND_LO_BUF"')){
    s=s.replace('"VCO_RX_AND_LOBUF_V1.4.kicad_sch"','"VCO_RX_AND_LOBUF_V1.6.kicad_sch"')
     .replace("(instances ",pin("VCC_VCO5",304.8,68.58,180)+"\n"+pin("VCC_BUF5",304.8,116.84,180)+"\n(instances ");
   }else throw Error("Sheet changed in V1.4");
  }
  if(s.startsWith("(text ")&&s.includes("V1.4 FOUR SHEETS"))s=s.replace("V1.4 FOUR SHEETS","V1.6 FIVE SHEETS");
  return s;
 });
 root.push(`(sheet (at 177.8 208.28) (size 86.36 71.12) (stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0.0000)) (uuid "${POWER}")
 (property "Sheetname" "PWR_5V_RAILS" (at 177.8 207.01 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
 (property "Sheetfile" "POWER5_DISTRIBUTION_V1.6.kicad_sch" (at 177.8 280.67 0) (effects (font (size 1.27 1.27)) (justify left top)))
 ${pin("+5V_PLL",264.16,228.6,0)}
 ${pin("VCC_VCO5",264.16,241.3,0)}
 ${pin("VCC_BUF5",264.16,254,0)}
 ${pin("GND",177.8,264.16,180)}
 (instances (project "${NAME}" (path "/${ROOT}" (page "5")))))`);
 for(const [name,x1,y,x2] of [
  ["+5V_PLL",33.02,96.52,43.18],["+5V_PLL",264.16,228.6,274.32],
  ["VCC_VCO5",294.64,68.58,304.8],["VCC_VCO5",264.16,241.3,274.32],
  ["VCC_BUF5",294.64,116.84,304.8],["VCC_BUF5",264.16,254,274.32]
 ]){root.push(wire(x1,y,x2,y));root.push(lbl(name,x1===264.16?x2:x1,y))}
 root.push(wire(154.94,165.1,154.94,264.16),wire(154.94,264.16,177.8,264.16),
 `(junction (at 154.94 165.1) (diameter 0) (color 0 0 0 0) (uuid "${uid()}"))`);
 function convert(s,flags){
   s=s.replaceAll(`(project "${OLDNAME}"`,`(project "${NAME}"`);
   const wanted=new Set(flags),found=new Set();
   const arr=childForms(s).map(f=>{
    if(f.startsWith("(label ")){
      for(const net of wanted){
       if(!found.has(net)&&f.startsWith(`(label "${net}"`)){
        found.add(net);return f.replace(`(label "${net}"`,`(hierarchical_label "${net}" (shape passive)`);
       }
      }
    }return f;
   });
   if(found.size!==wanted.size)throw Error("Missing sheet label "+JSON.stringify({flags,found:[...found]}));
   return "(kicad_sch\n"+arr.join("\n")+"\n)\n";
 }
 const digi=convert(core,["+5V_PLL"]);
 const ana=filter.replaceAll(`(project "${OLDNAME}"`,`(project "${NAME}"`);
 const vc=convert(vco,["VCC_VCO5","VCC_BUF5"]);
 let ps=supply.replaceAll('(project "THT_5V_POWER_DISTRIBUTION_V1.5"',`(project "${NAME}"`);
 ps=ps.replaceAll(`(path "/${OLDPOWER}"`,`(path "/${ROOT}/${POWER}"`);
 ps=ps.replace(`(uuid "${OLDPOWER}")`,`(uuid "${POWER}")`);
 ps=ps.replace('(sheet_instances (path "/" (page "1")))',`(sheet_instances (path "/${ROOT}/${POWER}" (page "5")))`);
 if(ps.includes('(project "THT_5V_POWER_DISTRIBUTION_V1.5"')||ps.includes(`(path "/${OLDPOWER}"`))throw Error("Old standalone instance remains");
 let p5=convert(ps,["+5V_PLL","VCC_VCO5","VCC_BUF5","GND"]);
 // Source V1.5 had an ERC-only EXTERNAL GND PWR_FLAG. In the now integrated circuit,
 // PWR402 is the existing verified global ground driver. Do NOT permit duplicate power-output drivers.
 const drop=childForms(p5);let nRemoved=0;
 const cleaned=drop.filter(f=>{
  if(f.startsWith("(symbol ")&&f.includes('(property "Reference" "PWR602"')){nRemoved++;return false;}
  if(f.startsWith("(wire ")&&f.includes("(xy 53.34 187.96)")&&f.includes("(xy 48.26 187.96)")){nRemoved++;return false;}
  if(f.startsWith('(label "GND"')&&f.includes('(at 48.26 187.96 0)')){nRemoved++;return false;}
  return true;
 });
 if(nRemoved!==3)throw Error("V1.6 expected to remove exactly one redundant external ground PWR_FLAG and isolated stub");
 p5="(kicad_sch\\n"+cleaned.join("\\n")+"\\n)\\n";
 p5=p5.replace("NOT IN MASTER. NO FAB / NO TX.","IN MASTER V1.6 WITH UNQUALIFIED INPUT. NO FAB / NO TX.");
 const table='(sym_lib_table\n (lib (name "THT_V10") (type "KiCad") (uri "${KIPRJMOD}/../V1.0/THT_V10.kicad_sym") (options "") (descr "THT analog"))\n (lib (name "THT_V11") (type "KiCad") (uri "${KIPRJMOD}/../V1.1/THT_V11.kicad_sym") (options "") (descr "THT PLL"))\n (lib (name "THT_V14") (type "KiCad") (uri "${KIPRJMOD}/../V1.4/THT_V14.kicad_sym") (options "") (descr "THT VCO"))\n (lib (name "THT_V15") (type "KiCad") (uri "${KIPRJMOD}/../V1.5/THT_V15.kicad_sym") (options "") (descr "THT 5V power"))\n)\n';
 return {root:"(kicad_sch\n"+root.join("\n")+"\n)\n",digital:digi,analog:ana,vco:vc,power:p5,table};
}
const repo=path.resolve(__dirname,"../..");
const originalPaths=["04_KiCad/V1.4/PLL_RX_HIERARCHICAL_MASTER_V1.4.kicad_sch","04_KiCad/V1.4/PLL_CORE_DIGITAL_V1.4.kicad_sch","04_KiCad/V1.4/PD_FILTER_DRIVER_V1.4.kicad_sch","04_KiCad/V1.4/VCO_RX_AND_LOBUF_V1.4.kicad_sch","04_KiCad/V1.5/THT_5V_POWER_DISTRIBUTION_V1.5.kicad_sch"];
const original=originalPaths.map(p=>fs.readFileSync(path.join(repo,p),"utf8"));
const generated=integrate(original);
const files={"PLL_RX_HIERARCHICAL_MASTER_V1.6.kicad_sch":generated.root,
"PLL_CORE_DIGITAL_V1.6.kicad_sch":generated.digital,
"PD_FILTER_DRIVER_V1.6.kicad_sch":generated.analog,
"VCO_RX_AND_LOBUF_V1.6.kicad_sch":generated.vco,
"POWER5_DISTRIBUTION_V1.6.kicad_sch":generated.power,
"sym-lib-table":generated.table};
for(const [f,src] of Object.entries(files))fs.writeFileSync(path.join(__dirname,f),src,"utf8");
console.log(JSON.stringify({native_child_sheets:4,physically_integrated_rails:["GND","+5V_PLL","VCC_VCO5","VCC_BUF5"],scope:"PARTIAL_RX_PLL_ONLY",vin_protection:"NOT_DESIGNED",thermal_qualified:false,rf_qualified:false,pcb:false,fab_authorized:false,tx_authorized:false}));
