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
