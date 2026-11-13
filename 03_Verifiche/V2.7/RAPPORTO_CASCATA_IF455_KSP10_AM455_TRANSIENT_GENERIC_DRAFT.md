# V2.7 — confronto transitorio IF455 → KSP10BU THT → AM455 (MODELLO GENERICO)

**13 novembre 2026 — DRAFT di simulazione non qualificata, nessuna autorizzazione NO FAB/NO TX rimossa.**

## Problema tecnico e circuito effettivo

La PR #97 ha introdotto uno schema KiCad 9 standalone THT a collettore comune (10 posizioni, ERC0, Q1701 KSP10BU pin 1=B, 2=E, 3=C). La PR #99 ha verificato nove scenari DC/AC del solo follower. Mancava tuttavia il test **combinato** del filtro IF455 caricato dal suo ingresso e del diodo AM455 non lineare caricato dalla sua uscita. Una risposta AC isolata di 0,97 non implica che il circuito completo funzioni meglio.

Nuovo deck `03_Verifiche/V2.7/spice/if455_ksp10_am455_combined_generic_transient.cir` con **due catene separate e sorgenti ideali identiche**:

- **Riferimento diretto:** generatore AM 455 kHz / modulazione 1 kHz al 50% / Rgen=50Ω → filtro IF455 L=1mH, ESR serie assunta 16,5Ω, 82pF + trimmer fissato a 30pF, C coupling 10pF in ingresso e in uscita → diode `DGENERIC` + inviluppo 47kΩ/1nF + accoppiamento 100nF + uscita AF 100kΩ.
- **Catena con buffer:** filtro IF455 identico ma separato → C1701 10nF → Q1701 a collettore comune, alimentazione di laboratorio 6V, bias 22kΩ/10kΩ, resistenza emettitore 2,2kΩ, C1702 10nF, R1704 100kΩ → stesso circuito di rivelazione AM con `DGENERIC`.

Lo script `03_Verifiche/V2.7/verify_if455_ksp10_am455_combined_native.py` invoca **ngspice nativo** con ingresso di 0,5V e 2,0V picco, acquisisce misure `.meas` sui segnali audio filtrati, sul nodo di uscita dei due filtri e sull'emettitore; verifica che il percorso diretto a 2V sia coerente con il modello **già integrato** in PR #94/#95. Il confronto non asserisce artificiosamente che il buffer debba migliorare il segnale. Se il modello mostra carico peggiorativo, questo va documentato e affrontato con una nuova proposta di adattamento.

## Modelli, limiti e criteri di qualifica

- BJT `QGEN` con beta=80, Is=1e-14, Vaf=100, Cje=5pF, Cjc=1pF; **NON** modello onsemi KSP10BU OEM o curva produttore verificata.
- Diodo `DGENERIC` della PR #94; **NON** macromodello OEM della 1N4148.
- Sorgente 50Ω ideale, rail 6V ideale senza impedenza/rumore, induttanza con ESR assunta e trimmer ideale; non rappresentano la vera radio.
- Non misurati noise figure, sensibilità µV, SINAD, SNR, distorsione d'inviluppo, banda di selettività, effetti AGC, stabilità RF/PVT o EMI.
- Pinout e footprints dei moduli standalone KiCad9 sono verificati separatamente; questo deck **non** è un nuovo master KiCad integrato e non dimostra né PCB routing né DRC.

**Decisione:** non integrare ancora i tre moduli nel master MAIN V2.6 e non approvare un MPN finale finché il confronto non sia riesaminato e l'interfaccia non abbia modelli rappresentativi, misure PVT, impedenza IF, carico del tank, analisi rumore e una revisione CAD gerarchica reale.

**Gate:** FAST/FULL/required sul commit finale; rapporto dei risultati numerici nativi solo dopo aver letto i log. Nessun waiver o job di sola facciata. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

## Esito misurato con ngspice nativo (dati al commit tecnico testato)

Run GitHub Actions [#43473046507](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43473046507), commit `c4daea8772a00aef9b48151acedd2ce72d1e350a`: FAST, FULL e required gate **3/3 PASS**; FULL con 111 comandi storici e `PASS_NGSPICE_IF455_KSP10_AM455_GENERIC_NONLINEAR_CASCADE_NOT_OEM_NO_FAB_NO_TX`.

| Generatore AM, picco | AFpp percorso diretto | AFpp con follower KSP10 candidato | Rapporto buffered/direct | Picco RF in uscita tank diretto | Picco RF tank caricato dal follower |
|---:|---:|---:|---:|---:|---:|
| 0,5 V | 0,023326606 V | 0,000741563 V | 0,031790 | 0,3938995 V | 0,09449585 V |
| 2,0 V | 0,214324050 V | 0,014614407 V | 0,068188 | 0,7549801 V | 0,3779901 V |

**Conclusione del modello:** la rete BJT d'ingresso (polarizzazione 22k/10k e parassiti generici) con C1701=10nF, collegata all'uscita C1604=10pF del tank, costituisce un carico RF significativo. Nel modello non è possibile giustificare l'aggiunta di Q1701 come miglioramento: la tensione audio con follower è circa **3,18%** del riferimento diretto a 0,5V e **6,82%** a 2V. L'ampiezza positiva RF sul nodo tank buffer è ~**24%** e ~**50%** del caso diretto. Il buffer candidato **non è approvato**, anche se la simulazione ha superato i test funzionali.

### Ripetibilità numerica: correggere l'interpretazione delle simulazioni precedenti

Il primo tentativo con passo `200 ns` ha fallito la verifica di coerenza con PR #94/#95: il percorso diretto a 2V produceva `0,16578788 Vpp` contro `0,17444891 Vpp` dal test storico. È stato ridotto il massimo passo a **50 ns** e implementata una seconda esecuzione indipendente del deck storico alla medesima risoluzione. A 2V, il vecchio deck ricalcolato dà `0,21445359 Vpp`; il nuovo deck diretto `0,21432405 Vpp`. Scostamento relativo **0,0604%**. Tuttavia il valore a 50ns è circa **22,9% maggiore** dell'originario 200ns: i numeri delle PR #94/#95/#96 **sono dipendenti dalla risoluzione temporale** e non sono risultati quantitativi convergenti. Questo controllo dimostra ripetibilità fra due netlist al passo 50ns, **non** una convergenza temporale assoluta; richiede ulteriore raffinamento (25ns/10ns) prima di dimensionamenti conclusivi.

Il primo gate fallito è stato mantenuto come evidenza e corretto senza disabilitare asserzioni fondamentali: ora il riferimento del deck storico è ricalcolato e confrontato allo stesso passo, con tolleranza del 3%. Non eseguire merge di proposte di buffer OEM o aggiornamenti CAD integrati sulla base di queste sole misure.
