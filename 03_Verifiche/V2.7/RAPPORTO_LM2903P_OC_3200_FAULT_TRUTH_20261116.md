# V2.7 — LM2903P THT: 3.200 scenari di guasto alle uscite open collector

16 novembre 2026 — **solo fault screening su netlist KiCad9 reale**, non qualificazione hardware.

## Stato confermato

PR [#311](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/311) MERGED su main `df7e088d4890075b378894d426a2b9594681ab25`. Run [#43853755257](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43853755257) sul final head `739c1d333613055d8f9be5aa3170811600caf7c1`: FAST/FULL/Required **3/3 SUCCESS**, `PASS_NATIVE_KICAD9_LM2903P_PDIP8_30PIN_8NET_128_WINDOW_NONFAB`, ERC KiCad9 **0 errori / 0 warning**. U2201 PDIP8, R2201..R2207 e J2201..J2204: 30 pin fisici/8 reti. L'alimentazione 5V è una **sorgente ESTERNA ipotizzata sul connettore J2202**, dichiarata `power_out` nel simbolo locale per rendere esplicito il contratto ERC, non generata sulla scheda. Nessuna PCB.

## Modello di logica e di guasti

`03_Verifiche/V2.7/verify_lm2903p_oc_fault_truth_native.py` esporta **netlist KiCad9** del circuito fisico e verifica esattamente pin 1/7 uscite OC, 3/6 ingressi VIN_SENSE, supply 5V e reference esterno. Testa **3.200 scenari matematici** = 128 tolleranze resistive/ref ×5 valori VIN (0, 8, 13,8, 16, 48V ipotetici) ×5 stati (sano, R2202 aperto, R2202 corto, riferimento assente, 5V assente).

Con U2201A ingresso '+' su VIN_SENSE e '−' su UVLO_REF, la sua uscita idealmente conduce a LOW sotto soglia UVLO. U2201B con ingresso '+' su OVP_REF e '−' su VIN_SENSE conduce a LOW sopra soglia OVP. Le uscite open collector in parallelo, con pullup R2207, producono consenso HIGH idealizzato solo fra ~10 e ~15V e per supply/reference alimentati. **Non esiste uscita fail-OFF garantita durante fault**.

| Stato sintetico | Interpretazione vincolante |
| --- | --- |
| 5V sano, ref sano, VIN 13,8V | Consenso HIGH nominale per tutti i corner |
| VIN 0, 8, 16, 48V, senza difetti | Uscita LOW nominale, ma VIN 48V non autorizzato sul circuito reale |
| R2202 inferiore aperto | Il pin VIN_SENSE può arrivare a **VIN raw**; a 8/13,8/16/48 V supera persino la rail 5V. Nessun clamp, non si può fare affidamento sull'uscita |
| R2202 corto | Il pin sense idealmente è 0V, uscita LOW finché supply/ref funzionano; corrente/elettronica non qualificate |
| Riferimento 2,5V perso | Con VIN>0, modello LOW; a VIN=0 i comparatori sono entrambi a zero, stato non qualificabile senza offset e startup |
| Supply 5V persa | **Pullup R2207 senza energia**: il nodo OC non costituisce un consenso digitale HIGH affidabile; ingresso del downstream non noto. Una catena separata deve garantire OFF |

Il modello non simula reale I/V del comparatore, input common-mode durante startup, thermal, isteresi, surge, guasti Q806, o circuito di disconnessione separato. Un output open collector può essere lasciato fluttuante; il test NON certifica alcun hardware safe state. Le tensioni VIN 48 V sono solamente scenari teorici di fault.

## Priorità hardware obbligatorie

1. Proteggere fisicamente gli ingressi U2201 con limiti di corrente e tensione anche sotto **OPEN/SHORT** di ogni singolo resistore. Verificare modello OEM per input overrail e correnti negative.
2. Progettare una **fonte 5V e VREF2.5V indipendente e protetta** che scada in OFF quando manca energia o riferimento, con MOSFET switch autonomo sul percorso serie non bypassabile dal corto C–E Q806; verificare condizioni doppio fail e body diode.
3. Convalidare footprint, thermal, IV, pinout e test reali, e poi integrare nel MAIN soltanto con revisione indipendente.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
