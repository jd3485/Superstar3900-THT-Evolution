#!/usr/bin/env node
/* KiCad 9 native reproducible six-sheet THT 13.8V high-side OVP prototype.
 * Original V1.7 CAD is read-only, no production approval. 
 * --check requires byte-for-byte equality, --write regenerates.
 */
const fs=require("fs"),path=require("path"),assert=require("assert");
function buildV18(s){
 const [root,core,filter,vco,power,input]=s;
 const OLD="PLL_RX_HIERARCHICAL_MASTER_V1.7",NAME="PLL_RX_HIERARCHICAL_MASTER_V1.8",ROOT="7b14bcd1-faae-4e37-bf14-000000000001",SHEET="9e17bcd1-faae-4e37-bf17-000000000006";
 let count=0;const uid=()=>`af18bcd1-faae-4e37-bf18-${String(++count).padStart(12,"0")}`;
 const eff="(effects (font (size 1 1)))",diodefp="Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal",resfp="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal";
 function sym(key,ref,fp,pins,w=7.62,h=10.16,board=true){
  const ps=pins.map(p=>`(pin ${p[2]} line (at ${p[3]} ${p[4]} ${p[3]<0?0:180}) (length 5.08) (name "${p[1]}" ${eff}) (number "${p[0]}" ${eff}))`).join("\n");
  return `(symbol "${key}" (pin_numbers (hide yes)) (pin_names (offset 0.76)) (in_bom ${board?"yes":"no"}) (on_board ${board?"yes":"no"})
(property "Reference" "${ref}" (at 0 17.78 0) ${eff})
(property "Value" "${key}" (at 0 -17.78 0) ${eff})
(property "Footprint" "${fp}" (at 0 0 0) (effects (font (size 1 1)) (hide yes)))
(symbol "${key}_0_1" (rectangle (start ${-w} ${h}) (end ${w} ${-h}) (stroke (width 0.254) (type default)) (fill (type background))))
(symbol "${key}_1_1" ${ps})
)`;
 }
 const lm=[["1","OUT_A","open_collector",15.24,10.16],["2","IN_A_MINUS","input",-15.24,7.62],["3","IN_A_PLUS","input",-15.24,5.08],["4","GND","power_in",-15.24,-17.78],["5","IN_B_PLUS","input",-15.24,-5.08],["6","IN_B_MINUS","input",-15.24,-7.62],["7","OUT_B","open_collector",15.24,-5.08],["8","VCC","power_in",-15.24,17.78]];
 const pmos=[["1","G","input",-10.16,0],["2","D","passive",10.16,-5.08],["3","S","passive",10.16,5.08]];
 const ref=[["1","CATHODE","passive",10.16,5.08],["2","ANODE","passive",10.16,-5.08],["3","REF","input",-10.16,0]];
 const npn=[["1","E","passive",10.16,-5.08],["2","B","input",-10.16,0],["3","C","passive",10.16,5.08]];
 const two=[["1","1","passive",-5.08,0],["2","2","passive",5.08,0]];
 const zener=[["1","K","passive",-7.62,0],["2","A","passive",7.62,0]];
 const flag=[["1","PWR","power_out",-5.08,0]];
 const libs=[
 sym("LM393N_DIP8","U","Package_DIP:DIP-8_W7.62mm",lm,10.16,22.86),
 sym("TL431CLP_TO92","U","Package_TO_SOT_THT:TO-92_Inline",ref,7.62,10.16),
 sym("IRF9540NPBF_TO220","Q","Package_TO_SOT_THT:TO-220-3_Vertical",pmos,7.62,12.7),
 sym("2N3904_TO92","Q","Package_TO_SOT_THT:TO-92_Inline",npn,7.62,10.16),
 sym("1N4742A_ZENER12","D",diodefp,zener,5.08,3.81),
 sym("R_1P_THT","R",resfp,two,2.54,1.27),
 sym("POWER_FLAG_ERC","PWR","",flag,2.54,2.54,false)
 ];
 const library='(kicad_symbol_lib (version 20241209) (generator "tht_v18_ovp_generator")\n'+libs.join("\n")+'\n)\n';
 const embedded=libs.map(x=>x.replace('(symbol "','(symbol "THT_V18:')).join("\n");
 let result=input.replaceAll('(project "'+OLD+'"','(project "'+NAME+'"').replace('(paper "A3")','(paper "A2")');
 result=result.replace('(lib_symbols','(lib_symbols\n'+embedded+'\n');
 let swaps=0;
 result=result.replace('(label "FUSED_RAW" (at 152.4 66.04 0)',()=>{swaps++;return '(label "OVP_SWITCHED" (at 152.4 66.04 0)'});
 if(swaps!==1)throw Error("Expected exactly one physical D701 anode stub to reroute after OVP switch");
 // Original power flag PWR701 sits AFTER the MOSFET. New separate PWR801 acknowledges upstream source only for KiCad ERC.
 const instance=[];
 function wire(a,b,c,d){instance.push(`(wire (pts (xy ${a} ${b}) (xy ${c} ${d})) (stroke (width 0) (type default)) (uuid "${uid()}"))`)}
 function attach(net,x,y,off){const z=+(x+off).toFixed(2);wire(x,y,z,y);instance.push(`(label "${net}" (at ${z} ${y} 0) ${eff} (uuid "${uid()}"))`)}
 function place(key,ref,val,fp,x,y,pins,board=true){
  instance.push(`(symbol (lib_id "THT_V18:${key}") (at ${x} ${y} 0) (unit 1) (in_bom ${board?"yes":"no"}) (on_board ${board?"yes":"no"}) (dnp no) (uuid "${uid()}")
 (property "Reference" "${ref}" (at ${x} ${+(y-13.97).toFixed(2)} 0) ${eff})
 (property "Value" "${val}" (at ${x} ${+(y+13.97).toFixed(2)} 0) ${eff})
 (property "Footprint" "${fp}" (at ${x} ${y} 0) (effects (font (size 1 1)) (hide yes)))
 ${pins.map(n=>`(pin "${n}" (uuid "${uid()}"))`).join("\n")}
 (instances (project "${NAME}" (path "/${ROOT}/${SHEET}" (reference "${ref}") (unit 1)))))`);
 }
 function connectPins(cx,cy,pins,nets){
  if(pins.length!==nets.length)throw Error("Wrong pin binding");
  for(let i=0;i<pins.length;i++){
   const [n,nam,typ,x,y]=pins[i];
   if(nets[i]===null)continue;
   attach(nets[i],+(cx+x).toFixed(2),+(cy-y).toFixed(2),x<0?-5.08:5.08);
  }
 }
 place("IRF9540NPBF_TO220","Q801","IRF9540NPBF_PCH_100V","Package_TO_SOT_THT:TO-220-3_Vertical",317.5,71.12,["1","2","3"]);
 connectPins(317.5,71.12,pmos,["PFET_GATE","OVP_SWITCHED","FUSED_RAW"]);
 place("LM393N_DIP8","U801","LM393N_DIP8_DUAL","Package_DIP:DIP-8_W7.62mm",330.2,167.64,["1","2","3","4","5","6","7","8"]);
 connectPins(330.2,167.64,lm,["CMP_OUT","SENSE_RAW","CMP_PLUS","GND","GND","VREF2V5",null,"FUSED_RAW"]);
 instance.push(`(no_connect (at 345.44 172.72) (uuid "${uid()}"))`);
 place("TL431CLP_TO92","U802","TI_TL431CLP_TO92","Package_TO_SOT_THT:TO-92_Inline",459.74,109.22,["1","2","3"]);
 connectPins(459.74,109.22,ref,["VREF2V5","GND","VREF2V5"]);
 place("2N3904_TO92","Q802","ON_SEMI_2N3904_TO92","Package_TO_SOT_THT:TO-92_Inline",458.47,205.74,["1","2","3"]);
 connectPins(458.47,205.74,npn,["GND","Q_BASE","GATE_SINK"]);
 place("1N4742A_ZENER12","D803","ONSEMI_1N4742A_12V_GATE_LIMIT",diodefp,515.62,71.12,["1","2"]);
 connectPins(515.62,71.12,zener,["FUSED_RAW","PFET_GATE"]);
 const resistors=[
 ["R801","3k3_0p5W","FUSED_RAW","VREF2V5"],
 ["R802","54k9_1pct","FUSED_RAW","SENSE_RAW"],
 ["R803","10k_1pct","SENSE_RAW","GND"],
 ["R804","100k_1pct","VREF2V5","CMP_PLUS"],
 ["R805","1Meg_HYST","CMP_OUT","CMP_PLUS"],
 ["R806","2k2_PULLUP","VREF2V5","CMP_OUT"],
 ["R807","22k_BASE","CMP_OUT","Q_BASE"],
 ["R808","47k_GATE_SOURCE","FUSED_RAW","PFET_GATE"],
 ["R809","10k_GATE_SINK","PFET_GATE","GATE_SINK"],
 ["R810","100k_BASE_GND","Q_BASE","GND"]
 ];
 for(let i=0;i<resistors.length;i++){
  const [refid,val,a,b]=resistors[i],x=i<5?254:400.05,y=242.57+(i%5)*29.21;
  place("R_1P_THT",refid,val,resfp,x,y,["1","2"]);
  connectPins(x,y,two,[a,b]);
 }
 place("POWER_FLAG_ERC","PWR801","FUSED_DC_EXTERNAL_SOURCE_ERC","",553.72,147.32,["1"],false);
 connectPins(553.72,147.32,flag,["FUSED_RAW"]);
 instance.push(`(text "V1.8 OVP CANDIDATE: IRF9540N P-CH high-side source FUSED_RAW / drain OVP_SWITCHED -> D701 ANODE2.\\nLM393N (U801) uses TL431CLP 2.5V (U802) and 54k9/10k divider. R804=100k R805=1Meg nominal hysteresis.\\nQ802 pulls gate low only when VREF valid and comparator releases; R808 gate-source defaults OFF.\\nD803 1N4742A 12V clamps |VGS|. Threshold nominal approx 16.2V rising / 14.75V falling, NO vendor/load model proof.\\nLM393 raw input must stay within MAX 36V; continuous high-voltage and source energy still unsafe. NO FAB / NO TX." (at 203.2 402.59 0) ${eff} (uuid "${uid()}"))`);
 result=result.replace('(sheet_instances (path',instance.join("\n")+'\n(sheet_instances (path');
 result=result.replace("V1.7: F701 candidate","V1.8: F701 candidate");
 const ren=x=>x.replaceAll('(project "'+OLD+'"','(project "'+NAME+'"');
 let newRoot=ren(root).replaceAll("_V1.7.kicad_sch","_V1.8.kicad_sch").replace("V1.7 SIX SHEETS","V1.8 SIX SHEETS");
 const table='(sym_lib_table\n (lib (name "THT_V10") (type "KiCad") (uri "${KIPRJMOD}/../V1.0/THT_V10.kicad_sym") (options "") (descr "THT analog"))\n (lib (name "THT_V11") (type "KiCad") (uri "${KIPRJMOD}/../V1.1/THT_V11.kicad_sym") (options "") (descr "THT PLL"))\n (lib (name "THT_V14") (type "KiCad") (uri "${KIPRJMOD}/../V1.4/THT_V14.kicad_sym") (options "") (descr "THT VCO"))\n (lib (name "THT_V15") (type "KiCad") (uri "${KIPRJMOD}/../V1.5/THT_V15.kicad_sym") (options "") (descr "THT power"))\n (lib (name "THT_V17") (type "KiCad") (uri "${KIPRJMOD}/../V1.7/THT_V17.kicad_sym") (options "") (descr "THT fuse and TVS"))\n (lib (name "THT_V18") (type "KiCad") (uri "${KIPRJMOD}/THT_V18.kicad_sym") (options "") (descr "THT LM393N TL431CLP IRF9540N OVP pilot"))\n)\n';
 return {root:newRoot,digital:ren(core),filter:ren(filter),vco:ren(vco),power:ren(power),input:result,lib:library,table};
}
const repo=path.resolve(__dirname,"../..");
const paths=["04_KiCad/V1.7/PLL_RX_HIERARCHICAL_MASTER_V1.7.kicad_sch","04_KiCad/V1.7/PLL_CORE_DIGITAL_V1.7.kicad_sch","04_KiCad/V1.7/PD_FILTER_DRIVER_V1.7.kicad_sch","04_KiCad/V1.7/VCO_RX_AND_LOBUF_V1.7.kicad_sch","04_KiCad/V1.7/POWER5_DISTRIBUTION_V1.7.kicad_sch","04_KiCad/V1.7/INPUT_FUSE_REVERSE_TVS_V1.7.kicad_sch"];
const input=paths.map(f=>fs.readFileSync(path.join(repo,f),"utf8"));
const results=buildV18(input);
const out={"PLL_RX_HIERARCHICAL_MASTER_V1.8.kicad_sch":results.root,
"PLL_CORE_DIGITAL_V1.8.kicad_sch":results.digital,
"PD_FILTER_DRIVER_V1.8.kicad_sch":results.filter,
"VCO_RX_AND_LOBUF_V1.8.kicad_sch":results.vco,
"POWER5_DISTRIBUTION_V1.8.kicad_sch":results.power,
"INPUT_FUSE_REVERSE_TVS_OVP_V1.8.kicad_sch":results.input,
"THT_V18.kicad_sym":results.lib,"sym-lib-table":results.table};
for(const [file,data] of Object.entries(out)){
 const dest=path.join(__dirname,file);
 if(process.argv.includes("--check"))assert.strictEqual(fs.readFileSync(dest,"utf8"),data,file+" is not reproducible");
 else if(process.argv.includes("--write"))fs.writeFileSync(dest,data);
 else throw Error("Requires --check or --write");
}
console.log(JSON.stringify({status:"NATIVE_KICAD_V18_REPRODUCIBLE",files:Object.keys(out).length,
nominal_trip_v:16.2,nominal_reclose_v:14.7,hardware_qualified:false,pcb:false,fab_authorized:false,tx_authorized:false}));
