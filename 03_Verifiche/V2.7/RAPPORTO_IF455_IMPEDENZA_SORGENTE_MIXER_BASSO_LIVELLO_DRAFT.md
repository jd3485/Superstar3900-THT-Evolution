# V2.7 — impedenza equivalente d'uscita mixer IF455 e segnali deboli (due catene D/J113)

**15 novembre 2026 — studio di rischio elettrico.** Le precedenti PR #242 e #244 hanno riscontrato che il follower J113 con C1801=10pF riduce la tensione AF del rivelatore a basso livello nel modello e che aumentare C1801 a 22pF non batte il rivelatore diretto. Il generatore comune usato finora aveva **50Ω ideali**: non è stata qualificata l'impedenza vera dell'uscita mixer/trasformatore IF. Pertanto occorre analizzare separatamente la dipendenza dal generatore, anziché interpretare il rendimento simulato di un follower come sensibilità RF.

## Esperimento nativo

Il gate `03_Verifiche/V2.7/verify_if455_mixer_source_impedance_lowdrive_native.py` riusa esattamente il deck `spice/if455_j113_am455_front_lm386_loaded_generic_comparison.cir` (due tank separati e uguali a 455k, rivelatori non lineari DGENERIC, JGEN J113 con C1801 **10pF**, carico R1502/FRONT RV1301 10k al 90%/C1201 100n/R1201 10k/LM386 Rin=50k tipica). Cambia SOLO le due resistenze equivalenti di sorgente identiche RGEND/RGENB da 50Ω a 1k/10kΩ e il picco AM modulato a 0,01/0,10V. Esegue **6 transitori ngspice** a passo massimo 25ns, 12ms, misura AFpp ai due pin3, picco positivo ai due tank, e rifiuta numeri non finiti/non positivi, amplificazioni della rete AF passiva e risultati non crescenti al crescere dell'ampiezza con la medesima sorgente. Le porte fisiche dell'alternativa J113 sono verificabili via netlist KiCad9 nativa: J1801/C1801→Q1801 gate pin3, C1802/J1802 uscita. **Nessun cambiamento ai componenti KiCad del master MAIN (176 refs) e FRONT.**

| Variabile | Condizioni |
|---|---|
| Generatore sinusoidale AM a 455kHz / 1kHz / 50% | 10 e 100mV picco *ideali* |
| Impedenza serie della sorgente IF | 50Ω / 1kΩ / 10kΩ, **scenari non OEM** |
| C1801 del J113 | 10pF THT candidato, unico valore effettivo CAD |
| Carico audio | RV1301 10k 90%, C1201 100n, R1201 10k, Rin 50k tipica |
| Diodo/JFET | modelli generici DGENERIC/JGEN non forniti dai fabbricanti |

## Evidenze CI finali e risultati del modello

**[PR #246](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/246) MERGED** su main SHA `76d8ec22fceeb4e16c3762142631dee27b5f1916`, final technical head `d0d68660705a8680cd4585d99b903a0a501b0d02`; [run #43721827904](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43721827904): FAST/FULL/required **3/3 SUCCESS**, 111 regressioni storiche e sei transienti nuovi verificati.

| Sorgente 455kHz, picco | Rsource | Diretto LM386 pin3 | J113 LM386 pin3 | J113/diretto |
|---:|---:|---:|---:|---:|
| 10mV | 50Ω | 59,33µVpp | 40,91µVpp | 0,6894 |
| 10mV | 1kΩ | 57,88µVpp | 39,92µVpp | 0,6898 |
| 10mV | 10kΩ | 46,36µVpp | 31,96µVpp | 0,6894 |
| 100mV | 50Ω | 0,5939mVpp | 0,4096mVpp | 0,6896 |
| 100mV | 1kΩ | 0,5793mVpp | 0,3997mVpp | 0,6900 |
| 100mV | 10kΩ | 0,4639mVpp | 0,3199mVpp | 0,6896 |

**Decisione:** queste variazioni della resistenza serie del generatore **non recuperano** il deficit AF a basso segnale del J113 con C1801=10pF: circa 31% in meno nel modello. Un aumento di Rsource fino a 10k riduce in modo simile la tensione recuperata in entrambi i percorsi. Non è una misura dell'impedenza reale mixer/IF del Superstar né una vera sensibilità in µV antenna. La selezione del buffer e l'integrazione KiCad di prodotto restano bloccate fino alla qualifica RF/rumore/OEM.

## Gate tecnico prima di integrare hardware

Qualsiasi differenza numerica con Rsource identifica una sensibilità del **modello**, non fissa da sola l'impedenza del mixer reale. Questi dati NON sono misure in microvolt dell'antenna né NF, SINAD, selettività RF, AGC, linearità in temperatura, distorsione AM/FM/SSB, protezioni ESD o capacità del layout RF. La rete LC con ESR 16,5Ω e 50Ω del benchmark è una rappresentazione parziale del banco; lo stadio mixer/trasformatore IF reale, accoppiamenti e impedenza di carico/matching non sono ancora qualificati.

**Decisione:** non congelare il J113 né il rivelatore diretto come soluzione di prodotto prima di definire i dati dell'uscita IF, dei rientri di massa e dei guadagni/rumore. I due restano alternative di progettazione. Se il test ha successo, documentare il suo run FAST/FULL/required su final HEAD e i Vpp reali; non interpretare CI verde come PCB pronta.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
