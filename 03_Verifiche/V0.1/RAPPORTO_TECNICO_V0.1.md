# Rapporto tecnico V0.1 — baseline indipendente THT

**Data:** 10 novembre 2026. **Ambito:** requisiti, architettura preliminare, governance e regole di produzione. Nessun circuito completo progettato e nessun esperimento RF.

## Controlli eseguiti
- `python3 -m unittest discover -s 03_Verifiche/V0.1 -p 'test_*.py' -v` — **12 PASS / 0 FAIL / 0 SKIP** nell'ambiente di preparazione, su JSON e file locali. Sono **soltanto controlli statici** del pacchetto.
- Integrità del pacchetto: `MANIFEST_SHA256_V0.1.csv` riporta SHA-256 degli elaborati V0.1; controllabile soltanto sulla baseline V0.1 identica, non sul `main` evoluto.

## Non eseguito
- **NON ESEGUITI:** calcoli dettagliati sulle 270 frequenze RX (tabella vuota, da sviluppare), sintesi PLL numerica/circuitale, simulazioni SPICE/EM, KiCad ERC/DRC e layout, schemi di produzione, verifiche termiche, PCBWay DFM, prove di laboratorio, misure RX/TX, controlli normativi.

## Risultato
La V0.1 è una **baseline organizzativa e di requisiti**, non un rilascio elettrico o un prototipo funzionale. **NO FAB / NO TX.**

## Rischi prioritari
Scelta di sintetizzatore realmente THT/reperibile; filtri THT con prestazioni verificabili; single-PCB con layout RF e accordatore manuale; progettazione di protezioni e sicurezza TX.

## Prossimo sviluppo
V0.2: piano RX completo 270 posizioni + sintesi tradizionale THT confrontata e testata matematicamente. I valori IF rimangono candidati, non congelati.
