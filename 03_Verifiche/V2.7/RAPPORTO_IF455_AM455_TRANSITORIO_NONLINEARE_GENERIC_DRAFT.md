# V2.7 — IF455 -> AM455: test transitorio non lineare (modello non qualificato)

**13 novembre 2026.** Partenza dal checkpoint PR #92 (sensibilità ai carichi resistivi surrogate). Questo esperimento implementa una **netlist ngspice eseguibile** del filtro passivo 455 kHz direttamente collegato al diodo rivelatore, e un secondo detector alimentato direttamente come sola referenza numerica.

## Esito CI nativo verificato dopo PR #94

PR [#94](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/94) **MERGED** nel commit `9f218cbcc888b03247a03399bca41ea3b57c5bd9` dopo run [#43455702580](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43455702580): **FAST, FULL e required gate tutti SUCCESS** sul commit tecnico `75b6271b59d6ab16dddddf1d3ce2732041bb2f46`. Nel log FULL reale: `PASS_NGSPICE_GENERIC_DIODE_TRANSIENT_NOT_OEM_NOT_HARDWARE_NO_FAB_NO_TX` e 111 comandi legacy eseguiti.

| Misura ngspice del SOLO modello | Valore |
|---|---:|
| AF tank + diodo, pp | **0,17444891 V** |
| AF riferimento diretto, pp | **2,0377306 V** |
| Rapporto AF pp dei due modelli | **0,0856094** (~8,56%) |
| Massimo positivo RF in uscita dal tank | **0,6972108 V** |

Il confronto **non** è una misura d'attenuazione RF reale o guadagno/sensibilità commerciale: il percorso diretto esclude la selettività del filtro, entrambi sono alimentati da sorgenti ideali, e il diodo è un modello generico non qualificato. Serve uno sweep di livelli IF e corner del diodo, più la selezione e qualificazione di uno stadio IF/adattamento THT prima di decidere uno schema finale.

---

## Ipotesi esplicite e limite di validità
- Generatore modulato AM: portante 455 kHz, tono 1 kHz, indice 50%, picco sorgente 2 V, impedenza sorgente 50 ohm **ipotetica**, non livello IF effettivo della radio.
- Tank: 1 mH, 82 pF + 30 pF trimmer a metà corsa, condensatori accoppiamento da 10 pF, R1601 47 kohm, R1602 100 kohm, perdita bobina RCOIL 16.5 ohm **assunta**.
- Diodo: modello **DGENERIC** `Is=2.5n N=1.9 Rs=0.6 Cjo=4p Vj=0.75 Tt=4n`, già utilizzato nel banco AM standalone. **NON** macromodello OEM 1N4148 e **NON** predittivo di un pezzo reale.
- Demodulatore: R1501 47 kohm, C1501 1 nF, accoppiamento AF 100 nF e carico 100 kohm. Modello volutamente privo di mixer, stadio IF reale, AGC, stadio audio di potenza, FM/SSB.
- Misure ngspice native: ampiezza AF picco-picco tra 8 e 11 ms sia nel percorso tank+diodo sia nel riferimento diretto, picco RF positivo in uscita. I numeri nativi verificati nella CI sono riportati sopra.

## File e verifica
- `spice/if455_am455_nonlinear_transient_generic.cir`: deck con `.tran 0.2u 12m` e `.meas`.
- `verify_if455_am455_nonlinear_transient_native.py`: esegue `ngspice -b`, rifiuta errori/log incompleti, richiede risultati finiti e ampiezza AF non nulla. **Non** prescrive una soglia di sensibilità di ricezione inesistente.
- `ci/full_regressions.py`: include lo script nel gate FULL già esistente, **senza ulteriore job GitHub Actions**.

## Decisione
La prova serve a misurare la risposta di un circuito combinato **generico**, non a validare l'accoppiamento diretto del diodo. Prima di un blocco RF ricevente integrato: identificare impedenza e livello IF realistici, validare caratteristiche 1N4148 da datasheet OEM e corner, definire adattamento / buffer THT qualora necessario, riqualificare il tank alla luce del nuovo carico, ed effettuare riscontri su banco. La PR resta non integrabile fino a required gate SUCCESS e revisione dei risultati transitori.

**Master MAIN V2.6 invariato. PCB-MAIN e PCB-FRONT non ancora instradate. NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
