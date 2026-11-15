# FRONT V2.7 — RV1301 guard indipendente verso AF_GND: compromesso guasto/volume

**15 novembre 2026 · CANDIDATO NON INTEGRATO · NO FAB / NO TX**

## Problema e topologia

PR #257 ha dimostrato con modello AC e netlist KiCad9 che aprendo il
terminal 3 (lato basso) del volume RV1301 si perde l'attenuazione
del potenziometro al minimo: 1 kHz, 50 kΩ LM386 ipotetici,
cursore 1%, transfer normalizzato **0,008192 → 0,714219**.

Qui si modella un resistore **aggiuntivo permanente tra RV1301 pin2
(cursore) e AF_GND separato dal terminale pin3**. È necessario che
il ritorno AF_GND esterno resti valido, che il componente aggiuntivo
non sia aperto e che il cursore sia connesso. Se il cablaggio di massa
esterno si apre, tale mitigazione non ha effetto: nessuna
**tolleranza a guasto singolo end-to-end** dimostrata.
Non c'è modifica allo schematico attuale né PCB: studio
preliminare di componenti e parametri, senza footprint/MPN.

## Verifica

`03_Verifiche/V2.7/verify_front_volume_wiper_guard_tradeoff_native.py`
controlla la topologia sana KiCad9 esportata (J1301, RV1301, J1302,
demodulatore, LM386), poi 5 Rguard (100/330/1000/3300/10000 Ω)
× 5 frequenze (100–10000 Hz) × 5 posizioni (1–99%)
× 3 resistenze input ipotetiche (25/50/75 kΩ) = **375 punti**.
Ogni punto confronta sia normale sia terminale basso aperto
mediante **due metodi indipendenti**: riduzione serie/parallelo complessa
e KCL a tre nodi con residuo della matrice originale.
La FULL CI fallisce su divergenze, trasmissioni impossibili o
valori non finiti. Rinput 25/75k **non sono corner OEM dichiarati**.

| Rguard Ω | volume 1% normale | volume 1% guasto pin3 | guasto / guasto senza guardia | volume 99% normale | volume 99% / senza guardia |
|---:|---:|---:|---:|---:|---:|
| 100 | 0,004119 | 0,008192 | 1,15% | 0,051233 | 6,35% |
| 330 | 0,006304 | 0,026345 | 3,69% | 0,160195 | 19,86% |
| 1000 | 0,007455 | 0,074316 | 10,41% | 0,394240 | 48,87% |
| 3300 | 0,007954 | 0,198127 | 27,74% | 0,667371 | 82,73% |
| 10000 | 0,008112 | 0,384526 | 53,84% | 0,767867 | 95,19% |

<small>Magnitudini `V(LM386 pin3)/V(sorgente AF ideale)` a 1 kHz
con Rin ipotetica 50k, senza guadagno LM386. Sono risultati di
modello matematico, **non misure**; la CI dovrà convalidarli.</small>

## Decisione preliminare

Una resistenza passiva di guardia può ridurre l'effetto di un guasto
isolato del terminale basso **ma impone un compromesso forte**.
Rguard=100Ω riduce il trasferimento in guasto ma abbassa il massimo
volume sano al 6,35% del progetto attuale; Rguard=10k preserva
95,19% del massimo ma conserva oltre metà dell'audio di guasto.
**Nessuno dei cinque candidati è qualificato come fail-safe**.
Non modificare la BOM, non cablare la MAIN, non usare questo studio
per dichiarare sicurezza audio, limiti dB SPL o protezione uditiva.

Una soluzione potenzialmente migliore richiede una
**funzione di mute separata fail-closed** o ridondanza reale
al controllo audio, da sviluppare con circuito KiCad THT autonomo
e prove su startup/fault, evitando di impegnare il percorso RX
finché driver/sorgente/impedenze non sono qualificati.

## Gate ancora da chiudere

OEM potenziometro e curva audio, tolleranze del guard, wiper intermittente,
guasto open resistor, open AF_GND esterno, transitori d'accensione,
livello reale del rivelatore, guadagno/distorsione LM386,
termica e comportamento diffusore, ritorni/chassis, potenza/protezione,
prove di banco indipendenti e PCB prodotto. Qualunque nuovo CAD
si sottopone a KiCad9 ERC/netlist e CI finale. **NO FAB / NO TX /
NO BATTERIA / NO VEICOLO.**
