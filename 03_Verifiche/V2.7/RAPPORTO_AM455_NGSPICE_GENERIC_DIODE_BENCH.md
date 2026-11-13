# V2.7 — test dinamico AM 455 kHz con ngspice, **modello diodo GENERICO**

**13 novembre 2026.** Questo circuito serve a controllare **con simulazione ngspice transitoria reale** il principio della rivelazione d'inviluppo nel prototipo THT AM455, senza sostituire dati reali di Vishay, prova RF di sensibilità o circuito completo AM/FM/SSB della radio.

## Sorgenti e circuito
- Nuovo file `03_Verifiche/V2.7/spice/am455_envelope_1khz_generic_diode_bench.cir`.
- Due reti uguali alla topologia CAD di PR #77, una eccitata con portante **455 kHz**, ampiezza **2,0 V picco** e AM sinusoidale **1 kHz, indice 0,5**, l'altra con identica portante **non modulata**. La sorgente e la resistenza serie 50Ω sono **generatori da banco ideali**, non amplificatori IF reali.
- Il modello `.model DGENERIC` è una **diode model numerica scelto per esperimento**, non un macromodello OEM Vishay 1N4148-TAP né una prova di carica di giunzione per i lotti reali; nessuna licenza a dichiarare certificazione RF.
- Rilevatore: D anodo IF → catodo `env`, `47kΩ` e `1nF` verso massa, `100nF` serie verso uscita, `100kΩ` dall'AF verso massa, come nella netlist KiCad 9. Gli stessi componenti sono replicati nel caso senza modulazione.
- Transitorio fino a 42 ms con passo massimo 0,20µs per risolvere il periodo portante ~2,2µs; `.meas tran` rileva massimo e minimo AF fra 30 e 40 ms, per ridurre gli effetti del collegamento AC iniziale.

## Esito reale della prima esecuzione nativa (PR #78)

La [PR #78](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/78) è stata integrata al commit `caa5288fbb5ea6d6c26c8099ef62fb2f51b800fd`, dopo [Actions #43407974037](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43407974037) **3/3 PASS** sul final HEAD `5968ee408df3904c243c11faa3ccbeec2a1f6157`. La FULL ha eseguito ngspice reale e stampato:
- `AM455_SPICE_BENCH_AM_P2P_V 1.9125 UNMOD_P2P_V 0.1255`;
- `PASS_NGSPICE_AM455_GENERIC_DIODE_AM_VS_UNMOD_BENCH_NO_FAB_NO_SSB_FM`;
- `PASS_KICAD9_AM455_THT7_ERC0_DIODE_CATHODE_NETS_BENCH_ONLY_NO_FAB` con ERC nativo `0 Errors 0 Warnings`, e **111 regressioni storiche** eseguite.

**Interpretazione corretta:** il caso senza modulazione mostra **0,1255V picco-picco non nulli** nella finestra di misura, dovuti anche al transitorio ancora presente della rete di accoppiamento e al residuo di portante; il risultato non è una specifica di soppressione della RF. L'ampiezza del caso AM dipende dall'ampiezza di iniezione 2 Vpk e dal modello diodo generico, **non** è il livello che avremo nella radio. Questa PR non convalida sensibilità, selettività, THD, SSB, FM, né componenti OEM.

---

## Gate automatico aggiunto a FULL
Lo script `03_Verifiche/V2.7/verify_am455_generic_diode_spice.py` invoca **ngspice reale**, richiede le quattro misure numeriche AF, rifiuta errori e valori non finiti, verifica che la portante AM produca un segnale AF sensibilmente maggiore della portante non modulata, e confronta l'ampiezza picco-picco con un intervallo **molto ampio** per evitare di fingere un modello vendor. L'esito è `PASS_NGSPICE_AM455_GENERIC_DIODE_AM_VS_UNMOD_BENCH_NO_FAB_NO_SSB_FM` **solo se il simulatore termina e produce misure valide**. La CI FULL riutilizza l'unico runner KiCad9/ngspice già esistente e mantiene tutte le suite ERC/netlist storiche.

**Non confondere le grandezze:** questo test dimostra al massimo la separazione funzionale AM modulata vs non modulata nel **modello comportamentale**. Non valida profondità di modulazione in presenza di fading, distorsione d'inviluppo con bassi livelli, sensibilità CB, impedenza filtri ceramici, guadagno IF, reiezione spettrale, rumore, spur, sincronismo AM, modo FM o SSB. La scelta diodi e l'architettura V2.7 della radio restano aperte.

## Gate di fabbricazione invariati
MASTER MAIN V2.6 7 fogli/138 refs, i tre pilot audio V2.7 e AM455 THT standalone (7 refs) sono separati; nessuna PCB elettrica integrata, nessun layout, nessun DRC reale. Prima di qualunque routing RF occorrono la catena mixer/IF, filtri e MPN OEM attuali, AGC/S-meter, gli stadi di demodulazione corretti per AM/FM/SSB, la scelta audio 8Ω (LM386 6V solo poche centinaia mW, sotto il target alcuni W dei precedenti modelli) e la sicurezza di alimentazione. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
