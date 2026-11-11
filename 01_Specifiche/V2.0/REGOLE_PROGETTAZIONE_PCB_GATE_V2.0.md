# Regole guida PCB (V2.0) — NON sono DRC definitive o fab release

**Goal:** radio Superstar 3900 Evolution interamente THT, ricevitori PLL/VCO a ~36–39 MHz con IF, audio, controllo, alimentazione duale 5V/20V; futuro TX disabilitato finché non qualificato. Obiettivo zero violazioni **note** ERC/DRC, non garanzia matematica di zero difetti fisici.

**Architettura PCB consigliata (da confermare dopo schema completo):** singola PCB RX 4 layer THT: L1 componenti/percorsi RF brevi, L2 massa RF continua senza attraversamento di split o tagli, L3 alimentazione e segnali discreti, L4 segnali/audio/controllo. Impedenza delle piste RF calcolata **solo** con stackup del produttore. Ground return e correnti di alimentazione misurate; evitare di frammentare il riferimento a massa. Allontanare DC/DC VTUNE dal VCO, dal primo mixer e dalle linee audio, usare filtri e schermatura dove realmente necessaria. Piste RF, via stitching e vincoli crosstalk da determinare con simulazione e misure di banda.

**Design rules iniziali ipotetiche, NON released:** clearance ≥0,25mm per basse tensioni DC, larghezza piste segnali ≥0,25mm, via Ø0,70mm/drill0,30mm, distanze rame-bordo ≥0,5mm; cambiare dopo analisi del fab, della reale corrente e di isolamenti/transitori. Il foro su F701/D702 è volutamente diverso (0,90/1,10mm): usare specifiche drill finished-hole. Tutti i 14 domini della matrice devono avere uno schema completamente connesso, footprint reali e BOM acquistabile prima di qualunque layout definitivo.

**Gate necessari, nell'ordine:** 
- G0 requisiti elettrici: 11–15,5V nominali, condizioni di fault dichiarate e sorgente corrente/impedenza conosciute; RF/IF/audio/controller definito; NO BATTERY/NO VEHICLE.
- G1 schemi: tutti i fogli presenti, ERC0, netlist pin-to-pin con revisione dei componenti e dei loro modelli e datasheet; documentare reset/lock/supply transients e protezione in guasto.
- G2 BOM/footprint: nomi MPN singoli, pinout/package veri, fori/pad, 3D opzionali, quote massime, disponibilità e sostituzioni controllate; thermal rating/ripple/fuse/I²t/surge, nessun footprint mancante.
- G3 layout: board file completo, contorno quotato, fissaggi, keepout e separazione potenza/RF/PLL/IF/audio, stackup concordato, massa e shielding, test point accessibili, piano di assemblaggio e test.
- G4 indipendente: DRC 0 errori e 0 warning non giustificati, netlist↔PCB parità 100%, errori footprint/libreria zero, verifica 3D/meccanica, revisioni indipendenti, prototipo fisico e test EMC/RF/thermal. Nessun bypass del gate via file PWR_FLAG o silenziamento ERC/DRC.
- G5 release: soltanto dopo laboratorio qualificato, distinta BOM approvata, pannellizzazione e documentazione di fabbricazione finali, autorizzazione esplicita dell'utilizzatore per fare fabbricare; TX richiede ulteriore autorizzazione e conformità radio.

**Stop conditions aggiornate:** U801 LM393 esposto a >36V raw; D804/D805 non testati con inversione; Schottky gate-source zener non caratterizzato; fusibile F701 I²t e TVS D702 clamp/fault source non coordinati; R1001 thermal; 5V regulator e 20V VTUNE non qualificati; antenna/RF/IF/audio/controller incompleti; PCB non esistente. Queste condizioni impediscono release e si propagano nelle successive versioni.
