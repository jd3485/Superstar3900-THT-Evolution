#!/usr/bin/env node
/* V2.0 seven-sheet KiCad9 CAD derives all historical six child sheets byte-for-byte
 * from existing V1.9 sources. --check re-renders exact files. No hardware qualification.
 */
const fs=require("fs"),path=require("path"),assert=require("assert");
function buildV20(src){
 const OLD="PLL_RX_HIERARCHICAL_MASTER_V1.9",NEW="PLL_RX_HIERARCHICAL_MASTER_V2.0";
 const ROOT="7b14bcd1-faae-4e37-bf14-000000000001",SHEET="c020bcd1-faae-4e37-bf20-000000000007";
 const eff="(effects (font (size 1 1)))",footR="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal";
 let counter=0;const uuid=()=>`c020bcd1-faae-4e37-bf20-${String(++counter).padStart(12,"0")}`;
 const pinsMC=[["1","SW_COLLECTOR","passive",15.24,17.78],["2","SW_EMITTER","passive",15.24,10.16],
 ["3","TIMING_CT","passive",-15.24,-10.16],["4","GND","power_in",-15.24,-20.32],
 ["5","COMP_IN_MINUS","input",-15.24,0],["6","VCC","power_in",-15.24,20.32],
 ["7","I_PK_SENSE","input",-15.24,12.7],["8","DRIVER_COLLECTOR","passive",15.24,-12.7]];
 const pinsLM=[["1","ADJUST","input",-12.7,-10.16],["2","OUTPUT_TAB","power_out",12.7,0],["3","INPUT","power_in",-12.7,10.16]];
 const two=[["1","P1","passive",-7.62,0],["2","P2","passive",7.62,0]];
 const dia=[["1","CATHODE","passive",7.62,0],["2","ANODE","passive",-7.62,0]];
 const flag=[["1","ERC_SOURCE_NOT_HARDWARE","power_out",-5.08,0]];
 function sym(name,ref,fp,ps,w=5.08,h=5.08,onboard=true){
  const pins=ps.map(p=>`(pin ${p[2]} line (at ${p[3]} ${p[4]} ${p[3]<0?0:180}) (length 5.08) (name "${p[1]}" ${eff}) (number "${p[0]}" ${eff}))`).join("\n");
  const pinNames=ps.length===2?"(pin_names (offset 0.76) (hide yes))":"(pin_names (offset 0.76))";
  return `(symbol "${name}" (pin_numbers (hide yes)) ${pinNames} (in_bom ${onboard?"yes":"no"}) (on_board ${onboard?"yes":"no"})
(property "Reference" "${ref}" (at 0 15.24 0) ${eff})
(property "Value" "${name}" (at 0 -15.24 0) ${eff})
(property "Footprint" "${fp}" (at 0 0 0) (effects (font (size 1 1)) (hide yes)))
(symbol "${name}_0_1" (rectangle (start ${-w} ${h}) (end ${w} ${-h}) (stroke (width 0.254) (type default)) (fill (type background))))
(symbol "${name}_1_1" ${pins})
)`;
 }
 const descriptors=[
 ["MC34063ABN_DIP8","U","Package_DIP:DIP-8_W7.62mm",pinsMC,10.16,25.4],
 ["LM317T_TO220","U","Package_TO_SOT_THT:TO-220-3_Vertical",pinsLM,10.16,15.24],
 ["R_AXIAL_THT","R",footR,two,4,2.54],
 ["C_AXIAL_THT","C","",two,4,2.54],
 ["L_RADIAL_THT","L","",two,4,3.81],
 ["D_SCHOTTKY_1N5819","D","Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal",dia,5.08,3.81],
 ["D_1N4007","D","Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal",dia,5.08,3.81],
 ["PWR_FLAG_ERC","PWR","",flag,2.54,2.54]
 ];
 const lib=(prefix=false)=>descriptors.map(([name,ref,fp,ps,w,h])=>{
  const z=sym(name,ref,fp,ps,w,h,name!=="PWR_FLAG_ERC");
  return prefix?z.replace('(symbol "','(symbol "THT_V20:'):z;
 }).join("\n");
 const library=`(kicad_symbol_lib (version 20241209) (generator "tht_v20_boost_vtune_generator")\n${lib()}\n)\n`;
 const fpDiode="Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal";
 const fpCapSmall="Capacitor_THT:CP_Radial_D5.0mm_P2.00mm";
 const fpCapLarge="Capacitor_THT:CP_Radial_D12.5mm_P5.00mm";
 const fpCapMid="Capacitor_THT:CP_Radial_D8.0mm_P3.50mm";
 const fpCapCer="Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm";
 let child=`(kicad_sch (version 20250114) (generator "tht_v20_boost_vtune_generator") (generator_version "9.0")
(uuid "${SHEET}")
(paper "A2")
(lib_symbols\n${lib(true)}\n)
`;
 const ins=[];
 const wire=(x,y,a,b)=>ins.push(`(wire (pts (xy ${x} ${y}) (xy ${a} ${b})) (stroke (width 0) (type default)) (uuid "${uuid()}"))`);
 const label=(name,x,y)=>ins.push(`(label "${name}" (at ${x} ${y} 0) ${eff} (uuid "${uuid()}"))`);
 function place(symname,ref,val,fp,x,y,ps,nets,onboard=true){
  const propOffset=(symname==="MC34063ABN_DIP8"||symname==="LM317T_TO220")?35.56:12.7;
  ins.push(`(symbol (lib_id "THT_V20:${symname}") (at ${x} ${y} 0) (unit 1) (in_bom ${onboard?"yes":"no"}) (on_board ${onboard?"yes":"no"}) (dnp no) (uuid "${uuid()}")
(property "Reference" "${ref}" (at ${x} ${+(y-propOffset).toFixed(2)} 0) ${eff})
(property "Value" "${val}" (at ${x} ${+(y+propOffset).toFixed(2)} 0) ${eff})
(property "Footprint" "${fp}" (at ${x} ${y} 0) (effects (font (size 1 1)) (hide yes)))
${ps.map(p=>`(pin "${p[0]}" (uuid "${uuid()}"))`).join("\n")}
(instances (project "${NEW}" (path "/${ROOT}/${SHEET}" (reference "${ref}") (unit 1)))))`);
  if(nets.length!==ps.length)throw Error("Pin-net mapping mismatch: "+ref);
  for(let i=0;i<ps.length;i++){
   if(nets[i]===null)continue;
   const p=ps[i],px=+(x+p[3]).toFixed(2),py=+(y-p[4]).toFixed(2),edge=+(px+(p[3]<0?-5.08:5.08)).toFixed(2);
   wire(px,py,edge,py);label(nets[i],edge,py);
  }
 }
 const coords=[63.5,99.06,132.08,167.64,201.93,236.22,269.24]; // component rows
 place("MC34063ABN_DIP8","U911","ST_MC34063ABN_DIP8_STEUP_28V","Package_DIP:DIP-8_W7.62mm",149.86,114.3,pinsMC,
 ["SW20_NODE","GND","BOOST_CT","GND","BOOST_FB","+13V8_PROTECTED","BOOST_SENSE","DRIVER_BIAS"]);
 place("LM317T_TO220","U912","ONSEMI_LM317T_20V_ADJ_OUT2_TAB","Package_TO_SOT_THT:TO-220-3_Vertical",281.94,114.3,pinsLM,
 ["ADJ20","VREG20_RAW","VBOOST28"]);
 const rs=[
 ["R920","1R0_0p5W_PEAK_LIM","+13V8_PROTECTED","BOOST_SENSE","Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal"],
 ["R921","180R_DRIVER_BIAS","BOOST_SENSE","DRIVER_BIAS",footR],
 ["R922","47k_1pct_BOOST_FB","VBOOST28","BOOST_FB",footR],
 ["R923","2k2_1pct_BOOST_FB","BOOST_FB","GND",footR],
 ["R924","240R_1pct_LM317","VREG20_RAW","ADJ20",footR],
 ["R925","3k57_1pct_LM317","ADJ20","GND",footR],
 ["R926","10R_ISO_0p5W","VREG20_RAW","VANA20_FILT","Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal"],
 ["R927","2k2_0p5W_LM317_MIN_LOAD","VREG20_RAW","GND","Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal"]
 ];
 rs.forEach((r,i)=>place("R_AXIAL_THT",r[0],r[1],r[4],i<4?76.2:342.9,coords[i%4],two,[r[2],r[3]]));
 const cs=[
 ["C920","100u_25V_INPUT",fpCapMid,"+13V8_PROTECTED","GND"],
 ["C921","100n_50V_INPUT",fpCapCer,"+13V8_PROTECTED","GND"],
 ["C922","1n5_50V_CT",fpCapCer,"BOOST_CT","GND"],
 ["C923","330u_50V_BOOST",fpCapLarge,"VBOOST28","GND"],
 ["C924","100n_50V_BOOST",fpCapCer,"VBOOST28","GND"],
 ["C925","10u_50V_LM317_IN",fpCapSmall,"VBOOST28","GND"],
 ["C926","10u_35V_LM317_OUT",fpCapSmall,"VREG20_RAW","GND"],
 ["C927","10u_35V_ADJUST",fpCapSmall,"ADJ20","GND"],
 ["C928","100u_35V_ANALOG",fpCapMid,"VANA20_FILT","GND"],
 ["C929","100n_50V_ANALOG",fpCapCer,"VANA20_FILT","GND"]
 ];
 cs.forEach((c,i)=>place("C_AXIAL_THT",c[0],c[1],c[2],i<5?200.66:254,44.45+(i%5)*43.18,two,[c[3],c[4]]));
 place("L_RADIAL_THT","L920","BOURNS_RLB0914-681KL_680uH_490mA_THT_FOOTPRINT_TBD","",120.65,201.93,two,["BOOST_SENSE","SW20_NODE"]);
 place("D_SCHOTTKY_1N5819","D920","VISHAY_1N5819_A2_SWITCH_K1_BOOST",fpDiode,149.86,201.93,dia,["VBOOST28","SW20_NODE"]);
 place("D_1N4007","D921","1N4007_LM317_OUT_A2_IN_K1",fpDiode,281.94,201.93,dia,["VBOOST28","VREG20_RAW"]);
 place("D_1N4007","D922","1N4007_LM317_ADJ_A2_OUT_K1",fpDiode,281.94,241.3,dia,["VREG20_RAW","ADJ20"]);
 place("PWR_FLAG_ERC","PWR920","BOOST_SOURCE_KICAD_ERC_ONLY_NOT_HARDWARE","",331.47,254,flag,["VBOOST28"],false);
 // hierarchy wires are independent from local functional labels and pin stubs
 ins.push(`(hierarchical_label "+13V8_PROTECTED" (shape passive) (at 43.18 50.8 0) ${eff} (uuid "${uuid()}"))`);
 wire(43.18,50.8,50.8,50.8);label("+13V8_PROTECTED",50.8,50.8);
 ins.push(`(hierarchical_label "GND" (shape passive) (at 43.18 63.5 0) ${eff} (uuid "${uuid()}"))`);
 wire(43.18,63.5,50.8,63.5);label("GND",50.8,63.5);
 ins.push(`(hierarchical_label "VANA20_FILT" (shape passive) (at 391.16 76.2 180) ${eff} (uuid "${uuid()}"))`);
 wire(383.54,76.2,391.16,76.2);label("VANA20_FILT",383.54,76.2);
 ins.push(`(text "V2.0 THT PILOT ONLY: MC34063ABN DIP8 boost ~28V -> LM317T TO220 ~20V -> R926/C928 analog filter.\\nInput +13V8_PROTECTED is from V1.9 Q801 power cut-off; no vehicle/long transient qualification.\\nU911 p1 switch, p2 GND, p3 CT, p4 GND, p5 FB, p6 VCC, p7 Ipk, p8 driver collector.\\nU912 p1 ADJ, p2 OUTPUT/TAB (not GND), p3 INPUT. R927 explicit min-load candidate.\\nL920 680uH Bourns THT footprint UNSELECTED; switching EMI/RF coupling, saturation, current, boot,\\nboost/317 dropout and protection diode polarities NOT proven by vendor model or hardware. NO FAB / NO TX." (at 45.72 281.94 0) ${eff} (uuid "${uuid()}"))`);
 child+=ins.join("\n")+
 `\n(sheet_instances (path "/${ROOT}/${SHEET}" (page "7")))\n(embedded_fonts no)\n)\n`;
 // convert inherited native KiCad 9 6-sheet baseline without modifying sources
 const migrate=t=>t.replaceAll(`(project "${OLD}"`,`(project "${NEW}"`);
 let root=migrate(src[0]).replaceAll("_V1.9.kicad_sch","_V2.0.kicad_sch")
   .replace("V1.9 SIX SHEETS","V2.0 SEVEN SHEETS")
   .replace("RF performance, +5V supplies, L501 footprint, phase margin and hardware unverified.","Boost/LM317 pilot integrated; RF phase margin and PCB/hardware still unverified.");
 const parentEff="(effects (font (size 1.27 1.27)))";
 const rootThings=[
 `(sheet (at 304.8 208.28) (size 86.36 71.12) (stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0)) (uuid "${SHEET}")
 (property "Sheetname" "PWR20_VTUNE_BOOST_LDO" (at 304.8 207.01 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
 (property "Sheetfile" "POWER20_VTUNE_BOOST_LDO_V2.0.kicad_sch" (at 304.8 280.67 0) (effects (font (size 1.27 1.27)) (justify left top)))
 (pin "+13V8_PROTECTED" passive (at 304.8 228.6 180) (uuid "${uuid()}") (effects (font (size 1.27 1.27)) (justify left)))
 (pin "GND" passive (at 304.8 254 180) (uuid "${uuid()}") (effects (font (size 1.27 1.27)) (justify left)))
 (pin "VANA20_FILT" passive (at 391.16 241.3 0) (uuid "${uuid()}") (effects (font (size 1.27 1.27)) (justify right)))
 (instances (project "${NEW}" (path "/${ROOT}" (page "7")))))`,
 `(wire (pts (xy 294.64 228.6) (xy 304.8 228.6)) (stroke (width 0) (type default)) (uuid "${uuid()}"))`,
 `(label "+13V8_PROTECTED" (at 294.64 228.6 0) ${parentEff} (uuid "${uuid()}"))`,
 `(wire (pts (xy 294.64 254) (xy 304.8 254)) (stroke (width 0) (type default)) (uuid "${uuid()}"))`,
 `(label "GND" (at 294.64 254 0) ${parentEff} (uuid "${uuid()}"))`,
 `(wire (pts (xy 391.16 241.3) (xy 401.32 241.3)) (stroke (width 0) (type default)) (uuid "${uuid()}"))`,
 `(label "VANA20_FILT" (at 401.32 241.3 0) ${parentEff} (uuid "${uuid()}"))`,
 `(label "+13V8_PROTECTED" (at 152.4 228.6 0) ${parentEff} (uuid "${uuid()}"))`,
 `(label "GND" (at 200.66 165.1 0) ${parentEff} (uuid "${uuid()}"))`,
 `(wire (pts (xy 167.64 116.84) (xy 177.8 116.84)) (stroke (width 0) (type default)) (uuid "${uuid()}"))`,
 `(label "VANA20_FILT" (at 167.64 116.84 0) ${parentEff} (uuid "${uuid()}"))`
 ];
 if(!root.includes('(sheet_instances (path "/" (page "1")))'))throw Error("Master root format unexpected");
 // add PD hierarchy pin just before sheet instances of PD
 const pdSheetAnchor='(instances (project "'+NEW+'" (path "/'+ROOT+'" (page "3")))))';
 if(root.split(pdSheetAnchor).length!==2)throw Error("PD master sheet instances anchor not unique");
 root=root.replace(pdSheetAnchor,
   `(pin "VANA20_FILT" passive (at 177.8 116.84 180) (uuid "${uuid()}") (effects (font (size 1.27 1.27)) (justify left)))\n`+pdSheetAnchor);
 root=root.trimEnd();
 if(!root.endsWith(")"))throw Error("Root not closed");
 root=root.slice(0,-1)+"\n"+rootThings.join("\n")+"\n)\n";
 let pd=migrate(src[2]);
 const originalPD='(label "VANA20_FILT" (at 157.48 87.63 0)';
 if(pd.split(originalPD).length!==2)throw Error("PD local rail label anchor unexpectedly changed");
 pd=pd.replace(originalPD,'(hierarchical_label "VANA20_FILT" (shape passive) (at 157.48 87.63 0)');
 const symtab=src[6].replaceAll('${KIPRJMOD}/../V1.8/THT_V18.kicad_sym','${KIPRJMOD}/../V1.8/THT_V18.kicad_sym')
 + " "; // updated below: remove final closing and add V20 entry.
 const tab=src[6].trimEnd().replace(/\)\s*$/,' (lib (name "THT_V20") (type "KiCad") (uri "${KIPRJMOD}/THT_V20.kicad_sym") (options "") (descr "MC34063ABN DIP8 boost and LM317 THT VTUNE rail"))\n)\n');
 return {root,core:migrate(src[1]),pd,vco:migrate(src[3]).replaceAll("C500B","C509"),power5:migrate(src[4]),input:migrate(src[5]),power20:child,library,symtab:tab};
}
const repo=path.resolve(__dirname,"../..");
const sources=["04_KiCad/V1.9/PLL_RX_HIERARCHICAL_MASTER_V1.9.kicad_sch","04_KiCad/V1.9/PLL_CORE_DIGITAL_V1.9.kicad_sch","04_KiCad/V1.9/PD_FILTER_DRIVER_V1.9.kicad_sch","04_KiCad/V1.9/VCO_RX_AND_LOBUF_V1.9.kicad_sch","04_KiCad/V1.9/POWER5_DISTRIBUTION_V1.9.kicad_sch","04_KiCad/V1.9/INPUT_FUSE_REVERSE_TVS_OVP_V1.9.kicad_sch","04_KiCad/V1.9/sym-lib-table"];
const old=sources.map(x=>fs.readFileSync(path.join(repo,x),"utf8"));
const v=buildV20(old);
const files={"PLL_RX_HIERARCHICAL_MASTER_V2.0.kicad_sch":v.root,
"PLL_CORE_DIGITAL_V2.0.kicad_sch":v.core,
"PD_FILTER_DRIVER_V2.0.kicad_sch":v.pd,
"VCO_RX_AND_LOBUF_V2.0.kicad_sch":v.vco,
"POWER5_DISTRIBUTION_V2.0.kicad_sch":v.power5,
"INPUT_FUSE_REVERSE_TVS_OVP_V2.0.kicad_sch":v.input,
"POWER20_VTUNE_BOOST_LDO_V2.0.kicad_sch":v.power20,
"THT_V20.kicad_sym":v.library,"sym-lib-table":v.symtab};
for(const [file,value] of Object.entries(files)){
 const dst=path.join(__dirname,file);
 if(process.argv.includes("--check"))assert.strictEqual(fs.readFileSync(dst,"utf8"),value,file+" not reproducible");
 else if(process.argv.includes("--write"))fs.writeFileSync(dst,value);
 else throw Error("Use --check or --write");
}
console.log(JSON.stringify({status:"PASS_SEVEN_SHEET_NATIVE_SOURCE_REPRODUCTION",
files:Object.keys(files).length,boost:"MC34063ABN nominal 28V",post:"LM317T candidate 20V",
hardware_qualified:false,pcb:false,fab_authorized:false,tx_authorized:false}));
