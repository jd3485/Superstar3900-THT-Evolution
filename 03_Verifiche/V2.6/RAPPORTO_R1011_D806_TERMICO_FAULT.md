# V2.6 — Audit termico e guasti di R1011/D806/D804, NON qualifica hardware

Ultima revisione CAD autorevole: V2.6 su main, sette fogli THT, ERC0 già confermato. Questa PR aggiunge un **audit indipendente sul circuito esistente**, senza cambiare valori, pin o componenti né introdurre nuovi workflow automatici.

## Collegamenti da controllare con netlist KiCad9 autentica
D804 1N5819 anodo/pin2 FUSED_RAW, catodo/pin1 OVP_PRECLAMP; R1011 Vishay PR03 820 Ω 3 W dalla rete OVP_PRECLAMP a OVP_CTL_VCC; D806 Diotec 1N5352B pin1 K OVP_CTL_VCC, pin2 A GND; U801 LM393 pin8 OVP_CTL_VCC, pin4 GND; R1001 e D805 collegati al controller rail. Il nuovo script `03_Verifiche/V2.6/audit_r1011_d806_thermal_fault.py` esegue **675 combinazioni illustrative** di VIN, VF, tolleranza R, Zener *ipotizzato* e temperatura, poi compara questi pin alla netlist nativa reale.

## Dati confermati dai costruttori
- Vishay PR03 Cu-lead P70=3 W, derating da 100% a 70 °C fino a 0% a 200 °C (datasheet revisione 08-Jul-2025, grafico p.5). Potenza massima teorica **1,3846 W a 140 °C**, **1,1538 W a 150 °C**, prima di valutare disposizione PCB, montaggio, accoppiamento termico e guasti.
- Diotec 1N5352B 15 V / 5 W / ±5% a **IZtest=75 mA**; tensione **14,2–15,8 V** riferita a quella corrente, **non garantita** a quella del nostro circuito. Diotec segnala *RoHS exemption 7(a)-I* e *lead free: No*: MPN non qualificato per distinta finale senza review compliance.
- Vishay 1N5819 ha **VRRM=40 V**; esposizione effettiva a 48 V inversi non provata senza il fault-path completo (D702/TVS/fusibile), ma non è lecito assumere un margine >40 V.
- TI LM393-N ha **Vs max=36 V**: Zener aperto e altri guasti al controller rail restano bloccanti.

## Screening numerico riproducibile — esempi, NON corner vendor garantiti
Assunzioni: VIN 13,8/16,5/24/36/48 V; VF=0,2/0,4/0,7 V; R1011=779/820/861 Ω (5%); diodo ideale con VZ=14,2/15/15,8 V; ambiente 70/110/125/140/150 °C. Si assume *tutta* la corrente di R1011 al diodo, senza carico LM393/TL431 e senza curva I-V reale.

- A VIN=48 V / T=140 °C, dissipazione teorica **1,1524–1,4492 W**. **3/27** combinazioni superano **1,3846 W** ammessi dal modello di derating PR03. A 150 °C il margine peggiora.
- In guasto **D806 in corto** con VIN=36 V, VF=0,2 V, R=779 Ω, P resistore **1,6452 W**, oltre 1,3846 W ammessi a 140 °C. Con VIN=48 V il guasto è ancora più gravoso. Non assumere protezione automatica per fusione della resistenza.
- I valori ideali dello Zener NON delimitano il comportamento fisico a 48 V: la prova di tensione 15 V è fatta a 75 mA, mentre il circuito potrebbe fornire correnti inferiori. Un guasto D806 aperto può esporre U801 a sovratensione; non è risolto.
- Queste simulazioni descrivono **esposizioni vietate / casi di guasto**, NON stabiliscono un dominio sicuro a 24/36/48 V. Nessuna autorizzazione all'alimentazione da veicolo, laboratorio ad alta tensione o radio in TX.

### Decisioni e prossimo circuito
Prima di cambiare R1011, misurare/caratterizzare intervallo VIN autorizzato, corrente di U801/TL431, comportamento Zener al knee, T ambiente e hotspot reale, derating, tempo guasto, diodo D804, TVS D702/fusibile, LM393/TL431 short/open. Un aumento del valore R1011 abbasserebbe il margine di polarizzazione TL431 durante UVLO; non è una sostituzione sicura senza test integrali. Issue #27 rimane **APERTA**. Nessuna PCB/DRC/fab/TX.

**Fonti vendor:** Vishay PR01/02/03 https://www.vishay.com/docs/28729/pr010203.pdf ; Diotec D806 https://diotec.com/en/product/1N5352B.html ; Vishay 1N5819 https://www.vishay.com/docs/94614/1n5819.pdf ; TI LM393-N https://www.ti.com/product/LM393-N .
