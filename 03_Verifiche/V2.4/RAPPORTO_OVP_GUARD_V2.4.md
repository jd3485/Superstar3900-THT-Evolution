# V2.4 — candidato di guardia LM393 upstream, ancora NON safety-qualified

Baseline: V2.3 realmente integrata (PR26). **Sette fogli KiCad9 nativi** V2.4.
Modifiche elettriche intenzionali su INPUT_FUSE_REVERSE_TVS_OVP soltanto:
- **D804 K1** da `OVP_CTL_VCC` a nuovo `OVP_PRECLAMP`.
- **R1011** Vishay `PR02000206800JR500` 680Ω/2W 5% assiale tra `OVP_PRECLAMP` e `OVP_CTL_VCC`; footprint THT KiCad DIN0414 L11.9/D4.5/pitch15.24 candidato, corpo conservativamente più grande della PR02 10.0 × Ø3.9 mm: verificare forma terminali, foratura e montaggio sul campione.
- **D806** onsemi `1N4744A` zener 15V 1W DO-41, **catodo pin1 a OVP_CTL_VCC**, anodo pin2 a GND. Compatibilità ingombro, derating e energia richiedono prototipo.
- **R1002 pin1** da `OVP_CTL_VCC` a **FUSED_RAW**, per far sì che il sensore OVP misuri ancora VIN effettivo e non la nuova alimentazione limitata. R1002 pin2 resta `SENSE_RAW`. Non bypassa fusibile/TVS.
- U801, U802, Q801, Q802, D803 e tutte le altre reti/gate legacy restano INALTERATE. Questa revisione non rivendica powergood/mute fail-closed.

Datasheet originali:
TI [LM393-N](https://www.ti.com/product/LM393-N): Vs operativa 2..36V, ingressi max Vcc−1.5; transistor open collector. **36V non è specifica di immunità alle sovratensioni di veicolo**.
Infineon [IRF9540N](https://www.infineon.com/part/IRF9540N): VGS assoluto ±20V. D803 zener esistente resta privo di prova RF/di guasto per Q801.
onsemi [1N4728A–1N4758A](https://www.onsemi.com/download/data-sheet/pdf/1n4736at-d.pdf): 1N4744A 15V nominale, 14.25..15.75V @17mA/25°C, 1W **solo con terminali ≤50°C e 3/8 pollice di lead**; derating6.67mW/°C sopra50°C. A 10mA o con fault di durata arbitraria il clamp non è garantito nominale 15V!
Vishay [PR01/02/03](https://www.vishay.com/docs/28729/pr010203.pdf): PR02 2W P70, Ø3.9mm max, lunghezza10mm max, conduttori varianti Cu/FeCu. Occorre campione e confermare lead forming/courtyard.
TI [TL431](https://www.ti.com/lit/ds/symlink/tl431.pdf): min catodo per regulation dipende da revisione/suffisso; screening prudenziale **1mA**.
D702 P6KE20CA bidirezionale a 600W pulse / max clamp ~27.7V alla corrente di test, **non** sovratensione continua.

**Analisi preliminare, non SPICE vendor:** con R1011 680±5%, VD804 0.25..0.65V, Icc LM393 0.5..1mA, carico da 3.3k e riferimento TL431 a 2.5V, lo screening verifica corrente disponibile nominale a VIN 13.8V e segnala **regolazione TL431 non garantita in brownout ~10–12V**. A VIN36/48V screening P_R, P_Z con zener ideale; 48V non dichiarati rating per durata perché derating zener, energia TVS, VGS e reverse non qualificati. Il TL431 potrebbe non arrivare a regime, comparatore open collector e PFET possono non garantire fail-closed su tutte le condizioni. La configurazione non è una protezione affidabile per batteria e NON ha ancora modello transitorio vendor.

**Merge gate CAD:** generator 10 output bit-for-bit; ERC0 KiCad9, netlist da master 7 fogli; **72 gruppi prima, 73 attesi dopo**: solamente due pin esistenti D804/1 e R1002/1 migrano, due nuovi componenti aggiunti (R1011,D806). 131/131 campi footprint; 7 SVG; regression suite. **Qualifica safety NON completata anche se CI verde**.

**Prossimo V2.5 obbligatorio**: UVLO/powergood fail-closed e gate latch, modelli e stress test per disturbi e guasti, definire alimentazione di laboratorio e termica. Nessuna DRC PCB (PCB non esiste). **NO FAB / NO TX**, no battery or vehicle.
