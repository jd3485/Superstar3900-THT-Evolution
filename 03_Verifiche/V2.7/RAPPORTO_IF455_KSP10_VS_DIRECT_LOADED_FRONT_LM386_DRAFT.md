# V2.7 — confronto dell'IF455 diretto e con follower KSP10 al vero ingresso LM386 (modello da banco)

**15 novembre 2026 — non qualifica hardware/OEM.** La precedente PR #102 aveva quantificato il buffer KSP10 sul carico AF isolato di 100 kΩ, riscontrando **peggioramento importante** del percorso rispetto al diodo diretto. PR #235 e #236 hanno mostrato inoltre che il potenziometro e l'impedenza di ingresso LM386 caricano il rivelatore. È quindi necessario confrontare **entrambe le scelte IF** quando sono alimentate dal carico AF reale, senza usare come unico criterio la tensione su AF 100kΩ.

## Esperimento verificabile

Il deck `03_Verifiche/V2.7/spice/if455_ksp10_am455_front_lm386_loaded_generic_comparison.cir` deriva dal circuito `spice/if455_ksp10_am455_combined_generic_transient.cir`, preservando ogni carta IF455, diodo DGENERIC, BJT QGEN, bias e nodo AF originali. Due **sorgenti AM ideali separate** a 455 kHz, 1 kHz audio e 50% modulazione, con stessa impedenza sorgente 50 Ω, alimentano due LC e rivelatori indipendenti. Il primo è **diretto**; il secondo usa Q1701 KSP10 emitter follower con 22k/10k/2k2, C1701=C1702 10nF, uscita R1704 100k. A ciascun AF viene aggiunta **la stessa** catena RV1301=10k, C1201=100nF, R1201=10k, R_in(LM386)=50kΩ tipica, senza amplificatore attivo.

Lo script `verify_if455_ksp10_am455_front_loaded_comparison_native.py` confronta i due segnali **sul pin 3 idealizzato LM386** su **6 transienti ngspice** (ingresso 0,5/2 V picco × wiper 10/50/90%), passo massimo **50 ns**, 12 ms di transitorio, misure 8–11 ms, e controlla che entrambi i carichi non generino un guadagno passivo. Testa l'identità delle carte SPICE originali e verifica via esportazione KiCad9 le reti IF455_TANK_OUT, IFBUF_AC_OUT, VLAB6_IFBUF_ONLY e IF_BENCH_GND del componente fisico Q1701/THT.

## Criterio di decisione

Una diversa ampiezza AF tra le due soluzioni non equivale a migliore ricezione: senza rumore, selettività, impedenze reali, modelli OEM, distorsione, saturazione, PVT e prova del cablaggio/chassis, non è possibile selezionare uno stadio di prodotto. **Se il modello generico conferma che il follower riduce il segnale rispetto alla soluzione diretta, non integrare quel follower nel percorso RF del MAIN.** Sviluppare un adattamento IF ad alta impedenza verificato, mantenendo il MASTER 176-ref a cinque fogli completamente separati per ora.

La fonte Vishay 1N4148 (doc 81857 rev 1.6) è solo una verifica di alcuni limiti; il diodo DGENERIC non è un modello OEM, e il transistor QGEN non è un modello onsemi KSP10BU. Il rail 6 V è ideale e indipendente, le masse idealizzate; nessuna analisi di NF, SINAD, distorsione, layout, reverse supply, EMI/ESD, FRONT meccanico, produzione del filtro ceramico o quota di PCB completata. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

**Stato del branch:** esito FAST/FULL/required da verificare sul final SHA prima del merge. Il percorso corretto di qualifica prevede una reale impedanza d'ingresso IF, alimentazione validata, dati dei componenti attivi e misure RF sul banco.
