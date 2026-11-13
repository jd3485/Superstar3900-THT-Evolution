# V2.7 — KSP10BU IF455 THT: corner DC e AC 455kHz (simulazione generic BJT)

**13 novembre 2026.** Segue il vero schematico KiCad9 10 posizioni di PR #97; lo stadio è ancora standalone, NON collegato al tank e non certificato RF.

## Verifica che eseguiamo

- Deck reale ngspice `03_Verifiche/V2.7/spice/if455_ksp10_generic_bjt_bias_ac.cir`: deriva i componenti e le connessioni del banco Q1701 a collettore comune; supply 6V LAB, bias resistivo 22k/10k, emettitore 2k2, C ingresso/uscita 10n, carico 100k e impedenza sorgente 50Ω *ipotetica*.
- Modello `QGEN` con parametri BJT illustrativi `Is=1e-14 Vaf=100 Cje=5p Cjc=1p Tf=0.3n Tr=20n`, NON ricevuto da onsemi. Beta variabile `40/80/160` **scelto come scenario**, non rappresenta tolleranze OEM certificate a 455 kHz.
- Tre alimentazioni di test `5,5/6,0/6,5V` incrociate con 3 beta: **9 simulazioni ngspice native**. Per ognuna un transitorio DC 1ms e una AC 454–456kHz a tre frequenze; misura base, emettitore, rail, corrente emettitore nominale da RE, rapporto output/source a 455k.
- Script `verify_if455_ksp10_generic_bjt_bias_ac.py`: esecuzione subprocess reale, parsing dati nativi, controllo input/valori finiti, assenza di saturazione nei nove casi del *solo modello* e crescita della tensione di emettitore rispetto al riferimento di massa. I limiti del test non diventano criteri OEM.

## Status

Nessun numero è dichiarato misurato fino a completamento della CI del commit definitivo. Non si valuta rumore, selettività, dissipazione sotto sollecitazioni RF, margine termico worst-case, controreazione dinamica, impedenza d'ingresso vista dal tank o guadagno IF totale. Il filtro/diode resta scollegato. La modalità di controllo è KiCad9 + ngspice già presenti nel runner FULL; il progetto rimane **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

## Risultati verificati — PR #99 MERGED

[PR #99](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/99) integrata su `main` commit `30dca9bc5187b40a9a54a6fbb2af079ea5d59ec5`. Run [#43469630157](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43469630157) sul commit tecnico finale `e12c2e681f498e89bdd97ecdd65dea61782c96c8`: **FAST, FULL e required gate 3/3 SUCCESS**; 111 comandi legacy e `PASS_NGSPICE_IF455_KSP10_GENERIC_BJT_9_BIAS_AC_CORNERS_NOT_OEM_NO_FAB_NO_TX`.

| Rail laboratorio V | Beta GENERICO | Base V | Emettitore V | Corrente E mA | |Vout/Vsource| @455k |
|---:|---:|---:|---:|---:|---:|
|5,5|40|1,644481|1,011065|0,459575|0,966637|
|5,5|80|1,679888|1,045297|0,475135|0,967716|
|5,5|160|1,698856|1,063656|0,483480|0,968254|
|6,0|40|1,790528|1,153784|0,524447|0,969707|
|6,0|80|1,830799|1,192877|0,542217|0,970670|
|6,0|160|1,852372|1,213841|0,551746|0,971162|
|6,5|40|1,936612|1,296928|0,589513|0,972108|
|6,5|80|1,981729|1,340868|0,609486|0,972997|
|6,5|160|2,005899|1,364428|0,620195|0,973451|

**Interpretazione critica:** i numeri sono SOLO del modello generic BJT; i beta e i capacitivi sono scenari illustrativi. `Vout/Vsource` non significa guadagno della catena IF455, attenuazione del tank o qualità radio: la simulazione AC non include il filtro IF455, il diodo AM455, rumore e tolleranze OEM. Serve una verifica con filtro realmente caricato e modello qualificato, e poi analisi di stabilità termica e PCB. NO FAB/NO TX.
