# Audit passivi THT V2.6 — primo lotto di MPN candidati (12/11/2026)

## Fonte e portata
Dopo il merge PR #47 (`e210a17642c89c8825694b6a1cfbdfc66cc2189c`, CI #43245509954 PASS 3/3), il raggruppamento Value+Footprint distingue 114 gruppi su 138 posizioni. Questo lotto esamina **sei posizioni fisiche** senza cambiarne il valore, footprint o lifecycle.

| Riferimenti | CAD attuale | MPN candidato | Evidenza | Qualifica mancante |
|---|---|---|---|---|
| R403, R502, R804 | 10 kΩ; assiale DIN0207, pitch 7.62 mm | Yageo **CFR-25JB-52-10K** | Datasheet pubblicato sul dominio ufficiale Yageo: https://www.yageogroup.com/component-documentation/download/specsheet/CFR-25JB-52-10K; distribuzione segnala Active, 0.25W, ±5%, corpo 6.3x2.4 mm: https://www.digikey.it/en/products/detail/yageo/CFR-25JB-52-10K/338 | Il distributore **non** certifica produzione attuale secondo criterio B; verificare status OEM MPN, accettabilità ±5%, coefficiente termico, rumore in VCO, potenza, tensione, 7.62 mm e diametro lead per tutte e tre le posizioni |
| C401, C405, C406 | 100 nF; disco THT Ø3 mm, passo 2.50 mm | Vishay **K104K15X7RF53L2** (solo candidato di confronto) | Cross-reference ufficiale Vishay (100 nF, 50V, X7R, ±10%, passo 2.54 mm): https://www.vishay.com/docs/45177/crmllccspraguevsbcc.pdf ; codifica generale leaded MLCC: https://www.vishay.com/docs/45163/geninfmlleadedgenpurp.pdf | Tabella cross-reference **non** conferma produzione attuale; passo **2.54 mm**, NON esattamente 2.50 mm nel CAD: possibili altre differenze di diametro/spessore. Non dichiarare drop-in. Verificare DC bias effettivo, derating e fisica; RLC parassiti e decoupling PLL |

### Decisioni
- Entrambe le famiglie sono **candidature**, non scelta definitiva. Non basta il prezzo o lo stock di distributore e neppure il solo datasheet OEM per essere certi dell'attuale produzione.
- **Non** trattare uguali i tre resistori solo perché condividono valore e footprint: R502 è nella sezione VCO, R403 PLL digitale, R804 filtro/driver PLL. Qualificare tolleranza, rumorosità e tensioni in base a ciascuna funzione.
- Il disallineamento 2.50 / 2.54 mm del condensatore impone controllo meccanico e, se rilevante, modifica CAD versionata con KiCad9. Non alterare ora il footprint.
- Test normali `verify_mpn_inventory_v26.py` e `--release` devono continuare a contare **6 ACTIVE / 132 DA_VERIFICARE**; nessuna nuova approvazione.
- Per U401 Lansdale ML145151YP e L501 Coilcraft resta obbligatoria conferma produttiva OEM sul codice esatto; Issue #42 e #19. **STOP V2.7 / NO FAB / NO TX / NO alimentazione batteria/veicolo.**
