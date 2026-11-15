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

## Decisioni e limiti tecnici

La variazione del coupling può alterare sia carico del tank, sia tensione sul gate, punto di lavoro e distorsione. Un valore che massimizza il picco AF non garantisce rumore inferiore, migliore selettività o minore distorsione; non è consentito ricavare direttamente sensibilità radio in µV, SINAD o THD, perché il generatore è a 50Ω ideale, il filtro ha 16,5Ω DCR assunto e il modello JGEN/DGENERIC **non è OEM**. Mancano curve PVT/temperature, impedenza uscita mixer, filtro ceramic/455k reale, alimentazione, Cgs/Cgd vendor, carico d'antenna, disturbi, ritorni chassis e layout RF.

Dopo la CI del **final SHA**, il confronto numerico può eliminare candidati evidentemente peggiori e motivare un successivo schema THT ad alta impedenza; **non** autorizza a cambiare C1801 in produzione o collegare elettricamente J113 al tank. Nessuna PCB prodotto e nessun DRC radio.

**Stato iniziale:** CI non ancora attribuita a questo branch. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
