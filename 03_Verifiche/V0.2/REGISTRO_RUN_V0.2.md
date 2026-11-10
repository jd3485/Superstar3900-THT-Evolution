# V0.2 — Registro verifiche pubblicate
V0.1: 12/12 PASS nel checkout locale, software statico.
V0.2: 24/24 PASS nel checkout locale, aritmetica e coerenza file.
GitHub Actions `.github/workflows/verifica_v02.yml` predispone l'esecuzione sul checkout completo a ogni push su main e pull request. **Non dichiarare una run PASS prima di averne verificato l'esito su GitHub.**
KiCad ERC/DRC, circuiti/SPICE, EMI, termica, misure hardware: NON ESEGUITI.
TX e fabbricazione: NON AUTORIZZATE.


## GitHub Actions verificata dopo integrazione
- **Run ID**: [42803142196](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42803142196)
- **Commit testato**: `7da67271bc9c33416b695053c4e9d9ed1f1f60b2` (V0.2).
- **Job `static-regression`**: `success`; verificati i passi `Baseline V0.1 structural tests` e `V0.2 channel plan and candidate PLL arithmetic tests`, entrambi `success`.
- Si tratta **solo** di test Python riproducibili. KiCad, SPICE, hardware e TX rimangono **NON ESEGUITI**.
