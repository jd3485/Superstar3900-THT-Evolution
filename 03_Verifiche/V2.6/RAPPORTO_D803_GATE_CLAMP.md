# Verifica indipendente V2.6 — D803, protezione gate IRF9540NPBF

**Correzione tecnica importante:** il progetto integrato V2.6 contiene già **D803 (onsemi 1N4742A Zener 12 V / 1 W DO-41)** collegato con **catodo pin1 a FUSED_RAW/source Q801** e **anodo pin2 a PFET_GATE/gate Q801**. Non aggiungere un secondo Zener senza ragione. Il precedente script `screen_series_interlock_v26.py` analizzava una rete di due resistori **senza rappresentare D803**: il suo avviso a 48 V riguarda il guasto **D803 aperto**, non il circuito sano.

## Audit riproducibile (Python locale + gate KiCad nativo)
`03_Verifiche/V2.6/audit_d803_gate_clamp_v26.py` esegue **486 combinazioni illustrative**: VIN 11 / 13,8 / 16,5 / 24 / 36 / 48 V; R1008=47k e R1009=10k ±5%; sink 0,1/0,3/0,6 V; Zener *idealizzato* 11,4/12/12,6 V.

Risultati del *solo modello ideale*:
- A 13,8 V, |VGS| circa **10,687–11,488 V**.
- Con **D803 aperto** e VIN 48 V, |VGS| **38,376–40,168 V**: supera il limite assoluto ±20 V del MOSFET.
- Con **D803 idealizzato sano** a 48 V, corrente Zener circa **3,032–3,611 mA**, potenza max circa **43,602 mW**, e |VGS| limitata al valore di clamp *assunto*, NON garantito.
- Con **D803 in corto** (ipotesi ideale) VGS=0: transistor spento finché gli altri componenti funzionano; nessuna garanzia di comportamento a guasto multiplo.

**AVVERTENZA DECISIVA:** secondo la tabella onsemi per **1N4742A**, Vz=11,4..12,6 V è caratterizzato a **IZ=21 mA**, con **IZK=0,25 mA e ZZK fino a 700Ω**. Le nostre correnti previste sono molto inferiori a 21 mA; pertanto il test **non può attribuire ±5% alla tensione di clamp reale in questo circuito**, né garantirne comportamento ai transitori, temperatura o guasto singolo. L'audit KiCad controlla i pin/net effettivamente esportati, non soltanto i nomi delle etichette.

Fonti: onsemi https://www.onsemi.com/products/discrete-power-modules/diodes-rectifiers/zener-diodes/1n4742a ; Infineon IRF9540N https://www.infineon.com/part/IRF9540N .

**Non qualificato:** LM393 >36 V, 2N3904 >40 V, diodo D803 open/corto, fault TL431, avvio e rumore, TVS/fusibile, polarità inversa, VGS dinamica, power-good/mute e laboratorio. Non esiste una PCB completa o DRC scheda. Issue #27 resta aperta. **NO FAB / NO TX / NO BATTERIA/VEICOLO.**
