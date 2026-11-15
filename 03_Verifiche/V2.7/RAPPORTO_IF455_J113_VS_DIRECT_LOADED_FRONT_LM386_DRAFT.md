# V2.7 — confronto J113 high-Z vs IF diretto a valle del carico FRONT/LM386

**15 novembre 2026 — prova numerica generica, non qualifica OEM o prototipo.** PR #241 ha verificato che con il carico FRONT 10k/LM386 50k tipico il follower KSP10 10nF conserva solo ~9–10% dell'AF diretta, in sei scenari. L'alternativa onsemi J113 TO-92 era stata studiata con condensatore IF→gate **10pF C0G**, polarizzazione source 2k2, gate 1Meg e carico uscita 100k, ma non era stata confrontata al pin3 LM386 con il volume frontale. Questo rapporto indirizza il gap.

## Verifica CAD e SPICE

Deck `spice/if455_j113_am455_front_lm386_loaded_generic_comparison.cir` deriva **senza modificare le carte RF/IF precedenti** dal `if455_j113_am455_generic_jfet_transient.cir` di 12 scenari. Due sorgenti separate IF455 modulate AM al 50%, L1601/ESR=16,5Ω assunta, DGENERIC e RC envelope identici. Il ramo J113 usa JGEN generico, alimentazione ideale 6V LAB e coupling C1801=10pF. Due carichi equivalenti FRONT/LM386 per entrambi i rami: RV1301=10k, C1201=100n, R1201=10k e Rin IC=50kΩ tipica, senza guadagno IC attivo.

Il gate `verify_if455_j113_am455_front_loaded_comparison_native.py` verifica su **netlist KiCad9 reale** le nove posizioni fisiche J1801-1803/Q1801/R1801-1803/C1801-1802, porta input J1801→gate, source/output J1802 e rail 6V laboratorio separato. Per livelli sorgente 0,5 e 2 Vpicco, e volume 10/50/90%, esegue **sei** veri transitori ngspice da 12ms, passo 25ns, misura Vpp nel periodo 8-11ms su pin3 ideale. Conferma assenza di guadagno in rete passiva e monotonicità con wiper nel modello, senza inventare soglie prestazionali di qualifica.

## Significato del confronto

Una maggiore ampiezza non è rumore inferiore: nessun calcolo di NF, SINAD, IMD, dinamica AGC, compatibilità FM/SSB, banda RF e massa fisica. Nessun macromodello OEM J113 o Vishay 1N4148, né l'ingresso 50k tipico prova un min/max garantito LM386; sorgente IF 50Ω e filtro idealizzato non descrivono il vero mixer. Il gate serve a identificare candidati *da provare* prima di collegare il modulo standalone al master MAIN. **Restano aperte** qualificazione pin/package/produzione OEM, interazione impedenza C1801 col tank, alimentazione 6V e ritorni, controllo EMI/ESD, misura su banco.

**Stato iniziale: CI da verificare sul final HEAD.** Nessuna PCB o prodotto fabbricabile, DRC radio non eseguito. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
