# V2.7 — IF455 J113: sensibilità a basso livello del condensatore di accoppiamento C1801

**15 novembre 2026 — screening numerico, non qualifica RF/OEM.** Nella [PR #242](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/242) il follower J113 con C1801=10pF nominale perde circa 40% di Vpp al pin3 LM386 con generatore idealizzato IF 0,5Vpicco rispetto al rivelatore AM diretto, mentre a 2Vpicco supera il riferimento (~2,34×). La risposta è dipendente dal livello. Prima di scegliere un componente, il presente esperimento isola l'effetto del condensatore C1801 e riduce il livello d'ingresso.

## Esperimento elettrico

Lo script `03_Verifiche/V2.7/verify_if455_j113_c1801_lowdrive_loaded_native.py` utilizza il deck **già approvato solo come modello generico** `spice/if455_j113_am455_front_lm386_loaded_generic_comparison.cir`, senza alterare mixer, tank, circuito bias, JFET, diodo, rivelatore AM o caricamenti FRONT/LM386. Restano due catene identiche e indipendenti, una diretta e una tramite J113. L'unico parametro modificato sul secondo ramo è C1801.

| Parametro | Scenari |
|---|---|
| C1801 (collegamento IF tank→JFET gate) | 2,2 / 4,7 / **10** / 22 pF |
| Sorgente AM ideale 455 kHz / 1 kHz / modulazione 50% | 0,10 / 0,25 / 0,50 V picco |
| Potenziometro FRONT | 90% da massa, RV1301 10k |
| Ingresso IC audio | C1201 100nF, R1201 10kΩ, Rin LM386 50kΩ tipica |
| Simulazione | 12 transitori ngspice, passo massimo 25ns, 12ms, misure 8–11ms |

Il gate rifiuta deriva del percorso diretto in funzione di C1801 (tolleranza numerica <1e-6), verifica ampiezza al pin3 e livello tank, escursione source e Vgs; controlla realmente con **netlist KiCad9** la porta J1801/1→C1801/1, C1801/2→Q1801 gate pin3 e il riferimento 6V LAB sul drain pin1. La **sola** versione realmente presente nello schema J113 corrente è **C1801=10pF**. Tutte le altre capacità sono *candidati di simulazione* e non modificano il CAD master 176-ref.

## Risultati effettivi (GitHub Actions, non misura fisica)

**[PR #244](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/244) MERGED** main `8d1f8f13d91e82e8aeb30cd9730af82d0b7996d8`, head tecnico `02843df600a0c1ccecf306c9edd5a5ca50597ae6`; [run #43719947367](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43719947367): FAST/FULL/required verde 3/3, 111 verifiche legacy e 12 transienti effettivamente PASS.

| Generatore IF ideale, picco | Diretto LM386 pin3 (mVpp) | J113 a 10pF realmente in CAD (mVpp) | J113 a 22pF, solo SPICE (mVpp) | Rapporto J113 22p/diretto |
|---:|---:|---:|---:|---:|
| 0,10 V | 0,594 | 0,410 | 0,442 | 0,744 |
| 0,25 V | 1,517 | 1,030 | 1,112 | 0,733 |
| 0,50 V | 5,737 | 3,427 | 4,417 | 0,770 |

Il modello con 22pF genera più AF al pin3 rispetto a 10pF su tutti e tre i livelli, ma **rimane comunque inferiore al percorso diretto**. In parallelo il picco positivo al nodo IF tank del buffer si riduce all'aumentare del C1801: a 0,5 V sorgente, da 0,5917 V (2,2p) a 0,5639 V (22p), segnalando maggiore influenza sul tank in questa rete. I valori sono di un generatore 455k ideale con modelli generici, *non* livelli minimi del Superstar né misure OEM.

La prima FULL del branch ha fermato un controllo di confronto numerico troppo rigido (1 ppm contro oscillazione ~5 ppm del calcolo con integrazione adattiva in rami separati); la verifica è stata resa fisicamente motivata con soglia **0,01%** di deriva tra rami diretti invarianti, senza deroghe ERC o alterazioni delle carte del circuito. La FULL **finale** è verde. Non congelare il condensatore a 22p o il follower nel progetto: mancano modello di impedenza di ingresso IF, noise figure, livello RF minimo, carico del tank reale e prova produttore.

## Decisioni e limiti tecnici

La variazione del coupling può alterare sia carico del tank, sia tensione sul gate, punto di lavoro e distorsione. Un valore che massimizza il picco AF non garantisce rumore inferiore, migliore selettività o minore distorsione; non è consentito ricavare direttamente sensibilità radio in µV, SINAD o THD, perché il generatore è a 50Ω ideale, il filtro ha 16,5Ω DCR assunto e il modello JGEN/DGENERIC **non è OEM**. Mancano curve PVT/temperature, impedenza uscita mixer, filtro ceramic/455k reale, alimentazione, Cgs/Cgd vendor, carico d'antenna, disturbi, ritorni chassis e layout RF.

Dopo la CI del **final SHA**, il confronto numerico può eliminare candidati evidentemente peggiori e motivare un successivo schema THT ad alta impedenza; **non** autorizza a cambiare C1801 in produzione o collegare elettricamente J113 al tank. Nessuna PCB prodotto e nessun DRC radio.

**Stato verificato:** PR #244 integrata dopo FULL finale verde su HEAD tecnico, nessuna approvazione hardware. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
