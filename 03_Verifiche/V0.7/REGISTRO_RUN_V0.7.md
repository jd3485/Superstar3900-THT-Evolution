# Registro prove V0.7

**Ngspice del modello comportamentale:** run [42827358481](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42827358481) SUCCESS, eseguiti 3 transienti a VIN 11 / 13,8 / 15,5V. Esercitati **interruttore, PWM e feedback ideali**, non la dinamica del reale MC34063 o LM317. Valori effettivi registrati nel dataset `MISURE_BOOST_V0.7.json`.

**CI regressione software V0.7:** attivare dopo la PR; previsto 157 test storici più nuovi test. Registrare esito reale dopo merge.

**NON ESEGUITI:** KiCad GUI/CLI ERC/DRC, bootstrap alimentatore reale, EMI/RF phase noise, test di laboratorio, PCBWay. **NO FAB / NO TX**.

## CI verificata su main dopo PR #3

- [Pull request #3](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/3) integrata con merge `b83710dd92cd77d80b2b237aa6a9d5a5e52cbdda`.
- [Regressioni software V0.1–V0.7](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42829647107): **SUCCESS**, 12+24+32+34+34+21+33 = **190 test**.
- [VCO V0.6 con ngspice](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42829647299): **SUCCESS** (esecuzione di un modello RF, non qualifica hardware).
- [Boost VTUNE V0.7 comportamentale](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42829647279): **SUCCESS** (3 transitori su switch/PWM ideali; il componente fisico MC34063 e l'LM317 NON sono stati simulati).
- Gli esiti verdi **non** rappresentano test hardware, KiCad ERC/DRC, assenza di spurie RF, lock PLL, prototipo o autorizzazione PCBWay/TX. **NO FAB / NO TX**.
