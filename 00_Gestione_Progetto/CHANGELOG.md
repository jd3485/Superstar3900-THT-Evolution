# V0.4 — 10 novembre 2026 — VCO analitico e primo CAD digitale THT

- Primo **sottoschema KiCad S-expression `.kicad_sch`** di U402 prescaler con simboli locali e quattro header THT. File generato e controllato staticamente; **non aperto in KiCad e non validato con ERC**.
- BB204G Philips TO-92 trovato in documentazione originale, circuito VCO studiato con modello LC e varactor equivalente: C_var teoriche 29.83..18.20 pF, tensioni interpolate 4.87..15.97 V. Non simulazione RF.
- Filtro di anello passivo tipo B candidato 2.2kΩ / 10kΩ / 100nF; polo e zero calcolati, nessun margine fase certificato.
- Controller `PIC18F47Q43-I/P` PDIP40 candidato per 270 posizioni, CH9/ALFA/mute, senza DSP o funzioni escluse.
- Aggiunti test software V0.4, modello Python, rapporto, BOM e rischi. Le versioni storiche continuano a leggere snapshot di configurazione coerenti.
- VCO reale, filtri/buffer LO, ERC/DRC, SPICE, meccanica, hardware, TX e PCBWay ancora non eseguiti.

---

# V0.3 — 10 novembre 2026 — Core PLL THT pin-to-net

- Sviluppo vero del nucleo PLL candidato: ML145151YP DIP28 e TC74AC74P(F) DIP14, **tutti i 42 pin mappati**, reti logiche, sequenza RX e 270 parole N.
- Quarzo THT Citizen 10,24 MHz CL18pF trovato a catalogo e carico stimato ~17,727pF; emerge il limite ±30ppm/±50ppm per la SSB.
- Prestudio VCO LC con 220nH e Ceq 87,33–75,70pF su gamma LO. Modello numerico riproducibile; NON VCO reale.
- BOM candidato THT con 13 righe, passivi di avvio e interfacce ancora da completare.
- Creati 32 test V0.3 e regressioni V0.2 riagganciate alla baseline `CONFIGURAZIONE_V0.2.json`; workflow GitHub aggiornato.
- Restano tutti OPEN: schematico KiCad nativo, VCO/buffer/loop, SPICE, ERC/DRC, hardware, gate produzione e TX.

---

# V0.2 — 10 novembre 2026 — Frequenze e sintetizzatore tradizionale THT

- Piano RX a 270 posizioni A–F, con 30 ALFA, CH9 D/9 e codici N a 14 bit; sorgente Python di rigenerazione e CSV.
- IF1/LO/immagini calcolate, 24 test statici V0.2 e 12 regressivi V0.1 superati.
- Alternative PLL: MC145151P2 legacy + SN74AC74N /2 oppure CD74HC4046AE + contatori THT; nessuna BOM finale.
- Aggiornati rapporto, stato, decisioni, istruzioni per nuove chat. Nessun KiCad, SPICE, prototipo, ordine o TX.

---

# Changelog

## V0.1 — 10 novembre 2026 — Fondazione progetto THT indipendente
- Confermata architettura prevalentemente analogica THT, costruzione manuale e fabbricazione PCB nude via PCBWay.
- Delimitate funzioni incluse/escluse e scelta accordatore manuale con bypass.
- Definiti protocollo di continuità, registro decisioni, rischi, piano di sviluppo e gates.
- Preparati test strutturali riproducibili e manifest SHA-256 del pacchetto V0.1.
- Non realizzati schemi KiCad, PCB, simulazioni circuitali, prototipi o misure. **NO FAB / NO TX.**
