# Rapporto tecnico V0.9 — PDout tre stati, filtro PLL THT e primo CAD KiCad nativo

**Data 10 novembre 2026.** Revisionamento della parte RX del progetto autonomo Superstar 3900 THT Evolution. **NO FAB / NO TX**.

## 1. Fatti da datasheet verificati
- ML145151YP PDIP28: **PDout PIN 4** è un phase detector **three-state**. Quando il feedback fV anticipa fR produce impulsi negativi; quando ritarda, impulsi positivi; in coincidenza ideale è ad **alta impedenza**. **LD pin 28** fornisce un'indicazione di aggancio a impulsi; prima del desilenziamento servono alimentazioni e stabilità temporale. Fonte ufficiale della famiglia: [Lansdale PDF, pp.3–4 e 27–28](https://lansdale.com/datasheets/ML145151_ML145152_ML145155_ML145156_ML145157_ML145158_revA.pdf).
- Modello di guadagno PDout `Kphi=VDD/(4π)` con VDD 5V; questa è una **linearizzazione**, non misura di Kphi reale.
- In V0.8 il driver LM358N pin3 `PD_FILTER` riceveva una DC sintetica. In V0.9 si definisce **R901=22kΩ / C901=100nF THT** fra `PLL_PDOUT_3STATE` e `PD_FILTER`, come circuito candidato vero a due componenti. Un filtro puro RC comporta smorzamento limitato in alcuni segmenti VCO: non ancora scelto come compensazione finale.

## 2. Modellazione numerica small-signal
Fonte dei dati VCO: cinque simulazioni V0.6 (36,04773–39,19647MHz ai campioni 8..15V). Il rapporto equivalente LO/comparatore è `Ntotal≈LO/5kHz`, cioè *include già* U402 divide-by-two. Se si usasse per errore solo il valore N programmato ~3700 si sovrastimerebbe la frequenza naturale del loop.

Con `fPFD=10,24MHz/2048=5kHz`, `Kphi=5/(4π)≈0,398 V/rad`, `Gdriver≈4`, filtro R22k/C100n:
- RC=2,2ms, polo ≈72,34Hz, attenuazione sinusoidale ideale a 5kHz circa−36,8dB.
- Modello lineare fornisce f_n≈68–110Hz, ζ≈0,33–0,53. Sovraelongazione di step nel modello dell'ordine **14–33%**, variabile con il canale. La stima di assestamento lineare ~17,6ms **non è lock time** e non è valida per i salti di banda, limitazione uscita LM358, carico del VCO o transitori di potenza.
- Se l'uscita PDout restasse high-Z per15ms e un bias ipotetico20nA scaricasse C100nF, il modello calcola ~12mV di deriva su VTUNE per guadagno4, equivalente a un errore LO fino a **~9kHz** nel tratto più ripido. Un PLL veramente agganciato continua a correggere l'errore tramite impulsi: questa è una prova di sensibilità, **non** una misura di deriva della radio.

## 3. Circuito e CAD cumulativo
- **Schema nativo isolato**: `04_KiCad/V0.9/PLL_LOOP_RX_PARTIAL_V0.9.kicad_sch`, prodotto dal generatore deterministico `genera_pll_loop_v09.py`.
- Simbolo U803 LM358N PDIP8, U803A gain4 (R80330k/R80410k), U803B follower di parcheggio a massa, R90122k/C901100n di PDout→PD_FILTER, R805220Ω verso VTUNE, C803 di disaccoppiamento. **C805=100nF marcato DNI**, perché sul VCO esiste già C505=100nF su VTUNE: non raddoppiare involontariamente il carico.
- J901 PDout, J902 rail analogica +20V, J903 VTUNE, J904 segnale LD, tutti con GND. Simboli dei flag di alimentazione dichiarano esclusivamente che la rail arriva dall'esterno; **non dimostrano alcuna alimentazione reale**.
- Nessun U401 nel file, nessun PCB e nessun ERC del resto della radio. Integrazione multi-foglio e schermo RF ancora aperta.
- KiCad 9 è eseguito da GitHub Actions su Ubuntu con il PPA ufficiale. Al primo tentativo il file non si caricava a causa di `newline` non escaped in un testo, corretto prima di valutare ERC. Lo storico degli errori resta nella cronologia Actions; **lo stato del gate nativo si dichiara solo dopo un risultato effettivo della CI**.

## 4. Simulazioni fisiche
- `PLL_TRISTATE_HOLD_V0.9.cir` propone un test di **switch IDEALI** a tre stati, una prova UP/HOLD/DOWN da negativo e positivo finti, e corrente di fuga assunta. Questo non è un modello IC ML145151, né PLL closed-loop, né LM358 vendor. Le misure devono essere registrate dalla run ngspice effettiva.
- Firmware MCU/LD lock temporale non è ancora progettato a livello di logica fisica; la funzione Python di riferimento RX fail-closed rimane sola, non abilita TX.
- La sintesi di riferimenti PLL, VCO e booster RF resta *candidate*. Zero prove su PCB/prototipo e zero misure di fase, spurie, mixer, selettività, rumore o ROS.

## 5. Gate
**PASS software** soltanto dopo GitHub Actions regressioni V0.1..V0.9; **PASS ngspice** soltanto se effettivamente corre su 3 condizioni di perdita; **PASS ERC** soltanto su singolo sottoschema KiCad eseguito, non sull'intera radio. Rimangono FOPEN:
- loop compensato con Kphi e Kvco fisici, margini di fase e transitori largo segnale;
- progettazione fisica della rail20V e di U401/LM358 con modelli vendor;
- LD, powergood e mute hardware;
- fixture KiCad integrate, regole CAD e DRC layout;
- disponibilità THT legacy reale, EMC e prove hardware.

**NO FAB / NO TX**.

## Prossima V0.10
Validare un filtro type-II/lead-lag in un modello reale ed eseguire simulazioni con step frequenza, portare U401/U402 e VCO nello stesso progetto KiCad e verificare ERC multi-foglio, progettare hardmute da LD+powergood e calcolare la parte EMI del booster. Non rilasciare Gerber PCBWay finché il sottosistema completo e le prove non saranno qualificati.
