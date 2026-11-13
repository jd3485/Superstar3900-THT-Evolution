# V2.7 — IF455: controprova della banda sui sei assetti di rumore e carico

**13 novembre 2026 · analisi AC nativa ngspice, selettività radio e OEM non qualificati.**

La [PR #114](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/114) ha studiato R1601 smorzamento 47/100/220kΩ e R1602 uscita 100/220kΩ tramite 30 trasferimenti AC di segnale e rumore termico indipendente. Lo sweep mostra nel modello che **la minore densità di rumore equivalente riferita al generatore a 455kHz** appare nel caso 220k/220k (**14,73551 nV/√Hz**) rispetto alla baseline47k/100k (**27,75511 nV/√Hz**), ma cambia anche il trasferimento 0,835→2,557. Una classifica a singola frequenza NON determina un filtro RF corretto.

Questo studio aggiunge `03_Verifiche/V2.7/verify_if455_resistor_noise_bandwidth_crosscheck_native.py`: sei **nuove analisi AC ngspice effettive** su 300–650kHz/1401 campioni; due resistori modificati direttamente nel netlist ed esattamente la stessa rete passiva L1mH + loss16,5Ω assunta, C82p+30p, 10p input/output, RGEN50Ω. Raccoglie per ognuno: fpeak, limiti inferiori/superiori di −3dB, BW−3dB, indice fpeak/BW, trasferimento a 455k e quota |H455|/|Hpeak|. Valida <1% i sei valori di trasferimento risultanti dalla PR #114 e riproduce lo storico PR #110 (R47k/100k: fpeak ~454,75kHz, BW~42,56kHz).

**Criterio di utilizzo:** un maggiore valore di picco con resistenze alte può derivare da riduzione di damping/loaded-Q diverso e può alterare la banda utile per modulazione AM e la selettività. La miglior opzione per trasferimento e rumore di singola frequenza non è promossa a MPN né a stadio IF definitivo senza impedenza di sorgente realmente misurata, carico del rivelatore in tensione e frequenza, banda necessaria, PVT/OEM Rcoil ESR/Q, margini di accordo, e filtro multi-stadio a selettività adeguata.

Nessuna modifica al master V2.6, ai moduli KSP10/J113 standalone o alle PCB. Non sono stati effettuati test di ricezione, distorsione audio, noise figure completa o veicolo.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

## Esiti nativi verificati — PR #115 MERGED

[PR #115](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/115) **MERGED**, commit `9e677634f9facde583cab8a48c9b190d4337b5af`, run finale [#43508971077](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43508971077): FAST/FULL/required **3/3 PASS**, 111 comandi legacy e `PASS_NGSPICE_IF455_6_NOISE_TRADEOFF_AC_BANDWIDTH_NATIVE_NOT_RECEIVER_NO_FAB_NO_TX`. Sei AC ngspice reali su 300–650kHz/1401 punti, valori di H(455k) verificati entro 1% vs PR #114.

| R1601 damping | R1602 out | H455 V/V | picco (kHz) | banda−3dB (kHz) | rumore equip. sorgente PR114 (nV/√Hz) |
|---:|---:|---:|---:|---:|---:|
|47kΩ|100kΩ|0,835056|454,75|42,557|27,755|
|47kΩ|220kΩ|1,016659|456,00|36,521|24,486|
|100kΩ|100kΩ|1,280374|454,00|27,482|21,300|
|100kΩ|220kΩ|1,711592|455,50|21,576|18,306|
|220kΩ|100kΩ|1,723341|454,00|20,289|17,955|
|220kΩ|220kΩ|2,556853|455,25|14,419|14,736|

**Decisione:** nel SOLO circuito passivo con 16,5Ω di perdita RF ipotizzata e sorgente50Ω idealizzata, l'assetto 220kΩ/220kΩ è il più favorevole dei sei esaminati per **H455, rumore termico equivalente alla sorgente e banda a −3 dB più stretta**, ma NON è ancora uno stadio IF prodotto o selettività CB. Il trasferimento V/V superiore a 1 è risonanza passiva, non guadagno di potenza. La banda a −3dB di un solo risonatore non definisce la reiezione del canale adiacente e potrebbe non soddisfare AM/FM/SSB, soprattutto dopo altri filtri e carichi. Non modificare il CAD standalone o il master prima di: dati reali mixer/IF, banda audio obiettivo, curva completa maschera, PVT, rapporto RF loss/Q OEM, BOM THT, AGC e misure SINAD/THD. NO FAB/TX.
