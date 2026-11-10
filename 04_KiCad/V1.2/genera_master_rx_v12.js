#!/usr/bin/env node
/* Deterministic flat KiCad9 pilot integration of THT CAD-01+CAD-02.
   DO NOT substitute this for final hierarchical master, PCB, PLL lock test or approval to fabricate/transmit. */
const fs=require("fs"),path=require("path");
function generateMaster(core,filter){
 const ROOT="5c01bcb6-faae-4e37-bf12-000000000001",NAME="PLL_RX_MASTER_CAD_V1.2",DX=300,DY=10;
 function forms(src){
  const result=[];let start=-1,level=0,quoted=false,escape=false;
  for(let i=0;i<src.length;i++){
   const c=src[i];
   if(quoted){if(escape)escape=false;else if(c==="\\")escape=true;else if(c==='"')quoted=false;continue;}
   if(c==='"'){quoted=true;continue;}
   if(c==="("){if(level===0)start=i;level++;}
   if(c===")"){level--;if(level===0){result.push(src.slice(start,i+1));start=-1;}if(level<0)throw Error("Unbalanced parentheses");}
  }
  if(level!==0||quoted)throw Error("Unclosed expression");return result;
 }
 function children(src,head){
  const prefix="("+head;if(!src.trimStart().startsWith(prefix))throw Error("Expected "+head);
  return forms(src.trim().slice(prefix.length,-1));
 }
 const a=children(core,"kicad_sch"),b=children(filter,"kicad_sch");
 const libsA=a.find(x=>x.startsWith("(lib_symbols")),libsB=b.find(x=>x.startsWith("(lib_symbols"));
 if(!libsA||!libsB)throw Error("Missing native symbol definitions");
 const mergedLibs=children(libsA,"lib_symbols").concat(children(libsB,"lib_symbols"));
 const IDs=mergedLibs.map(x=>{const m=x.match(/^\(symbol "([^"]+)"/);return m?m[1]:"";});
 if(IDs.length!==new Set(IDs).size)throw Error("Duplicate symbol identifiers");
 const drop=new Set(["version","generator","generator_version","uuid","paper","lib_symbols","sheet_instances","embedded_fonts"]);
 const body=x=>x.filter(c=>{const k=/^\(([\w-]+)/.exec(c);return k&&!drop.has(k[1])});
 const coreBody=body(a).filter(s=>!s.startsWith("(text "));
 let filtBody=body(b).filter(s=>!s.startsWith("(text "));
 // One external ground power flag per actual GND net: remove the duplicated CAD-01 PWR902 flag and its detached wire+label.
 const removed=[];
 filtBody=filtBody.filter(s=>{
  const gone = (s.startsWith("(symbol ")&&s.includes('(property "Reference" "PWR902"')) ||
   (s.startsWith("(wire ")&&s.includes("(xy 129.54 156.21)")) ||
   (s.startsWith("(label ")&&s.includes('(label "GND" (at 124.46 156.21'));
  if(gone)removed.push(s.slice(0,75));return !gone;
 });
 if(removed.length!==3)throw Error("Expected to remove PWR902 symbol+wire+label; got "+removed.length);
 function fmt(n){return String(+Number(n).toFixed(5))}
 function shift(s){
  s=s.replace(/\(xy (-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)/g,(_,x,y)=>`(xy ${fmt(Number(x)+DX)} ${fmt(Number(y)+DY)}`);
  s=s.replace(/\(at (-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)(?=[\s)])/g,(_,x,y)=>`(at ${fmt(Number(x)+DX)} ${fmt(Number(y)+DY)}`);
  return s;
 }
 function instance(s,originalName,uuid){
  return s.replaceAll(`(project "${originalName}"`,`(project "${NAME}"`).replaceAll(`(path "/${uuid}"`,`(path "/${ROOT}"`);
 }
 const coreInst=coreBody.map(s=>instance(s,"PLL_CORE_RX_CAD_V1.1","4bbbe51d-3f7d-4f18-aa11-000000000001"));
 const filtInst=filtBody.map(s=>instance(shift(s),"PLL_FILTER_DRIVER_CAD_V1.0","3d86fc80-36d7-4d76-a243-000000000001"));
 if(!coreInst.some(x=>x.includes('"U401"'))||!filtInst.some(x=>x.includes('"R901"')))throw Error("Missing pins");
 const title='(text "V1.2 REAL FLAT INTEGRATION RX ONLY: U401 pin4 PDout is ONE ELECTRICAL NET with R901 pin1 via PLL_PDOUT_3STATE.\\n+5V_PLL and VANA20_FILT are still separate EXTERNAL rails, LO1 CMOS and N bus EXTERNAL. VTUNE external to unbuilt VCO.\\nJ401 and J901 are temporary test headers and NOT final production ports; not a compensated closed PLL. NO FAB / NO TX." (at 265 360 0) (effects (font (size 1.35 1.35))) (uuid "5c01bcb6-faae-4e37-bf12-000000000002"))';
 const schematic=['(kicad_sch (version 20250114) (generator "tht_v12_master_generator") (generator_version "9.0")',`(uuid "${ROOT}")`,'(paper "A2")',`(lib_symbols\n${mergedLibs.join("\n")}\n)`,...coreInst,...filtInst,title,'(sheet_instances (path "/" (page "1")))','(embedded_fonts no)',')'].join("\n")+"\n";
 const table='(sym_lib_table\n (lib (name "THT_V11") (type "KiCad") (uri "${KIPRJMOD}/../V1.1/THT_V11.kicad_sym") (options "") (descr "CAD02 original KiCad symbols"))\n (lib (name "THT_V10") (type "KiCad") (uri "${KIPRJMOD}/../V1.0/THT_V10.kicad_sym") (options "") (descr "CAD01 original KiCad symbols"))\n)\n';
 return {schematic,table,components:coreInst.filter(x=>x.startsWith("(symbol ")).length+filtInst.filter(x=>x.startsWith("(symbol ")).length,labels:new Set([...schematic.matchAll(/\(label "([^"]+)"/g)].map(x=>x[1])).size,shared_net:['PLL_PDOUT_3STATE','GND']};
}
const root=path.resolve(__dirname,"../..");
const core=fs.readFileSync(path.join(root,"04_KiCad/V1.1/PLL_CORE_RX_CAD_V1.1.kicad_sch"),"utf8");
const filter=fs.readFileSync(path.join(root,"04_KiCad/V1.0/PLL_FILTER_DRIVER_CAD_V1.0.kicad_sch"),"utf8");
const out=generateMaster(core,filter);
fs.writeFileSync(path.join(__dirname,"PLL_RX_MASTER_CAD_V1.2.kicad_sch"),out.schematic,"utf8");
fs.writeFileSync(path.join(__dirname,"sym-lib-table"),out.table,"utf8");
console.log(JSON.stringify({components:out.components,labels:out.labels,scope:"FLAT_RX_PLL_PARTIAL",fab_authorized:false,tx_authorized:false}));
