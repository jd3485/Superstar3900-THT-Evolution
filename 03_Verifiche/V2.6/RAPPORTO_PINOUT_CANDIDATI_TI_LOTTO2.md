# Audit funzionale OEM/CAD per U801, U803, U912 — 12 novembre 2026

## Origine
Dopo PR #43, merge su `main` `5a43da52e5eb73188832f050c7786c01ec24d0a1`, CI #43215777733 con 3/3 job PASS. Questo è un **confronto documentale delle assegnazioni dei pin**, **non** export netlist nativo su una nuova versione di KiCad né qualifica elettrica/fisica. Nessuna modifica a simboli, valori, impronte o netlist.

| Componente | Sorgente CAD V2.6 / simbolo locale | Candidato OEM | Confronto nominativo pin del contenitore | Risultato |
|---|---|---|---|---|
| U801 comparatore | INPUT_FUSE_REVERSE_TVS_OVP_V2.6, THT_V18:LM393N_DIP8, DIP-8_W7.62mm | TI **LM393N/NOPB** PDIP-8 (P), ACTIVE | 1 OUT A, 2 IN A-, 3 IN A+, 4 GND, 5 IN B+, 6 IN B-, 7 OUT B, 8 VCC | Nomi e numeri simbolo **coerenti a livello di pin**; **non approvato** (0..70°C, Vs 36V e guasto rail a monte) |
| U803 operazionale | PD_FILTER_DRIVER_V2.6, THT_V10:LM358N_PDIP8, DIP-8_W7.62mm | TI **LM358N/NOPB** PDIP-8 (P), ACTIVE | 1 OUT A, 2 IN A-, 3 IN A+, 4 V-, 5 IN B+, 6 IN B-, 7 OUT B, 8 V+ | Nomi e numeri simbolo **coerenti a livello di pin**; **non approvato** (0..70°C, alimentazione, stabilità, offset, ripple) |
| U912 regolatore | POWER20_VTUNE_BOOST_LDO_V2.6, THT_V20:LM317T_TO220, TO-220-3_Vertical | TI **LM317T/NOPB** TO-220 (NDE), ACTIVE | 1 ADJ, 2 VOUT con TAB=VOUT, 3 VIN | Nomi e numeri simbolo **coerenti a livello di pin**; **non approvato** perché CAD indica onsemi e non TI, da verificare termica/SOA e geometria reale TO-220 |

### Fonti OEM esatte
- LM393N/NOPB https://www.ti.com/product/LM393-N/part-details/LM393N/NOPB (ACTIVE; PDIP 8; 0..70°C; supply max 36V).
- LM358N/NOPB https://www.ti.com/product/LM358-N/part-details/LM358N/NOPB (ACTIVE; PDIP 8; 0..70°C).
- LM317T/NOPB https://www.ti.com/product/LM317-N/part-details/LM317T/NOPB (ACTIVE; TO-220; 0..125°C nella tabella package addendum).
- Datasheet U912 con pin/tab: https://www.ti.com/lit/ds/symlink/lm317-n.pdf ; front view TO-220: ADJ/OUTPUT/INPUT, tab OUTPUT.
- Schemi locali KiCad9 consultati direttamente dal repository V2.6; NON sostituiscono netlist nativa.

## Rischi e gate rimasti
1. **U801:** il limite 36V e l'intervallo 0..70°C NON rendono sicura la protezione LM393/TL431 su reverse/OVP/failure; Issue #27 resta bloccante. Esaminare ampiezza reale dei transitori, common-mode, riferimento guasto, output high e dissipa.
2. **U803:** il candidato LM358N/NOPB è commercialmente ACTIVE, ma richiede verifica sui valori effettivi filtro PLL, frequenza/stabilità, rumore, riserva di alimentazione a 20V e temperatura. Evitare promozione in BOM prima della valutazione PVT.
3. **U912:** la corrispondenza numerica dei pin non prova compatibilità fisica dell'impronta o SOA. Il disegno del package TI NDE e la linguetta a potenziale VOUT devono essere confrontati con il foro, spaziatura, altezza e dissipatore effettivo; occorrono simulazione startup/short/corner e calcoli di potenza.
4. La gamma commerciale **0..70°C** dei candidati LM393/LM358 potrebbe essere limitante per condizioni ambientali severe; non equiparare automaticamente 'ACTIVE' a 'idoneo'. Valutare alternative OEM ACTIVE THT a range esteso prima dell'approvazione definitiva.
5. **Manca la comparazione delle connessioni netlist KiCad pin↔rete** verso la gerarchia nativa ed una verifica footprint/pad; non si dichiara completata qui. Nessuna macro vendor-SPICE o prova banco eseguita in questa revisione.

## Decisione
Mantenere U801, U803, U912 `DA_VERIFICARE` finché requisiti ambientali/elettrici, CAD MPN esatti, pin-pad-net e margini siano approvati. **6/138 ACTIVE confermati nella V2.6**, nessuna modifica CAD, progetto MAIN V2.6 e FRONT non ancora disegnata. Gate BOM `--release` intenzionalmente BLOCCATO, NO FAB / NO TX / NO BATTERIA / NO VEICOLO.
