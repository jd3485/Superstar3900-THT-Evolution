# Registro esecuzione V0.8

**Fase di studio iniziale:** ngspice [42841818820](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42841818820) **SUCCESS** (6 corse di driver analogico IDEALE con R/C). Vedi misure esatte `MISURE_DRIVER_V0.8.json`. Nessuna prova di fase del PLL, nessuna sorgente switching realmente modellata.

**Controlli regressivi:** 190 test Python dalle V0.1–V0.7 + nuova suite V0.8 da lanciare in PR e successivamente su main; registrare CI autentica dopo l'integrazione.

**NON ESEGUITI:** KiCad GUI ERC/DRC, modello reale MC34063 LM317 LM358, EMI/rumore fase, carichi reali e hardware; 0 PCB, 0 Gerber, 0 ordini. **NO FAB / NO TX**.

## Risultati GitHub reali verificati sul commit di merge

- [PR #4](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/4) **MERGED**, commit `cdd4941fb0ba3aab3edcefa0ff8cdcfd0b717d21`.
- [Software CI V0.1..V0.8](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42843501500): **SUCCESS, 226 test Python** (=12+24+32+34+34+21+33+36). Questi test controllano consistenza matematica/dati/testo, non l'elettronica reale.
- [ngspice storico VCO V0.6](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42843501265): **SUCCESS**, modello VCO limitato e non qualificato.
- [ngspice storico boost V0.7](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42843501213): **SUCCESS**, soltanto convertitore ideale/comportamentale, non MC34063 vero.
- [ngspice nuovo driver V0.8](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42843501144): **SUCCESS**, sei transienti del modello di amplificatore ideale con limitazione artificiale, non LM358 vero.
- **GATE NON ESEGUITI:** simulazione SPICE vendor IC e completo PLL, KiCad native ERC/DRC, EMC/rumore fase, hardware e fabbricazione. **NO FAB / NO TX**.

**Importante:** GitHub SUCCESS significa processo/test previsti terminati; non significa il circuito fisico funzionante.
