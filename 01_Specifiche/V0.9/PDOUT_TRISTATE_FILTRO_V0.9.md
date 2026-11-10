# V0.9 — Phase detector ML145151 PDout a tre stati e filtro d'anello THT

**Revisione progettuale RX, 10 novembre 2026.** Questo è un sottoinsieme del PLL tradizionale, non una radio fabbricabile e non un PLL chiuso. Nessun TX.

## Correzione concettuale prioritaria

Il prodotto storico **Lansdale ML145151YP** usa il **pin 4 PDout** come uscita del *phase detector A a tre stati*. La documentazione specifica:
- `fV > fR` (segnale VCO diviso in anticipo/frequenza maggiore): impulsi **negativi** verso GND;
- `fV < fR`: impulsi **positivi** verso VDD PLL;
- coincidenza di frequenza e fase: uscita **alta impedenza**, non una tensione analogica di riferimento stabile.

L'uscita `LD` pin28 è indicatore di lock, **non un consenso alla TX**. I segnali `phiR` pin8 e `phiV` pin9 sono un'altra coppia di uscite: non confonderli con pin4. Fonte primaria: https://lansdale.com/datasheets/ML145151_ML145152_ML145155_ML145156_ML145157_ML145158_revA.pdf e archivio `04_KiCad/V0.3/PLL_U401_U402_PINNET_V0.3.csv`.

**Conseguenza:** il `PD_FILTER` analogico 2–3,75V del driver V0.8 deve essere **generato da un filtro RC di accumulo/integrazione della PDout**, non può essere una tensione imposta dal software. I vecchi calcoli di filtraggio V0.4–V0.5 non sono verifiche dell'anello completo.

## Circuito di prova candidato (tutto THT)

```
U401 pin4 PLL_PD_RAW (impulsi tri-state 0 / +5V / Hi-Z)
      |
      R901 10 kΩ assiale (alternativa di studio 47 kΩ)
      |
      +----- PD_FILTER ---- U803 LM358N pin3 (+IN)
      |
      C901 1 µF film THT a GND
      |
      R902 =100 MΩ SOLO PER IL MODELLO NUMERICO DELLA PERDITA;
             NON è un componente definito da acquistare.
```

Il nodo è governato da uscite PFD digitali e il valore mantiene il livello quando U401 entra in Hi-Z, **finché la corrente di bias reale LM358, il leakage C901, la resistenza del PCB e tutte le perdite lo consentono**. Le sole due opzioni da testare R90110k e47k non sono filtro approvato: il primo reagisce più in fretta, il secondo trattiene più il ripple ma risponde più lentamente. C901 film1µF THT a bassa perdita è ipotesi; il valore definitivo/ingombro e la capacità d'accoppiamento sul PLL richiedono layout e misure.

`04_KiCad/V0.9/PLL_PDOUT_FILTRI_CANDIDATI_V0.9.csv` contiene la nuova matrice net pin/funzione; **non è ancora schema KiCad nativo**.

## Due alternative di sola analisi lineare

- `10k/1µF`: `tau=10ms`, taglio teorico 15,915Hz, attenuazione ideale dei 5kHz a circa **−49,94dB**.
- `47k/1µF`: `tau=47ms`, taglio teorico 3,386Hz, attenuazione ideale dei 5kHz a circa **−63,39dB**.

Sono reiezioni `R-C` di un singolo polo **a sorgente ideale a impedenza bassa**; la PDout del ML145151 è tri-state ed ha impedenza durante Hi-Z, il VCO/LM358 sono non lineari e la compensazione PLL può esigere uno zero. **Non dedurre stabilità di anello e lock da queste attenuazioni.**

Dalle 5 frequenze VCO V0.6 campionate, sensibilità media `(39,19647−36,04773)/(15−8) ≈ 0,44982MHz/V` sulla VTUNE. Con stadio LM358 guadagno ideale4, `~1,799MHz` per volt sull'ingresso PD_FILTER **solo come pendenza media sui campioni**. La derivata Kvco nel range e a temperatura è non nota. Per una vera analisi PLL occorrono (K_\phi) effettivo della PDout, (K_\mathrm{VCO}) differenziale, divisore N e doppio prescaler, margine di fase/peaking, stabilità su tutti 270 canali, tempi di riaggancio, spur a5kHz e rumore di fase SSB. Nessuno dei quali è validato.

## Simulazioni ngspice eseguite V0.9

`03_Verifiche/V0.9/PDOUT_TRISTATE_SURROGATE_V0.9.cir` implementa una **sorgente sostitutiva a due interruttori ideali**, uno verso+5V e uno versoGND, entrambi aperti per stato Hi-Z, impulsi di1ms ogni10ms. R901/C901 **sono componenti passivi realmente modellati**; R902100Meg è placeholder di perdita. La simulazione inizializza artificialmente PD_FILTER a2,5V per testare la conservazione della carica, non il power-on o l'aggancio.

6 condizioni (UP/DOWN/HOLD × 10k/47k) eseguite in vera simulazione ngspice; registrate con `run_tristate_v09.py`. La suite verifica matematicamente il verso della regolazione e la caduta su Hi-Z. Non simula i segnali di U401, frequenza realistica dei fronti 5kHz, periodo PLL, saturazione RF, errore fase, LM358 reale, lock o risposta nel sistema chiuso. Nessuna evidenza di stabilità.

## Nuovi rischi da risolvere
1. `100 MΩ` di perdita fittizia crea uno stato di mantenimento apparentemente perfetto; sul PCB reale leakage e bias del LM358 possono essere molto maggiori; una corrente di bias di20nA su1µF modifica V di0,02V al secondo, **rilevante per precisione a37MHz**.
2. Pin4 PDout ha uscite push/pull tri-state; la sua corrente di pilotaggio e impedenza devono rispettare R901 e condensatore reale. VDD=+5V PLL, la tensione del condensatore e dell'LM358 deve restare nel common-mode e rail vero.
3. L'alta impedenza in lock non è un 'campione e tieni' ideale: gli errori richiedono correzioni e il loop può oscillare, driftare o avere spurie.
4. `LD` richiede deglitch e valutazione riferimenti/alimentazioni prima di liberare RX mute; nessun TX.
5. `R901/C901` produce un primo polo, non necessariamente un filtro PLL stabile: `Kphi`, Kvco, fase, zero e capture non simulati.
6. **Non promuovere U401 a BOM di acquisto**: ML145151YP rimane candidato storico con fornitura non qualificata.

## Prossimo sviluppo V1.0
Progettare filtro di compensazione reale usando modello fisico `PDout`/PLL dinamico e misurare capture/hold/spurie; descrivere interblocco POWER_GOOD+LD+retune sul circuito THT; realizzare netlist KiCad completa del sottoblocco e lanciare ERC nativo, poi DRC su PCB RF separata dalla supply switching. Le funzioni RX, manual tuner e condizioni di produzione restano invariate.

**GATE: NO FAB / NO TX.**
