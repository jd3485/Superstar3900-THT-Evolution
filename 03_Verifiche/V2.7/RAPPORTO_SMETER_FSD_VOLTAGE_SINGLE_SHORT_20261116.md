# FRONT S-meter V2.7 — limiti di tensione condizionali prima della qualifica FSD

Data: 16 novembre 2026. L'analisi **non definisce un'alimentazione ammessa**, né qualifica un movimento a bobina mobile.

Lo schema KiCad FRONT `FRONT_SMETER_THT_V2_7_DRAFT.kicad_sch` rappresenta RV1801 10 kΩ e due limitatori R1801/R1802 da 100 kΩ ciascuno in serie tra cursore e J1802. Il gate analitico conserva il -5% di resistenza illustrativo, quindi almeno 190 kΩ con entrambi integri, 95 kΩ con un solo resistore cortocircuitato. Il calcolo assume worst-case cursore a piena scala, impedenza sorgente nulla e resistenza bobina ignorata, senza garantire il comportamento a transitori o con cortocircuiti del cablaggio che bypassano i limitatori.

| FSD ipotetica | |Vdrive| max, entrambi integri | |Vdrive| max, singolo limitatore corto |
|---|---:|---:|
| 25 µA | 4,75 V | 2,375 V |
| 50 µA | 9,50 V | 4,75 V |
| 100 µA | 19,0 V | 9,50 V |
| 200 µA | 38,0 V | 19,0 V |

La tensione di 20 V **non è dimostrata compatibile** con una bobina ipotetica da 50 o 100 µA: 20/190k ≈105,3 µA con entrambi i limitatori integri; 20/95k ≈210,5 µA con un cortocircuito. Per due cortocircuiti il limite basato sui resistori diventa 0 V nel modello conservativo che ignora Rcoil; non è una prova di comportamento a guasto reale. Anche un caso sotto soglia non qualifica la linearità, la calibrazione o la resistenza meccanica dello strumento.

Il nuovo gate `verify_front_smeter_fsd_fault_screen.py` verifica la funzione inversa di tensione massima su quattro FSD ipotetiche, confrontando soglia/oltre soglia con il modello di corrente già presente. Richiesti prima di procedere con un driver MAIN reale: MPN OEM attivo e FSD/coil/tolleranze del meter, fonte limitata e relative soglie, pinout J1801/J1802 e ritorni, hotplug/ESD, reverse, dissipazione e derating di R1801/R1802. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
