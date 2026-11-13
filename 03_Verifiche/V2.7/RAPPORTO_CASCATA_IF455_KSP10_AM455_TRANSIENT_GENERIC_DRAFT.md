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
