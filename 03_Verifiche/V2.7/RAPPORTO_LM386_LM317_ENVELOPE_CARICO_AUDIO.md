# V2.7 — Analisi quantitativa carico audio 6 V LM386 / LM317 (13 novembre 2026)

**Risultato:** un gate numerico ripetibile per distinguere corrente nell'altoparlante, corrente nel rail di alimentazione e riscaldamento LM317. **NON è simulazione ngspice, prova termica o verifica THD, e non approva l'hardware.** Il master radio MAIN V2.6 (7 fogli, 138 refs) e i tre schemi DRAFT non vengono modificati in questa revisione.

## Fonti primarie
- Texas Instruments **LM386 SNAS545D** (revisione agosto 2023), §6.5: LM386N-1 intervallo VS=4–12 V; a **6 V, 8 Ω, THD=10%**, potenza d'uscita **250 mW MIN, 325 mW TYP**; a 6 V/8 Ω/**125 mW**, f=1 kHz, pin1/8 aperti, **0,2% THD TYP**, non massimo garantito. Corrente di riposo a 6 V, VIN=0: 4 mA tipica, 8 mA massima. https://www.ti.com/lit/ds/symlink/lm386.pdf
- Texas Instruments **LM317-N** datasheet, prodotto ACTIVE TO-220 3-pin: https://www.ti.com/product/LM317-N e https://www.ti.com/lit/ds/symlink/lm317-n.pdf . La specifica di ingresso del DRAFT è esclusivamente **10–10,5 V al pin VIN U1401.3**, da banco e con limitazione di corrente. Regolazione effettiva, protezioni, dissipatore e SOA non sono qualificati.

## Carico resistivo ideale, NON corrente prelevata dal regolatore

Formula `V_RMS=sqrt(P_spk × R_spk)`; `I_RMS=sqrt(P_spk/R_spk)`; per tono sinusoidale `I_peak=sqrt(2)×I_RMS`. La frequenza di taglio approssimata del condensatore di uscita **C1202=220 µF** su carico puramente resistivo è `fc=1/(2π×R_spk×C1202)` ed esclude ESR, tolleranze, impedenza reale e carico dinamico.

| Speaker ideale | Potenza sul carico | Tensione RMS | Corrente RMS | Picco sinusoidale | fc ideale C1202 |
|---|---:|---:|---:|---:|---:|
| 8 Ω | 100 mW | 0,894 V | 0,112 A | 0,158 A | 90,4 Hz |
| 8 Ω | 125 mW | 1,000 V | 0,125 A | 0,177 A | 90,4 Hz |
| 8 Ω | 250 mW | 1,414 V | 0,177 A | 0,250 A | 90,4 Hz |
| 4 Ω | 100 mW | 0,632 V | 0,158 A | 0,224 A | 180,9 Hz |
| 4 Ω | 125 mW | 0,707 V | 0,177 A | 0,250 A | 180,9 Hz |

I casi 4 Ω sono **solo calcoli matematici**: la tabella OEM citata non garantisce potenza/dissipazione/THD su 4 Ω. **La corrente RMS o di picco nello speaker NON è la corrente di alimentazione dell'LM386.** La corrente di rail dipende dal regime amplificatore, efficienza, quiescenza e dinamica, che richiedono modello vendor o misure. Non trasformare i 250 mW a 10% THD in una specifica di audio pulito.

## Dissipazione regolatore: limiti di uno scenario parametrico
La PR #62 ha imposto VOUT di riferimento statico compreso circa **5,6055–6,3091 V** con VREF, IADJ e resistori ±1%. Assumendo artificialmente nel solo modello:
- VIN alto = 10,5 V, VOUT basso = 5,6055 V;
- ambiente = 60 °C; θJA = **50 °C/W assunto**, non qualificato per la PCB;
- budget prudenziale Tj ≤125 °C, **non** permesso di fabbricazione;
- `P_reg≈(VIN−VOUT)×I_supply_dc` (approssimazione che non considera tutte le perdite, correnti o transitori).

La temperatura stimata è `Tj≈60+(10,5−5,6055)×I_supply_dc×50`.

| Corrente DC ipotetica nel rail | Tj stimata (θJA assunto) | Lettura |
|---|---:|---|
| 0,10 A | ~84,5 °C | Solo scenario |
| 0,20 A | ~108,9 °C | Solo scenario, non approvazione |
| 0,25 A | ~121,2 °C | Margine molto piccolo |
| 0,35 A | ~145,7 °C | Supera 125 °C nell'ipotesi |

Se realmente servissero 0,35 A DC medi, occorrerebbe θJA effettiva **≤37,9 °C/W** per restare sotto 125 °C nello scenario: non è un dissipatore selezionato né un limite garantito in situ. Il minimo teorico per trasferire 125 mW attraverso un rail ideale da 6 V è 20,8 mA al 100% di efficienza; non è la corrente effettiva dell'amplificatore.

## Strumento ripetibile integrato
- `03_Verifiche/V2.7/verify_audio_load_envelope.py` verifica formule, scenari di carico, differenza 4/8 Ω, frequenza di taglio ideale, scenari di temperatura e vincoli di riferimento LM317; impone che i numeri siano coerenti con `AUDIO_LOAD_ENVELOPE_LM386_6V.csv`.
- Il nuovo gate gira in `ci/fast_regressions.py`, **senza aprire un ulteriore job KiCad9** per i calcoli puri. Il test non dichiara `PASS` sul progetto elettronico, ma solo consistenza numerica e condizioni di stop.
- Per non allargare falsamente il progresso, i dati di classe 125mW/10% THD vengono tenuti separati. A 125mW il dato THD 0,2% è **TYP**, non un requisito garantito su tutte le frequenze/temperature.

## Decisione ingegneristica
**Non congelare ancora LM386 + LM317 come alimentazione radio definitiva.** Necessari: specifica SPL/carico 8Ω (o 4Ω motivati), output THD e risposta in frequenza per voce AM/FM, effettiva corrente di alimentazione nel tempo, stabilità/ripple, THD con PSU reale, verifica potenza e corrente dei cavi, termica PCB con dissipatore e linguetta LM317 in tensione, protezione input automotive e massa RF. Il pilot resta limitato ad alimentatore da laboratorio da 10–10,5 V. La scelta di potenziometro FRONT 10k lineare è ancora da qualificare meccanicamente/ergonomicamente.

Stima complessiva del progetto **circa 20% (non metrica)**; PCB-MAIN/PCB-FRONT **layout/routing 0%**. Non esiste ancora una PCB con DRC. BOM finali e #27/#42 restano bloccati. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
