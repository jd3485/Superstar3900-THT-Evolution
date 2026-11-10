#!/usr/bin/env node
/* Deterministic native 3-sheet KiCad9 THT RX PLL from V1.0/V1.1. NO FAB / NO TX */
const fs=require("fs"),path=require("path");
function generate(c,a){
 const ROOT="6a13bcd1-faae-4e37-bf13-000000000001",D="6a13bcd1-faae-4e37-bf13-000000000002",A="6a13bcd1-faae-4e37-bf13-000000000003",NAME="PLL_RX_HIERARCHICAL_MASTER_V1.3";
 function forms(src){let out=[],start=0,n=0,q=false,esc=false;for(let i=0;i<src.length;i++){let x=src[i];if(q){if(esc)esc=false;else if(x==="\\")esc=true;else if(x==='"')q=false;continue;}if(x==='"'){q=true;continue}if(x==="("){if(!n)start=i;n++}if(x===")"){n--;if(!n)out.push(src.slice(start,i+1));if(n<0)throw Error("extra )")}}if(n||q)throw Error("bad parens");return out}
 function transform(src,oldProj,oldRoot,uuid,kind){
  let f=forms(src.trim().slice("(kicad_sch".length,-1)),out=[],p=0,g=0,removed=0;
  for(let x of f){
   if(x.startsWith("(sheet_instances ")||x.startsWith("(text "))continue;
   if(kind==="ana"&&x.startsWith("(symbol ")&&x.includes('(property "Reference" "PWR902"')){removed++;continue}
   if(kind==="ana"&&x.startsWith("(wire ")&&x.includes("(xy 129.54 156.21)")){removed++;continue}
   if(kind==="ana"&&x.startsWith('(label "GND" (at 124.46 156.21')){removed++;continue}
   if(x.startsWith("(symbol ")){let old=`(project "${oldProj}" (path "/${oldRoot}"`;if(!x.includes(old))throw Error("bad instance "+x.slice(0,110));x=x.replace(old,`(project "${NAME}" (path "/${ROOT}/${uuid}"`)}
   if(x.startsWith('(label "PLL_PDOUT_3STATE"')&&p===0){x=x.replace('(label "PLL_PDOUT_3STATE"',`(hierarchical_label "PLL_PDOUT_3STATE" (shape ${kind==="dig"?"tri_state":"input"})`);p++}
   if(x.startsWith('(label "GND"')&&g===0){x=x.replace('(label "GND"',`(hierarchical_label "GND" (shape passive)`);g++}
   out.push(x);
  }
  if(p!==1||g!==1||(kind==="ana"&&removed!==3))throw Error("missing label/ground cleanup "+JSON.stringify({kind,p,g,removed}));
  out.push(`(sheet_instances (path "/${ROOT}/${uuid}" (page "${kind==="dig"?2:3}")))`);
  return "(kicad_sch\n"+out.join("\n")+"\n)\n";
 }
 const digital=transform(c,"PLL_CORE_RX_CAD_V1.1","4bbbe51d-3f7d-4f18-aa11-000000000001",D,"dig");
 const analog=transform(a,"PLL_FILTER_DRIVER_CAD_V1.0","3d86fc80-36d7-4d76-a243-000000000001",A,"ana");
 function sh(nm,filename,x,w,uuid,page,side){
  let end=x+w,px=side==="right"?end:x,ang=side==="right"?0:180,j=side==="right"?"right":"left",id=side==="right"?11:13;
  const p=(label,typ,y,idx)=>`(pin "${label}" ${typ} (at ${px} ${y} ${ang}) (uuid "6a13bcd1-faae-4e37-bf13-${String(idx).padStart(12,"0")}") (effects (font (size 1.27 1.27)) (justify ${j})))`;
  return `(sheet (at ${x} 46.99) (size ${w} 76.2) (stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0.0000)) (uuid "${uuid}")
 (property "Sheetname" "${nm}" (at ${x} 45.72 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
 (property "Sheetfile" "${filename}" (at ${x} 124.46 0) (effects (font (size 1.27 1.27)) (justify left top)))
 ${p("PLL_PDOUT_3STATE",side==="right"?"tri_state":"input",66.04,id)}
 ${p("GND","passive",87.63,id+1)}
 (instances (project "${NAME}" (path "/${ROOT}" (page "${page}")))))`;
 }
 const master=`(kicad_sch (version 20250114) (generator "tht_v13_hierarchy_generator") (generator_version "9.0")
(uuid "${ROOT}")
(paper "A3")
(lib_symbols)
${sh("PLL_CORE_DIGITAL","PLL_CORE_DIGITAL_V1.3.kicad_sch",43.18,86.36,D,2,"right")}
${sh("PD_FILTER_DRIVER","PD_FILTER_DRIVER_V1.3.kicad_sch",177.8,86.36,A,3,"left")}
(wire (pts (xy 129.54 66.04) (xy 177.8 66.04)) (stroke (width 0) (type default)) (uuid "6a13bcd1-faae-4e37-bf13-000000000031"))
(wire (pts (xy 129.54 87.63) (xy 177.8 87.63)) (stroke (width 0) (type default)) (uuid "6a13bcd1-faae-4e37-bf13-000000000032"))
(text "V1.3 TRUE HIERARCHY of RX PLL PARTIAL: U401 PDout pin4 to R901 pin1; shared GND.\\n+5V_PLL/VANA20_FILT, N bus, LO source and VTUNE feedback still EXTERNAL. NO FAB / NO TX." (at 48.26 153.67 0) (effects (font (size 1.27 1.27))) (uuid "6a13bcd1-faae-4e37-bf13-000000000041"))
(sheet_instances (path "/" (page "1")))
(embedded_fonts no)
)\n`;
 const table='(sym_lib_table\n (lib (name "THT_V11") (type "KiCad") (uri "${KIPRJMOD}/../V1.1/THT_V11.kicad_sym") (options "") (descr "THT PLL core"))\n (lib (name "THT_V10") (type "KiCad") (uri "${KIPRJMOD}/../V1.0/THT_V10.kicad_sym") (options "") (descr "THT analog filter"))\n)\n';
 return {master,digital,analog,table,core_count:(digital.match(/\(property "Reference" "[A-Z]+\d+"/g)||[]).length,analog_count:(analog.match(/\(property "Reference" "[A-Z]+\d+"/g)||[]).length};
}
const repo=path.resolve(__dirname,"../..");
const core=fs.readFileSync(path.join(repo,"04_KiCad/V1.1/PLL_CORE_RX_CAD_V1.1.kicad_sch"),"utf8");
const filter=fs.readFileSync(path.join(repo,"04_KiCad/V1.0/PLL_FILTER_DRIVER_CAD_V1.0.kicad_sch"),"utf8");
const files=generate(core,filter);
for(const [dest,key] of Object.entries({"PLL_RX_HIERARCHICAL_MASTER_V1.3.kicad_sch":"master","PLL_CORE_DIGITAL_V1.3.kicad_sch":"digital","PD_FILTER_DRIVER_V1.3.kicad_sch":"analog","sym-lib-table":"table"}))fs.writeFileSync(path.join(__dirname,dest),files[key],"utf8");
console.log(JSON.stringify({scope:"3_PAGE_HIERARCHICAL_RX_PLL_ONLY",core_symbols:files.core_count,analog_symbols:files.analog_count,pcb:"NOT_STARTED",fab_authorized:false,tx_authorized:false}));
