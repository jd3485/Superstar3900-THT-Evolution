# V0.6 — Simulazione elettrica reale del VCO e correzione delle condizioni iniziali

**Scopo:** verificare con ngspice il circuito RX-only V0.5 e le varianti THT. I risultati elettrici indicano un problema **REALE nel modello**, che non era rilevabile con soli calcoli LC. Non sono misure di laboratorio e i modelli BJT/BB204G sono sintetici, non certificati dai produttori.

## 1. Prima esecuzione elettrica V0.5

ngspice **45.2** eseguito tramite GitHub Actions (Ubuntu). Misura su 25 µs, finestra 15–25 µs; frequenza derivata da 200 attraversamenti crescenti della tensione sul tank.

| VTUNE (V) | Frequenza calcolata dalla waveform (MHz) | Escursione TANK (Vpp) | Tensione A-K MAX del varicap (V) |
|---:|---:|---:|---:|
| 3,2 | 38,30610 | 19,27198 | **+0,53747** |
| 5,0 | 38,31858 | 19,28957 | **+0,53140** |
| 7,5 | 38,35018 | 19,32335 | **+0,51412** |

**Decisione REV-046:** questa topologia originale è **RESPINTA** come VCO funzionante per 270 RX. L'estensione di accordo misurata nel modello è ~0,044 MHz su 3,2–7,5 V a fronte di 2,690 MHz richiesti, e il varicap entra in **polarizzazione diretta per ogni punto**. Non dichiarare V0.5 una progettazione elettrica valida per PCB.

Run della tripla misura: https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42820065706 (SUCCEEDED nel senso di esecuzione della misura; **RF GATE FAIL**).

## 2. Esplorazione con 36 combinazioni circuitali

Parameter sweep documentato in `03_Verifiche/V0.6/explore_vco_v06.py`: VCC 5/7 V, resistenza emettitore 680/1200 Ω, accoppiamento varicap 100/220/470 pF, L 150/180/220 nH, ciascuno a VTUNE 3,5/7/12 V, per **108 vere transienti ngspice**. Sei varianti mantengono i varicap polarizzati inversamente nei tre punti provati ma la loro frequenza è inizialmente sfasata. La successiva scansione L 165–172 nH ha mostrato potenziale copertura aritmetica sotto quelle condizioni.

**Criticità scoperta:** i primi file conservavano `.ic v(TANK)=9,05V` e `uic` persino quando l'alimentazione è stata ridotta a 5 V. Le condizioni iniziali innaturali alterano sensibilmente lo stato non lineare e la frequenza simulata. **Le varianti apparentemente riuscite con quell'avvio NON sono validazioni di avviamento**.

## 3. Prima variante rifinita e avvio realistico

`VCO_COLPITTS_REWORKED_V0.6.cir`: VCC=5 V, R503=1200 Ω, L501=168 nH (valore ideale, non part number da acquistare), C504=470 pF. BB204G doppio TO-92, Q501/Q502 2N3904 THT e resto del circuito conservati.

Con avvio seedato **coerente con 5 V**:
- 6,5 V → **36,26145 MHz**, varicap sempre inversamente polarizzato nel modello.
- 7 V → **36,57912 MHz**, varicap sempre inversamente polarizzato.
- 14 V → **39,09686 MHz**, varicap sempre inversamente polarizzato.

Ma con un'alimentazione che sale **da 0 a 5 V in 100 ns** e senza `.ic`/ `uic`:
- 6,5 V → **34,67166 MHz**, varicap avanti di +0,4002 V (FAIL).
- 7 V → **34,84867 MHz**, varicap avanti di +0,3188 V (FAIL).
- 15 V → **38,96433 MHz**, alta gamma non ancora raggiunta (FAIL).

**Decisione:** nemmeno questa variante può essere promossa a PLL/VCO operativo. Una simulazione con avvio seedato non sostituisce test dell'avvio dalla situazione reale. Eventuale cambio L/capacità deve essere verificato esplicitamente con ramp e senza `uic`.

## 4. Requisiti per promuovere una successiva candidata

- Oscillazione con partenza da alimentazioni reali e transitori su tutte le tensioni di controllo utilizzate.
- Copertura della banda **36,310–39,000 MHz**, possibilmente con margine di taratura.
- Polarizzazione inversa istantanea del doppio BB204G, nessun picco forward e rispetto della tensione inversa massima.
- Ampiezza utile al buffer/limitatore, controllo carico mixer e prescaler, spurie e fase.
- Disponibilità reale e autenticità di varicap, BJT e induttanza THT; package e pinout secondo datasheet originali, non soltanto un netlist.
- PLL completo: trasferimento del filtro e margine di fase con KVCO effettivo e stadio VTUNE, precisione SSB del riferimento; **non ancora validati**.
- Schemi KiCad nativi completi; ERC/DRC, layout RF e DFM PCBWay. **NO FAB / NO TX**.

## 5. Riproduzione

- `run_spice_v06.py`: 3 transitori sul V0.5 originale e frequenza reale.
- `explore_vco_v06.py`: 36 combinazioni / 108 transitori (diagnostico).
- `refine_vco_v06.py`: 6 induttanze / 18 transitori.
- `run_reworked_v06.py`: 8 punti di accordo sulla variante L168.
- `run_operating_window_v06.py`: 14 transitori, confronto `uic` vs accensione da zero.
- `run_ramp_scan_v06.py`: 16 combinazioni / 80 transitori basati **solo sull'avvio da zero**; risultati e validità da leggere dall'ultimo report e artifact della run corrispondente.

La pipeline `.github/workflows/vco_spice_v06.yml` installa ngspice e pubblica un artifact JSON/log. L'eventuale esito verde della pipeline indica esecuzione corretta, **non RF PASS**. I dati SPICE restano modellazioni, non misure.

**GATE FISSI:** NO FAB / NO TX; KiCad ERC/DRC NON ESEGUITI, PCB inesistente.

## 6. Esito dello sweep con alimentazione da zero: CANDIDATA B

Run [42821991921](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42821991921): **16 varianti L/C × 5 tensioni = 80 transitori reali ngspice**; **4 combinazioni** sono risultate monotone, con diodi inversamente polarizzati nei punti campionati e finestra che include i limiti 36,310–39,000 MHz.

**Candidata B scelta SOLO per sviluppo successivo**, confermata da run dedicata [42822739779](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42822739779):

- VCO Q501+Q502 `2N3904-AP` in TO-92, BB204G doppio TO-92 in parallelo; VCC **5 V**; R503 **1,2 kΩ**; C504 **470 pF** THT; L501 effettiva **166 nH** candidata, da realizzare con bobina RF THT regolabile e Q/SRF adeguati.
- Accensione VCC 0→5 V in 100 ns, **senza `.ic` né `uic`**. VTUNE già presente a 8/9/10/12/15 V nello studio (sequenze relative delle due alimentazioni ancora da verificare).

| VTUNE (V) | LO ngspice (MHz) | A−K max BB204G (V) | VR inversa max (V) |
|---:|---:|---:|---:|
| 8 | 36,04773 | −0,44691 | 10,01986 |
| 9 | 36,80801 | −1,35499 | 11,24530 |
| 10 | 37,39017 | −2,29059 | 12,40106 |
| 12 | 38,26433 | −4,19276 | 14,59204 |
| 15 | 39,19647 | −7,09365 | 17,74675 |

**Esito:** **PASS LIMITATO AL MODELLO E AI CINQUE PUNTI**: frequenza monotona nei punti misurati, gamma che include i target, zero polarizzazione diretta e tensione inversa inferiore a 30 V nei punti simulati. Non è PASS su tutti i 270 canali, sulle temperature/deriva, sui valori reali di bobina, sui transitori di tensione o sul carico RF del mixer.

**Blocco progettuale ancora rilevante:** VTUNE fino a **15 V** è maggiore dell'alimentazione prevista della radio (13,8 V). Occorre una sorgente analogica più alta e silenziosa o una nuova revisione LC che richieda meno tensione; nessun driver/boost THT è stato progettato. Il BB204G legacy non ha fornitura affidabile confermata. Niente KiCad ERC/DRC e niente PCBWay.

**Prossima revisione V0.7:** qualificare startup sotto altre condizioni e temperatura, tolleranze L/C e varicap, sorgente VTUNE, interfaccia LO/limitatore e loop PLL dinamico, quindi schematico KiCad nativo. **NO FAB / NO TX.**
