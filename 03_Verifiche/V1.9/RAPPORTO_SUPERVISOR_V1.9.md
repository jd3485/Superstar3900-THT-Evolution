# V1.9 — KiCad9 nativo: alimentazione del supervisore OVP separata dalla linea raw + resistenza 1 W

## Problema reale lasciato in V1.8
U801 (LM393N) pin8, R1001 pin1 e R1002 pin1 erano direttamente sul nodo `FUSED_RAW` prima di D701. L'OVP P-MOSFET spegneva il regolatore U601, ma **la sezione di controllo era ancora esposta all'inversione di polarità**. R1001 3k3 in footprint resistore da ¼ W poteva dissipare oltre 0,3 W a 36 V. I due problemi sono stati registrati in PR #15.

## Nuovo hardware THT candidato sul sesto foglio reale
`04_KiCad/V1.9/INPUT_FUSE_REVERSE_TVS_OVP_V1.9.kicad_sch` eredita ogni componente V1.8 e introduce:
- **D804 Vishay 1N5819**, DO-41, anodo pin2 su `FUSED_RAW` e catodo pin1 su **`OVP_CTL_VCC`**. La nuova rail alimenta U801 LM393 pin8, R1001 pin1 (riferimento TL431) e R1002 pin1 (partitore di sensing). Si impedisce la conduzione diretta in polarità inversa attraverso questa porta, **non** si garantisce protezione integrale da inversione di batteria/inductive wiring.
- **D805 Vishay 1N5819**, DO-41, anodo pin2 su GND e catodo pin1 su `OVP_CTL_VCC`: clamp antiparallelo candidato contro una tensione negativa generata da correnti di fuga in D804. Anche la caduta diretta del clamp può essere incompatibile con i massimi di alcuni pin elettronici; servono stress vendor, non solo CAD.
- **R1001 Vishay PR01000103301JR500**, 3,3 kΩ ±5%, 1 W, assiale THT; footprint KiCad `Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal`. Il corpo nominale di catalogo circa 6,5 x 2,5 mm entra nella geometria 9 x 3,2 mm, ma occorre conferma fisica del pezzo per assiemaggio. A 36 V raw e Vf D804 ipotizzata 0,25–0,60 V, dissipa ~0,33 W (contro 1 W nominale, **derating non verificato**). La BOM delta sostituisce il precedente R1001 sottodimensionato.
- **PWR802**, sola annotazione ERC power_out sul nodo di controllo, senza equivalente hardware.

**Connettività:** D804 pin1, D805 pin1, U801 pin8, R1001 pin1 e R1002 pin1 condividono `OVP_CTL_VCC`; D804 pin2 resta insieme a F701 pin2, D702 pin1 e Q801 source pin3 su `FUSED_RAW`. D805 pin2 va a GND. R1008 e zener D803 restano fra gate e SOURCE raw del MOSFET. Nessuna alterazione delle altre rail PLL/VCO o del diodo D701. File KiCad V1.8 ed SMD immutati.

## Fonti vendor e limiti
- Vishay 1N5819, DO-41, 1A / 40V e Vf fino a 0,60V a IF 1A (la Vf alle correnti mA non è specificata da quella tabella): https://www.vishay.com/docs/88525/1n5817.pdf
- Vishay PR01 3.3kΩ 1W 5%, MPN PR01000103301JR500, corpo nominale 6,5 x 2,5 mm, resistore assiale: https://www.vishay.com/docs/28729/pr010203.pdf e https://www.digikey.com/en/products/detail/vishay-beyschlag-draloric-bc-components/PR01000103301JR500/596047
- Scheda tecnica TL431BCLP e LM393N già censita nella V1.8, e circuiti Q801/SQ802 invariati.

## Esposizioni non risolte
Non si dichiara il circuito fail-safe: D804/D805 sono diodi Schottky con leakage inverso dipendente dalla temperatura; il ramo Q802 gate è tuttora riferito alla SOURCE raw; **LM393 massimo 36 V resta un limite invalicabile**, TVS P6KE20CA può lasciare passare impulsi oltre questo limite, e D804 non risolve transienti load dump. Le soglie dipendono dalla Vf D804: lo script aritmetico analizza 21 coppie VIN/Vf, ma non è un modello vendor. Rimane possibile che il comparatore non riarmi correttamente se VIN è vicina al limite, e il MOSFET può subire stress gate-source. R1001 1W richiede comunque derating reale a temperatura elevata e prova fisica. Fusibile F701 e TVS D702 non coordinati/footprint non scelti. Nessuna PCB, DRC, EMC, alimentazione VTUNE 20V, test RF, TX o fabbricazione.

## Gate CAD
Sorgenti V1.8 intatte, generatore deterministico `node 04_KiCad/V1.9/genera_supervisore_v19.js --check`, KiCad9 ERC sull'intera gerarchia (sei pagine), netlist V1.8 63 gruppi vs V1.9 **64 attesi** e con tutte le vecchie partizioni pin preservate eccetto spostamento intenzionale di U801/8 R1001/1 R1002/1. SVG 6 pagine e stress DC ipotetico. **GATE CAD VERIFICATO:** [GitHub Actions 42971502918](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42971502918) **PASS**, ERC KiCad9 **0 violazioni** in sei pagine, **64 gruppi netlist nativi** con conservazione di tutte le connessioni preesistenti tranne 3 pin migrati, generatore 7 file bit-per-bit, sei SVG. Il gate ha inizialmente evidenziato che i `PWR_FLAG` non-montati non figurano nella netlist; il controllo corretto li verifica come metadati nello schematico e controlla solo i componenti fisici nella netlist. **Nessuna affermazione di protezione hardware. NO FAB / NO TX.**

## Risultati numerici screening V1.9 (solo analisi DC)
Lo script [screen_supervisor_v19.py](../../03_Verifiche/V1.9/screen_supervisor_v19.py) ha esaminato 21 combinazioni VIN = 11/13,8/15,5/17/24/36/48V e caduta D804 assunta 0,25/0,45/0,60V. A VIN 36V: P(R1001) ~0,3281–0,33512W nominali, valore inferiore a 1W ma **non prova di derating termico**. Il trip raw derivato dai vecchi corner e da Vf D804 è indicativamente **16,2053–17,5133V** e il riarmo **14,9098–16,0407V**, con tutte le ipotesi del precedente studio; **non sono valori garantiti**. A 48V le dissipazioni possono restare inferiori a 1W ma il supervisore LM393 supererebbe la tensione massima: caso esplicitamente NON OPERATIVO. F701/D702 restano sottosistemi incompleti.
