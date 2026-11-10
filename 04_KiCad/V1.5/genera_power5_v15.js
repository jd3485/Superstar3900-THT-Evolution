#!/usr/bin/env node
/* Deterministic native KiCad9 THT 5V supply candidate: schematic only, NO FAB / NO TX. */
const fs=require("fs"),path=require("path");
function buildSupply(){
 const NAME="THT_5V_POWER_DISTRIBUTION_V1.5",ROOT="8c15bcd1-faae-4e37-bf15-000000000001";
 let seq=1;const uid=()=>`8c15bcd1-faae-4e37-bf15-${String(++seq).padStart(12,"0")}`;
 const q=s=>JSON.stringify(String(s)),eff=(n=1)=>`(effects (font (size ${n} ${n})))`;
 const point=n=>Number(n.toFixed(2)), snap=n=>point(Math.round(n/1.27)*1.27);
 const pin=([n,label,type,x,y])=>`(pin ${type} line (at ${x} ${y} ${x<0?0:180}) (length 5.08) (name ${q(label)} ${eff()}) (number ${q(n)} ${eff()}))`;
 const rectangle=(left,top,right,bottom)=>`(rectangle (start ${left} ${top}) (end ${right} ${bottom}) (stroke (width 0.254) (type default)) (fill (type background)))`;
 const libs=[];
 function library(key,ref,val,fp,pins,shape,noBoard=false){
  libs.push(`(symbol ${q("THT_V15:"+key)} (pin_numbers (hide yes)) (pin_names (offset 0.76)) (in_bom ${noBoard?"no":"yes"}) (on_board ${noBoard?"no":"yes"})
(property "Reference" ${q(ref)} (at 0 15.24 0) ${eff()})
(property "Value" ${q(val)} (at 0 -15.24 0) ${eff()})
(property "Footprint" ${q(fp)} (at 0 0 0) (effects (font (size 1 1)) (hide yes)))
(symbol ${q(key+"_0_1")} ${shape})
(symbol ${q(key+"_1_1")} ${pins.map(pin).join("\n")})
)`);
 }
 library("L7805CV_TO220","U","L7805CV","Package_TO_SOT_THT:TO-220-3_Vertical",
    [["1","INPUT","power_in",-15.24,5.08],["2","GROUND","power_in",-15.24,-5.08],["3","OUTPUT","power_out",15.24,5.08]],rectangle(-10.16,10.16,10.16,-10.16));
 const two=[["1","1","passive",-5.08,0],["2","2","passive",5.08,0]];
 library("R_AXIAL","R","Resistor","Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",two,rectangle(-2.54,1.27,2.54,-1.27));
 library("C_DISC","C","Ceramic","Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm",two,rectangle(-1.27,2.54,1.27,-2.54));
 library("CP_RADIAL","C","Electrolytic","Capacitor_THT:CP_Radial_D6.3mm_P2.50mm",
  [["1","+","passive",-5.08,0],["2","-","passive",5.08,0]],rectangle(-2.54,2.54,2.54,-2.54));
 library("D_1N4007","D","1N4007","Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal",
  [["1","K","passive",-7.62,0],["2","A","passive",7.62,0]],rectangle(-3.81,1.27,3.81,-1.27));
 library("HEADER02","J","Header02","Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
  [["1","1","passive",-7.62,2.54],["2","2","passive",-7.62,-2.54]],rectangle(-3.81,5.08,3.81,-5.08));
 library("EXT_PWR_FLAG","PWR","EXT_SOURCE","",[["1","FLAG","power_out",-5.08,0]],rectangle(-2.54,2.54,2.54,-2.54),true);
 const sch=['(kicad_sch (version 20250114) (generator "tht_v15_supply_generator") (generator_version "9.0")',
 `(uuid ${q(ROOT)})`,'(paper "A3")',`(lib_symbols ${libs.join("\n")})`];
 function instance(key,ref,val,fp,x,y,nums,noBoard=false){
  x=snap(x);y=snap(y);
  sch.push(`(symbol (lib_id ${q("THT_V15:"+key)}) (at ${x} ${y} 0) (unit 1) (in_bom ${noBoard?"no":"yes"}) (on_board ${noBoard?"no":"yes"}) (dnp no) (uuid ${q(uid())})
 (property "Reference" ${q(ref)} (at ${x} ${point(y-13.97)} 0) ${eff()})
 (property "Value" ${q(val)} (at ${x} ${point(y+13.97)} 0) ${eff()})
 (property "Footprint" ${q(fp)} (at ${x} ${y} 0) (effects (font (size 1 1)) (hide yes)))
 ${nums.map(n=>`(pin ${q(n)} (uuid ${q(uid())}))`).join("\n")}
 (instances (project ${q(NAME)} (path ${q("/"+ROOT)} (reference ${q(ref)}) (unit 1)))))`);
 }
 function lab(net,x,y,dir){const a=snap(x),b=snap(y),c=snap(a+dir*5.08);
   sch.push(`(wire (pts (xy ${a} ${b}) (xy ${c} ${b})) (stroke (width 0) (type default)) (uuid ${q(uid())}))`);
   sch.push(`(label ${q(net)} (at ${c} ${b} 0) ${eff()} (uuid ${q(uid())}))`);
 }
 const Rfp="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal";
 const Cfp="Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm";
 const CPfp="Capacitor_THT:CP_Radial_D6.3mm_P2.50mm";
 const Jfp="Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical";
 const Dfp="Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal";
 instance("L7805CV_TO220","U601","ST L7805CV", "Package_TO_SOT_THT:TO-220-3_Vertical",132.08,76.2,["1","2","3"]);
 lab("+13V8_PROTECTED",116.84,71.12,-1);lab("GND",116.84,81.28,-1);lab("+5V_REG",147.32,71.12,1);
 function passive(ref,val,key,fp,x,y,a,b){
  instance(key,ref,val,fp,x,y,["1","2"]);lab(a,x-5.08,y,-1);lab(b,x+5.08,y,1);
 }
 function connector(ref,val,x,y,a,b){
  instance("HEADER02",ref,val,Jfp,x,y,["1","2"]);lab(a,x-7.62,y-2.54,-1);lab(b,x-7.62,y+2.54,-1);
 }
 connector("J601","PROTECTED_13V8_INPUT",53.34,73.66,"+13V8_PROTECTED","GND");
 passive("C600","330nF_50V","C_DISC",Cfp,81.28,109.22,"+13V8_PROTECTED","GND");
 passive("C601","47uF_35V","CP_RADIAL",CPfp,81.28,129.54,"+13V8_PROTECTED","GND");
 instance("D_1N4007","D601","1N4007",Dfp,132.08,109.22,["1","2"]);
 lab("+13V8_PROTECTED",132.08-7.62,109.22,-1);lab("+5V_REG",132.08+7.62,109.22,1);
 passive("C602","100nF_25V","C_DISC",Cfp,177.8,109.22,"+5V_REG","GND");
 passive("C603","47uF_16V","CP_RADIAL",CPfp,177.8,129.54,"+5V_REG","GND");
 connector("J605","5V_REG_TEST",248.92,73.66,"+5V_REG","GND");
 for(const [i,y,net] of [[1,170.18,"+5V_PLL"],[2,200.66,"VCC_VCO5"],[3,231.14,"VCC_BUF5"]]){
   passive(`R61${i}`,"1R_0.25W","R_AXIAL",Rfp,167.64,y,"+5V_REG",net);
   passive(`C61${i}`,"10uF_16V","CP_RADIAL",CPfp,218.44,y,net,"GND");
   passive(`C61${i+3}`,"100nF_25V","C_DISC",Cfp,248.92,y,net,"GND");
   connector(`J60${i+1}`,net+"_TEST",320.04,y,net,"GND");
 }
 instance("EXT_PWR_FLAG","PWR601","EXT13V8","",58.42,157.48,["1"],true);
 lab("+13V8_PROTECTED",53.34,157.48,-1);
 instance("EXT_PWR_FLAG","PWR602","EXT_GND","",58.42,187.96,["1"],true);
 lab("GND",53.34,187.96,-1);
 sch.push(`(text "V1.5 PILOT: 5V THT REGULATION ONLY, FROM ALREADY PROTECTED EXTERNAL 13.8V SOURCE. 3 ISOLATED RC BRANCHES.\\nR611/612/613=1 ohm: rail voltage and transient isolation depend on actual current; LOADS NOT QUALIFIED.\\nNo input fuse/TVS/polarity protection designed here. D601 only OUT-to-IN discharge path.\\nU601 TO220 tab is GND. Verify thermal at VIN max, true branch load and heatsink. NOT IN MASTER. NO FAB / NO TX." (at 64.77 269.24 0) ${eff(1.2)} (uuid ${q(uid())}))`);
 sch.push('(sheet_instances (path "/" (page "1")))','(embedded_fonts no)',')');
 const lib='(kicad_symbol_lib (version 20241209) (generator "tht_v15_supply_generator")\n'+libs.map(x=>x.replace('(symbol "THT_V15:','(symbol "')).join("\n")+'\n)\n';
 const table='(sym_lib_table\n (lib (name "THT_V15") (type "KiCad") (uri "${KIPRJMOD}/THT_V15.kicad_sym") (options "") (descr "THT 5V RF power distribution pilot"))\n)\n';
 return {schematic:sch.join("\n")+"\n",lib,table,device_count:20,net_count:6};
}
const x=buildSupply();for(const [file,contents] of Object.entries({"THT_5V_POWER_DISTRIBUTION_V1.5.kicad_sch":x.schematic,"THT_V15.kicad_sym":x.lib,"sym-lib-table":x.table}))fs.writeFileSync(path.join(__dirname,file),contents);
console.log(JSON.stringify({devices:x.device_count,expected_nets:x.net_count,scope:"BENCH_SUPPLY_PILOT_NOT_INTEGRATED",fab_authorized:false,tx_authorized:false}));
