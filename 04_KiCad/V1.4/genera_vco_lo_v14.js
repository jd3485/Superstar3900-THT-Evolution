#!/usr/bin/env node
/* Reproducible V1.4 FOUR-sheet KiCad9 THT VCO model-B candidate, NOT a qualified RF design. */
const fs=require("fs"),path=require("path");
function build(lib10,root13,dig13,ana13){
 const name="PLL_RX_HIERARCHICAL_MASTER_V1.4",uuidRoot="7b14bcd1-faae-4e37-bf14-000000000001",uuidVco="7b14bcd1-faae-4e37-bf14-000000000004",oldRoot="6a13bcd1-faae-4e37-bf13-000000000001";
 let seq=20;const uid=()=>`7b14bcd1-faae-4e37-bf14-${String(++seq).padStart(12,"0")}`,fmt=x=>String(+Number(x).toFixed(5));
 function forms(src){let out=[],start=0,level=0,quote=false,esc=false;for(let i=0;i<src.length;i++){const c=src[i];if(quote){if(esc)esc=false;else if(c==="\\")esc=true;else if(c==='"')quote=false;continue}if(c==='"'){quote=true;continue}if(c==="("){if(!level)start=i;level++}if(c===")"){level--;if(!level)out.push(src.slice(start,i+1));if(level<0)throw Error("unbalanced")}}if(level||quote)throw Error("unclosed");return out}
 const libItems=forms(lib10.trim().slice("(kicad_symbol_lib".length,-1));
 const libSym=k=>{let s=libItems.find(z=>z.startsWith(`(symbol "${k}"`));if(!s)throw Error("Missing "+k);return s};
 const rect=(w,h)=>`(rectangle (start ${-w} ${h}) (end ${w} ${-h}) (stroke (width 0.254) (type default)) (fill (type background)))`;
 const custom=(key,ref,fp,pins,shape)=>`(symbol "${key}" (pin_numbers (hide yes)) (pin_names (offset 0.76)) (in_bom yes) (on_board yes)
(property "Reference" "${ref}" (at 0 17.78 0) (effects (font (size 1 1))))
(property "Value" "${key}" (at 0 -17.78 0) (effects (font (size 1 1))))
(property "Footprint" "${fp}" (at 0 0 0) (effects (font (size 1 1)) (hide yes)))
(symbol "${key}_0_1" ${shape})
(symbol "${key}_1_1" ${pins.map(p=>`(pin ${p[2]} line (at ${p[3]} ${p[4]} ${p[3]<0?0:180}) (length 5.08) (name "${p[1]}" (effects (font (size 1 1)))) (number "${p[0]}" (effects (font (size 1 1)))))`).join("\n")})
)`;
 const npn=[[1,"E","passive",10.16,-5.08],[2,"B","input",-10.16,0],[3,"C","passive",10.16,5.08]];
 const dual=[[1,"A1","passive",-12.7,5.08],[2,"K_COMMON","passive",12.7,0],[3,"A2","passive",-12.7,-5.08]];
 const two=[[1,"1","passive",-5.08,0],[2,"2","passive",5.08,0]];
 const ac=[[1,"1A","input",-15.24,17.78],[2,"1Y","output",15.24,17.78],[3,"2A","input",-15.24,15.24],[4,"2Y","output",15.24,15.24],[5,"3A","input",-15.24,12.7],[6,"3Y","output",15.24,12.7],[7,"GND","power_in",-15.24,-17.78],[8,"4Y","output",15.24,10.16],[9,"4A","input",-15.24,10.16],[10,"5Y","output",15.24,7.62],[11,"5A","input",-15.24,7.62],[12,"6Y","output",15.24,5.08],[13,"6A","input",-15.24,5.08],[14,"VCC","power_in",-15.24,-15.24]];
 const original=["Resistor","Capacitor","Connector02","ExternalPowerFlag"].map(k=>libSym(k));
 const extras=[custom("NPN_2N3904_TO92","Q","Package_TO_SOT_THT:TO-92_Inline",npn,rect(5.08,7.62)),
 custom("DUAL_BB204G_TO92","D","Package_TO_SOT_THT:TO-92_Inline",dual,rect(7.62,10.16)),
 custom("L_RF_UNSELECTED","L","",two,rect(2.54,1.27)),
 custom("POLAR_C_THT","C","Capacitor_THT:CP_Radial_D5.0mm_P2.00mm",two,rect(2.54,1.27)),
 custom("SN74AC14N_DIP14","U","Package_DIP:DIP-14_W7.62mm",ac,rect(10.16,22.86))];
 const lib14=`(kicad_symbol_lib (version 20241209) (generator "tht_v14_generator")\n${extras.join("\n")}\n)\n`;
 const embed=[...original.map(k=>k.replace('(symbol "','(symbol "THT_V10:')),...extras.map(k=>k.replace('(symbol "','(symbol "THT_V14:'))].join("\n");
 const R=(ref,val,a,b)=>[ref,"THT_V10:Resistor",val,[[1,a],[2,b]]];
 const C=(ref,val,a,b)=>[ref,ref==="C500B"||ref==="C512"?"THT_V14:POLAR_C_THT":"THT_V10:Capacitor",val,[[1,a],[2,b]]];
 const J=(ref,val,a,b)=>[ref,"THT_V10:Connector02",val,[[1,a],[2,b]]];
 const parts=[
 ["Q501","THT_V14:NPN_2N3904_TO92","2N3904",[[1,"EMIT1"],[2,"BASE1"],[3,"TANK"]]],
 ["Q502","THT_V14:NPN_2N3904_TO92","2N3904",[[1,"EMIT2"],[2,"BASE2"],[3,"VCC_VCO5"]]],
 ["D501","THT_V14:DUAL_BB204G_TO92","BB204G",[[1,"VAR_A"],[2,"VTUNE_RAIL"],[3,"VAR_A"]]],
 ["U520","THT_V14:SN74AC14N_DIP14","SN74AC14N",[[1,"LO_BUF_INPUT"],[2,"INV_STAGE1"],[3,"INV_STAGE1"],[4,"DIGITAL_DRV"],[5,"GND"],[7,"GND"],[9,"GND"],[11,"GND"],[13,"GND"],[14,"VCC_BUF5"]]],
 ["L501","THT_V14:L_RF_UNSELECTED","166nH_MODEL",[[1,"VCC_VCO5"],[2,"TANK"]]],
 R("R501","33k","VCC_VCO5","BASE1"),R("R502","10k","BASE1","GND"),R("R503","1k2","EMIT1","GND"),R("R505","100k","VAR_A","GND"),
 R("R506","47k","VCC_VCO5","BASE2"),R("R507","22k","BASE2","GND"),R("R508","470","EMIT2","GND"),R("R509","1Meg","LO1_ANALOG_OUT","GND"),
 R("R510","47k","VCC_BUF5","LO_BUF_BIAS"),R("R511","47k","LO_BUF_BIAS","GND"),R("R512","100k","LO_BUF_BIAS","LO_BUF_INPUT"),R("R513","100","DIGITAL_DRV","LO1_CMOS_BUFFERED"),
 C("C500","100n","VCC_VCO5","GND"),C("C500B","10u","VCC_VCO5","GND"),C("C501","1n","BASE1","GND"),
 C("C502","68p","TANK","EMIT1"),C("C503","220p","EMIT1","GND"),C("C504","470p","TANK","VAR_A"),
 C("C505","100n","VTUNE_RAIL","GND"),C("C506","2p2","TANK","BASE2"),C("C507","100p","EMIT2","LO1_ANALOG_OUT"),
 C("C508","5p","TANK","GND"),C("C510","100p","LO1_ANALOG_OUT","LO_BUF_INPUT"),
 C("C511","100n","VCC_BUF5","GND"),C("C512","10u","VCC_BUF5","GND"),
 J("J520","EXT_5V_VCO","VCC_VCO5","GND"),J("J521","EXT_5V_BUF","VCC_BUF5","GND"),
 J("J522","LO_CMOS_MON","LO1_CMOS_BUFFERED","GND"),J("J523","LO_ANALOG_MON","LO1_ANALOG_OUT","GND"),
 J("J524","VTUNE_MON","VTUNE_RAIL","GND"),
 ["PWR520","THT_V10:ExternalPowerFlag","EXTERNAL_VCO5",[[1,"VCC_VCO5"]]],
 ["PWR521","THT_V10:ExternalPowerFlag","EXTERNAL_BUF5",[[1,"VCC_BUF5"]]]
 ];
 if(parts.length!==37)throw Error("Component count "+parts.length);
 const pinPos={
 "THT_V10:Resistor":{1:[-5.08,0],2:[5.08,0]},
 "THT_V10:Capacitor":{1:[-5.08,0],2:[5.08,0]},
 "THT_V10:Connector02":{1:[-7.62,2.54],2:[-7.62,-2.54]},
 "THT_V10:ExternalPowerFlag":{1:[-5.08,0]},
 "THT_V14:NPN_2N3904_TO92":Object.fromEntries(npn.map(p=>[p[0],[p[3],p[4]]])),
 "THT_V14:DUAL_BB204G_TO92":Object.fromEntries(dual.map(p=>[p[0],[p[3],p[4]]])),
 "THT_V14:SN74AC14N_DIP14":Object.fromEntries(ac.map(p=>[p[0],[p[3],p[4]]])),
 "THT_V14:L_RF_UNSELECTED":{1:[-5.08,0],2:[5.08,0]},
 "THT_V14:POLAR_C_THT":{1:[-5.08,0],2:[5.08,0]}
 };
 const footprints={
 "THT_V10:Resistor":"Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
 "THT_V10:Capacitor":"Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm",
 "THT_V10:Connector02":"Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
 "THT_V10:ExternalPowerFlag":"",
 "THT_V14:NPN_2N3904_TO92":"Package_TO_SOT_THT:TO-92_Inline",
 "THT_V14:DUAL_BB204G_TO92":"Package_TO_SOT_THT:TO-92_Inline",
 "THT_V14:SN74AC14N_DIP14":"Package_DIP:DIP-14_W7.62mm",
 "THT_V14:POLAR_C_THT":"Capacitor_THT:CP_Radial_D5.0mm_P2.00mm",
 "THT_V14:L_RF_UNSELECTED":""
 };
 let countLabels={GND:0,VTUNE_RAIL:0,LO1_CMOS_BUFFERED:0};let body=[];
 for(let idx=0;idx<parts.length;idx++){
  const [ref,id,value,connections]=parts[idx],x=76.2+(idx%5)*101.6,y=55.88+Math.floor(idx/5)*43.18,isFlag=ref.startsWith("PWR");
  body.push(`(symbol (lib_id "${id}") (at ${fmt(x)} ${fmt(y)} 0) (unit 1)
 (in_bom ${isFlag?"no":"yes"}) (on_board ${isFlag?"no":"yes"}) (dnp no) (uuid "${uid()}")
 (property "Reference" "${ref}" (at ${fmt(x)} ${fmt(y-16.51)} 0) (effects (font (size 1 1))))
 (property "Value" "${value}" (at ${fmt(x)} ${fmt(y+16.51)} 0) (effects (font (size 1 1))))
 (property "Footprint" "${footprints[id]}" (at ${fmt(x)} ${fmt(y)} 0) (effects (font (size 1 1)) (hide yes)))
 ${Object.keys(pinPos[id]).map(pin=>`(pin "${pin}" (uuid "${uid()}"))`).join("\n")}
 (instances (project "${name}" (path "/${uuidRoot}/${uuidVco}" (reference "${ref}") (unit 1))))
 )`);
  for(const [pin,net] of connections){
   const [px,py]=pinPos[id][pin],ax=x+px,ay=y-py,bx=ax+(px<0?-5.08:5.08);
   body.push(`(wire (pts (xy ${fmt(ax)} ${fmt(ay)}) (xy ${fmt(bx)} ${fmt(ay)})) (stroke (width 0) (type default)) (uuid "${uid()}"))`);
   let typ="label";
   if(Object.prototype.hasOwnProperty.call(countLabels,net)&&countLabels[net]++===0)typ="hierarchical_label";
   let shape=typ==="hierarchical_label"?` (shape ${net==="GND"?"passive":net==="VTUNE_RAIL"?"input":"output"})`:"";
   body.push(`(${typ} "${net}"${shape} (at ${fmt(bx)} ${fmt(ay)} 0) (effects (font (size 1 1))) (uuid "${uid()}"))`);
  }
  if(ref==="U520")for(const pin of [6,8,10,12]){const [px,py]=pinPos[id][pin];body.push(`(no_connect (at ${fmt(x+px)} ${fmt(y-py)}) (uuid "${uid()}"))`)}
 }
 const vco=`(kicad_sch (version 20250114) (generator "tht_v14_generator") (generator_version "9.0")
 (uuid "${uuidVco}") (paper "A2")
 (lib_symbols\n${embed}\n)
 ${body.join("\n")}
 (text "V1.4 SPICE model B CAD RECONSTRUCTION, not validated PLL. VCO 5V and BUF 5V separate EXTERNAL supplies. L501 FOOTPRINT UNDEFINED. NO FAB / NO TX." (at 76.2 389 0) (effects (font (size 1.27 1.27))) (uuid "${uid()}"))
 (sheet_instances (path "/${uuidRoot}/${uuidVco}" (page "4")))
 (embedded_fonts no)
 )\n`;
 const child=(src,net,shape)=>{const mark=`(label "${net}"`;if(!src.includes(mark))throw Error("Absent label "+net);return src.replaceAll("PLL_RX_HIERARCHICAL_MASTER_V1.3",name).replaceAll(oldRoot,uuidRoot).replace(mark,`(hierarchical_label "${net}" (shape ${shape})`)};
 const dig=child(dig13,"LO1_CMOS_BUFFERED","input"),ana=child(ana13,"VTUNE_RAIL","output");
 let root=root13.replaceAll("PLL_RX_HIERARCHICAL_MASTER_V1.3",name).replaceAll(oldRoot,uuidRoot)
  .replace('PLL_CORE_DIGITAL_V1.3.kicad_sch','PLL_CORE_DIGITAL_V1.4.kicad_sch')
  .replace('PD_FILTER_DRIVER_V1.3.kicad_sch','PD_FILTER_DRIVER_V1.4.kicad_sch')
  .replace('tht_v13_hierarchy_generator','tht_v14_hierarchy_generator');
 const rootParts=forms(root.trim().slice("(kicad_sch".length,-1));let count=0;let formsOut=[];
 for(let s of rootParts){
  if(s.startsWith("(text "))continue;
  if(s.startsWith("(sheet ")){
   count++;
   if(count===1)s=s.replace(`(instances (project "${name}"`,`(pin "LO1_CMOS_BUFFERED" input (at 43.18 109.22 180) (uuid "${uid()}") (effects (font (size 1.27 1.27)) (justify left)))\n (instances (project "${name}"`);
   if(count===2)s=s.replace(`(instances (project "${name}"`,`(pin "VTUNE_RAIL" output (at 264.16 109.22 0) (uuid "${uid()}") (effects (font (size 1.27 1.27)) (justify right)))\n (instances (project "${name}"`);
  }
  formsOut.push(s);
 }
 if(count!==2)throw Error("Expected 2 old sheets");
 const sheet=`(sheet (at 304.8 46.99) (size 86.36 101.6) (stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0)) (uuid "${uuidVco}")
(property "Sheetname" "RX_VCO_AND_LO_BUF" (at 304.8 45.72 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
(property "Sheetfile" "VCO_RX_AND_LOBUF_V1.4.kicad_sch" (at 304.8 149.86 0) (effects (font (size 1.27 1.27)) (justify left top)))
(pin "GND" passive (at 304.8 87.63 180) (uuid "${uid()}") (effects (font (size 1.27 1.27)) (justify left)))
(pin "VTUNE_RAIL" input (at 304.8 109.22 180) (uuid "${uid()}") (effects (font (size 1.27 1.27)) (justify left)))
(pin "LO1_CMOS_BUFFERED" output (at 391.16 129.54 0) (uuid "${uid()}") (effects (font (size 1.27 1.27)) (justify right)))
(instances (project "${name}" (path "/${uuidRoot}" (page "4")))))`;
 const wire=coords=>`(wire (pts ${coords.map(p=>`(xy ${p[0]} ${p[1]})`).join(" ")}) (stroke (width 0) (type default)) (uuid "${uid()}"))`;
 formsOut.push(sheet,wire([[264.16,109.22],[304.8,109.22]]),
 `(junction (at 154.94 87.63) (diameter 0) (color 0 0 0 0) (uuid "${uid()}"))`,
 wire([[154.94,87.63],[154.94,165.1]]),wire([[154.94,165.1],[292.1,165.1]]),
 wire([[292.1,165.1],[292.1,87.63]]),wire([[292.1,87.63],[304.8,87.63]]),
 wire([[391.16,129.54],[402.59,129.54]]),wire([[402.59,129.54],[402.59,27.94]]),
 wire([[402.59,27.94],[30.48,27.94]]),wire([[30.48,27.94],[30.48,109.22]]),wire([[30.48,109.22],[43.18,109.22]]),
 `(text "V1.4 FOUR SHEETS: candidate VCO B + provisional AC14 conditioner connected to U402 clock.\\nRF performance, +5V supplies, L501 footprint, phase margin and hardware unverified. NO FAB / NO TX." (at 50.8 195.58 0) (effects (font (size 1.27 1.27))) (uuid "${uid()}"))`);
 const master="(kicad_sch\n"+formsOut.join("\n")+"\n)\n";
 const table='(sym_lib_table\n (lib (name "THT_V10") (type "KiCad") (uri "${KIPRJMOD}/../V1.0/THT_V10.kicad_sym") (options "") (descr "THT original analog"))\n (lib (name "THT_V11") (type "KiCad") (uri "${KIPRJMOD}/../V1.1/THT_V11.kicad_sym") (options "") (descr "THT original PLL"))\n (lib (name "THT_V14") (type "KiCad") (uri "${KIPRJMOD}/THT_V14.kicad_sym") (options "") (descr "THT VCO candidate BB204G + AC14 pin verified"))\n)\n';
 return {master,dig,ana,vco,lib14,table,count:parts.length,nets:[...new Set(parts.flatMap(p=>p[3].map(n=>n[1])))].length};
}
const base=path.resolve(__dirname,"../..");
const rd=p=>fs.readFileSync(path.join(base,p),"utf8");
const a=build(rd("04_KiCad/V1.0/THT_V10.kicad_sym"),rd("04_KiCad/V1.3/PLL_RX_HIERARCHICAL_MASTER_V1.3.kicad_sch"),rd("04_KiCad/V1.3/PLL_CORE_DIGITAL_V1.3.kicad_sch"),rd("04_KiCad/V1.3/PD_FILTER_DRIVER_V1.3.kicad_sch"));
for(const [k,v] of Object.entries({"PLL_RX_HIERARCHICAL_MASTER_V1.4.kicad_sch":a.master,"PLL_CORE_DIGITAL_V1.4.kicad_sch":a.dig,"PD_FILTER_DRIVER_V1.4.kicad_sch":a.ana,"VCO_RX_AND_LOBUF_V1.4.kicad_sch":a.vco,"THT_V14.kicad_sym":a.lib14,"sym-lib-table":a.table}))fs.writeFileSync(path.join(__dirname,k),v,"utf8");
console.log(JSON.stringify({scope:"FOUR_SHEET_CANDIDATE_ONLY",new_components:a.count,new_nets:a.nets,pcb_drc:"NOT_RUN",fab_authorized:false,tx_authorized:false}));
