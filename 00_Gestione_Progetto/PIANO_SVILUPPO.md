# Piano di sviluppo progressivo — baseline V0.1

La numerazione indica una **sequenza proposta**, non una dichiarazione che i moduli siano già completi; si può rivedere quando emergono dipendenze. A ogni revisione: elaborati veri, test riproducibili quando possibili, rischi e rapporto tecnico.

| Revisione obiettivo | Modulo | Deliverable minimi |
|---|---|---|
| V0.1 | Fondazione | Requisiti, esclusioni, architettura preliminare, registro decisioni, metodo GitHub |
| V0.2 | Piano frequenze + sintesi | CSV di 270 posizioni RX, gamma oscillatori, scelta IF candidata, almeno due alternative PLL/VCO THT documentate e verifiche matematiche |
| V0.3 | Sintetizzatore classico | Schema elettrico candidato PLL/VCO/prescaler/divisori, alimentazioni, pinout verificati, filtri di loop, BOM preliminare, calcoli stabilità/rumore |
| V0.4 | RF ricezione e prima FI | Antenna RX, protezione, preselettore, amplificazione, mixer, FI1, stima NF/gain/blocker con ipotesi esplicite |
| V0.5 | FI2, BFO e demodulazione | Filtri, oscillatori e rami AM/FM/USB/LSB/CW, AGC, interfacce audio; componenti THT reperibili |
| V0.6 | Audio, squelch, ANL/NB, PA | Catena audio, mute, altoparlanti, PA audio, Roger Beep/Echo solo se dimostrata fattibilità THT |
| V0.7 | TX in sicurezza (progetto, NON ON) | Modulazione, mixer/driver/PA candidati, LPF, protezioni, interblocchi indipendenti; nessuna uscita TX collegata |
| V0.8 | Strumentazione e accordatore | ROS/SWR, potenza/PEP, modulazione, frequenzimetro, tuner LC manuale e BYPASS, budget di potenza e isolamento |
| V0.9 | Alimentazione, comandi, pannello | Protezioni, dissipazione, pinout pannello, cablaggi, interfacce fisiche e meccanica |
| V1.0 | Integrazione elettrica/KiCad | Schemi nativi coerenti e completi, BOM consolidata, layout PCB principale candidato, verifica interfacce |
| V1.1 | Validazione virtuale/pre-produzione | Simulazioni effettivamente eseguibili, KiCad ERC/DRC/refill, controlli meccanici e dei footprint, review RF, risoluzione criticità |
| V1.2+ | Rilascio PCB e prototipo | Soltanto dopo gate: Gerber/Excellon, DFM PCBWay, ordine PCB nude, saldatura interna, collaudo su strumenti, revisioni correttive |

**Regola pratica:** non rimandare errori evidenti alla V1.1: ogni modulo viene controllato e corretto quando sviluppato. Il riesame globale avviene prima dell'ordine PCB.
