# V2.7: carico AC effettivo del percorso audio post-mute

Data: 16 novembre 2026. Analisi del solo percorso **RX** con contatto NO ideale selezionato, senza abilitare trasmissioni e senza qualificare hardware.

## Differenza verificabile rispetto al modello precedente

Il test `verify_am455_front_lm386_loaded_ac_native.py` modellava il segnale dal detector AM455 attraverso RV1301 direttamente verso l'ingresso LM386 (C1201 100 nF, R1201 10 kΩ, Rin LM386 ipotetica 25–75 kΩ); rimane un utile modello storico di volume isolato, ma **non** la topologia di ascolto dopo l'aggiunta di K1901.

Nel CAD FRONT il relè K1901/3 (NO) riceve `VOL_WIPER_TO_AMP`, mentre COM K1901/1 si connette a R1902/1 (1 kΩ), R1902/2 a `AMP_INPUT_MUTED` con R1901 (100 kΩ) in shunt ad `AF_GND`; J1902/1 è l'uscita effettiva verso l'amplificatore. Un contatto NC, quando non energizzato, porta COM a massa, ma ciò **non** certifica il mute sicuro con contatto NO saldato, AF_GND aperta o guasto driver.

## Nuovo modello e gate

`verify_front_postmute_loaded_ac_native.py` verifica prima le netlist KiCad9 effettive di detector, potenziometro, mute e amplificatore, poi risolve **75 combinazioni** (5 frequenze 100 Hz–10 kHz, 5 posizioni cursore, 3 resistenze ingresso ipotetiche LM386). Due algoritmi indipendenti — riduzione di impedenze e **KCL complessa a quattro nodi** — devono coincidere. Il nuovo modello confronta il trasferimento con il vecchio modello che ometteva R1902/R1901, esigendo attenuazione aggiuntiva per i parametri selezionati. Il test viene aggiunto alla suite FULL.

Non copre contatti reali, sorgente detector non ideale, non linearità di demodulazione, guadagno e distorsione LM386, cavi schermati, EMI/ESD, return-current, ground loop, PVT o capacità dei contatti a microsegnale. Il codice non prescrive layout fisico né hardware fabbricabile.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**