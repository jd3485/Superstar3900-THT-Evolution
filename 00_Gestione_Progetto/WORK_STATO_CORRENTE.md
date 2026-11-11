# WORK_STATO_CORRENTE.md — checkpoint canonico Superstar 3900 THT Evolution

**Aggiornato:** 11 novembre 2026. **Repository esclusivo:** `jd3485/Superstar3900-THT-Evolution`.
**Branch autoritativo:** `main`. Questo file documenta l'ultima revisione verificata,
non sostituisce il controllo live di GitHub a ogni nuova sessione. Leggere
[AGENTS.md](../AGENTS.md) **e questo file da main all'inizio**; poi verificare
SHA di main, PR, issue, GitHub Actions e i rapporti CAD.
Non utilizzare la memoria delle chat o lo stato di branch draft come verità di main.


## Ottimizzazione dei controlli GitHub Actions, distinta dallo stato elettrico

La revisione CAD realmente integrata resta **V2.3** (PR #26,
commit tecnico `faa146e2bdd12b13df1cbb4d20e67196ad5098b9`).
Nell'intervento infrastrutturale successivo sono stati identificati
**20 workflow legacy** auto-attivati su ogni PR e su push main, di cui
**14 native KiCad9** con download indipendente via PPA Launchpad,
**5 simulazione ngspice**, **1 regressioni Python V0.1–V1.0**.
Questo moltiplicava consumi e fallimenti di rete (issue #29).

Policy disponibile nel nuovo `.github/workflows/ci_optimized.yml` e
[ci/CI_COST_OPTIMIZATION.md](../ci/CI_COST_OPTIMIZATION.md):
- nessun push main automatico o invocazione di venti suite distinte;
- regressioni Python sulla PR, anche se solo documentale;
- per qualunque modifica non documentale, **tutte** le 19 suite storiche
  KiCad/ngspice eseguite in un solo job dentro il container KiCad 9.0.9
  ufficiale, digest pinned e pilota ERC0 [43054348749](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43054348749);
- 20 workflow originali restano invocabili manualmente e i loro singoli
  step di verifica sono eseguiti fedelmente dal runner aggregato;
- gate unico MUST PASS su SHA finale prima di ogni integrazione tecnica;
  nessuna inferenza di DRC PCB senza PCB.
**Avvertenza:** i file documentano la policy ma la piena migrazione si considera
realizzata solo dopo esito CI e merge confermato della relativa PR su main.

**Lavoro tecnico ancora OPEN**: [PR #28 V2.4](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/28)
(candidato guardia LM393/R1011/D806 non integrato, ERC e netlist native
V2.4 da ripetere con runner funzionante), [issue #27](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/27)
(guasti, UVLO, power-good/mute fail-closed non qualificati), [issue #29](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/29)
(storico PPA Launchpad); issue #19 e #21 RF/termica.
Non cambiare il conto/budget Github. **NO FAB / NO TX**.

## Ultima revisione realmente integrata — V2.3

| Campo | Ultimo stato accertato |
|---|---|
| **Ultima revisione ELETTRICA/CAD MERGED** | **V2.3 — sette fogli KiCad9 RX PLL/VCO/5V/13,8V OVP/VTUNE20, footprint L501 Coilcraft candidato** |
| **HEAD main all'ultimo controllo tecnico** | `faa146e2bdd12b13df1cbb4d20e67196ad5098b9` (merge PR #26; un successivo commit solo-documentale cambierà naturalmente HEAD: RIVERIFICARLO live) |
| PR #20 **V2.1 MERGED** | [#20](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/20) — merge `b7b475e05b7279f2944fbfa6ea50d38680f874c4`, footprint assiali F701 e D702 THT candidati |
| CI V2.1 sul final HEAD | **18/18 workflow PASS** (17 regressioni storiche + gate V2.1); [native KiCad run 42991959540, tentativo 3](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42991959540): ERC 0, 72 partizioni pin-net, 7 SVG, 2 footprint SVG |
| PR #24 **V2.2 MERGED** | [#24](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/24) — merge `30328084e72339f3909e618ff37162e8f31827d4`, footprint THT candidato L920 Bourns 680µH |
| CI V2.2 sul final HEAD | **19/19 workflow PASS** su `574abd13c5591a1cbb3ccc0c8cd2289a2df05339`; [native run 43011468320](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43011468320): ERC0, 72 partizioni intatte, 128/129 campi footprint |
| PR #26 **V2.3 MERGED** | [#26](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/26) — merge `faa146e2bdd12b13df1cbb4d20e67196ad5098b9`, candidato Coilcraft 150-05J08L L501 e nuova impronta THT |
| CI V2.3 sul final HEAD | **20/20 workflow PASS** su `d0b31d413a044e0c8035c0460086b5193e52197f`; [native run 43012377058](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43012377058): KiCad9 ERC0, sette fogli SVG, **72 gruppi netlist e tutte le partizioni pin→net invariate** |
| Master KiCad autorevole | [04_KiCad/V2.3/PLL_RX_HIERARCHICAL_MASTER_V2.3.kicad_sch](../04_KiCad/V2.3/PLL_RX_HIERARCHICAL_MASTER_V2.3.kicad_sch) |
| Copertura CAD nel master RX **parziale** | **129 riferimenti fisici, 129/129 campi Footprint valorizzati**; passaggio di audit **non** equivale a qualifica componenti/package né al completamento radio |
| PCB unica, routing, DRC PCB | **NON ESISTONO / NON ESEGUITI**. Nessun `.kicad_pcb` completo. Nessun Gerber produttivo, nessun prototipo o test hardware |
| Autorizzazioni | **NO FAB / NO GERBER PRODUZIONE / NO TX**; vietata connessione a batteria, veicolo o catena TX senza autorizzazione |

### File reali della revisione V2.3

Sette schemi nativi nuovi `04_KiCad/V2.3/*.kicad_sch`, generatore
`04_KiCad/V2.3/genera_L501_v23.js`, tabelle librerie e
`THT_V23.pretty/Inductor_Coilcraft_150-05J08L_Uni7_Tunable_THT.kicad_mod`,
audit `03_Verifiche/V2.3/verify_kicad_v23.py`, gate aritmetico
`screen_vco_l501_v23.py`, rapporto `RAPPORTO_L501_VCO_V2.3.md`, workflow
`.github/workflows/cad_native_v23.yml` e delta BOM. Solo proprietà
**Value** e **Footprint** di L501 variate intenzionalmente da V2.2; tutte
le 72 partizioni elettriche native invariate.
La V2.2 conserva F701, D702, L920 e la gerarchia BOOST/VTUNE20; V2.1
conserva l'intero master V2.0 a sette fogli.

## Qualifiche ancora NON superate — blocchi reali

1. **[Issue #19, L501 VCO](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/19)**: Coilcraft **150-05J08L THT regolabile** candidato 165nH, range 137–193nH, Q min 114 a 50 MHz, SRF min 650 MHz **senza nucleo**, impronta diagonale con foro 0,8/pad 1,8mm proposta. Non è una qualifica RF. Mancano campione/fit, disponibilità MPN, tuning con BB204G, **KVCO, lock 270 canali, phase noise, deriva termica, Q caricato, EMI** e schermatura del boost. [Datasheet Coilcraft](https://www.coilcraft.com/getmedia/aaa9fcd2-5ef1-4ee2-b9b8-0ec1aa8c8db0/uni7.pdf). Lasciare issue aperta.
2. **[Issue #21, L920 boost](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/21)**: candidato Bourns **RLB0914-681KL** 680µH THT, footprint Ø2mm/drill1mm/pitch5mm. Irms tipica 0,49A, Isat tipica 0,9A, DCR max1,6Ω. Da validare stress, ripple, Ipk MC34063, saturazione termica, ingresso, EMC e spur sul VCO/IF; hardware e dimensioni pezzo. [Datasheet Bourns](https://www.bourns.com/docs/product-datasheets/rlb.pdf).
3. **Ingresso 13,8 V / protezione**: LM393 upstream ha **36V massimo** non protetto per sovratensioni sopra limite; reverse battery, transitori, load dump e rete Q802/gate-source non qualificati. **F701** Littelfuse 0251.500MXL e **D702** ST P6KE20CA hanno impronte THT candidate ma **senza** coordinamento sorgente/fusibile I²t/TVS energy e senza prova meccanica del pitch assiale 12,70 mm.
4. **Regolatori e sicurezza funzionale**: 7805/boost 20V LM317 non qualificati per correnti, termica, startup, brownout, PSRR/ripple e comportamento da guasto; **power-good/mute fail-closed non integrati**. Non attribuire sicurezza ai soli ERC0 o test ideali.
5. **Ricevitore completo assente**: preselector/front-end RF, mixer, IF, demodulazione AM/FM/USB/LSB, audio, squelch, controllo canali e front-panel completamente da progettare THT. Nessuna PCB completa, nessuna DRC, layout RF/IF o netlist↔PCB qualificata.
6. **Sola evidenza da software**: ngspice storico è modello surrogato/comportamentale; non sono eseguiti macro-modelli vendor completi o misure elettriche/RF su prototipi. Nessuna trasmissione ammessa.

## Issue, PR e GitHub Actions al checkpoint

- **Issue #22 (quota Actions)**: [CLOSED](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/22), 2.000/2.000 minuti consumati in precedenza; titolare ha sbloccato Actions. Runner ripartiti: gate V2.1/V2.2/V2.3 **eseguiti davvero** e passati. Diversi tentativi hanno incontrato **HTTP 500/504 Launchpad PPA** durante installazione KiCad; quelli falliti sono stati ritentati, non reinterpretati come test CAD. Non cambiare budget senza consenso.
- Nessuna **PR tecnica** rimasta aperta al merge della V2.3. La sola PR documentale [#25](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/25) era OPEN/DRAFT ed è stata **aggiornata con questo checkpoint**. Verificare live prima di usarla come fonte.
- Project SMD **mai modificato** in questa sessione. Non trasferire specifiche SMD.

## Prossima sequenza tecnica autonoma

Partire da `main` V2.3 e dagli issue aperti: prima progettare e verificare **protezione OVP del comparatore LM393 e network gate su fault, startup/brownout, power-good/mute fail-closed**, con datasheet originali e analisi fault; evitare falsi PWR_FLAG. Poi validare componenti magnetici/TVS con dimensionamento PVT, modelli vendor e criteri meccanici; proseguire verso front-end RF e mixer/IF THT, demodulazione/audio/controlli.
Ogni revisione reale: branch → nuovo file KiCad nativo → ERC e netlist pin-net in KiCad9 + test appropriati → PR/CI su **HEAD finale** → merge solo dopo gate verdi. Dopo merge aggiornare questo checkpoint.
Non creare una PCB dimostrativa o Gerber fintanto che l'intera radio RX/THT e safety non sono completati e riesaminati.

**VINCOLI ASSOLUTI: NO FAB / NO TX, NO BATTERIA / VEICOLO.**

## Ripresa in una nuova sessione

«Leggi `AGENTS.md` e `00_Gestione_Progetto/WORK_STATO_CORRENTE.md` da `main` del repo `jd3485/Superstar3900-THT-Evolution`. Verifica in tempo reale SHA main, PR, Actions e issue. Riparti dall'ultima revisione effettivamente MERGED, prosegui autonomamente con più revisioni KiCad THT, CI e merge solo dopo tutti i test; aggiorna checkpoint. NO FAB / NO TX; non toccare SMD.»
