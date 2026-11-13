# V2.7 — studio convergenza timestep IF455 tank → BJT → AM455 (generico)

**13 novembre 2026.** Segue la PR #101, che ha dimostrato **nel modello** un forte degrado audio con il follower Q1701, a causa del carico sul filtro. Questa revisione **non cambia** il circuito KiCad9 né approva il KSP10BU.

## Problema emerso

La prima prova PR #101 a passo massimo **200 ns** non era ripetibile contro i risultati storici PR #94; a 50 ns il modello diretto invece ha riprodotto il riferimento storico ricalcolato a parità di passo entro **0,0604%**. Tuttavia i due valori a 2 V differivano fortemente: **0,17444891 Vpp (200ns storico) → 0,21445359 Vpp (50ns ricalcolato)**. Quindi la ripetibilità *fra modelli* non dimostra da sola la convergenza *rispetto al passo temporale*.

## Nuovo test ingegneristico

`03_Verifiche/V2.7/verify_if455_ksp10_cascade_timestep_convergence_native.py` esegue **sei simulazioni ngspice reali** del deck della PR #101, usando **ampiezza di ingresso 0,5V e 2,0V** × **timestep massimo 50ns / 25ns / 12,5ns**, su 12ms di segnale AM 455kHz modulato a 1kHz. Riporta AFpp diretto e con follower, picco RF positivo ai due nodi tank e rapporto buffer/diretto, assieme alle variazioni relative 50→25ns e 25→12,5ns. Verifica i risultati finiti e positivi e la riproduzione del caso 50ns già misurato in PR #101.

**Politica di test:** se un'ampiezza varia oltre il 2% al dimezzarsi del passo, la registriamo come `below_two_percent: false` e la consideriamo **non convergente**, senza camuffare il dato in un PASS qualitativo hardware. Il test che termina con SUCCESS significa solo che *tutte le simulazioni e il confronto numerico sono stati eseguiti e resi visibili*. Non qualifica alcun circuito reale.

## Limiti tecnici

Il BJT è `QGEN` non OEM, il diodo è `DGENERIC` non 1N4148 OEM, la bobina ha Rcoil=16,5Ω **assunta**, e la sorgente 50Ω e rail 6V sono ideali. Nessuna simulazione copre noise figure, SNR, SINAD, distorsione di modulazione, deriva termica RF, selettività o AGC. **Lo schema follower della PR #97 non va integrato nel master RX**: il carico osservato nella PR #101 è un blocco funzionale e servono alternative di adattamento e modelli/MPN qualificati.

**Nessuna PCB reale, nessun DRC: NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
