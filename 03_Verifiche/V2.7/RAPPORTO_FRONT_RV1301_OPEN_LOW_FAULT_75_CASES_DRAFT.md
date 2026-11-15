# V2.7 — FRONT RV1301, apertura contatto basso: studio AC su topologia KiCad9

**Stato:** analisi elettrica LINEARE e completamente ipotetica di guasto; non
qualifica componenti, né sicurezza d'uso, né firmware, né layout finale.
La gerarchia V2.7 del FRONT mantiene `RV1301` da 10 kΩ lineari,
pin 1 = `DEMOD_AUDIO`, pin 2 = `VOL_WIPER_TO_AMP`, pin 3 =
`AF_GND`. La catena a valle resta `C1201` 100 nF, `R1201`
10 kΩ, ingresso LM386 stimato 25/50/75 kΩ; a monte `C1502` 100 nF e
`R1502` 100 kΩ. Queste connessioni si verificano tramite vera netlist KiCad9
nella FULL CI, senza toccare `.kicad_sch` o la PCB.

## Modalità di guasto studiata

Si apre **soltanto il terminale basso 3 di RV1301**, pur lasciando
l'AF_GND del connettore e la massa ingresso dell'amplificatore collegate.
Il potenziometro non divide più fra segnale e massa: il percorso residuo
è ingresso segnale → resistenza fra terminale alto e cursore → ingresso
amplificatore. L'invariante `pin3` aperto è una perturbazione nel modello,
**non è una modifica elettrica sul CAD**.

Il gate `verify_front_volume_open_low_fault_kcl_native.py` confronta
due metodi distinti: riduzione complessa serie/parallelo e soluzione nodale
KCL a tre nodi con residuo indipendente. Verifica 5 frequenze
100/300/1000/3000/10000 Hz × 5 posizioni cursore 1/10/50/90/99%
× 3 ingressi LM386 25/50/75 kΩ = **75 casi**.
Controlli: differenza complessa inferiore a 3·10⁻¹⁰, residuo KCL
inferiore a 10⁻⁸, trasmissione passiva finita inferiore a uno,
guasto sempre più alto del percorso sano. Vengono stampati i risultati
esatti nel log CI (nessun valore sintetico spacciato per misura).

A **1 kHz e ingresso illustrativo 50 kΩ**, modulo
`V(LM386 pin3)/V(sorgente AF)`, senza guadagno LM386:

| Cursore | Sano | Pin3 RV1301 aperto | Rapporto del modello |
|---:|---:|---:|---:|
| 1% | 0,0082 | 0,7142 | circa 87× |
| 10% | 0,0808 | 0,7235 | circa 9× |
| 50% | 0,3934 | 0,7679 | circa 2× |
| 90% | 0,7245 | 0,8181 | circa 1,13× |
| 99% | 0,8067 | 0,8303 | circa 1,03× |

**Rischio progettuale:** un contatto basso aperto nella topologia
attuale può rendere quasi inefficace la regolazione a basso volume,
pur senza guadagno attivo. È necessario riesaminare il comportamento
fail-safe prima del congelamento dello schema del FRONT e prima di
qualificare un OEM potenziometro. Nessun criterio di danno uditivo è
dedotto da tensioni normalizzate senza livello AF reale o misure audio.

## Limiti

Modello generatore AF ideale, rete passiva e massa ideale; non considera
corrente di wiper, guasti intermittenti, scariche di condensatori,
pop transitori, capacità parassite, cablaggio/chassis, potenziometro
logaritmico, diodo AM non lineare, amplificatore attivo, speaker,
altri stadi RF, OEM PVT, prove a banco. La corrente reale IF e il
driver audio non sono qui qualificati; nessuna modifica alla board
FRONT 13 THT / 28 pad / 12 reti / 35 piste.

**GATE:** FAST, FULL e Required CI devono essere SUCCESS sullo SHA finale
prima dell'integrazione. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
