# V2.7 — Interfaccia SBL-1+ IF → filtro IF455, contratto di banco nativo
**14 novembre 2026. Progetto THT, due schematici indipendenti; nessuna PCB né connessione fabbricata.**

## Architettura e fonti effettivamente verificate
- Lo schematico nativo Mini-Circuits SBL-1+ in `04_KiCad/V2.7_DRAFT/MIXER_SBL1_CANDIDATE/MIXER_SBL1_BENCH_THT_V2_7_DRAFT.kicad_sch` porta **entrambi MX1701/3 e MX1701/4** alla rete `IF455_MIXER_IF` e al connettore `J1703/1`, ritorno `J1703/2 = IF_BENCH_GND`. Il requisito di unire IF3/4 è OEM: https://www.minicircuits.com/pdfs/SBL-1%2B.pdf .
- Il banco LC nativo `04_KiCad/V2.7_DRAFT/IF455_TANK/IF455_TANK_THT_V2_7_DRAFT.kicad_sch` ha `J1601/1 = IF455_SOURCE`, `J1601/2 = IF_BENCH_GND`. Tra ingresso e nodo LC esiste **C1601=10 pF C0G THT** in serie. L'uscita è `J1602/1 = IF455_FILTER_OUT`, ritorno pin2 a massa.
- **Interconnessione solo proposta** `J1703/1→J1601/1` e `J1703/2→J1601/2`. Il test `03_Verifiche/V2.7/verify_mixer_if455_interface_native.py` esporta **entrambe le netlist con KiCad9** e controlla riferimenti/pin/partizioni, incluso MX1701/3+4, masse, isolamento LO e RF, posizioni di C1601, L1601, C1602, R1601, C1604 e J1602. Questo non significa che le due schede siano integrate.

## Perché il collegamento non è qualificato
Alla frequenza nominale 455 kHz, il valore ideale del solo condensatore di ingresso C1601=10 pF equivale a `|Xc|=1/(2π×455k×10pF)=34,98 kΩ`. Si tratta di una **reattanza in serie**, non dell'impedenza complessa totale del filtro. I precedenti studi ngspice del banco IF455 hanno mostrato che la risposta varia con l'ipotetica impedenza sorgente (50Ω, 1kΩ, 10kΩ) e con il carico downstream; il mixer non è stato modellato elettricamente come sorgente vera.

**Non impostare Rs(mixer)=50Ω come dato OEM**, non equivalere la specifica 5,6 dB di conversion loss a guadagno 455k a questa terminazione, non affermare adattamento, sensibilità o noise figure: mancano Zout IF mixer complesso/nonlineare, livelli LO reali, bypass/matching lato ingresso e verifica del piano frequenze. C1601 e il filtro rimangono candidati non congelati.

## Condizioni per la successiva revisione
1. Ottenere il modello reale/equivalente RF/IF del mixer con definizione di terminazioni a 455 kHz e livello LO, oppure acquisire su banco VNA/impedenza IF e misure di conversione in sicurezza.
2. Simulare e riprogettare l'adattamento C1601/LC verso il mixer sotto le condizioni dichiarate (sorgente complessa, perdite bobina, carico rivelatore), con controllo native ngspice e verifica dei componenti passivi THT.
3. Validare fisicamente i connettori e i ritorni massa; disegnare eventualmente un vero schema completo soltanto dopo la qualifica elettrica. **Nessun TX e nessun hardware approvato.**
4. La footprint A06 del mixer resta PR #123 DRAFT, separata e non autorizzata per produzione.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
