# Architettura elettrica candidata — V0.1

> Diagramma **funzionale**, non schema pin-to-pin, netlist né progetto KiCad fabbricabile.

## RX — percorso candidato
`ANTENNA` → `Protezione/commutazione RX` → `Preselettore THT` → `LNA/attenuatore candidato` → `Mixer 1` → `FI1 (10,695 MHz candidata)` → `Mixer 2 / LO2` → `FI2 (455 kHz candidata)` → `Demod AM/FM/SSB/CW` → `Squelch/ANL/NB audio` → `Amplificatore audio THT` → `Altoparlante`.

Il percorso effettivo di AM/FM/SSB/CW potrebbe differire; frequenze e numero di conversioni vanno stabiliti in base a filtri, rumorosità, rejezione di immagine e disponibilità dei componenti **THT**.

## LO e controllo frequenza
`Riferimento stabile THT` → `PLL classico + prescaler/divisori programmabili THT` → `Filtro loop` → `VCO` → `Buffer isolato` → `Mixer 1`. Eventuale BFO/LO2 tradizionale da sviluppare.

**Obiettivo di studio V0.2:** per un primo IF a 10,695 MHz e conversione LO alto, su una finestra RX candidata 25,615–28,305 MHz il LO teorico sarebbe 36,310–39,000 MHz. Questa relazione è solo un esempio di architettura, non programma registri né prova fattibilità del PLL.

Un phase detector tradizionale non basta da solo a generare 36–39 MHz: servono VCO, divisori compatibili, budget di segnale e un loop dimensionato.

## TX — solo blocchi di progetto, percorso fisicamente aperto
`Microfono` → `Preamplificazione / modulazione analogica candidata` → `IF e conversioni TX (non abilitate)` → `Driver e PA (NON CONNESSI)` → `LPF / misure (da progettare)` → `Accordatore manuale/BYPASS` → `Antenna TX (NON CONNESSA)`.

In V0.1 **il percorso RF TX è concettuale**, senza rete o enable alimentabile. Gli interblocchi di TX e la commutazione antenna dovranno avere impostazione fail-closed indipendente dal comando software.

## Accordatore manuale
- Candidato: rete LC con induttanza selezionabile e condensatori variabili, commutatore BYPASS meccanico.
- Da dimensionare: intervallo impedenze, potenza, tensione RF, isolamento contatti, spazi PCB, dissipazione; possibile fissaggio meccanico al telaio con connessioni robuste.
- La rete non viene specificata con valori numerici finché potenza e carico non saranno fissati.

## Integrazione fisica
Preferenza per **una PCB principale THT** con sezioni analogiche separate e schermi RF quando necessari. I fili dei terminali, i ritorni GND e gli ingombri dei variabili influenzano il layout; l'uso eventuale di parti montate al telaio non cambia il vincolo di assenza SMD sulle schede.
