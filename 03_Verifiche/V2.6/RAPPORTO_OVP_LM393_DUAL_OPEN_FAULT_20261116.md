# V2.6 — U801 LM393N: rischio di sovratensione con D806 e TL431 aperti

16 novembre 2026. **Analisi diagnostica del circuito MAIN KiCad9, non una qualifica di sicurezza o modello vendor.**

## Circuito realmente tracciato

Nella gerarchia V2.6 a 7 fogli: D804 pin 1 → R1011 pin 1 (OVP_PRECLAMP); R1011 pin 2 → D806 catodo, U801 pin 8 (OVP_CTL_VCC), R1001 pin 1. R1001 pin 2 → catodo/riferimento U802 TL431. D806 anodo, U802 anodo e U801 GND sono sul ritorno. Verificare netlist nativa KiCad9, non solo stringhe nello schema. Il modello non altera il master.

Il nuovo verificatore `03_Verifiche/V2.6/verify_ovp_dual_open_lm393_supply_native.py` esamina le **2.268 combinazioni già esistenti** di VIN 10–48 V, caduta D804, R1011, R1001, riferimento TL431 e consumo ipotetico U801. Per ciascuna confronta **quattro stati**: Zener idealmente operativo/aperto × TL431 idealmente in regolazione/aperto = **9.072 condizioni**. Calcola il nodo con formula KCL ed esegue una seconda soluzione numerica indipendente per bisezione.

- **D806 aperto, TL431 ipoteticamente ancora in regolazione:** il riferimento drena corrente e mantiene il nodo sotto i 36 V in questa griglia specifica. Non è prova di robustezza TL431 durante guasto.
- **D806 e TL431 entrambi aperti:** soltanto il consumo assunto dell'LM393 limita la corrente; `V_CTL ≈ VIN − VF(D804) − R1011·Icc`. A 48 V, VF=0,2 V, R1011=779 Ω e Icc=0,5 mA si ottengono **47,4105 V sul pin VCC U801**, oltre il massimo 36 V di alimentazione dichiarato per LM393-N. Uno scenario con massimi assoluti superati **non va trattato come test sicuro**.
- **Zener idealmente attivo:** si limita matematicamente a 15 V quando la soluzione non limitata è superiore. Questo *non* conferma la vera Vz D806 al punto operativo, dispersioni, avalanche/surge, guasti fisici o start-up.
- **TL431 aperto ma D806 ideale operativo:** differente dal doppio guasto; non si può dedurre che gli stati futuri del MOSFET high-side, PG o mute siano fail-closed.

## Divieti e prossimi gate

Restano non qualificati: comportamento non lineare reale del Diotec 1N5352B, corrente di alimentazione e common-mode LM393 ai corner, UVLO brownout, TVS/fusibile, carico/gate high-side, single point faults e reverse, grado termico R1011 e isolamento del modulo. Il test segnala un **rischio condizionale**, non una stima di guasto in un veicolo.

Occorrono datasheet primari, specifiche di laboratorio VIN e sorgente energetica, protezione indipendente hardware e controllo delle reti di gate, KiCad9 ERC e verifica PCB solo quando esiste un layout. Nessun collegamento a batteria/veicolo e nessuna alimentazione TX: **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.
