#!/usr/bin/env node
"use strict";
const fs=require("fs"),path=require("path"),assert=require("assert");
const root=path.resolve(__dirname,"../..");
const names=["PLL_RX_HIERARCHICAL_MASTER","PLL_CORE_DIGITAL","PD_FILTER_DRIVER","VCO_RX_AND_LOBUF","POWER5_DISTRIBUTION","INPUT_FUSE_REVERSE_TVS_OVP","POWER20_VTUNE_BOOST_LDO"];
const once=function once(s,a,b){if(s.split(a).length!==2)throw Error("Nonunique "+a);return s.replace(a,b)};
const makeR=function makeR(ref,value,y,idx,leftLabel,rightLabel){
 const x=335.28,L=330.2,R=340.36,LL=325.12,RR=345.44;
 const id=k=>`b025cbd1-faae-4e37-bf25-${String(idx+k).padStart(12,"0")}`;
 const yref=Number((y-13.97).toFixed(2)),yvalue=Number((y+13.97).toFixed(2));
 return `(symbol (lib_id "THT_V18:R_1P_THT") (at ${x} ${y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "${id(0)}")
(property "Reference" "${ref}" (at ${x} ${yref} 0) (effects (font (size 1 1))))
(property "Value" "${value}" (at ${x} ${yvalue} 0) (effects (font (size 1 1))))
(property "Footprint" "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" (at ${x} ${y} 0) (effects (font (size 1 1)) (hide yes)))
(pin "1" (uuid "${id(1)}"))
(pin "2" (uuid "${id(2)}"))
(instances (project "PLL_RX_HIERARCHICAL_MASTER_V2.5" (path "/7b14bcd1-faae-4e37-bf14-000000000001/9e17bcd1-faae-4e37-bf17-000000000006" (reference "${ref}") (unit 1)))))
(wire (pts (xy ${L} ${y}) (xy ${LL} ${y})) (stroke (width 0) (type default)) (uuid "${id(3)}"))
(label "${leftLabel}" (at ${LL} ${y} 0) (effects (font (size 1 1))) (uuid "${id(4)}"))
(wire (pts (xy ${R} ${y}) (xy ${RR} ${y})) (stroke (width 0) (type default)) (uuid "${id(5)}"))
(label "${rightLabel}" (at ${RR} ${y} 0) (effects (font (size 1 1))) (uuid "${id(6)}"))
`;
};
const transform=function transform(name,raw){
 let result=raw.replaceAll('"PLL_RX_HIERARCHICAL_MASTER_V2.4"','"PLL_RX_HIERARCHICAL_MASTER_V2.5"').replaceAll("_V2.4.kicad_sch","_V2.5.kicad_sch");
 if(name==="INPUT_FUSE_REVERSE_TVS_OVP"){
   result=once(result,'(label "GND" (at 309.88 172.72 0)','(label "UVLO_SENSE" (at 309.88 172.72 0)');
   result=once(result,'(no_connect (at 345.44 172.72) (uuid "af18bcd1-faae-4e37-bf18-000000000034"))',
`(wire (pts (xy 345.44 172.72) (xy 350.52 172.72)) (stroke (width 0) (type default)) (uuid "b025cbd1-faae-4e37-bf25-000000000001"))
(label "CMP_OUT" (at 350.52 172.72 0) (effects (font (size 1 1))) (uuid "b025cbd1-faae-4e37-bf25-000000000002"))`);
   result=once(result,"VISHAY_PR01000103301JR500_3K3_1W","VISHAY_PR01000101801JR500_1K8_1W");
   const add=makeR("R1012","YAGEO_MFR-25FBF52-36K_36K_1PCT",300.99,100,"FUSED_RAW","UVLO_SENSE")
             +makeR("R1013","YAGEO_MFR-25FBF52-10K_10K_1PCT",337.82,200,"UVLO_SENSE","GND")
             +`(text "V2.5 UVLO candidate: U801B + input pin5 UVLO_SENSE, minus pin6 VREF2V5, OC out pin7 wired AND with U801A pin1 CMP_OUT. R1012=36k raw upper, R1013=10k GND lower, nominal low threshold ~11.5V. R1001=1k8 increases TL431 reference bias. UNVERIFIED startup, faults, hysteresis, thermal and manufacturer models. NO FAB / NO TX." (at 20.32 411.48 0) (effects (font (size 1 1))) (uuid "b025cbd1-faae-4e37-bf25-000000000003"))
`;
   result=once(result,"(embedded_fonts no)",add+"(embedded_fonts no)");
 }
 return result;
};
const files=[];
for(const n of names){
 const original=fs.readFileSync(path.join(root,"04_KiCad/V2.4",n+"_V2.4.kicad_sch"),"utf8");
 files.push([path.join(__dirname,n+"_V2.5.kicad_sch"),transform(n,original)]);
}
files.push([path.join(__dirname,"sym-lib-table"),fs.readFileSync(path.join(root,"04_KiCad/V2.4/sym-lib-table"),"utf8").replace("V2.4 1N4744A 15V Zener","V2.4 Diotec 1N5352B 15V 5W Zener")]);
files.push([path.join(__dirname,"fp-lib-table"),fs.readFileSync(path.join(root,"04_KiCad/V2.4/fp-lib-table"),"utf8")]);
files.push([path.join(__dirname,"THT_V24.kicad_sym"),fs.readFileSync(path.join(root,"04_KiCad/V2.4/THT_V24.kicad_sym"),"utf8")]);
const check=process.argv.includes("--check"),write=process.argv.includes("--write");
assert(check!==write,"exactly --check or --write");
for(const [p,v] of files){if(check)assert.strictEqual(fs.readFileSync(p,"utf8"),v,p+" mismatch");else fs.writeFileSync(p,v)}
console.log(JSON.stringify({gate:"PASS_V25_GENERATOR_REPRODUCIBLE",outputs:files.length,no_fab:true,no_tx:true}));
