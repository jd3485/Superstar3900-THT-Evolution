# V2.7 — Stima di corrente media del rail audio dai grafici TI LM386 (13/11/2026)

**Ambito:** amplificatore LM386N-1 THT già in DRAFT standalone, rail LAB 6 V e regolatore LM317T/NOPB THT da banco. **Non è una misura, non è una simulazione SPICE vendor, non determina la potenza garantita dell'altoparlante, non prova dissipatore né sicurezza.**

## Evidenza originale
Texas Instruments **LM386, SNAS545D**, revisione agosto 2023, §6.5–6.6:
[scheda tecnica e Figura 6-7 “Device Dissipation vs Output Power”](https://www.ti.com/lit/ds/symlink/lm386.pdf). La figura contiene curve **tipiche** V_S=6, 9 e 12 V. La curva **6 V** indica valori indicativi di dissipazione del chip che dipendono dalla potenza resa al carico. I grafici **non** sono min/max, e l'incertezza di lettura da figura è significativa.

Per evitare falsa precisione, il CSV `03_Verifiche/V2.7/LM386_GRAPH_6V_RAIL_CURRENT_BRACKETS.csv` conserva **intervalli larghi letti visivamente** dal grafico, da non interpretare come limiti garantiti o come dati ottenuti da digitalizzazione scientifica:

| Condizione | Dissipazione LM386 letta approssimativamente, 6 V / 8 Ω | I media rail LM386 inferita |
|---|---:|---:|
| **125 mW** speaker | ~0,30–0,42 W (banda di lettura, non range OEM) | **71–91 mA** |
| **250 mW** speaker | ~0,38–0,55 W (banda di lettura, non range OEM) | **105–133 mA** |

La relazione energetica in regime stazionario stimato, **solo per un punto tipico** dello stesso grafico, è `P_VS ≈ P_speaker + P_diss_LM386` e dunque `I_VS_media ≈ (P_speaker + P_diss_LM386)/6 V`. Non tiene conto di altri eventuali carichi, del comportamento in saturazione, dell'uscita non perfettamente sinusoidale, della variazione di VS, della potenza dei connettori e del transitorio di accensione.

**Importante:** la scheda TI specifica a VS=6V/8Ω la potenza **250 mW minima al 10% THD**, non come soglia di alta fedeltà. La distorsione **0,2% tipica** si riferisce a **125 mW, 1kHz**, non a 250 mW. Nessuna stima di corrente può sostituire prove THD.

## Regolatore LM317 — aggiungere il suo carico di feedback

R1401 da **110 Ω ±1%** tra OUT e ADJ assorbe almeno ~**10,80 mA** usando Vref minimo 1,20 V e R max=111,1Ω e al più ~**11,94 mA** con Vref massimo 1,30 V e R minimo 108,9Ω (questi sono calcoli della *corrente di feedback*, non una garanzia PVT della PSU). L'LM317 alimenta **sia** questa rete **sia** l'LM386 e qualunque altro carico di uscita. Per gli intervalli indicativi di corrente:

| Scenario figurativo | Corrente LM386 stimata dalla curva tipica | Corrente complessiva al pin OUT LM317, con feedback |
|---|---:|---:|
| 125 mW / 8 Ω | 71–91 mA | **82–103 mA** |
| 250 mW / 8 Ω | 105–133 mA | **116–145 mA** |

**Attenzione:** questi intervalli non sono margini worst-case di progetto; potrebbero essere superati da esemplari diversi, load clipping, basse impedenze, startup, rumore e tolleranze. Non determinano il fusibile né una corrente minima garantita della sorgente.

Nel DRAFT LM317 input **10–10,5 V da laboratorio**, il Vout parametrico MIN da formula di riferimento è ~**5,6055 V** (non PVT globale garantito). Assumendo artificialmente `Tamb=60°C`, `θJA=50°C/W` e V_IN max=10,5V, usando 145mA DC come esempio si ottiene `Tj≈60+(10,5−5,6055)×0,145×50 ≈ 95,5°C`. Un caso a **0,35 A DC** darebbe invece ≈145,7°C, oltre il nostro budget prudenziale di 125°C. La resistenza termica **non** è ancora definita su PCB e il modello non include ogni perdita o transitorio.

I **125mA RMS nello speaker a 125mW/8Ω** non sono una misura del prelievo dalla PSU: la corrente è alternata, circola fra driver e speaker, e l'energia dissipata e prelevata dipende dalle fasi del transistor d'uscita e dalla topologia.

## Test tecnico ripetibile e limiti
- `verify_audio_rail_current_graph_v27.py` carica il CSV degli intervalli approssimativi, esegue i calcoli di bilancio energetico, verifica separatamente il bleed LM317, confronta il punto con un riferimento **Classe B sinusoidale ideale** (`I_DC_ideal≈I_peak/π`) e un semplice scenario di temperatura. È test di **coerenza del modello** e integrità della tabella, non validazione del chip reale.
- Il gate è aggiunto alla regressione `ci/fast_regressions.py`. Non richiede un nuovo runner KiCad9: si risparmiano costi senza sacrificare il gate completo già esistente.
- La lettura dei grafici è intrinsecamente imprecisa. Per accettazione del progetto servono **profilo reale corrente LM386 a 6V/8Ω**, ripple al pin 6 sotto audio e commutazioni RX, temperatura chip LM386 e LM317, test 1kHz/voce 300Hz–3kHz a potenze controllate e THD, comportamento a clipping, cavo e protezioni. Solo un modello TI ufficiale verificato o misure fisiche appropriate possono restringere l'incertezza.

**Decisione:** si può usare come *punto di partenza* per pianificare un banco prova isolato, NON per fissare dissipatore, PCB, alimentazione veicolare o produzione. Il master V2.6 (7 fogli, 138 refs) e i 3 DRAFT LM386, LM317 e FRONT restano invariati. Percentuale gestionale ~20% stimata, layout fisico/routing 0%. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
