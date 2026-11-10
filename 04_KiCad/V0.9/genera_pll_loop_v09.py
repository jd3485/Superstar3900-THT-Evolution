#!/usr/bin/env python3
"""Deterministically generate the V0.9 KiCad native receive PLL loop interface.

Scope: real instantiated THT symbols/nets + external interface ports, not full
PLL, MC34063, PIC firmware, VCO or PCB. NO FAB / NO TX. Pin assignments match
Lansdale ML145151 pin4 PDout tri-state and TI LM358N PDIP8 package.
Usage: python3 04_KiCad/V0.9/genera_pll_loop_v09.py
"""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'04_KiCad/V0.9/PLL_LOOP_RX_PARTIAL_V0.9.kicad_sch'
DOC='PLL_LOOP_RX_PARTIAL_V0.9'
ROOT_UUID='3d86fc80-36d7-4d76-a243-000000000001'
IDS={}
def uid(s):
    if s not in IDS:
        IDS[s]=f'3d86fc80-36d7-4d76-a243-{len(IDS)+2:012d}'
    return IDS[s]
def q(s):
    return '"'+str(s).replace('\\','\\\\').replace('"','\\"')+'"'
def effects(size=1.0):
    return f'(effects (font (size {size} {size})))'
def prop(name,value,x,y,hide=False):
    return f'(property {q(name)} {q(value)} (at {x} {y} 0) (effects (font (size 1 1))'+(' (hide yes)' if hide else '')+'))'
def pin(num,name,kind,x,y,angle):
    return f'(pin {kind} line (at {x} {y} {angle}) (length 5.08) (name {q(name)} {effects()}) (number {q(num)} {effects()}))'
def lib_symbol(name,ref,value,footprint,pin_lines,rect=None,noboard=False):
    x='(in_bom '+('no' if noboard else 'yes')+') (on_board '+('no' if noboard else 'yes')+')'
    draw=rect or '(rectangle (start -7.62 12.7) (end 7.62 -12.7) (stroke (width 0.254) (type default)) (fill (type background)))'
    return (f'(symbol {q("THT_V09:"+name)} (pin_numbers (hide yes)) (pin_names (offset 0.76)) {x}\n'+
      f'(property "Reference" {q(ref)} (at 0 17.78 0) {effects()})\n'+
      f'(property "Value" {q(value)} (at 0 -17.78 0) {effects()})\n'+
      f'(property "Footprint" {q(footprint)} (at 0 0 0) (effects (font (size 1 1)) (hide yes)))\n'+
      f'(symbol {q(name+"_0_1")} {draw})\n'+
      f'(symbol {q(name+"_1_1")} '+ '\n'.join(pin_lines)+'))')
def symbol_inst(name,ref,value,footprint,x,y,pinnos,dnp=False,noboard=False):
    sy=f'(symbol (lib_id {q("THT_V09:"+name)}) (at {x} {y} 0) (unit 1)\n'
    sy+='(in_bom '+('no' if noboard else 'yes')+') (on_board '+('no' if noboard else 'yes')+') (dnp '+('yes' if dnp else 'no')+') '
    sy+=f'(uuid {q(uid("inst-"+ref))})\n'
    sy+=prop('Reference',ref,x,y-15.24)+ '\n'
    sy+=prop('Value',value,x,y+15.24)+ '\n'
    sy+=prop('Footprint',footprint,x,y,True)+ '\n'
    for p in pinnos:sy+=f'(pin {q(str(p))} (uuid {q(uid("pin-"+ref+"-"+str(p)))}) )\n'
    sy+=f'(instances (project {q(DOC)} (path {q("/"+ROOT_UUID)} (reference {q(ref)}) (unit 1))))\n)'
    return sy
def wire_label(net,x,y,side,tag):
    # Symbol pin connections with real wires + local net labels.
    end=x+side*5.08
    return '\n'.join([
     f'(wire (pts (xy {x:.2f} {y:.2f}) (xy {end:.2f} {y:.2f})) (stroke (width 0) (type default)) (uuid {q(uid("wire-"+tag))}))',
     f'(label {q(net)} (at {end:.2f} {y:.2f} 0) {effects()} (uuid {q(uid("label-"+tag))}))'])
def xpin(x,y,localx,localy):
    return (x+localx,y-localy)
PINS=[
 ("1","OUT_A","output",12.7,7.62,180),
 ("2","IN_A_MINUS","input",-12.7,7.62,0),
 ("3","IN_A_PLUS","input",-12.7,5.08,0),
 ("4","V_MINUS","power_in",-12.7,-7.62,0),
 ("5","IN_B_PLUS","input",-12.7,-2.54,0),
 ("6","IN_B_MINUS","input",-12.7,-5.08,0),
 ("7","OUT_B","output",12.7,-2.54,180),
 ("8","V_PLUS","power_in",12.7,-7.62,180)
]
parts=[
 ('R901','Resistor','22k','Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm',65,48,'PLL_PDOUT_3STATE','PD_FILTER'),
 ('C901','Capacitor','100n','Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm',65,70,'PD_FILTER','GND'),
 ('R803','Resistor','30k','Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm',190,48,'OPA_OUT_A','OPA_FB_A'),
 ('R804','Resistor','10k','Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm',190,70,'OPA_FB_A','GND'),
 ('R805','Resistor','220','Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm',190,92,'OPA_OUT_A','VTUNE_RAIL'),
 ('C805','Capacitor','100n DNI (VCO C505 present)','Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm',190,114,'VTUNE_RAIL','GND'),
 ('C803','Capacitor','100n','Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm',65,92,'VANA20_FILT','GND')
]
conn=[
 ('J901','PDout + GND','PLL_PDOUT_3STATE','GND',55,135),
 ('J902','20V + GND','VANA20_FILT','GND',95,135),
 ('J903','VTUNE + GND','VTUNE_RAIL','GND',155,135),
 ('J904','LD + GND','PLL_LD_RAW','GND',205,135)
]
libs=[
 lib_symbol('LM358N_PDIP8','U','LM358N','Package_DIP:DIP-8_W7.62mm',[
  pin(*p) for p in PINS]),
 lib_symbol('Resistor','R','R','Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm',
            [pin('1','~','passive',-5.08,0,0),pin('2','~','passive',5.08,0,180)],
            '(rectangle (start -2.54 1.27) (end 2.54 -1.27) (stroke (width 0.254) (type default)) (fill (type background)))'),
 lib_symbol('Capacitor','C','C','Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm',
            [pin('1','~','passive',-5.08,0,0),pin('2','~','passive',5.08,0,180)],
            '(rectangle (start -1.27 2.54) (end 1.27 -2.54) (stroke (width 0.254) (type default)) (fill (type none)))'),
 lib_symbol('Connector02','J','Conn02','Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',
            [pin('1','1','passive',-7.62,2.54,0),pin('2','2','passive',-7.62,-2.54,0)],
            '(rectangle (start -2.54 5.08) (end 2.54 -5.08) (stroke (width 0.254) (type default)) (fill (type background)))'),
 lib_symbol('ExternalPowerFlag','PWR','EXT_PWR_FLAG','',
            [pin('1','FLAG','power_out',-5.08,0,0)],
            '(rectangle (start -2.54 2.54) (end 2.54 -2.54) (stroke (width 0.254) (type default)) (fill (type none)))',True)
]
elements=[
 '(kicad_sch (version 20250114) (generator "tht_v09_generator")',
 f'(uuid {q(ROOT_UUID)})',
 '(paper "A3")',
 '(lib_symbols '+'\n'.join(libs)+')',
 symbol_inst('LM358N_PDIP8','U803','LM358N','Package_DIP:DIP-8_W7.62mm',140,80,[p[0] for p in PINS])
]
for n,name,kind,dx,dy,ang in PINS:
    net={'1':'OPA_OUT_A','2':'OPA_FB_A','3':'PD_FILTER','4':'GND',
         '5':'GND','6':'OPA_OUT_B','7':'OPA_OUT_B','8':'VANA20_FILT'}[n]
    x,y=xpin(140,80,dx,dy)
    elements.append(wire_label(net,x,y,-1 if dx<0 else 1,'U803-'+n))
for ref,typ,value,fp,x,y,a,b in parts:
    elements.append(symbol_inst(typ,ref,value,fp,x,y,[1,2],dnp=ref=='C805'))
    elements.append(wire_label(a,x-5.08,y,-1,ref+'-1'))
    elements.append(wire_label(b,x+5.08,y,1,ref+'-2'))
for ref,value,net1,net2,x,y in conn:
    elements.append(symbol_inst('Connector02',ref,value,
       'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',x,y,[1,2]))
    elements.append(wire_label(net1,x-7.62,y-2.54,-1,ref+'-1'))
    elements.append(wire_label(net2,x-7.62,y+2.54,-1,ref+'-2'))
for ref,x,y,net in [('PWR901',95,156,'VANA20_FILT'),('PWR902',135,156,'GND')]:
    elements.append(symbol_inst('ExternalPowerFlag',ref,'EXTERNAL_SUPPLY_ASSUMED','',x,y,[1],noboard=True))
    elements.append(wire_label(net,x-5.08,y,-1,ref+'-1'))
elements.append(f'(text {q("V0.9 RX ONLY: ML145151 PDout pin4 THREE-STATE is EXTERNAL. PD_FILTER resistor/cap are CANDIDATES, NOT COMPENSATED PLL.\nExternal +20V and GND power flags only DECLARE supplied ports for partial ERC.\nC805 is DNI because VCO candidate already has C505 100nF on VTUNE.\nNo native schematic for U401, power converter, VCO here. NO FAB / NO TX.")} (at 145 180 0) {effects(1.2)} (uuid {q(uid("notice"))}))')
elements.append(')')
src='\n'.join(elements)+'\n'
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(src,encoding='utf-8')
print('Created',OUT,'length',len(src),'instances',1+len(parts)+len(conn)+2)
