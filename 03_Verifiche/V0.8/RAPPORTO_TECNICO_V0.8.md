# RAPPORTO TECNICO V0.8 — margine boost/LM317 e pilotaggio VTUNE THT

**2026-11-10**, repository indipendente `jd3485/Superstar3900-THT-Evolution`, progettazione RX. **NO FAB / NO TX**.

## Avanzamenti documentati
1. **Correzione di dimensionamento della V0.7:** soglia sense MC34063 ST ufficiale 250/300/350mV min/typ/max, quindi Rsc1Ω su L470uH non ha margine garantito. Nuova proposta U701 DIP8 **boost ~27V**, Rsc0,47Ω THT0,5W, L470uH candidato Bourns RLB0914-471KL con Irms560mA e Isat tipico1A, RFB24,7k/1,2k. Con Vin11V e fsw40kHz *assunta* ΔIL=0,3312A; corrente di soglia min0,5319A, margine matematico ΔIL→soglia=0,2007A. **Questo margine non include corrente continua iniziale, minimo L, temperatura né controllo interno e non qualifica Rsc**.
2. **Diodo rettificatore:** da 1N5819 40V a **SB160-E3/54 Vishay 1A/60V DO-41 assiale** candidato; riduce il rischio di superare la tensione nominale inversa per uscita27V, ma sovratensioni di commutazione non misurate né garantite.
3. **LM317T TO-220:** regolazione target **20,02225V** con R710=240Ω, R711=3,57kΩ, Iadj assunta50µA, nuovo precarico **R713=2,4kΩ 0,5W**. La corrente nominale del divisore + precarico minima modellata12,94mA, maggiore dei10mA massimi di carico minimo LM317 del datasheet. Power Rbleed ~0,167W nominali e fino0,184W nel worst assuntivo, derating reale non qualificato.
4. **Interfaccia analogica:** U803 **LM358N PDIP8**, canale A gain non invertente ideale4 (Rf30k, Rg10k), isolatore R220/C100n al nodo VTUNE, seconda unità inutilizzata chiusa come follower a 0V. Un segnale **PD_FILTER** già filtrato di2–3,75V potrebbe pilotare VTUNE8–15V, ma `PD_FILTER` non è collegato direttamente a ML145151 `PDOUT`; la polarità/impedenza del phase detector, il filtro di compensazione e i limiti di corrente del loop PLL **non sono progettati**.
5. **Documento pin-to-net e parti THT:** `04_KiCad/V0.8/VTUNE_PINNET_V0.8.csv` assegna tutti i **19 pin fisici** U701+U702+U803, `VTUNE_RETI_PASSIVE_V0.8.csv` ha **22 reti passivi** a 2 terminali, `07_Componenti/BOM_VTUNE_V0.8.csv` ha **25 righe componenti** (3 IC +22 passivi). Sorgenti produttore e limiti caveat in `01_Specifiche/V0.8/VTUNE_POWER_DRIVER_THT_V0.8.md`. Non è ancora .kicad_sch integrato completo, né PCB.
6. **Margine di alimentazione:** boost divider nominale26,979V, finestra tolleranze assunte25,940–28,049V; LM317 modellato19,05–20,9945V; headroom minima combinata **4,9458V** vs dropout3V assunta, ignorando ripple, startup e modello vendor. LM358 con rail min19,05V−RC0,25V−headroom assunta3V darebbe massimo15,80V. Se headroom fosse4,3V, massimo14,50V: non garantito. La soluzione resta **candidata**.

## ngspice reale — limitato al DRIVER COMPORTAMENTALE

La run [42841818820](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42841818820) ha eseguito **6 transitori** del modello `VTUNE_DRIVER_BEHAVIORAL_V0.8.cir`, con saturazione `rail−headroom` *inventata come ipotesi*, feedback R30k/R10k e R220/C100n; no LM358 macro device, no MC34063, no LM317, no PLL chiuso.

| PD_FILTER (V) | Rail (V) | headroom assunta (V) | VTUNE media ngspice (V) | esito modello |
|---:|---:|---:|---:|---|
| 2,00 | 19,05 | 3,0 | 7,99792 | risposta circa8V |
| 2,50 | 19,05 | 3,0 | 9,99740 | risposta circa10V |
| 3,75 | 19,05 | 3,0 | 14,99610 | risposta circa15V |
| 3,75 | 20,02225 | 3,0 | 14,99610 | risposta circa15V |
| 4,30 | 19,05 | 3,0 | 16,04647 | LIMITAZIONE output |
| 3,75 | 19,05 | 4,3 | **14,74676** | **FAIL obiettivo15V** |

**PASS:** esecuzione SPICE del modello, interfaccia con intervallo funzionale ipotetico.

**NON PASS / NON ESEGUITI:** modelli dispositivi reali, frequenza switching Ct, ripple LM317/rumore di fase, margini e lock PLL, potenza termica reale, ERC/DRC KiCad, prova hardware, DFM e radio completa.

## Errori da non perpetuare
- MC34063 **470pF non significa 40kHz**: il datasheet ST cita frequenza oscillatore tipica33kHz a C_T=1nF, 470pF tende a frequenza differente; nel modello40kHz era solo input matematico, **non circuito realmente verificato**.
- Non usare la vecchia V0.7 a 24V/18V per concludere che l'opamp raggiunga VTUNE15V con margine garantito.
- `OPA197` moderno è disponibile **solo SMD nelle versioni verificate**, quindi non utilizzarlo per aggirare il vincolo THT. In V0.8 LM358N esiste PDIP8 ma le sue prestazioni reali restano da simulare.
- Calcoli di duty/threshold NON sostituiscono SMPS loop, ESR/switching loss, jitter, DCM/CCM, temperatura e continuità di funzionamento. L'induttore Bourns è non schermato e necessita distanza/schermatura dal RF.
- Alimentazione U803 e VCO devono avere masse e separazione gestite su layout; nessun PCB disponibile.

## Gate e prossima V0.9
- **GATE THT:** tutti i candidati elencati DIP/TO220/DO41/THT assiali o radiali; disponibilità di fornitura da riconfermare al momento dell'ordine; non acquistare ora.
- **GATE elettrico:** non promuovere la supply senza SPICE real device, lock/phase margin, verifica 11–15,5V e Iload, depurazione ripple a 5kHz e RF.
- **GATE CAD:** assenti schemi nativi completi VCO+PLL+boost+LM358; KiCad ERC/DRC non eseguiti.
- **GATE sicurezza e produzione:** TX fisicamente disabilitata, nessuna PCBWay ancora. **NO FAB / NO TX**.

Prossima revisione: realizzazione simulazione IC switching e LM358 reale dove disponibile, filtro loop da Kphi/Kvco, powergood hardware e rilievo KiCad/ERC progressivo, senza aggirare standard di progetto.

**Fonti:** https://www.st.com/resource/en/datasheet/mc34063ab.pdf , https://www.ti.com/product/LM317 , https://www.ti.com/product/LM358 , https://www.bourns.com/docs/product-datasheets/rlb.pdf , https://www.vishay.com/doc?88715
