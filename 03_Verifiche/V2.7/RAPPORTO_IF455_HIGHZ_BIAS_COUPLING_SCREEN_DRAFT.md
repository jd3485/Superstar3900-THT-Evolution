# V2.7 — screening numerico alta impedenza ingresso IF455 → follower THT → AM455

**13 novembre 2026 · MODELLO GENERICO NON OEM · DRAFT**. Revisione tecnica successiva a PR #102: lo stadio Q1701 nella sua forma originale (C1701=10nF, bias 22kΩ/10kΩ) carica il tank e riduce drasticamente AFpp dopo il rivelatore non lineare. La presente revisione confronta **modifiche vere ai parametri del circuito**, non una lista astratta di componenti, senza promuovere il transistor reale a componente approvato.

## Ipotesi elettriche da testare

Il percorso C1604=10pF–R1602=100kΩ è già ad alta impedenza. L'inseguitore candidato, polarizzato da 22kΩ/10kΩ con ingresso C1701=10nF, introduce una resistenza AC verso massa considerevolmente più bassa. Si esplorano C1701 tra 2,2pF e 10nF e resistenze del partitore fino a 470kΩ/220kΩ, misurando sia la modifica di **carico RF sul nodo tank** sia l'uscita audio dopo il diodo. Non è garantito che un disaccoppiamento maggiore migliori AFpp: un piccolo condensatore può limitare troppo il segnale utile, e un partitore ad alta impedenza può essere più sensibile a correnti di base, disturbi e tolleranze.

| Scenario | C1701 | R1701 (+6V→base) | R1702 (base→GND) |
|---|---|---|---|
| Originale PR #97 | 10nF | 22kΩ | 10kΩ |
| High bias | 10nF | 220kΩ | 100kΩ |
| Very high bias | 10nF | 470kΩ | 220kΩ |
| Mid-cap + high bias | 47pF | 220kΩ | 100kΩ |
| Low-cap + high bias | 10pF | 220kΩ | 100kΩ |
| Very-low cap + high bias | 2,2pF | 220kΩ | 100kΩ |
| Mid-cap + very high bias | 47pF | 470kΩ | 220kΩ |
| Low-cap + very high bias | 10pF | 470kΩ | 220kΩ |

Per ogni scenario due ampiezze AM (0,5 e 2V picco), portante 455kHz e modulazione 1kHz/50%, massimo passo 25ns, transitorio 12ms, misure 8–11ms. **16 esecuzioni ngspice native** dal file di cascata integrato in PR #101; non si cambiano transistor `QGEN`, diodo `DGENERIC`, modello coil-loss 16,5Ω assunto, carico rivelatore né la sorgente ideale 50Ω. Confronto interno in ogni deck fra tank diretto+diodo e tank+follower+diodo, con due sorgenti identiche isolate.

Script: `03_Verifiche/V2.7/verify_if455_highz_bias_coupling_screen_native.py`. Log `IF455_HIGHZ_BIAS_COUPLING_CORNER`: AFpp diretto, AFpp con follower, rapporto AFpp buffer/diretto, rapporto dei picchi positivi RF del tank e swing emettitore. Verifica che il caso originale riproduca realmente i due baseline a 25ns della PR #102. Il ranking per AFpp è **solo un indice numerico**, non una scelta RF corretta o una qualifica.

## Vincoli e decisione

- Il transistor onsemi **KSP10BU** è candidato THT TO‑92 con pinout OEM 1 base, 2 emettitore, 3 collettore (datasheet https://www.onsemi.com/pdf/datasheet/ksp10-d.pdf), ma il modello ngspice non deriva da macro-modello vendor. La scheda OEM riporta guadagno minimo a una condizione di corrente diversa da quella del banco; la condizione qui usata non è garantita dall'OEM.
- Il rapporto AFpp NON misura rumore, SNR, sensibilità di ricezione, selettività, intermodulazione, immunità agli spuri, stabilità termica, impedenza RF complessa o PVT.
- Anche un ipotetico miglioramento rispetto all'originale non autorizza l'integrazione nel master MAIN V2.6 e non basta per fissare MPN/R/C del prodotto; serve successiva revisione KiCad 9 di variante reale e verifica OEM/temperatura.
- Lo screening non modifica KiCad né qualsiasi PCB. Solo FAST+FULL+required verdi sul commit finale rendono valida l'integrazione di questa **evidenza esplorativa**.
- **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
