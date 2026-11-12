# V2.7 DRAFT — Interfaccia FRONT_VOLUME THT

**12 novembre 2026.** Primo circuito elettrico **standalone** per il controllo volume sulla futura PCB-FRONT, conforme a ADR-001 (PCB-MAIN e PCB-FRONT separate). La documentazione non costituisce release meccanica, BOM o PCB; nessun collegamento è stato aggiunto al master V2.6 o al modulo audio MAIN esistente.

## Collegamenti progettati

| Posizione | Funzione | Montaggio |
|---|---|---|
| J1301 | Ingresso audio dal **futuro demodulatore RX**: pin 1 `DEMOD_AUDIO`, pin 2 `AF_GND` | Connettore 2 pin THT, da rivedere in base a interconnessione reale |
| RV1301 | Potenziometro **10 kΩ, legge lineare B**: pin 1 `DEMOD_AUDIO`, pin 2 cursore `VOL_WIPER_TO_AMP`, pin 3 `AF_GND` | **Impronta THT 3 pin PROVVISORIA**, non qualificata per produzione |
| J1302 | Uscita verso ingresso modulo LM386: pin 1 `VOL_WIPER_TO_AMP`, pin 2 `AF_GND` | Connettore 2 pin THT, da rivedere |

Tutti i simboli e i tre componenti fisici sono in `04_KiCad/V2.7_DRAFT/FRONT_VOLUME/FRONT_VOLUME_THT_V2_7_DRAFT.kicad_sch`, con libreria locale e `sym-lib-table`. Pattern preliminare `TH_FRONT.pretty/Potentiometer_THT_3Pin_PROVISIONAL.kicad_mod` con **soli pad passanti** 1/2/3 a 2,54 mm. **Non è una sagoma di potenziometro reale** e non deve essere usato per layout finale, acquisto o fabbricazione.

## Collegamento logico con MAIN audio (non ancora eseguito nel master)

Il pilot MAIN precedente `AUDIO_RX_MONO_LM386_V2_7_DRAFT.kicad_sch` espone un connettore J1202 (segnale AUDIO_IN + GND). La futura interconnessione proposta, da documentare e verificare su schemi collegati, è:

`RX demod AF -> J1301 pin 1 -> RV1301 pin 1 -> RV1301 wiper pin 2 -> J1302 pin 1 -> J1202 pin 1 -> C1201/R1201 -> LM386`.

La massa audio è comune **solo nello schema funzionale**: va progettata la strategia delle masse/ritorni di corrente analogici per evitare ronzio, loop di massa e interferenze RF; non collegare le masse alla cieca. Nessun demodulatore è stato ancora aggiunto. Il pannello finale richiede anche fissaggio meccanico, albero e manopola compatibili con il modello Evolution, distanze e fori.

## Prove e rischi

- Il test `03_Verifiche/V2.7/verify_front_volume_native.py` richiede **ERC nativo KiCad9 senza violazioni**, netlist esportata da KiCad9 con i tre riferimenti e le tre reti. È stato incluso nella CI FULL attraverso `ci/full_regressions.py`. I risultati devono essere acquisiti dalla CI PR su SHA finale; non dichiarare anticipatamente ERC0.
- La sola conformità ERC **non prova** legge di regolazione, rumore del cursore, costanza dell'impedenza di ingresso e risposta del LM386. L'amplificatore attuale mantiene R1201=10k; con un pot 10k la curva audio finale e il guadagno vanno rivalutati. La scelta lineare vs logaritmica deve essere basata su ergonomia/audio e disponibilità di codici THT attivamente fabbricati.
- Prima del freeze meccanico: selezione OEM esatta del potenziometro **100% THT per PCB-FRONT**, disegno meccanico reale di corpo/asse/fori, footprint pin/pad e tolleranze; verificare se serva una soluzione diversa per un frontale radio a manopola.
- Rimane da progettare alimentazione del modulo audio MAIN isolata dai rail RF; nessun ingresso o uscita TX né cablaggio batteria/veicolo.

**Stato complessivo:** master radio MAIN V2.6 invariato, modulo audio RX MAIN DRAFT nativo precedente da 12 ref verificato, nuovo FRONT_VOLUME da 3 ref in revisione. I 138 riferimenti dell'inventario OEM V2.6 sono solo del master e non includono i DRAFT. Gate BOM finale e Issue #27/#42 invariati. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
