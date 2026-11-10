# Decisioni V0.8 — 10 novembre 2026

- **DT-058 STUDY:** incrementare target boost a **27V** con U701 MC34063ABN DIP8, Rsc0,47Ω THT e L701 470µH; soglia MC34063 ST 250/300/350mV min/typ/max, a Vin11V deltaI stimata0,331A e soglia minima0,532A, margine _solo da corrente zero_0,201A. **Non prova comportamento CCM/timing Ct**.
- **DT-059 STUDY:** D701 Schottky Vishay **SB160-E3/54 60V 1A DO41**, sostituisce 1N5819 40V candidato, nuovo margine nominale ma switching overshoot da verificare.
- **DT-060 STUDY:** L701 Bourns **RLB0914-471KL** THT 470µH, Irms560mA typ, Isat1A typ, DCR1,3Ω max; NON schermato, disturbo RF e dissipazione da validare.
- **DT-061 STUDY:** U702 LM317T TO220 con R710240Ω e R7113570Ω ->20,022V tipici, precarico R7132400Ω 0,5W per soddisfare10mA minimo in ipotesi conservativa. Verificare spesa termica, temperatura, dropout e protezione cap ADJ.
- **DT-062 STUDY:** U803 LM358N PDIP8, non-inverting ×4 con Rf30k e Rg10k, input `PD_FILTER` esterna 2–3,75V, uscita VTUNE8–15V in modello, second amp terminato. Non è phase detector né PLL funzionante.
- **DT-063 EVIDENCE:** run ngspice del driver con modello ideale limitato da output rail−headroom, 6 transitori. Headroom3V output14,996V a PD3,75V; headroom4,3V output14,747V (**FAIL obiettivo**). Nessuna simulazione del LM358 fisico.
- **DT-064 WARNING:** CT470pF non implica f40kHz reale; l'oscillatore MC34063 e corrente sense non sono verificati; 27V SMPS può interferire con la radio.
- **DT-065 HISTORY:** congelare `CONFIGURAZIONE_V0.7.json` e puntare vecchia regressione V0.7 allo snapshot, aggiornarne solo l'asserzione fragile della posizione dell'handoff; config corrente a V0.8. Preservare V0.1–V0.7 cumulativamente.
- **DT-066 GATE:** nessun PCB, ERC/DRC, apparecchio o TX autorizzati; **NO FAB / NO TX**.

---

# Decisioni V0.7 — 10 novembre 2026

- **DT-051 (PROPOSTA BOOST THT):** per superare il fabbisogno VTUNE fino15V da 13,8V, adottare architettura **ST MC34063ABN DIP8 boost~24V**, solo candidata per studio; pin 1–8 secondo datasheet ST. Nessun MC34063 realmente simulato.
- **DT-052 (REGOLAZIONE):** dopo booster utilizzare **LM317 TO-220** regolatore ~18,287V con R240Ω/3,24kΩ, pin ADJ1 VOUT/TAB2 VIN3, e RC isolamento 10Ω/100µF. Tab a VOUT, non massa. Protezioni input/ADJ/output ancora aperte.
- **DT-053 (PRE-DIMENSIONAMENTO):** booster L470µH Rsc1Ω, fsw target40kHz (non certificata), Rfb21,8k/1,2k e 1N5819 assiale DO-41. A VIN11V salto corrente ideale0,3056A, soglia sense typ0,33A: **margine solo24,4mA**, non approvare per PCB.
- **DT-054 (SIMULAZIONE LIMITATA):** run ngspice 42827358481 è **vero ngspice su switch/comparatore IDEALI** a Vin11/13,8/15,5V (~24V). Non equivale al MC34063, LM317, EMC, phase noise o elettronica reali. Non marchiare circuito RF PASS.
- **DT-055 (DRIVER VTUNE APERTO):** LM358N DIP8 e uscita15V non garantite con rail minimo17,4V e headroom2–3V; non collegare booster a VTUNE, servono driver analogico/loop PLL/POWER GOOD progettati e verificati.
- **DT-056 (STORICO CUMULATIVO):** congelare CONFIGURAZIONE_V0.6.json, test V0.6 leggono il proprio snapshot, V0.7 in CONFIGURAZIONE_CORRENTE.json. Preservare prove V0.5 RF FAIL e V0.6 candidata solo nel modello.
- **DT-057 (GATES):** nessun componente SMD, no PCBWay finché KiCad/ERC/DRC e prototipi non validati; nessun TX. **NO FAB / NO TX.**

---

# Decisioni e misure V0.6 — 10 novembre 2026

- **DT-045 (EVIDENZA ELETTRICA):** ngspice 45.2 transitorio VCO V0.5: a VTUNE 3,2..7,5 V f=38,306..38,350 MHz, diodo BB204G avanti +0,51..+0,54 V. V0.5 **RESPINTO come circuito di sintonia valido**; revisioni storiche lasciate intatte.
- **DT-046 (METODO):** simulazione RF deve includere sweep di tensione e avvio senza condizioni iniziali artificiali, non solo formule LC, né singola oscillazione a una frequenza. Le prime combinazioni UIC a 9V per VCC5V non qualificano il progetto.
- **DT-047 (CANDIDATA B, NON APPROVAZIONE ACQUISTO):** VCC5 V, R503 1,2kΩ, C504 470pF, L501=166nH effettivi, doppio BB204G, due BJT THT 2N3904; 5 prove ngspice ramp VCC zero e VTUNE8/9/10/12/15V, f36,04773..39,19647MHz, A-K max sempre negativo e VR inversa max17,74675V. **PASS LIMITATO AL MODELLO IN 5 PUNTI**, non prova 270 frequenze, tolleranze o hardware.
- **DT-048 (NUOVO VINCOLO):** VTUNE desiderata fino15V > alimentazione nominale13,8V; obbligatorio circuito analogico THT a basso rumore o nuova topologia a tensione inferiore. LM358 a12V V0.5 non idoneo automaticamente a erogare15V; nessun acquisto/PCB.
- **DT-049 (GESTIONE):** V0.6 congela `CONFIGURAZIONE_V0.5.json` per preservare 34 test storici, riporta esiti SPICE, script di prova e report senza cancellare originali o forzare RF PASS. La CI statica deve mantenere le suite cumulativamente.
- **DT-050 (SICUREZZA):** RX modellata, TX hardware disattivata. Simulazione non autorizza ordini di PCBWay, emissione o costruzione. **NO FAB / NO TX.**

---

# Decisioni V0.5 — 10 novembre 2026

- **DT-038 CANDIDATA:** passaggio da *una giunzione BB204G + 220nH* (studio V0.4) a *due giunzioni BB204G in parallelo + 150nH* per ridurre VTUNE richiesta. Fisico: D501 pin1/3 anodi al nodo VAR_A, pin2 catodo a VTUNE_RAIL; C504 blocca DC fra tank e diodi. Non garantisce copertura senza taratura.
- **DT-039 CANDIDATA:** primo circuito oscillatore Colpitts Q501 2N3904-AP (E1/B2/C3) con feedback C502=68p C503=220p, bias 33k/10k/330Ω; buffer emitter follower Q502 E1/B2/C3 con accoppiamento debole 2,2p. SPICE scritto, **NON ESEGUITO**.
- **DT-040 EVIDENZA ANALITICA:** VCO model L150nH, C_fixed_eff 61pF assunta (capacità feedback+dispositivo+PCB+trimmer), varicap model non ufficiale, 270 Vtune nominali 3,13..6,95V. **Non certificata tolleranza**.
- **DT-041 CORREZIONE PROGETTUALE:** vecchia rete PLL 2.2k/10k/100n dà solo -1,73dB a 5kHz nel modello. Un 2 poli RC candidate dà -41,43dB ma **non certifica stabilità, lock o ripple del PLL**. Necessita Kphase/Kvco/margine.
- **DT-042 CANDIDATA:** serve driver di tensione attivo THT (LM358N PDIP8 su rail ~12V) per generare Vtune fino a circa 7V a partire da PDout 0..5V; non è ancora nel circuito SPICE, dunque non approvato.
- **DT-043 CONTROLLO RX:** modello software di mute prima del cambio N e di sblocco solo dopo lock/ref/power/code stabili. MCU PIC18F47Q43-I/P PDIP40 futuro, **non firmware compilabile**. TX fisicamente bloccato.
- **DT-044 REGRESSIONE:** congelare `CONFIGURAZIONE_V0.4.json`, test V0.4 leggono lo snapshot; `CONFIGURAZIONE_CORRENTE.json` sale a V0.5. Mantenerlo stabile nelle future chat.

---

# Decisioni V0.4 — 10 novembre 2026

- **DT-031 (CANDIDATO VCO, non circuito approvato):** D501 `BB204G` Philips varactor doppio TO-92 storico come possibile tuning; L_eff=220nH e C_fixed_eff=57.5pF; una sola giunzione equivalente nel modello, non definito utilizzo terminale del secondo diodo. Fattibilità solo analitica; stock storico non garantito.
- **DT-032 (FILTRO LOOP CANDIDATO):** per U401 PDout scegliere la topologia passiva tipo B del manuale Lansdale; valori preliminari R1=2.2kΩ, R2=10kΩ, C=100nF, f_polo≈130.5Hz, f_zero≈159.2Hz. Non dichiarare loop stabile/compensato prima di Kvco e fase effettivi.
- **DT-033 (LO BUFFER CANDIDATO):** `SN74AC14N` TI PDIP14 Schmitt ad alta velocità candidato per produrre clock CMOS dal VCO solo dopo buffer/condizionamento RF reale. Non collegare VCO sine direttamente a pin clock.
- **DT-034 (CONTROLLO CANDIDATO):** `PIC18F47Q43-I/P` Microchip PDIP40 per controllo semplice di canali, ALFA, CH9 e N[11:0] parallelo; nessun DSP avanzato o funzioni escluse. Pinout MCU e firmware futuri; TX inibita fisicamente.
- **DT-035 (CAD PARZIALE):** primo .kicad_sch nativo solo U402 prescaler e connettori, con simboli locali. **Non è schema della radio né KiCad ERC/DRC eseguito**; GUI e tool CAD non disponibili in questa revisione.
- **DT-036 (REGRESSIONI):** la configurazione V0.3 è congelata in `CONFIGURAZIONE_V0.3.json` e i test storici V0.3 leggono lo snapshot; `CONFIGURAZIONE_CORRENTE.json` procede a V0.4.
- **DT-037 (VINCOLI RIBADITI):** 100% THT, tuner manuale, PCBWay solo PCB nude, assemblaggio interno. Non produrre né trasmettere RF: **NO FAB / NO TX**.

---

# Decisioni nuove — V0.3

- **DT-024 (CANDIDATA, non approvazione acquisto):** prima architettura circuitale U401 `ML145151YP` (Lansdale DIP28, equivalente legacy MC145151P2) con N0..N11 codificati e N12=N13=0. Lansdale offre documentazione e quote su richiesta, **stock e quantità non verificati**; alternativa B con CD74HC4046AE resta aperta.
- **DT-025 (CANDIDATA):** U402 `TC74AC74P(F)` Toshiba DIP14 come prescaler /2; /Q→D, ingresso 36,31–39 MHz condizionato a CMOS; 5V rail separata, pin seconda sezione in stato definito.
- **DT-026 (CANDIDATA per banco, NON adatta SSB finale):** quarzo THT Citizen HC-49/U-S10240000ABJB 10,240 MHz CL18pF; Pierce integrato, C403/C404 22pF candidate. Il budget iniziale ±30ppm più ±50ppm stabilità può corrispondere fino a 3,12kHz a LO=39MHz. Richiesta fonte più stabile/calibrata futura.
- **DT-027 (DATASHEET):** U401 riferimento R=2048 con pin RA2/RA1/RA0 = 1/0/1, T/R pin21 HIGH tramite pullup, fIN=LO/2 18,155–19,5MHz; VDD=5V. Non confondere T/R del chip con una autorizzazione TX.
- **DT-028 (SCELTA DI METODO):** pin-net U401/U402 e primi passivi documentati, **non sono uno schema KiCad, non superano ERC/DRC**, e il lock detect non è ancora un interblocco RX garantito.
- **DT-029 (APERTA):** VCO, buffer clock, varicap THT, loop filter compensato, controller N parallelo, power-good e supervisor devono essere progettati con pin e MPN reali prima della validazione fisica. Nessun montaggio/ordine.
- **DT-030 (REGRESSIONE):** rendere `CONFIGURAZIONE_V0.2.json` snapshot immutabile per i test V0.2, mantenendo `CONFIGURAZIONE_CORRENTE.json` aggiornata a V0.3; test V0.2 ora leggono snapshot storico per continuare a funzionare.

---

# Decisioni introdotte in V0.2 — 10 novembre 2026

- **DT-017 (confermata come tabella RX):** 270 posizioni RX indipendentemente derivate dai dati Superstar 3900 (CBTricks), 30 ALFA, ordine tradizionale 23/24/25; priorità CH9 D/9 27,065 AM. Nessuna autorizzazione TX.
- **DT-018 (candidata reversibile):** IF1=10,695 MHz e LO1 high-side, immagini da RF+21,390 MHz; filtri RF ancora da progettare.
- **DT-019 (modello aritmetico):** REF=10,240 MHz, R=2048, fPFD=5 kHz, divisore RF /2, N=3631..3900 su 270 RX.
- **DT-020 (due opzioni da confrontare):** (A) MC145151P2 legacy DIP28 e SN74AC74N /2; (B) CD74HC4046AE con contatori THT, /2 e VCO RF esterno. Non selezionare MPN definitivamente prima del controllo disponibilità/timing.
- **DT-021 (vincolo):** non collegare direttamente 36–39 MHz all'ingresso fIN MC145151; il suo T/R deve rimanere alto nel modello RX, perché il livello basso introduce offset +856.
- **DT-022 (sicurezza):** tutto il piano è RX, TX_PERMITTED=FALSE su 270 posizioni; NO FAB / NO TX.
- **DT-023 (storicizzazione):** lasciare immutata la configurazione V0.1 e il vecchio segnaposto di tabella; V0.2 aggiunge nuova tabella versionata e `CONFIGURAZIONE_CORRENTE.json`.

---

# Registro decisioni — Superstar 3900 THT Evolution

Ogni decisione deve avere codice, data, stato, ragione e impatto. Una nuova scelta non cancella la precedente: si aggiunge un cambio con ID, data e motivazione.

| ID | Stato | Decisione / Vincolo | Motivazione |
|---|---|---|---|
| DT-001 | CONFERMATA | Progetto GitHub **privato, autonomo e non fork** | Identità tecnica e cronologia indipendenti |
| DT-002 | CONFERMATA | Sulle PCB **100% componenti elettronici THT**, senza adattatori SMD | Requisito fondamentale costruttivo |
| DT-003 | CONFERMATA | PCBWay produce **PCB nude**; montaggio e saldatura eseguiti internamente | Disponibilità dell'attrezzatura THT |
| DT-004 | CONFERMATA | Procedura per revisioni, log, rapporti, commit e continuità fra chat | Sviluppo tracciabile e riprendibile |
| DT-005 | CONFERMATA | Sei bande A–F, 40+5 ALFA per banda: **270 posizioni RX** | Esperienza d'uso di riferimento |
| DT-006 | CONFERMATA | Ricezione AM, FM, USB, LSB, CW; ALFA fisico e CH9 prioritario | Requisiti radio |
| DT-007 | CONFERMATA | Accordatore **manuale** con BYPASS; niente automatico | Semplificazione, controllo diretto |
| DT-008 | CONFERMATA | Escludere DSP audio avanzato, PLL moderno ad alta integrazione, Dual Watch, CTCSS/DCS, VOX | Allineamento con tecnologia THT |
| DT-009 | CONFERMATA COME DIREZIONE | Esplorare PLL **classico** + VCO/divisori o oscillatori tradizionali THT | Fattibilità 270 posizioni senza RF SMD |
| DT-010 | OBIETTIVO | Una PCB principale, salvo motivata impossibilità RF/meccanica | Prodotto concretamente realizzabile |
| DT-011 | OBIETTIVO | Sensibilità, selettività e audio elevati, **da quantificare** | Evitare numeri prestazionali inventati |
| DT-012 | CONFERMATA | TX fisicamente disabilitata finché non verificata; nessun Gerber rilasciato prematuramente | Sicurezza e normative |
| DT-013 | DA DEFINIRE | Pannello vintage e meccanica: compatibilità esatta con Superstar originale oppure stile ispirato | Servono dimensioni/disegni reali |
| DT-014 | DA DEFINIRE | Potenza TX, frequenze/mode TX consentiti, requisiti di laboratorio | Vincoli tecnici e normativi aperti |
| DT-015 | DA DEFINIRE | Roger Beep ed Echo analogico THT: studio di fattibilità, nessun chip assunto | Funzioni secondarie conservate come obiettivo |
| DT-016 | DA DEFINIRE | Alimentazione, consumo, piani di massa, numero strati PCB | Necessita budget elettrico e layout |

**Attenzione:** un PLL tradizionale non equivale automaticamente a un CD4046 usato da solo: la catena di divisori/prescaler, i livelli RF, la programmabilità, il loop e la stabilità devono essere dimostrati, con componenti autentici THT e reperibili.
