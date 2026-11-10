# V0.9 — U401 ML145151 PDout a tre stati → filtro loop → driver VTUNE THT

**11/2026.** Revisione cumulativa RX-only. La radio completa e le PCB restano non autorizzate. Tutte le simulazioni della V0.9 sono di sottosistemi **ideali/small-signal**, non hardware e non PLL chiuso.

## 1. Correzione fondamentale dall'origine dati

Datasheet ML145151 originale [Lansdale, Issue A, pagine 2–4 e 27–28](https://lansdale.com/datasheets/ML145151_ML145152_ML145155_ML145156_ML145157_ML145158_revA.pdf):
- U401 pin **4 = PDout**, phase detector A, uscita **tre stati**: impulsi NEGATIVI quando fV > fR/anticipa, POSITIVI quando fV < fR/ritarda, **alta impedenza** in aggancio ideale. Non è un'uscita DC analogica da connettere direttamente al positivo LM358.
- U401 pin **28 = LD**: livello alto sostanzialmente in aggancio, impulsi bassi fuori lock; occorre qualificazione temporale e alimentazioni buone prima di desilenziamento.
- Datasheet per PDout: **Kphi = VDD/(4π)** V/rad in modello medio. Lo schema suggerito è un filtro RC passivo oppure uno attivo con opamp.
- Il limite di controllo PLL è anche R=2048 con Fref10,24MHz→fPFD **5kHz**, prescaler /2 tra LO1 e fin; ratio di controreazione totale verso LO1 ~ **2N** (≈ 7262–7800).

## 2. Prima interfaccia THT progettata (NON già compensata)

```text
U401 PDout (pin4, ~0..5V o HIGH-Z) -- R901 22kΩ THT -- PD_FILTER
                                                       |
                                                     C901 100nF
                                                       |
                                                      GND
PD_FILTER --> U803 LM358N PDIP8 pin3 noninvertente, gain4 stimato
               R803 30kΩ R804 10kΩ --> OPA_OUT_A
                      |
                    R805 220Ω --> VTUNE_RAIL --> VCO D501
                                                C505 100nF nel VCO
+20V analogica filtrata VANA20_FILT -> U803 pin8, GND pin4.
U803 B: pin5=GND, pin6/7 uniti come follower inutilizzato.
U401 LD (pin28) -> J904 / PLL_LD_RAW; **NESSUN circuito di hard-mute ancora disegnato**.
```

**Decisione:** C805=100nF della V0.8 viene posta **DNI** nel sottoschema KiCad V0.9: il VCO candidata B ha già C505=100nF su VTUNE_RAIL; due capacità in parallelo o layout improprio altererebbero la dinamica del loop. Andrà verificata la posizione fisica e l'impedenza di alimentazione di entrambi i sistemi.

**R901=22k e C901=100n sono soltanto una PROPOSTA** che corrisponde a τ=2,2ms, polo ≈72,34Hz e attenuazione ideale verso 5kHz ≈−36,8dB in filtro RC linearizzato **non caricata**. Non è compensazione definitiva. Le perdite del pin PDout high-Z, corrente bias opamp, swing reale e clock di riferimento non sono ancora verificate su dispositivi.

## 3. Analisi small-signal di stabilità, non qualificazione di un PLL fisico

Modello `02_Piano_Frequenze/V0.9/pll_loop_model_v09.py`:
- frequenze VCO realmente estratte dal file dati **di simulazione** V0.6, 5 punti, quindi pendenze 0,310–0,760MHz/V;
- Kphi *nominale* =5/(4π)≈0,398V/rad; guadagno ipotetico non invertente LM358 ×4;
- rapporto di divisione totale **Ntotal=LO/5000** (include U402 /2 e il N programmato ML145151), NON semplicemente N del chip da~3700;
- filtro RC passivo `F(s)=1/(1+sRC)`. Per perturbazioni piccole, `omega_n^2=Kphi*(2π*4*Kvco)/(Ntotal*R*C)`, `zeta=1/(2*omega_n*R*C)`, coerentemente con le approssimazioni di datasheet.

| Segmento VTUNE | Kvco da 5 punti V0.6 | fn lineare | zeta lineare |
|---|---:|---:|---:|
| 8–9 V | ~760kHz/V | ~109,6Hz | ~0,330 |
| 9–10 V | ~582kHz/V | ~95,0Hz | ~0,381 |
| 10–12 V | ~437kHz/V | ~81,6Hz | ~0,444 |
| 12–15 V | ~311kHz/V | ~68,0Hz | ~0,532 |

**Interpretazione:** ammortizzamento nominale modesto. Transitori/sovraelongazione potenzialmente elevati; oltre a saturazione driver, instabilità del PD e dispersioni non modellate. Una previsione di tempo di assestamento lineare di ~18ms **non** è una previsione di tempo di lock vero, né vale per i cambi canali larghi. Non approvare R/C definitivamente.

**Stress high-impedance:** se PDout fosse in HIGH-Z per 15ms senza nuovi impulsi correttivi, una *corrente di ingresso/leakage assunta* 20nA su C901100nF darebbe ΔVfilter ≈3mV → ΔVTUNE ≈12mV → ΔLO fino a circa9,1kHz nel tratto più sensibile. Non è la deriva effettiva della radio (un PLL agganciato genera ulteriori impulsi), ma evidenzia il bisogno di leakage/bias reali bassi e controllo continuativo. Nel modello SPICE ideale gli impulsi +/− e l'hold sono sollecitati, senza fV reale.

## 4. Primo sottoschema KiCad nativo — ambito strettamente limitato

File: `04_KiCad/V0.9/PLL_LOOP_RX_PARTIAL_V0.9.kicad_sch`, generato in modo deterministico da `04_KiCad/V0.9/genera_pll_loop_v09.py`. Contiene U803 DIP8 con tutti gli 8 pin visibili, R901/C901, R803/R804/R805, C805 (DNI), C803 decoupling, quattro connettori THT d'interfaccia, due flag esterni di alimentazione. Simboli personalizzati sono **incorporati** nel file, così non richiedono libreria esterna per aprirsi; footprint standard THT proposti.

I flag esterni **non dimostrano** che VANA20_FILT sia davvero presente né che la scheda sia sicura: sono soltanto dichiarazioni di alimentazione a monte per l'ERC sul sottoschema parziale. J901 riceve PDout e GND, J902 +20V e GND, J903 VTUNE e GND, J904 LD e GND; nessuno di questi connettori è approvato come connettore definitivo della PCB finale.

**Cosa manca dal foglio:** U401/U402 in CAD integrato, sintesi/clock digitale, tutti i 270 canali, alimentatore boost/LM317 vero, VCO Q501/502 e mixer, VANA20 realmente filtrata, monitor LD/hard-mute, layout RF, distanze di isolamento, DRC.

Eseguire `kicad-cli sch erc --exit-code-violations` con KiCad >=9 in GitHub Actions. Eventuale ERC verde certifica **solo** coerenza topologica del singolo sottoschema, non la radio e non il circuito del PLL chiuso.

## 5. Prossima V0.10
- Progettare un vero filtro PLL con guadagno/impedenza phase detector e dispositivo opamp reale, misurare ESR, clock jitter, source drift e tempi lock su step canale.
- Implementare LD + comparatori powergood + hard mute con componenti THT e modello temporale, fermando TX fisicamente.
- Integrare la sezione VCO e U401/U402 con questo sottoschema in CAD, poi ERC nativo dell'insieme e revisione meccanica/PCB. Non costruire PCBWay finché i gate fabbricazione restano aperti.

**NO FAB / NO TX.**
