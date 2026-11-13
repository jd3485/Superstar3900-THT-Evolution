# V2.7 DRAFT — filtro IF a 455 kHz con risonatore LC THT, solo banco

**13 novembre 2026.** Realizzato un nuovo foglio KiCad9 `04_KiCad/V2.7_DRAFT/IF455_TANK/IF455_TANK_THT_V2_7_DRAFT.kicad_sch` con libreria locale e **9 riferimenti THT**, separato dal master radio V2.6 e dal rivelatore AM D1501, per un esperimento **passivo** di selezione 455 kHz. Non è amplificatore IF, non è filtro ceramico qualificato né sezione ricevente con specifiche di sensibilità.

## Collegamenti e valori di prova

| Ref | Funzione | Collegamenti |
|---|---|---|
| J1601 | ingresso IF 455k da generatore | pad1 `IF455_SOURCE`, pad2 `IF_BENCH_GND` |
| C1601 | 10 pF C0G coupling ingresso | `IF455_SOURCE` → `IF455_TANK` |
| L1601 | **1 mH** induttore RF THT CANDIDATO (OEM ignoto) | `IF455_TANK` → `IF_BENCH_GND` |
| C1602 | 110 pF C0G | `IF455_TANK` → `IF_BENCH_GND` |
| C1603 | 2,2 pF C0G | `IF455_TANK` → `IF_BENCH_GND` |
| R1601 | 47 kΩ shunt damping | `IF455_TANK` → `IF_BENCH_GND` |
| C1604 | 10 pF C0G coupling uscita | `IF455_TANK` → `IF455_FILTER_OUT` |
| R1602 | 100 kΩ output bias/load | `IF455_FILTER_OUT` → `IF_BENCH_GND` |
| J1602 | uscita verso strumento/altro pilot | pad1 `IF455_FILTER_OUT`, pad2 `IF_BENCH_GND` |

Frequenza di risonanza nominale ideale `1/(2π √(L·C))`: L=1mH e C1602+C1603=112,2pF ⇒ **475,12kHz**, **NON** centro effettivo perché i condensatori di ingresso e uscita alterano la reattanza. Questo numero **non** è risposta passante reale: tolleranza induttore, perdite del nucleo, R serie, self-resonance/SRF, capacità parassite dei cavi e della PCB, carico d'ingresso al D1501, frequenza del generatore e temperatura cambiano profondamente centro banda, Q e perdita d'inserzione. Il modello passivo è in particolare **non tarabile**: in una versione radio reale sono necessari trasformatore IF accordabile, preamplificatore, filtri, impedenze note e test RF.

**Connettori di banco** THT 2 pin 2,54mm con geometria generica, NON definitivi per la scheda. **L1601 ha un footprint locale `TH_TANK:L_1mH_Axial_THT_PROVISIONAL`** con due pad passanti provvisori distanti 15,24mm (file KiCad .kicad_mod). La geometria **non è ricavata da un datasheet OEM** ed è vietata in produzione. Non è stata selezionata una bobina con Q e SRF adatti alla IF 455kHz: questo è il vincolo critico. C/R rimangono valori standard schematici secondo ADR-002, da completare con specifiche termiche/MPN esatti prima di FAB.

## Revisione IF455 con carico di accoppiamento — PR tecnica in verifica

La prima PR #80 (integrata) usava 1mH+122,2pF e calcolava 455,29kHz **senza** includere il contributo dei due condensatori di accoppiamento da 10pF. Con la sorgente 50Ω e carico 100kΩ il centro risultava **spostato**, nel semplice modello di perdite della bobina da 30Ω in serie, verso ~437kHz. Il problema è stato individuato **prima della qualifica**, senza dichiarare fabbricabile il filtro.

**Modifica reale alla scheda KiCad9:** C1602 passa da **120pF a 110pF C0G**, C1603 rimane **2,2pF**, L1601 1mH provvisorio, C1601/C1604 coupling 10pF e R1601/R1602 invariati. La frequenza **LC scarica** non è più 455kHz: la formula semplificata L=1mH/C=112,2pF dà circa **475,1kHz**. In presenza di coupling, il picco simulato si sposta vicino a 455kHz; la correzione va validata con la CI nativa prima di dichiararla confermata.

**Nuovo test ngspice AC vero:** `spice/if455_loaded_tank_ac_comparison.cir`, due circuiti alimentati da sorgenti ideali 1Vac con **50Ω** di resistenza sorgente, R bobina **30Ω assunto**, condensatori e R di carico come KiCad; confronto C1602 vecchio 120pF e nuovo 110pF a 350–600kHz su 1001 punti. `verify_if455_loaded_ac_ngspice.py` legge i valori numerici `wrdata` prodotti da ngspice, cerca i picchi, verifica che quello nuovo sia vicino a 455kHz e migliori il vecchio centro di almeno 2× nella sola ipotesi del modello. Nessun nuovo job Actions: test dentro la FULL esistente.

**Dichiarazione di rischio invariata:** il valore 30Ω non è misurato né è una specifica OEM dell'induttore, e il footprint L1601 a 15,24mm resta **provisorio non fabbricabile**. La risposta effettiva dipende da Q/SRF, capacità parassite della bobina, PCB, temperatura, carico del diodo e valore d'impedenza del mixer/IF reale. La presenza di un picco in AC **non** costituisce specifica di banda selettiva o sensibilità. Occorre sostituire il modello e il footprint con un componente THT **attualmente prodotto**, verificare perdita d'inserzione/banda/ripple e taratura hardware.

---

## Verifiche

`03_Verifiche/V2.7/verify_if455_tank_native.py` esegue nativamente `kicad-cli sch erc --exit-code-violations`, esporta netlist KiCad9, richiede 9 refs, 4 reti, tutti i pin-verso-net prescritti e i due pad THT provvisori, rifiuta footprint non THT, calcola frequenza ideale. Inserito in `ci/full_regressions.py` usando il runner già esistente (nessun nuovo job). **Non dichiarare ERC0 finché GitHub Actions sul final HEAD non è PASS.**

**Rischi aperti:** accoppiamento di 10pF e carico a 100k potrebbero rendere il trasferimento nullo o fortemente distorto a 455kHz; non abbiamo scelto un filtro RF industriale né un trasformatore IF con impedenze specificate. Serve almeno una scansione AC con modelli di perdite e tolleranze, poi datasheet OEM e misure di risposta passante/ripple/selettività e sensibilità, prima di integrare con J1501 del rivelatore AM. Non è il percorso SSB 10,695MHz o il discriminatore FM. Non inferire banda passante, guadagno, Q, reiezione di canale adiacente o emissioni da KiCad ERC.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.** MAIN V2.6 intatta 7 fogli/138 refs, PCB-MAIN/FRONT fisiche non progettate/routed (0%), avanzamento complessivo circa 20% stima.
