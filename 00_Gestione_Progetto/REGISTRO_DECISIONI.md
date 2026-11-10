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
