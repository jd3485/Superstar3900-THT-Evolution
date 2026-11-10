# Piano generale di verifica — V0.1

**Mai confondere controlli di file e modelli con verifica hardware.** Ogni risultato futuro deve riportare comando, ambiente/versione, input, output, esito, limiti e revisione dei sorgenti.

| Categoria | Esempi | Stato V0.1 |
|---|---|---|
| Struttura/requisiti | Controllo JSON, 270=6×45, esclusioni e vincoli THT | Previsti ed eseguiti in test V0.1 |
| Piano RX/PLL | 270 posizioni, FI/LO, immagini, divisori, frequenza passo e lock | NON ESEGUITI, CSV da definire |
| RF teorica | NF Friis, guadagno, reiezione immagine, stabilità/rumore | NON ESEGUITA |
| SPICE circuito reale | Filtri, oscillatori, modulazione, power, termica | NON ESEGUITO |
| Simulazioni RF/EM | layout, grounding, accoppiamento, schermature | NON ESEGUITE |
| CAD KiCad | ERC, DRC, parità schema-PCB, footprint, riempimento zone | NON ESEGUITO: CAD non creato |
| Produzione PCBWay | Gerber/Excellon, stack-up, min drill, DFM, clearance THT | NON ESEGUITA |
| Laboratorio | stabilità, RX NF/sensibilità, dinamica, spur, audio, potenza/ROS | NON ESEGUITO |
| Normative e sicurezza | frequenze/potenze TX consentite, protezioni, EMC | NON ESEGUITO |

**Gate produzione:** tutti OPEN fino a evidenza tracciabile. Un test Python PASS non sblocca Gerber, ordini, alimentazione o TX.
