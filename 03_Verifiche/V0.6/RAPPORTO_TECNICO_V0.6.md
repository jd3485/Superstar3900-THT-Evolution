# Rapporto tecnico V0.6 — reale ngspice, anomalie e VCO da correggere

**2026-11-10 — Questa revisione è dedicata alla qualifica negativa della V0.5 e al nuovo processo di simulazione elettrica.**

## Evidenze prima del consolidamento finale
- L'esecuzione della vecchia netlist ha prodotto oscillazioni ma con **polarizzazione diretta BB204G (+0,51..+0,54 V)** e una frequenza quasi fissa **38,306..38,350 MHz** tra 3,2 e 7,5V. **RF FAIL**.
- Un primo sweep 36 configurazioni/108 ngspice ha individuato 6 varianti con diodi mantenuti inversamente polarizzati nei punti test, ma le prove erano state inizializzate con `.ic` inadatto al nuovo VCC 5V. **Non considerare queste varianti convalidate**.
- La variante Colpitts Q501/Q502 con 5V, R503 1,2kΩ, C504 470pF e L 168nH ha un accordo diverso tra inizializzazione `uic` e una salita progressiva dell'alimentazione.
- Con ramp da 0V il modello L168 mostra ancora un margine insufficiente e diodo avanti ai valori VTUNE 6–7V. **RF FAIL, nessun candidato autorizzato**.

## Cosa è stato realmente testato
- **PASS DI ESECUZIONE:** simulazioni `ngspice 45.2`, transienti e misurazioni quantitative waveform/rising crossings.
- **FAIL TECNICO:** V0.5 non sintonizzabile su 2,690 MHz con diodi sempre inversamente polarizzati.
- **NON ESEGUITO:** librerie SPICE ufficiali per ogni componente, simulazioni dettagliate del PLL chiuso, misura reale KVCO/fase/rumore, KiCad ERC/DRC e layout, prototipazione, EMC, prove normative.
- **BLOCCATO:** fabbricazione e TX.

## Prossima azione
Consolidare risultati del nuovo sweep con ramp, scegliere o scartare una nuova variante; proseguire con modello transistor e varicap qualificabile e test a regime con fase, tolleranze e alimentazione. Non costruire un PCB a partire da un solo punto di simulazione.

**NO FAB / NO TX**.

## Consolidamento: prima candidata B che passa lo screening nel modello

**Run elettriche realmente riuscite:** [ramp scan](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42821991921) e [verifica dedicata della candidata B](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42822739779).

La candidata **L501 166nH, C504 470pF, R503 1,2kΩ, VCC 5V** avvia l'oscillazione con alimentazione da zero senza condizioni iniziali artificiali e nei cinque punti **VTUNE 8–15V** copre nominalmente **36,04773–39,19647MHz**, comprendendo 36,310–39,000MHz. Tutte e cinque le misure mostravano diodi in inversa con margine minimo A−K `−0,44691V` e tensione inversa massima nel modello `17,74675V` (sotto 30V del datasheet Philips). Vedere tabella completa nel documento `01_Specifiche/V0.6/VCO_SIMULAZIONE_E_CORREZIONI_V0.6.md` e dataset `MISURE_SPICE_V0.6.json`.

**VERDETTO:** `PASS MODELLO SU 5 PUNTI`, non validazione fisica/PCB. Rimangono necessari altri punti di accordo, transienti completi di Vtune e alimentazioni, parametri vendor, impedenza carico, stabilità termica, rumore di fase, sorgente VTUNE >13,8V, filtri e mixer RX, KiCad ERC/DRC e laboratorio. **NO FAB / NO TX.**

## GitHub Actions e integrazione V0.6 verificate

- Pull request [#2](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/2) integrata su `main`, merge commit `33ee543225e335a2313792ceea09839b4907f624`.
- [CI software main](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42823693863) **SUCCESS**: V0.1 12 + V0.2 24 + V0.3 32 + V0.4 34 + V0.5 34 + V0.6 21 = **157 controlli Python**.
- [CI ngspice main](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42823693786) **SUCCESS**: eseguiti il VCO V0.5 respinto (rilevazione RF FAIL documentata) e i 5 punti SPICE della candidata B con avvio VCC da zero (PASS limitato al modello). Le esplorazioni complete sono conservate negli artifact delle run su branch.
- **Importante:** `SUCCESS` della pipeline significa che le simulazioni previste sono state eseguite e hanno restituito misure interpretabili. NON significa che vecchia V0.5 o la nuova radio siano omologate o pronte da fabbricare. KiCad/ERC/DRC e laboratorio **NON ESEGUITI; NO FAB / NO TX**.
