#!/usr/bin/env node
/* Deterministic THT KiCad9 V1.9: supervisor reverse-isolated feed and 1W reference resistor.
 * V1.8 input sources remain unchanged; no hardware safety qualification. NO FAB / NO TX.
 */
const fs=require("fs"),path=require("path"),assert=require("assert");
function makeV19(v){
  const OLD="PLL_RX_HIERARCHICAL_MASTER_V1.8",NAME="PLL_RX_HIERARCHICAL_MASTER_V1.9";
  const ROOT="7b14bcd1-faae-4e37-bf14-000000000001",SHEET="9e17bcd1-faae-4e37-bf17-000000000006";
  const eff="(effects (font (size 1 1)))",fp="Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal";
  const prefix="b019cbd1-faae-4e37-bf19-";
  let seq=0;const uid=()=>prefix+String(++seq).padStart(12,"0");
  const wires=(x,y,x2,y2)=>`(wire (pts (xy ${x} ${y}) (xy ${x2} ${y2})) (stroke (width 0) (type default)) (uuid "${uid()}"))`;
  const label=(name,x,y)=>`(label "${name}" (at ${x} ${y} 0) ${eff} (uuid "${uid()}"))`;
  let input=v[5],relabel=0;
  const edits=[
   ['(label "FUSED_RAW" (at 309.88 149.86 0)','(label "OVP_CTL_VCC" (at 309.88 149.86 0)'],
   ['(label "FUSED_RAW" (at 243.84 242.57 0)','(label "OVP_CTL_VCC" (at 243.84 242.57 0)'],
   ['(label "FUSED_RAW" (at 243.84 271.78 0)','(label "OVP_CTL_VCC" (at 243.84 271.78 0)']
  ];
  for(const [a,b] of edits){if(input.split(a).length!==2)throw Error("Expected exactly one old FUSED_RAW label: "+a);input=input.replace(a,b);relabel++}
  if(relabel!==3)throw Error("Missing supervisory control rail migration");
  const valueOld='(property "Value" "3k3_0p25W_SCREEN" (at 254 256.54 0)';
  const valueNew='(property "Value" "VISHAY_PR01000103301JR500_3K3_1W" (at 254 256.54 0)';
  if(input.split(valueOld).length!==2)throw Error("R1001 old value missing");
  input=input.replace(valueOld,valueNew);
  const oldFp='(property "Footprint" "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" (at 254 242.57 0)';
  const newFp='(property "Footprint" "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal" (at 254 242.57 0)';
  if(input.split(oldFp).length!==2)throw Error("R1001 footprint instance not found");
  input=input.replace(oldFp,newFp);
  const instance=(key,ref,val,foot,x,y,pins,on_board=true)=>`(symbol (lib_id "${key}") (at ${x} ${y} 0) (unit 1) (in_bom ${on_board?"yes":"no"}) (on_board ${on_board?"yes":"no"}) (dnp no) (uuid "${uid()}")
(property "Reference" "${ref}" (at ${x} ${+(y-13.97).toFixed(2)} 0) ${eff})
(property "Value" "${val}" (at ${x} ${+(y+13.97).toFixed(2)} 0) ${eff})
(property "Footprint" "${foot}" (at ${x} ${y} 0) (effects (font (size 1 1)) (hide yes)))
${pins.map(n=>`(pin "${n}" (uuid "${uid()}"))`).join("\n")}
(instances (project "${NAME}" (path "/${ROOT}/${SHEET}" (reference "${ref}") (unit 1)))))`;
  const additions=[];
  function putDiode(ref,x,y,anodeNet,cathodeNet){
    additions.push(instance("THT_V17:SCHOTTKY_1N5819",ref,"VISHAY_1N5819_40V_1A",fp,x,y,["1","2"]));
    const lx=+(x-7.62).toFixed(2), rx=+(x+7.62).toFixed(2);
    const ll=+(lx-5.08).toFixed(2), rr=+(rx+5.08).toFixed(2);
    additions.push(wires(lx,y,ll,y),label(anodeNet,ll,y),wires(rx,y,rr,y),label(cathodeNet,rr,y));
  }
  putDiode("D804",228.6,104.14,"FUSED_RAW","OVP_CTL_VCC");
  putDiode("D805",228.6,139.7,"GND","OVP_CTL_VCC");
  additions.push(instance("THT_V18:POWER_FLAG_ERC","PWR802","ERC_ONLY_PROTECTED_SUPERVISOR_VCC","",553.72,184.15,["1"],false));
  additions.push(wires(548.64,184.15,543.56,184.15),label("OVP_CTL_VCC",543.56,184.15));
  additions.push(`(text "V1.9: D804 A2 FUSED_RAW -> K1 OVP_CTL_VCC powers LM393 and VREF, D805 A2 GND -> K1 OVP_CTL_VCC clamps reverse leakage only.\\nR1001 Vishay PR01000103301JR500 3.3k 1W (PR01) at 12.70mm pitch; PWR802 is schematic-only.\\nSENSE_RAW is now after D804, so thresholds shift with actual diode VF/leakage. No guaranteed automotive reverse-battery or continuous surge survival.\\nNo vendor transient, fuse energy, SOA, board or RF qualification. NO FAB / NO TX." (at 38.1 388.62 0) ${eff} (uuid "${uid()}"))`);
  const insert='(sheet_instances (path';
  if(input.split(insert).length!==2)throw Error("Input child has unexpected sheet_instances count");
  input=input.replace(insert,additions.join("\n")+"\n"+insert);
  // Only actual KiCad project instances rewritten. The original six-sheet child UUID remains stable.
  const migrate=x=>x.replaceAll(`(project "${OLD}"`,`(project "${NAME}"`);
  input=migrate(input).replace("V1.8: F701", "V1.9: F701");
  const root=migrate(v[0]).replaceAll("_V1.8.kicad_sch","_V1.9.kicad_sch")
    .replace("V1.8 SIX SHEETS","V1.9 SIX SHEETS");
  const table=v[6].replace("${KIPRJMOD}/THT_V18.kicad_sym","${KIPRJMOD}/../V1.8/THT_V18.kicad_sym");
  const result={root,core:migrate(v[1]),filter:migrate(v[2]),vco:migrate(v[3]),power:migrate(v[4]),input,table};
  if(!result.root.includes("INPUT_FUSE_REVERSE_TVS_OVP_V1.9.kicad_sch"))throw Error("Root not migrated");
  if((result.input.match(/\(property "Reference" "D80[45]"/g)||[]).length!==2)throw Error("Missing reverse guard diodes");
  if((result.input.match(/\(label "OVP_CTL_VCC"/g)||[]).length!==6)throw Error("Wrong count of isolated supervisor supply labels");
  return result;
}
const repo=path.resolve(__dirname,"../..");
const paths=["04_KiCad/V1.8/PLL_RX_HIERARCHICAL_MASTER_V1.8.kicad_sch","04_KiCad/V1.8/PLL_CORE_DIGITAL_V1.8.kicad_sch","04_KiCad/V1.8/PD_FILTER_DRIVER_V1.8.kicad_sch","04_KiCad/V1.8/VCO_RX_AND_LOBUF_V1.8.kicad_sch","04_KiCad/V1.8/POWER5_DISTRIBUTION_V1.8.kicad_sch","04_KiCad/V1.8/INPUT_FUSE_REVERSE_TVS_OVP_V1.8.kicad_sch","04_KiCad/V1.8/sym-lib-table"];
const input=paths.map(f=>fs.readFileSync(path.join(repo,f),"utf8"));
const o=makeV19(input);
const files={"PLL_RX_HIERARCHICAL_MASTER_V1.9.kicad_sch":o.root,
"PLL_CORE_DIGITAL_V1.9.kicad_sch":o.core,
"PD_FILTER_DRIVER_V1.9.kicad_sch":o.filter,
"VCO_RX_AND_LOBUF_V1.9.kicad_sch":o.vco,
"POWER5_DISTRIBUTION_V1.9.kicad_sch":o.power,
"INPUT_FUSE_REVERSE_TVS_OVP_V1.9.kicad_sch":o.input,
"sym-lib-table":o.table};
for(const [name,source] of Object.entries(files)){
 const dest=path.join(__dirname,name);
 if(process.argv.includes("--check"))assert.strictEqual(fs.readFileSync(dest,"utf8"),source,"Nonreproducible KiCad9 "+name);
 else if(process.argv.includes("--write"))fs.writeFileSync(dest,source);
 else throw Error("Use --check or --write");
}
console.log(JSON.stringify({status:"V19_NATIVE_SCHEMATICS_DETERMINISTIC",count:Object.keys(files).length,
 supervisor_series_diode:"D804 A2 to fused K1 to OVP_CTL_VCC",reverse_leakage_clamp:"D805",r1001:"3.3k 1W",
 qualifications:"NONE",fab_authorized:false,tx_authorized:false}));
