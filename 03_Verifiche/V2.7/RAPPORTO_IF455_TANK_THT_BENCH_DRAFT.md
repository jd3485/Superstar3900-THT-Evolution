# V2.7 DRAFT — filtro IF a 455 kHz con risonatore LC THT, solo banco

**13 novembre 2026.** Realizzato un nuovo foglio KiCad9 `04_KiCad/V2.7_DRAFT/IF455_TANK/IF455_TANK_THT_V2_7_DRAFT.kicad_sch` con libreria locale e **9 riferimenti THT**, separato dal master radio V2.6 e dal rivelatore AM D1501, per un esperimento **passivo** di selezione 455 kHz. Non è amplificatore IF, non è filtro ceramico qualificato né sezione ricevente con specifiche di sensibilità.

## Collegamenti e valori di prova

| Ref | Funzione | Collegamenti |
|---|---|---|
| J1601 | ingresso IF 455k da generatore | pad1 `IF455_SOURCE`, pad2 `IF_BENCH_GND` |
| C1601 | 10 pF C0G coupling ingresso | `IF455_SOURCE` → `IF455_TANK` |
| L1601 | **1 mH** induttore RF THT CANDIDATO (OEM ignoto) | `IF455_TANK` → `IF_BENCH_GND` |
| C1602 | 120 pF C0G | `IF455_TANK` → `IF_BENCH_GND` |
| C1603 | 2,2 pF C0G | `IF455_TANK` → `IF_BENCH_GND` |
| R1601 | 47 kΩ shunt damping | `IF455_TANK` → `IF_BENCH_GND` |
| C1604 | 10 pF C0G coupling uscita | `IF455_TANK` → `IF455_FILTER_OUT` |
| R1602 | 100 kΩ output bias/load | `IF455_FILTER_OUT` → `IF_BENCH_GND` |
| J1602 | uscita verso strumento/altro pilot | pad1 `IF455_FILTER_OUT`, pad2 `IF_BENCH_GND` |

Frequenza di risonanza nominale ideale `1/(2π √(L·C))`: L=1mH e C1602+C1603=122,2pF ⇒ **455,29kHz**. Questo numero **non** è risposta passante reale: tolleranza induttore, perdite del nucleo, R serie, self-resonance/SRF, capacità parassite dei cavi e della PCB, carico d'ingresso al D1501, frequenza del generatore e temperatura cambiano profondamente centro banda, Q e perdita d'inserzione. Il modello passivo è in particolare **non tarabile**: in una versione radio reale sono necessari trasformatore IF accordabile, preamplificatore, filtri, impedenze note e test RF.

**Connettori di banco** THT 2 pin 2,54mm con geometria generica, NON definitivi per la scheda. **L1601 ha un footprint locale `TH_TANK:L_1mH_Axial_THT_PROVISIONAL`** con due pad passanti provvisori distanti 15,24mm (file KiCad .kicad_mod). La geometria **non è ricavata da un datasheet OEM** ed è vietata in produzione. Non è stata selezionata una bobina con Q e SRF adatti alla IF 455kHz: questo è il vincolo critico. C/R rimangono valori standard schematici secondo ADR-002, da completare con specifiche termiche/MPN esatti prima di FAB.

## Verifiche

`03_Verifiche/V2.7/verify_if455_tank_native.py` esegue nativamente `kicad-cli sch erc --exit-code-violations`, esporta netlist KiCad9, richiede 9 refs, 4 reti, tutti i pin-verso-net prescritti e i due pad THT provvisori, rifiuta footprint non THT, calcola frequenza ideale. Inserito in `ci/full_regressions.py` usando il runner già esistente (nessun nuovo job). **Non dichiarare ERC0 finché GitHub Actions sul final HEAD non è PASS.**

**Rischi aperti:** accoppiamento di 10pF e carico a 100k potrebbero rendere il trasferimento nullo o fortemente distorto a 455kHz; non abbiamo scelto un filtro RF industriale né un trasformatore IF con impedenze specificate. Serve almeno una scansione AC con modelli di perdite e tolleranze, poi datasheet OEM e misure di risposta passante/ripple/selettività e sensibilità, prima di integrare con J1501 del rivelatore AM. Non è il percorso SSB 10,695MHz o il discriminatore FM. Non inferire banda passante, guadagno, Q, reiezione di canale adiacente o emissioni da KiCad ERC.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.** MAIN V2.6 intatta 7 fogli/138 refs, PCB-MAIN/FRONT fisiche non progettate/routed (0%), avanzamento complessivo circa 20% stima.
