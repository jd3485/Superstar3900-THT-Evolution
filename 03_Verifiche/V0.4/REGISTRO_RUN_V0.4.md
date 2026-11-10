# Registro esecuzione V0.4

Il commit di V0.4 abilita il workflow GitHub Actions per **12 V0.1 + 24 V0.2 + 32 V0.3 + 34 V0.4 = 102** test statici/aritmetici.

**PRIMA dell'esecuzione sul commit:** stato `NOT_RUN` della run V0.4. Aggiornare questo registro con URL, SHA, esito reale e numero di test verificati.

Le categorie `KiCad GUI / KiCad CLI ERC / DRC`, `SPICE oscillatore PLL`, `EM / RF / prova hardware`, `PCBWay DFM` sono **NOT_RUN** nella V0.4. Schematic S-expression presente, ma non aperto/validato in applicazione KiCad. Nessun modello numerico autorizza TX.

## Esecuzione GitHub Actions effettivamente verificata

- **Run [42810567923](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42810567923)**, commit testato `68c8975d44a447f595269bd0eb3718602ffe2f68`, branch `main`.
- Job `static-regression`: **SUCCESS**; le suite V0.1 (12), V0.2 (24), V0.3 (32) e V0.4 (34) sono state eseguite con **successo**, per **102 test software** complessivi.
- Le verifiche riguardano solo dati/funzioni Python e struttura del file S-expression KiCad. **NON ESEGUITI**: apertura in KiCad GUI, ERC/DRC reali, SPICE, hardware, EMI, produzione o TX.
- Nella prima run V0.4 era fallito un test storico per il riferimento alla configurazione corrente anziché allo snapshot storico: ora corretto con `CONFIGURAZIONE_V0.2.json`; la regressione V0.3 è riferita a `CONFIGURAZIONE_V0.3.json`. La run definitiva è interamente verde.
