# Rapporto CAD-FIRST V1.0 — primo vero sottoschema KiCad THT e gate di sviluppo

**Superstar 3900 THT Evolution**, repository autonoma `jd3485/Superstar3900-THT-Evolution`. Data: 10 novembre 2026. Questo documento descrive un **pilot di realizzazione CAD** e non dichiara completata l'elettronica. **NO FAB / NO TX.**

## Cambio di metodo operativo

La progettazione ora cresce contemporaneamente attraverso **file KiCad nativi**, simulazioni fisiche (o modelli classificati correttamente), calcoli, firmware PIC THT, selezione di componenti fisici, BOM, prove automatiche e documentazione. È scritto in `00_Gestione_Progetto/METODO_CAD_FIRST_V1.0.md`. `MATRICE_COPERTURA_CAD_V1.0.csv` elenca 14 blocchi da trasformare progressivamente in schemi collegati e poi PCB.

## CAD concretamente realizzato in questa revisione

- Recuperata la sostanza della [PR #5](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/5), che era bloccata da **errore durante caricamento libreria simboli e non aveva completato ERC**, senza unirla né modificarla. Copiato in un percorso V1.0 indipendente per preservare traccia storica.
- Salvati sorgenti riproducibili `04_KiCad/V1.0/genera_pll_filter_v10.py`, schematico KiCad effettivo `PLL_FILTER_DRIVER_CAD_V1.0.kicad_sch`, libreria locale `THT_V10.kicad_sym`, `sym-lib-table`.
- **Causa compatibilità simboli**: nel generatore precedente la libreria era dichiarata con versione `20250114`, successiva al formato della libreria KiCad9. Aggiornata a `20241209`, che risulta leggibile dalla CLI. Il file dello **schema** conserva la propria versione `20250114` corretta.
- Circuito **isolato** con **13 simboli istanziati**: LM358N U803 DIP8, R901/C901 filtro di ingresso PDout, feedback R803/R804, R805/C805 sul VTUNE (C805 DNI), bypass C803, J901 ingresso PDout/GND, J902 alimentazione esterna20V/GND, J903 uscita VTUNE/GND e due flag di alimentazione esterna. Schemi recuperati e **non ancora il PLL completo**.
- Libreria native KiCad esportata: 5 simboli univoci. Rete e pin effettivi verificabili da **netlist prodotta da KiCad**; aggiunto uno script che controlla i pin reali del PDF/nessun connettore immaginario. (Il PDF non è sorgente elettrica.)
- I valori **R901=22k/C901=100n** sono una variante CAD dell'altra PR, **non** la candidata del modello V0.9 `R901=10k/47k C901=1µF`. Entrambe le varianti restano non compensate, non qualificano il lock e non devono essere ordinate in produzione.

## Evidenze già osservate, senza sovrastimare

- [GitHub Actions KiCad 9.0.9 — prima prova](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42857108005): **PASS** simboli e libreria, rigenerazione bit-a-bit, **ERC nativo 0 violazioni** senza soppressioni, export `sch netlist`, export SVG; artifact `v10-partial-cad-native-kicad-erc-netlist-svg-NOT-FAB`.
- [GitHub Actions Python 3.11 V1.0](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42858156232): regressioni V0.1..V0.9 **254** e **18 controlli di nuova continuità/CAD** = **272 verifiche statiche**, senza sostituire i test fisici.
- **Nuovo controllo sul netlist effettivo**: `03_Verifiche/V1.0/verify_kicad_netlist_v10.py` legge `pll_filter.net` generato da KiCad e impone le coppie `ref/pin` su `PD_FILTER`, `OPA_FB_A`, `OPA_OUT_A`, `VANA20_FILT`, `GND`, `VTUNE_RAIL` e la coppia del follower inutilizzato `OPA_OUT_B`. Gate **non qualificabile finché il nuovo workflow completo non riesce**. Il risultato non prova un PLL stabile.

## Stato del progetto realmente distinto

| Controllo | Esito |
|---|---|
| Compatibilità file KiCad9 per circuito U803 isolato | PASS sulla prima run |
| Libreria simboli KiCad locale / estrazione SVG | PASS sulla prima run |
| ERC isolato `PLL_FILTER_DRIVER_CAD_V1.0.kicad_sch` | PASS, 0 violazioni sulla prima run |
| Export netlist e grafica KiCad | PASS sulla prima run |
| Test effettivi di connessione pin/netlist | NUOVA CI, registrare dopo esito |
| 254 vecchie regressioni +18 nuove | PASS sulla run citata |
| ERC intera radio e master gerarchico | **NOT_RUN** |
| KiCad `.kicad_pcb` completo, footprint verificati su PCB e DRC | **NOT_RUN / NON REALIZZATI** |
| Prove di banco PLL/RF, frequenze/rumore, reale MC34063/LM358/BB204G | **NOT_RUN** |
| Pacchetto Gerber, PCBWay e TX | **NON AUTORIZZATI: NO FAB / NO TX** |

## Bloccanti da affrontare nella prossima fase

**Primo obiettivo CAD**: integrare il reale U401 ML145151 e U402 prescaler con PDout pin4, VDD/GND e quarzo/referenza in un progetto gerarchico KiCad; unire i nodi `PLL_PDOUT_3STATE` e `VTUNE_RAIL` al VCO e alla sorgente d'alimentazione analizzata; fissare i valori filtro solo dopo simulazioni PLL chiuso/margini. Continueranno contemporaneamente sourcing THT, firmware canali, RF/IF e meccanica della PCB.

**Nessun problema elettrico viene chiuso con il solo ERC:** un'opamp può essere mal compensato o fuori dalla finestra di common-mode pur avendo zero violazioni CAD.

## Validazione native netlist pin-per-pin — esito finale del pilot (branch)

[Run 42858721761](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42858721761) **SUCCESS**, KiCad CLI 9.0.9:

- `sch erc --exit-code-violations`: **0 violazioni**, nessuna waiver sul circuito isolato.
- `sch export netlist`: **PASS**; identificati **8 net reali** (alcuni con `/NET` perché KiCad prefissa i nomi gerarchici).
- `verify_kicad_netlist_v10.py`: **PASS_NETLIST_PARTIAL_ONLY**, controllati direttamente i riferimenti **J901/R901/C901/U803/R803/R804/R805/J902/J903/C803** e i pin per `PLL_PDOUT_3STATE`, `PD_FILTER`, `OPA_OUT_A`, `OPA_FB_A`, `OPA_OUT_B`, `VANA20_FILT`, `GND`, `VTUNE_RAIL`.
- Esportazione simboli KiCad e SVG schematico **PASS**. Generazione deterministica **PASS**.
- `NO FAB / NO TX`: 8 reti e zero errori ERC non equivalgono a circuito PLL chiuso, né a PCB / DRC, né a qualifica RF; le alimentazioni sono **esterne** e U401/U402/VCO non sono inseriti nello schematico.

La run Python [42858721619](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42858721619) è **SUCCESS 272 controlli** (254 V0.1–V0.9 +18 CAD-first).
