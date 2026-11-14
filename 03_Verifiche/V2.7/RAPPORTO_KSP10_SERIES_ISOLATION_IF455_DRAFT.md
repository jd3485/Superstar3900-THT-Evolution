# V2.7 — Isolamento resistivo tank IF455 → base KSP10BU (SPICE only)

**14 novembre 2026 — candidato non qualificato.**

Le prove del [PR #158](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/158) hanno mostrato che variare CIN 10pF…10nF non risolve contemporaneamente pilotaggio e carico del tank. Un primo passo controllato è verificare che cosa avviene aggiungendo una resistenza serie **senza modificare la capacità originale di 10nF**, in un deck esclusivamente di prova. La resistenza dissipativa può isolare il tank ma attenua il segnale alla base e non è un adattamento di rumore, potenza né filtro IF.

## Nuova prova nativa

`03_Verifiche/V2.7/verify_if455_ksp10_series_isolation_native.py` esporta le vere netlist KiCad9 dello standalone KSP10 e del tank IF455, preservando Q1701 B1/E2/C3 e i nodi di connessione. Riprende esattamente il banco ngspice comune [PR #156](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/156): sorgente Thevenin **ipotetica 50Ω**, tank con L1mH, loss16.5Ω **non qualificata in RF**, alimentazione di banco 6V, CIN10nF, COUT10nF e caricamento resistivo fittizio nominale dell'ingresso ceramico. Varia **soltanto** un resistore serie SPICE tra il tank e CIN: `Riso=0 / 1000 / 4700 / 10000 / 47000Ω` × beta BJT **generic** 40/80/160 × carico resistivo fittizio 1500/2000Ω = **30 casi ngspice AC nativi** a 455kHz.

Ogni caso registra tensione sul tank, ingresso base e uscita del KSP10; confronta tensione del tank e uscita rispetto alla stessa configurazione con Riso=0 e ancora i risultati verificati PR156 beta80, carico2k, CIN10nF (tank `0.124579814`, output `0.119093670` V/V). Non assume monotonicità e non nasconde eventuali peggioramenti del livello.

**Criterio di utilizzo:** i dati possono mostrare la penalizzazione dell'accoppiamento resistivo, ma **non** approvano alcun valore Riso. Un resistore serie può aumentare il rumore termico e alterare la banda e il Q; nessuna prova della figura di rumore, perdita di potenza, selettività ±canale, linearità, IMD o reiezione dei prodotti del mixer è inclusa. Il carico è solo un resistore, non il filtro ceramico reale `Z(f)`. Nessun macromodello OEM del KSP10 o LO-driven SBL-1+ è disponibile per questo banco.

Progetto master V2.6 e standalone KiCad invariati; nessun resistore serie aggiunto al circuito fisico. [PR #123](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/123) e [PR #143](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/143) restano draft per qualifica meccanica e assegnazione footprint. [Issue #141](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/141) resta aperta per specifiche RX AM/FM/USB/LSB/CW.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
