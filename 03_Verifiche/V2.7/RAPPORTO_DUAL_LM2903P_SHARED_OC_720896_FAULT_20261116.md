# V2.7 — nodo open-collector condiviso: guasto comune e fallimento del veto

16 novembre 2026. **Studio di laboratorio virtuale, non qualifica di sicurezza**; schema KiCad9 THT isolato.

## Contratto elettrico realmente presente
Il nodo `WINDOW_GOOD_OC_BIASED_LAB` contiene soltanto U2201 pin 1/7, U2202 pin 1/7, R2207 pin 2 e J2204 pin 1. R2207 pin 1 è sul 5 V esterno non qualificato. Non vi è un secondo MOSFET/contattore serie che interrompa autonomamente il carico dopo questo segnale. Il doppio LM2903P costituisce soltanto un veto logico a collettore aperto: i due canali non sono indipendenti rispetto a corto del nodo OC, rail5V, ritorno o interfaccia di attuazione.

## Regressione
`verify_dual_lm2903p_shared_oc_fault_native.py` in FULL ricostruisce tutte le 14 reti/60 pin da netlist KiCad9 effettiva e vincola ogni pin del nodo OC. Nel solo modello DC ideale percorre **720.896** vettori (256 tolleranze × 256 indipendenti per A/B × 11 VIN da 0 a 48 V sintetici) con entrambe VREF esterne ipoteticamente sane 2,5V.

- NORMAL: a VIN13,8V **65.536 GOOD**; per VIN<9V o >16V **zero falsi GOOD** nel modello.
- Nodo **ipoteticamente forzato HIGH da sorgente esterna**: **524.288 falsi GOOD** fuori banda (otto tensioni fuori banda × 65.536 tolleranze), *anche se il comparatore desidera LOW*. Questa condizione è un limite logico imposto, **non** una simulazione elettrica di SHORT a 5V: la contesa con il transistor OC e le correnti di corto non sono modellate e non si afferma che la tensione HIGH sia fisicamente garantita.
- Nodo **ipoteticamente forzato LOW**: **65.536 falsi OFF** al VIN sano 13,8V.
- R2207 OPEN, VCC5V assente o output OC senza pull-up: la tensione **è indeterminata** nel modello, *non* è classificata come zero volt sicuro. Richiede analisi OEM, leakage, capacità, pull-down, front-end attuatore e margini.
- Due canali o riferimenti sani non eliminano il nodo comune; riferimento simultaneo guasto è già coperto dalla PR #320. Una seconda interruzione *fisica* fail-OFF e un'autentica architettura di supervisione indipendente sono ancora mancanti.

## Gate prima dell'integrazione e del prototipo
Controllare uscita e ingresso con modelli/datasheet OEM, correnti di contesa, front-end fail-low durante ramp-down/brownout, common return, Q806 C–E SHORT e independent switch; verifiche reali e fail-safe hardware. MAIN V2.6 e FRONT invariati, nessuna PCB. Issue #27 OPEN.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
