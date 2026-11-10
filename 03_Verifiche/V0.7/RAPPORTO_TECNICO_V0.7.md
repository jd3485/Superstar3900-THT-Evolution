# Rapporto tecnico V0.7 — Alimentatore VTUNE THT, boost astratto e margini aperti

**10/11/2026.** Revisione cumulativa della repository indipendente Superstar3900-THT-Evolution. Non sono stati fabbricati PCB o prototipi, non sono state eseguite prove di laboratorio. **NO FAB / NO TX.**

## 1. Nuovi sottosistemi circuitali
- **U701 ST MC34063ABN DIP-8** boost 13,8V nominali → circa 24V candidati, documentati tutti **8 pin** con rete candidata Rsc1Ω, L470µH THT, D701 1N5819 DO-41, feedback 21,8k/1,2k, Ct470pF da verificare, C47µF.
- **U702 TI LM317 TO-220** 24V → ~18,287V nominali con 240Ω/3,24kΩ; tutti **3 pin** e tab associata all'uscita (da isolare meccanicamente quando necessario). 10Ω/100µF isolano idealmente la rail analogica da componenti a frequenza elevata.
- File: `01_Specifiche/V0.7/ALIMENTAZIONE_VTUNE_THT_V0.7.md`, `04_KiCad/V0.7/VTUNE_ALIMENTAZIONE_PINNET_V0.7.csv`, `04_KiCad/V0.7/VTUNE_PASSIVI_NETS_V0.7.csv`, `07_Componenti/BOM_VTUNE_ALIMENTAZIONE_V0.7.csv`. **Sono matrici pin/net e BOM candidate, NON lo schematico .kicad_sch completo.**
- Questa alimentazione è per il **driver analogico PLL/VTUNE**; non alimenta VCO Q501/Q502, che resta alimentato da +5V RF protetti e filtrati separatamente.

## 2. Numeri di progetto (ipotesi, non misure)
- Vin protetta 11..15,5V, Vboost target24V, carico progettuale 15mA, fsw ipotetica40kHz, Vsat1V, Vf0,5V, L470µH, Rsc1Ω, limitazione tipica0,33A.
- A Vin11V rapporto tON/tOFF1,35, duty ~57,45%, ton14,36µs, salto induttore ~0,3056A. Con soglia tipica0,33A margine appena **24,4mA**, prima di considerare corrente iniziale CCM e tolleranze: **non approvare L/Rsc**.
- Divider nominale booster `Vref=1,25V`, Rtop21,8k/Rbottom1,2k → **23,9583V**. Con ±2% Vref e ±1% resistenze → **23,0385..24,9054V** teorici, non worst case di hardware.
- LM317 con Vref1,25V e Iadj50µA → **18,287V**; gamma ipotetica Vref1,2..1,3V, Iadj0..100µA → **17,4..19,174V**. Il peggiore headroom combinato (min boost/max LDO) ~3,86V, contro dropout assunto3V, **margine non validato**.
- R71210Ω/C712100µF: RC ideale primo ordine attenuazione circa −48,0dB a 40kHz, caduta0,15V se assorbe15mA. **Il rumore residuo del convertitore reale / IMD è ignoto.**

## 3. Prima simulazione elettrica, perimetro onesto

`03_Verifiche/V0.7/BOOST_THT_BEHAVIORAL_V0.7.cir` contiene **interruttore SPICE ideale, oscillatore PWM ideale, regolazione ideale, diodo semplificato, L/C**. Questo **NON simula il circuito interno del vero MC34063**, non contiene LM317 reale, non dimostra la regolazione in tutti i punti di carico e non permette di concludere nulla su EMI/RF/rumore fase.

Prima run ngspice reale [42827358481](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42827358481), alimentazione ideale 11/13,8/15,5V, carico resistivo circa15mA nominali:

| Vin(V) | boost medio(V) | minimo(V) | massimo(V) |
|---:|---:|---:|---:|
| 11,0 | 23,9967 | 23,9799 | 24,0152 |
| 13,8 | 24,0096 | 23,9799 | 24,0466 |
| 15,5 | 24,0221 | 23,9800 | 24,0775 |

I valori sono **solo proprietà del modello comportamentale**. I risultati non sono alimentazione certificata e non provano pin/circuito di U701, U702. Registrati in `MISURE_BOOST_V0.7.json`.

## 4. Problema ancora aperto del driver VTUNE

Anche ammettendo una linea LM317 a18V, **non si è ancora progettato** un driver THT che raggiunga 15V con riferimento/PLL e rumore adeguati. `LM358N` PDIP8 resta candidato da valutare, non connesso. Nell'ipotesi di uscita high-side Vreg−2V e Vreg17,4V, cadutaRC0,15V → limite ~15,25V, solo 0,25V margine. Con Vreg−3V → **14,25V**, quindi FAIL del requisito15V. Soluzione opamp adeguato, rail/regolatore diverso o riprogettazione LC saranno oggetto della V0.8.

L'uscita fase U401 e `PDOUT` e i requisiti Kphi/Kvco, phase margin, lock e mute HW non sono ancora chiusi. La scelta di boost switching può produrre spurie e interferenze entro la radio e va filtrata/schermata e misurata. Non collegare l'uscita del booster direttamente a VTUNE.

## 5. Verifiche e limiti
- V0.1–V0.6: suite storiche preservate. Nuova suite statica V0.7 e workflow ngspice dedicato. Esiti CI da registrare **dopo il commit**.
- NON ESEGUITI: vera simulazione del MC34063+LM317 con modelli fisici, circuito power-good, Kphase/Kvco PLL, schemi CAD completi, KiCad ERC/DRC, PCB RF, test EMI e hardware.
- Lo stato gate resta **NO FAB / NO TX**.

## Prossimo V0.8
Dimensionare e validare alimentatore reale THT/rumore RF, compensazioni e protezioni, uscita analogica VTUNE e phase detector; in parallelo qualificare disponibilità BB204G o equivalente THT. Solo poi portare le reti della supply e PLL in KiCad completo, con ERC e DRC prima della fabbricazione.

## Datasheet ufficiali
- ST MC34063ABN (DIP8, Active): https://www.st.com/en/power-management/mc34063ab.html
- TI MC34063A pin e applicazioni: https://www.ti.com/product/MC34063A
- TI LM317 TO-220: https://www.ti.com/product/LM317
- ST 1N5819 DO-41: https://www.st.com/resource/en/datasheet/1n5819.pdf

## CI verificata su main dopo PR #3

- [Pull request #3](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/3) integrata con merge `b83710dd92cd77d80b2b237aa6a9d5a5e52cbdda`.
- [Regressioni software V0.1–V0.7](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42829647107): **SUCCESS**, 12+24+32+34+34+21+33 = **190 test**.
- [VCO V0.6 con ngspice](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42829647299): **SUCCESS** (esecuzione di un modello RF, non qualifica hardware).
- [Boost VTUNE V0.7 comportamentale](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42829647279): **SUCCESS** (3 transitori su switch/PWM ideali; il componente fisico MC34063 e l'LM317 NON sono stati simulati).
- Gli esiti verdi **non** rappresentano test hardware, KiCad ERC/DRC, assenza di spurie RF, lock PLL, prototipo o autorizzazione PCBWay/TX. **NO FAB / NO TX**.
