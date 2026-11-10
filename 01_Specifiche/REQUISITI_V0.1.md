# Requisiti di sistema V0.1

**BASELINE FUNZIONALE, NON SPECIFICA FINALE.** I numeri prestazionali non verificati sono deliberatamente lasciati `TBD`.

## Identità e costruzione
- Nuova radio CB ispirata al Superstar 3900: carattere analogico, comandi fisici, pannello vintage; compatibilità meccanica esatta con originale da verificare.
- Tutti i componenti elettronici installati sulle PCB **THT**; niente montaggio SMD e niente schedine/adattatori SMD. Componenti meccanici da pannello o telaio ammessi purché non occultino elettronica SMD.
- PCB nude prodotte da PCBWay, acquistate e assemblate internamente; preferenza per **una** PCB principale con schermature/comparti appropriati.

## Ricezione
- Bande A–F: **6 × (40 normali + 5 ALFA) = 270 posizioni RX**, tabella frequenze completa ancora da redigere e convalidare.
- Modi: AM, FM, USB, LSB, CW; frequenze, precisione e copertura specifiche da finalizzare.
- Selettore fisico ALFA e comando prioritario CH9 (27,065 MHz AM come obiettivo ereditato); la commutazione e le logiche devono essere progettate.
- Sensibilità, selectivity, image rejection, dinamica, S/N, deriva: **target misurabili da fissare**, non dichiarare automaticamente prestazioni superiori al riferimento storico.
- Squelch e circuito audio con filtri analogici; ANL/Noise Blanker da studiare.

## TX (solo obiettivo progettuale fino alla qualifica)
- Architettura analogica candidata TX AM/FM/SSB, con eventuale CW da definire, e filtro armoniche, protezione ROS, isolamento antenna e interblocchi fisici.
- **Nessuna alimentazione/enable di finale e nessuna connessione verso antenna TX autorizzata** nella fase V0.1; power e frequenze TX saranno subordinate a vincoli tecnici/normativi.

## Strumenti e accessori
- Frequenzimetro, wattmetro ROS/SWR, PEP e indicazione modulazione: previsti come obiettivi, accuracies e calibrazione TBD.
- Accordatore d'antenna **manuale** con BYPASS, rete LC e limite potenza/impedenze TBD.
- PA audio esterna, Roger Beep ed Echo tradizionale come funzioni candidate; fattibilità di Echo THT da verificare.

## Eliminazioni deliberate
**NON implementare:** DSP audio avanzato, PLL moderno RF ad alta integrazione, Dual Watch, CTCSS/DCS, VOX, accordatore automatico. Non sostituirli surrettiziamente con moduli SMD esterni.

## Decisioni tecniche non ancora congelate
- Sintesi frequenze: PLL classico programmabile con VCO/divisori/prescaler THT vs soluzione tradizionale alternativa; il PLL classico NON è stato ancora scelto a livello di MPN.
- Primo IF 10,695 MHz e secondo IF 455 kHz: **candidati da confrontare**, non requisiti bloccati né copiati automaticamente da altra radio.
- Tipo di commutazione RX/TX, filtri ceramic/quartz, convertitori, tensioni e potenza.

## Stato requisiti
I vincoli esplicitamente concordati sono `CONFERMATO`; per ogni altra caratteristica non numericamente specificata vale `DA_DEFINIRE`, senza accettazioni implicite.
