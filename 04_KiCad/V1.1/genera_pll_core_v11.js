#!/usr/bin/env node
/* Deterministic KiCad 9 V1.1 RX-only generator; no fabrication or TX. */
const fs=require("fs"),path=require("path");
function generate(){
 const DOC="PLL_CORE_RX_CAD_V1.1",ROOT_UUID="4bbbe51d-3f7d-4f18-aa11-000000000001";
 let num=1;const uid=()=>`4bbbe51d-3f7d-4f18-aa11-${String(++num).padStart(12,"0")}`,q=s=>JSON.stringify(String(s)),e=s=>`(effects (font (size ${s||1} ${s||1})))`;
 const pin=p=>`(pin ${p[2]} line (at ${p[3]} ${p[4]} ${p[5]}) (length 5.08) (name ${q(p[1])} ${e(1)}) (number ${q(p[0])} ${e(1)}))`;
 const rect=(a,b,c,d)=>`(rectangle (start ${a} ${b}) (end ${c} ${d}) (stroke (width 0.254) (type default)) (fill (type background)))`;
 const libs=[],all=[];
 function addlib(name,ref,val,fp,pins,shape,nb=false){
  libs.push(`(symbol ${q("THT_V11:"+name)} (pin_numbers (hide yes)) (pin_names (offset 0.76)) (in_bom ${nb?"no":"yes"}) (on_board ${nb?"no":"yes"})
(property "Reference" ${q(ref)} (at 0 20 0) ${e(1)})
(property "Value" ${q(val)} (at 0 -20 0) ${e(1)})
(property "Footprint" ${q(fp)} (at 0 0 0) (effects (font (size 1 1)) (hide yes)))
(symbol ${q(name+"_0_1")} ${shape})
(symbol ${q(name+"_1_1")} ${pins.map(pin).join("\n")})
)`);
 }
 const u401names=["fin","VSS","VDD","PDout","RA0","RA1","RA2","phiR","phiV","fV","N0","N1","N2","N3","N4","N5","N6","N7","N8","N9","T/R","N12","N13","N10","N11","OSCout","OSCin","LD"];
 const u401=u401names.map((name,i)=>{const n=i+1,left=n<=14,k=left?n-1:28-n;const type=[2,3].includes(n)?"power_in":n===4?"tri_state":[8,9,10,26,28].includes(n)?"output":"input";return [String(n),name,type,left?-15.24:15.24,Number((17.78-k*2.54).toFixed(2)),left?0:180]});
 const u402=[["1","/CLR1","input",-15.24,12.7,0],["2","D1","input",-15.24,10.16,0],["3","CLK1","input",-15.24,7.62,0],["4","/PRE1","input",-15.24,5.08,0],["7","GND","power_in",-15.24,0,0],["11","CLK2","input",-15.24,-5.08,0],["12","D2","input",-15.24,-7.62,0],["5","Q1","output",15.24,12.7,180],["6","/Q1","output",15.24,10.16,180],["8","/Q2","output",15.24,7.62,180],["9","Q2","output",15.24,5.08,180],["10","/PRE2","input",15.24,0,180],["13","/CLR2","input",15.24,-5.08,180],["14","VCC","power_in",15.24,-7.62,180]];
 addlib("ML145151YP_PDIP28","U","ML145151YP","Package_DIP:DIP-28_W15.24mm",u401,rect(-10.16,20.32,10.16,-20.32));
 addlib("TC74AC74P_DIP14","U","TC74AC74P(F)","Package_DIP:DIP-14_W7.62mm",u402,rect(-10.16,15.24,10.16,-12.7));
 const twopin=[["1","~","passive",-5.08,0,0],["2","~","passive",5.08,0,180]];
 addlib("Resistor","R","R","Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",twopin,rect(-2.54,1.27,2.54,-1.27));
 addlib("Capacitor","C","C","Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm",twopin,rect(-1.27,2.54,1.27,-2.54));
 addlib("Crystal","Y","10.240MHz","Crystal:Crystal_HC49-U_Vertical",twopin,rect(-2.54,3.81,2.54,-3.81));
 addlib("Conn02","J","Conn02","Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",[["1","1","passive",-7.62,2.54,0],["2","2","passive",-7.62,-2.54,0]],rect(-3.81,5.08,3.81,-5.08));
 const con12=Array.from({length:12},(_,i)=>[String(i+1),String(i+1),"passive",-7.62,Number((13.97-i*2.54).toFixed(2)),0]);
 addlib("Conn12","J","N_CODE_0_11","Connector_PinHeader_2.54mm:PinHeader_1x12_P2.54mm_Vertical",con12,rect(-3.81,16.51,3.81,-16.51));
 addlib("ExtPowerFlag","PWR","SUPPLIED_EXTERNALLY","",[["1","FLAG","power_out",-5.08,0,0]],rect(-2.54,2.54,2.54,-2.54),true);
 all.push('(kicad_sch (version 20250114) (generator "tht_v11_generator") (generator_version "9.0")',`(uuid ${q(ROOT_UUID)})`,'(paper "A3")',`(lib_symbols ${libs.join("\n")})`);
 function inst(name,ref,val,fp,x,y,pins,nb=false){
  all.push(`(symbol (lib_id ${q("THT_V11:"+name)}) (at ${x} ${y} 0) (unit 1) (in_bom ${nb?"no":"yes"}) (on_board ${nb?"no":"yes"}) (dnp no) (uuid ${q(uid())})
(property "Reference" ${q(ref)} (at ${x} ${y-25} 0) ${e(1)})
(property "Value" ${q(val)} (at ${x} ${y+25} 0) ${e(1)})
(property "Footprint" ${q(fp)} (at ${x} ${y} 0) (effects (font (size 1 1)) (hide yes)))
${pins.map(n=>`(pin ${q(n)} (uuid ${q(uid())}))`).join("\n")}
(instances (project ${q(DOC)} (path ${q("/"+ROOT_UUID)} (reference ${q(ref)}) (unit 1)))))`);
 }
 function label(net,x,y,dir){const a=Number(x.toFixed(2)),b=Number(y.toFixed(2)),c=Number((a+5.08*dir).toFixed(2));all.push(`(wire (pts (xy ${a} ${b}) (xy ${c} ${b})) (stroke (width 0) (type default)) (uuid ${q(uid())}))`);all.push(`(label ${q(net)} (at ${c} ${b} 0) ${e(1)} (uuid ${q(uid())}))`)}
 const map401={1:"PLL_FB_18M",2:"GND",3:"+5V_PLL",4:"PLL_PDOUT_3STATE",5:"+5V_PLL",6:"GND",7:"+5V_PLL",8:"TP_PHI_R",9:"TP_PHI_V",10:"TP_FV",21:"+5V_PLL",22:"GND",23:"GND",26:"XTAL_DRIVE",27:"XTAL_IN",28:"PLL_LD_OBSERVE"};
 for(let i=0;i<12;i++)map401[i<=9?11+i:14+i]=`N_CODE_${i}`;
 inst("ML145151YP_PDIP28","U401","ML145151YP","Package_DIP:DIP-28_W15.24mm",95.25,96.52,u401.map(x=>x[0]));
 for(const p of u401){if(!map401[+p[0]])throw Error("missing pin:"+p[0]);label(map401[+p[0]],95.25+p[3],96.52-p[4],p[3]<0?-1:1)}
 const map402={"1":"PRESCALER_RESET_N","2":"DIV2_QBAR","3":"LO1_CMOS_BUFFERED","4":"+5V_PLL","5":"PLL_FB_18M","6":"DIV2_QBAR","7":"GND","10":"+5V_PLL","11":"GND","12":"GND","13":"GND","14":"+5V_PLL"};
 inst("TC74AC74P_DIP14","U402","TC74AC74P(F)","Package_DIP:DIP-14_W7.62mm",211,96.52,u402.map(x=>x[0]));
 for(const p of u402){const x=211+p[3],y=96.52-p[4];if(["8","9"].includes(p[0]))all.push(`(no_connect (at ${Number(x.toFixed(2))} ${Number(y.toFixed(2))}) (uuid ${q(uid())}))`);else label(map402[p[0]],x,y,p[3]<0?-1:1)}
 const parts=[
 ["X401","Crystal","10.240MHz","Crystal:Crystal_HC49-U_Vertical",90,170.18,"XTAL_DRIVE","XTAL_IN"],
 ["C403","Capacitor","22pF","Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm",90,193.04,"XTAL_IN","GND"],
 ["C404","Capacitor","22pF","Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm",90,215.9,"XTAL_DRIVE","GND"],
 ["C401","Capacitor","100nF","Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm",153,170.18,"+5V_PLL","GND"],
 ["C402","Capacitor","10uF","Capacitor_THT:CP_Radial_D5.0mm_P2.00mm",153,193.04,"+5V_PLL","GND"],
 ["C405","Capacitor","100nF","Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm",153,215.9,"+5V_PLL","GND"],
 ["R403","Resistor","10k","Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",240,170.18,"+5V_PLL","PRESCALER_RESET_N"],
 ["C406","Capacitor","100nF","Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm",240,193.04,"PRESCALER_RESET_N","GND"]];
 for(const [r,n,v,f,x,y,a,b] of parts){inst(n,r,v,f,x,y,["1","2"]);label(a,x-5.08,y,-1);label(b,x+5.08,y,1)}
 const ports=[
 ["J401","PDout/GND",316.23,74.93,["PLL_PDOUT_3STATE","GND"]],
 ["J402","5V/GND",316.23,94,["+5V_PLL","GND"]],
 ["J403","LO_CMOS/GND",316.23,114.3,["LO1_CMOS_BUFFERED","GND"]],
 ["J404","RESET/GND",316.23,134.62,["PRESCALER_RESET_N","GND"]],
 ["J406","LD/GND",316.23,154.94,["PLL_LD_OBSERVE","GND"]]];
 const header2="Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical";
 for(const [r,v,x,y,nets] of ports){inst("Conn02",r,v,header2,x,y,["1","2"]);nets.forEach((net,i)=>label(net,x-7.62,y-(i? -2.54:2.54),-1))}
 const ncode=Array.from({length:12},(_,i)=>`N_CODE_${i}`);
 inst("Conn12","J405","N0-N11","Connector_PinHeader_2.54mm:PinHeader_1x12_P2.54mm_Vertical",322.58,213.36,ncode.map((_,i)=>String(i+1)));
 ncode.forEach((net,i)=>label(net,322.58-7.62,213.36-(13.97-i*2.54),-1));
 for(const [ref,net,x,y] of [["PWR401","+5V_PLL",286,177.8],["PWR402","GND",286,193.04]]){inst("ExtPowerFlag",ref,"EXTERNAL","",x,y,["1"],true);label(net,x-5.08,y,-1)}
 all.push(`(text ${q("V1.1 RX CAD-02: U401/U402 XTAL only; N controller, LO buffer, +5V supply and V1.0 PDout filter external.\\nNeither closed-loop PLL nor PCB is built. NO FAB / NO TX.")} (at 193 269 0) ${e(1.1)} (uuid ${q(uid())}))`);
 all.push('(sheet_instances (path "/" (page "1")))','(embedded_fonts no)',')');
 return {sch:all.join("\n")+"\n",lib:'(kicad_symbol_lib (version 20241209) (generator "tht_v11_generator")\n'+libs.map(x=>x.replace('(symbol "THT_V11:','(symbol "')).join("\n")+'\n)\n',table:'(sym_lib_table\n (lib (name "THT_V11") (type "KiCad") (uri "${KIPRJMOD}/THT_V11.kicad_sym") (options "") (descr "THT core RX PLL"))\n)\n'};
}
const d=generate(),dir=__dirname;
fs.writeFileSync(path.join(dir,"PLL_CORE_RX_CAD_V1.1.kicad_sch"),d.sch);
fs.writeFileSync(path.join(dir,"THT_V11.kicad_sym"),d.lib);
fs.writeFileSync(path.join(dir,"sym-lib-table"),d.table);
console.log("generated",d.sch.length,"bytes");
