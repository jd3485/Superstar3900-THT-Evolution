# V2.7 — studio convergenza timestep IF455 tank → BJT → AM455 (generico)

**13 novembre 2026.** Segue la PR #101, che ha dimostrato **nel modello** un forte degrado audio con il follower Q1701, a causa del carico sul filtro. Questa revisione **non cambia** il circuito KiCad9 né approva il KSP10BU.

## Problema emerso

La prima prova PR #101 a passo massimo **200 ns** non era ripetibile contro i risultati storici PR #94; a 50 ns il modello diretto invece ha riprodotto il riferimento storico ricalcolato a parità di passo entro **0,0604%**. Tuttavia i due valori a 2 V differivano fortemente: **0,17444891 Vpp (200ns storico) → 0,21445359 Vpp (50ns ricalcolato)**. Quindi la ripetibilità *fra modelli* non dimostra da sola la convergenza *rispetto al passo temporale*.

## Nuovo test ingegneristico

`03_Verifiche/V2.7/verify_if455_ksp10_cascade_timestep_convergence_native.py` esegue **sei simulazioni ngspice reali** del deck della PR #101, usando **ampiezza di ingresso 0,5V e 2,0V** × **timestep massimo 50ns / 25ns / 12,5ns**, su 12ms di segnale AM 455kHz modulato a 1kHz. Riporta AFpp diretto e con follower, picco RF positivo ai due nodi tank e rapporto buffer/diretto, assieme alle variazioni relative 50→25ns e 25→12,5ns. Verifica i risultati finiti e positivi e la riproduzione del caso 50ns già misurato in PR #101.

**Politica di test:** le variazioni di ogni metrica sono registrate con `below_two_percent`. Nell’ultimo dimezzamento **25→12,5ns** tutte le quattro metriche per ciascuno dei due livelli devono cambiare di **meno del 2%**, altrimenti il test FALLISCE. Questo è un gate di stabilità numerica del modello, **non** un PASS qualitativo hardware.

## Limiti tecnici

Il BJT è `QGEN` non OEM, il diodo è `DGENERIC` non 1N4148 OEM, la bobina ha Rcoil=16,5Ω **assunta**, e la sorgente 50Ω e rail 6V sono ideali. Nessuna simulazione copre noise figure, SNR, SINAD, distorsione di modulazione, deriva termica RF, selettività o AGC. **Lo schema follower della PR #97 non va integrato nel master RX**: il carico osservato nella PR #101 è un blocco funzionale e servono alternative di adattamento e modelli/MPN qualificati.

**Nessuna PCB reale, nessun DRC: NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

## Misure native registrate — run #43474410171, commit 8308761

[GitHub Actions #43474410171](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43474410171), commit iniziale tecnico `830876167be334752c54ff1f74b650526fe126a6`: FULL KiCad9/ngspice **success**, 111 comandi storici e `PASS_NGSPICE_IF455_KSP10_AM455_6_TIMESTEP_AUDITS_NOT_OEM_NO_FAB_NO_TX`. I valori e gli scostamenti rilevati sono:

| Ampiezza RF sorgente | Timestep massimo | AFpp diretto, V | AFpp con KSP10, V | Rapporto con/senza buffer |
|---:|---:|---:|---:|---:|
| 0,5V | 50ns | 0,023326606 | 0,000741563 | 3,1790% |
| 0,5V | 25ns | 0,023924605 | 0,000752869 | 3,1468% |
| 0,5V | 12,5ns | 0,024045417 | 0,000755608 | 3,1424% |
| 2,0V | 50ns | 0,214324050 | 0,014614407 | 6,8188% |
| 2,0V | 25ns | 0,216298180 | 0,015565562 | 7,1963% |
| 2,0V | 12,5ns | 0,216750780 | 0,015801883 | 7,2903% |

**Stato di convergenza del modello:** al dimezzamento finale **25→12,5ns**, scostamenti AFpp diretto e con buffer rispettivamente **0,502% / 0,362%** a 0,5V e **0,209% / 1,496%** a 2V; i quattro picchi RF dei due livelli presentano scostamenti inferiori allo **0,37%** nello stesso passo. **Tutte le otto misure AF/RF** variano di meno del **2%** nell'ultimo dimezzamento. Per questo la condizione viene trasformata in un controllo obbligatorio del test nativo (non basta stampare il flag). Questo indica una convergenza *pratica limitata al modello e alle misure verificate*, non una precisione certificata del componente OEM o del ricevitore.

Al precedente dimezzamento 50→25ns non tutte le metriche erano sotto 2%: AFpp diretto 0,5V **2,500%**; AFpp buffer 2V **6,111%**. L'uso indiscriminato dei precedenti dati a 200ns è quindi inappropriato per scelte di progetto definitive.

**Decisione tecnica invariata, con maggiore supporto numerico:** nel modello generico il filtro IF455 pilotato direttamente produce audio molto superiore al percorso con Q1701 a collettore comune, in entrambi i livelli. Il follower attuale con bias 22k/10k e C1701=10nF è **rifiutato come candidato integrabile** finché non si riprogetta l'adattamento ed è verificato con modelli/dati OEM e prove RF. Nessun master V2.6/PCB modificato.
