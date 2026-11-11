# WORK_STATO_CORRENTE.md — checkpoint canonico per la continuità ChatGPT Work THT

**Rilevazione iniziale:** mercoledì **11 novembre 2026**. Repository unico: **jd3485/Superstar3900-THT-Evolution**; branch autoritativo: **main**. Questo file è un indice verificabile, non una sostituzione dei branch, delle PR e dei run GitHub.

**IN OGNI NUOVA CHAT:** leggere **[AGENTS.md](../AGENTS.md)** da main insieme a questo checkpoint. Poi interrogare live GitHub e non fidarsi di uno stato obsoleto. Leggere [handoff storico](../RIPRENDI_IN_UNA_NUOVA_CHAT.md), [stato tecnico](STATO_PROGETTO.md), il [piano PCB RF THT](PIANO_PCB_RF_THT_V2.0.md), i rapporti e le CI.

## Ultima revisione effettivamente integrata in main (fotografia verificata)

| Campo | Stato verificato |
|---|---|
| Ultima **revisione elettrica effettivamente MERGED** | **V2.0 — sette fogli RX PLL/VCO/5V/13,8V OVP/VTUNE20** |
| PR merged | [#17 — V2.0 boost MC34063ABN + LM317T](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/17) |
| **HEAD main all'ultima lettura** | **284bd3641d7a0f905d14dc4c9f36ee9da84bbc93** |
| Esempio CI KiCad 9 V2.0 riuscita | [run 42986863110](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42986863110) |
| CI su main V2.0 verificata | [run 42989687101](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42989687101) — **success** |
| Master KiCad di main | [PLL_RX_HIERARCHICAL_MASTER_V2.0.kicad_sch](../04_KiCad/V2.0/PLL_RX_HIERARCHICAL_MASTER_V2.0.kicad_sch) |
| Contenuto KiCad reale | **7 pagine native; 72 gruppi netlist**. VANA20_FILT collegato fisicamente al driver PLL U803 pin8 tramite foglio MC34063ABN / LM317T |
| Stato ERC schematico | **0 violazioni** negli export KiCad9 verificati; **non** rappresenta qualifica hardware |
| Componenti nel master parziale | **129** riferimenti fisici (censimento netlist ultimo); **125** footprint valorizzati, **4** da completare: F701, D702, L501, L920 |
| PCB unica completa | **NON ESISTE**. Zero layout, nessun DRC PCB, nessun Gerber di produzione |
| Avanzamento | Stima complessiva precedente ~15% schemi/progetto; **PCB fisica 0%**. Evitare aumenti senza evidenze |
| Sicurezza/autorizzazione | **NO FAB / NO GERBER DI PRODUZIONE / NO TX**. Non collegare a veicolo o batteria |

## Lavoro in corso: NON fonderlo con lo stato di main

### PR #20 — V2.1, footprint assiali e master a sette fogli

- **PR:** [#20 — OPEN / DRAFT, NON MERGED](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/20).
- **HEAD di lavoro alla rilevazione:** **2d1402a20a5b25080f8d5039d38cafedf777c1e0**; branch feature/v2.1-7sheet-kicad9-tht-fuse-tvs-footprints.
- **Base esatta della PR:** main V2.0, commit 284bd3641d7a0f905d14dc4c9f36ee9da84bbc93. Il master V2.1 conserva **tutti i sette fogli** e modifica soltanto i due campi Footprint dei componenti **F701 0251.500MXL** e **D702 ST P6KE20CA**; 7/7 schemi confrontati deterministicamente con il master originale V2.0 al netto del nome progetto e di queste due proprietà.
- **Impronte candidate:** THT_V21.pretty, corpo/massimi datasheet e pad-fori assiali a **passo 12,70 mm non ancora approvato per produzione**. La vecchia PR #18 basata su sei fogli è stata chiusa **senza merge** per evitare di perdere il settimo foglio.
- **BOM dopo eventuale PR #20**: 127/129 footprint **attesi**, L501 e L920 residui; questo conteggio **NON è un risultato di CI finale V2.1**.
- **CI bloccata:** [issue #22](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/22): su SHA 2d1402a... **19/19 workflow falliti senza runner e con ZERO step eseguiti**. Non chiamarli test passati né diagnosi di errori CAD. Causa da confermare (runner/quotas/billing/status di GitHub Actions).
- **Azioni:** appena GitHub Actions riparte, eseguire/rilanciare veri test su HEAD PR #20; controllare 7 fogli, ERC0, 72 partizioni pin-net, footprint SVG reali, audit completo BOM THT e regressioni storiche. Se base/main si muove, riconciliare senza perdere revisioni concorrenti. **Merge solo dopo gate tutti verdi.**

### Problemi aperti a maggior priorità

1. **[Issue #22 — Actions senza runner](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/22):** ripristinare CI; è un blocker di integrazione, non una ragione per forzare il merge. Controllare dashboard Actions e limiti di utilizzo o problemi del servizio, senza presumere la causa.
2. **[Issue #19 — L501 VCO](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/19):** valore 166 nH di modello, componente THT reale e footprint non qualificati; servono Q, SRF, tolleranze, KVCO e RF.
3. **[Issue #21 — L920 boost](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/21):** Bourns RLB0914-681KL 680 µH candidato THT senza footprint; corrente di saturazione/termica/ripple/EMI ancora da qualificare.
4. **Sicurezza alimentazioni:** F701/D702 senza I²t/source/TVS energy coordination; LM393 non protetto per >36V raw, reverse-battery e gate-source non validati; regolatori 5V/VTUNE20 senza prove termiche/ripple o modelli vendor, power-good/mute non integrati.
5. **Blocchi radio mancanti:** front-end RF, mixer e IF, AM/FM/SSB, audio, squelch e controller interamente THT. Solo dopo schemi completi scegliere stackup RF, fissaggi, ritorni massa e routing della PCB e svolgere DRC realmente completo.

## Procedura obbligatoria di aggiornamento

Dopo ciascuna revisione/merge **verificato**, sostituire la fotografia iniziale con dati live: **SHA main**, PR e nuovo merge SHA, esatta revisione master e path, test/run IDs pass/fail, differenze netlist, ERC/DRC, componenti e footprint ancora mancanti, risultati hardware *se misurati*, prossima priorità e stato NO FAB/NO TX. Indicare separatamente branch/PR che **non** sono state integrate e i blocchi di infrastruttura.

Prima della fine di ogni sessione Work, aggiornare questo documento e l'handoff in GitHub, se consentito; se la CI non permette il merge, lasciare una **PR/commit/issue di handoff** distinguendo lo stato presente su main dallo stato ancora non integrato. Evitare in ogni caso di riscrivere la verità del repository da memoria, chat passate o PR draft.

## Ripresa in chat nuova

Con le istruzioni del Progetto ChatGPT: **«Riprendi.»**

Senza le istruzioni: **«Riprendi THT da jd3485/Superstar3900-THT-Evolution; leggi da main AGENTS.md e 00_Gestione_Progetto/WORK_STATO_CORRENTE.md, verifica GitHub live, prosegui con più revisioni CAD e CI/PR/merge verificate, aggiorna il checkpoint. NO FAB / NO TX.»**
