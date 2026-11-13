# V2.7 — KSP10BU IF455 THT: corner DC e AC 455kHz (simulazione generic BJT)

**13 novembre 2026.** Segue il vero schematico KiCad9 10 posizioni di PR #97; lo stadio è ancora standalone, NON collegato al tank e non certificato RF.

## Verifica che eseguiamo

- Deck reale ngspice `03_Verifiche/V2.7/spice/if455_ksp10_generic_bjt_bias_ac.cir`: deriva i componenti e le connessioni del banco Q1701 a collettore comune; supply 6V LAB, bias resistivo 22k/10k, emettitore 2k2, C ingresso/uscita 10n, carico 100k e impedenza sorgente 50Ω *ipotetica*.
- Modello `QGEN` con parametri BJT illustrativi `Is=1e-14 Vaf=100 Cje=5p Cjc=1p Tf=0.3n Tr=20n`, NON ricevuto da onsemi. Beta variabile `40/80/160` **scelto come scenario**, non rappresenta tolleranze OEM certificate a 455 kHz.
- Tre alimentazioni di test `5,5/6,0/6,5V` incrociate con 3 beta: **9 simulazioni ngspice native**. Per ognuna un transitorio DC 1ms e una AC 454–456kHz a tre frequenze; misura base, emettitore, rail, corrente emettitore nominale da RE, rapporto output/source a 455k.
- Script `verify_if455_ksp10_generic_bjt_bias_ac.py`: esecuzione subprocess reale, parsing dati nativi, controllo input/valori finiti, assenza di saturazione nei nove casi del *solo modello* e crescita della tensione di emettitore rispetto al riferimento di massa. I limiti del test non diventano criteri OEM.

## Status

Nessun numero è dichiarato misurato fino a completamento della CI del commit definitivo. Non si valuta rumore, selettività, dissipazione sotto sollecitazioni RF, margine termico worst-case, controreazione dinamica, impedenza d'ingresso vista dal tank o guadagno IF totale. Il filtro/diode resta scollegato. La modalità di controllo è KiCad9 + ngspice già presenti nel runner FULL; il progetto rimane **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.
