# V2.7 — R2102 Vishay PR01 THT 10kΩ 1W: vero CAD e controllo termico a guasto

**16 novembre 2026. Candidato THT NON QUALIFICATO e banco KiCad9 ISOLATO. NON autorizza VIN48V, hardware, PCB o TX.**

## CAD vero

Progetto `04_KiCad/V2.7_DRAFT/MAIN_SECONDARY_OVP_Q804_Q805_Q806_PR01_R2102/MAIN_SECONDARY_OVP_Q804_Q805_Q806_PR01_R2102_LAB_V2_7_DRAFT.kicad_sch`, derivato dal banco THT PR #306. Tutti i 27 terminali elettrici e 8 net restano invariati. R2102 collega collettore Q806/3 al gate comune PMOS Q804/1 Q805/1; source flottante ancora separato dal return. Componenti D2101/D2102 Microchip 1N4106-1 DO-35, Q804/Q805 e Q806 restano candidati.

**R2102** sostituisce il valore provvisorio 10k con candidato reale `Vishay PR01000101002JR500`, resistenza **10kΩ ±5% 1 W P70**, costruzione a film di potenza assiale THT (possibile comportamento fusibile/safety). Footprint generica `Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal` per corpo nominale 6,5×2,5mm. **Il precedente CAD aveva davvero impronta DIN0309 L9.0/D3.2/P12.70, non DIN0207**: nuova footprint intenzionalmente cambiata, ma quote OEM/fori/piegatura e distanze dai componenti **NON** sono verificate. Nessuna modifica al master MAIN V2.6 o FRONT.

## Evidenze OEM

Vishay [PR01/PR02/PR03 OEM Rev luglio 2025](https://www.vishay.com/docs/28729/pr010203.pdf): PR01 1 W a Ta70°C, da 70°C a 200°C derating nominale lineare a zero, -55..200°C funzionamento, tensione massima 350V e rating P70; nessuna estrapolazione dei pulse ratings. [Scheda MPN PR01000101002JR500](https://www.digikey.com/en/products/detail/vishay-beyschlag-draloric-bc-components/PR01000101002JR500/595971) riporta Active, 10k ±5%, THT assiale, corpo nominale 6,50×2,50mm e potenza 1W. Lo stato produttivo del singolo MPN va confermato direttamente da Vishay prima di BOM finale.

L'alternativa precedente Vishay MRS25 10k 0,6W, pur essendo DIN0207, **NON** assicura margine termico nel fault a125°C: derating teorico MRS25 70→155°C dà ~0,212 W contro 0,233W a Rmin1%. Per questo il candidato PR01 è tecnicamente più appropriato ma **NON qualificato**.

## Contratto di prova

`03_Verifiche/V2.7/verify_r2102_pr01_native_derating.py`, registrato FULL, impone KiCad9 ERC 0/0, la footprint **dell'istanza R2102** e netlist 27 pin/8 reti con segmenti driver e gate senza bypass. Controlla **567 scenari statici**: source imposto 0/8/13,8/16/24/36/48 V, 9 temperature -40..200°C, R2102 a 9,5/10/10,5 kΩ, tre stati gate schematici (clamp in corto/sintetico12V/off). Questi valori NON simulano la temperatura fisica del resistore, guasti transienti o una curva OEM Zener.

**Worst-case puramente teorico**: a source48V, Rmin 9,5k e clamp corto, `P=48²/9500≈0,242526W`, rispetto al PR01 `Pmax(125°C)=1×(200−125)/(200−70)≈0,576923W`; margine statico ~0,3344W. A 175°C `Pmax≈0,1923W` **inferiore** al medesimo guasto continuo; il crossover idealizzato è ~168,47°C. Dunque **neppure PR01 garantisce tolleranza termica in tutto il dominio**, e il PCB/ambiente può renderlo peggiore; rating fusibile e surge non testati. L'algoritmo registra esplicitamente i corner con potenza oltre il derating OEM.

## Bloccanti

VGS in doppio Zener OPEN, controllo reale sorgente flottante, guasto KSP42BU C–E SHORT, alimentazione + supervisore OVP/UVLO indipendenti e sicuri, alette drenanti TO-220, resistenza di corto e fiamma dell'effettivo MPN, clearance/pad veri, transienti e termica reale, prove banco e review indipendente. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
