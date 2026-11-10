# V0.2 — Contratto logico PLL RX (non netlist KiCad)

| Segnale | Origine → destinazione | Regola |
|---|---|---|
| RX_BAND, RX_CHANNEL, ALPHA_SW | Comandi THT → selettore N | Selezione 6×(40+5) |
| CH9_PRIORITY | Interruttore → controllo | Forza D/9 a 27,065 MHz AM |
| N[13:0] | Codifica canali → PLL | 3631..3900 integer, impostazioni RX-only |
| REF_10M240 | Quarzo 10,240 MHz candidato → R=2048 | Comparatori a 5 kHz |
| LO_FEEDBACK_DIV2 | SN74AC74N candidato → pin fIN o contatori | 18,155–19,500 MHz, livelli ancora da verificare |
| VCO_TUNE | Filtro loop → varicap VCO | Range/timing da definire |
| LO1_RX | VCO → buffer → mixer RX | 36,310–39,000 MHz candidato |
| PLL_LOCK_GOOD | Controllo lock → RX mute | Bloccare RX se non agganciato o alimentazione instabile |
| TX_GATE | **NESSUN CARICO** | **TX fisicamente inibita**, non dipende dal solo software |

**Non fabbricabile:** nessun MPN definitivo, nessuna mappa pin-to-net completa e nessuna conferma di livelli, correnti, spur o lock time.
