# V2.7 — regolazione trimmer IF455 dipendente dal carico: 36 casi AC nativi

**13 novembre 2026. Studio parametrico di rete passiva da banco, non filtro OEM certificato / non ricevitore.**

## Motivazione e dato di partenza

[PR #110](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/110) ha calcolato la vera Z complessa e il trasferimento AC del solo filtro IF455 V2.7 con quattro carichi. Ctrim fissato a 30pF produce nel modello un picco a **454,75kHz** con riferimento 100k, **440,25kHz** con shunt 10k, **439,0kHz** con shunt 1k, **450,25kHz** con surrogato gate JFET. Una perdita di trasferimento e spostamento di risonanza non possono essere compensati automaticamente solo chiamando un circuito 'buffer alta Z'.

## Test riproducibile

Script `03_Verifiche/V2.7/verify_if455_loaded_trimmer_retune_native.py`: **36 sweep AC ngspice indipendenti** (quattro carichi × 9 posizioni nominali trimmer EW GKG50015: 10,15,20,25,30,35,40,45,50pF). Frequenze **350–550kHz**, 1001 campioni, passo 200Hz. Configurazione **identica** al circuito KiCad9 IF455 standalone PR #110: L1mH, Rcoil16.5Ω *assunta*, C82p, 10p ingresso/uscita, R damping47k, R di riferimento 100k, sorgente ideale 50Ω.

Carichi: solo R100k; aggiunti 10k o 1k shunt; equivalente **passivo e non OEM** gate JFET con 10p serie, 1MΩ e 7p parassiti. La misura `|H(455k)|` viene effettuata esattamente a 455000 Hz, oltre a fpeak e trasferimento massimo di ogni assetto.

Criteri di regressione verificati: riproduzione entro 1% della risposta `|H(455k)|` dei quattro casi PR #110 a 30p, frequenza di picco 30p entro 350Hz, e direzione fisica di fpeak al crescere di Ctrim. Il codice riporta per ogni carico sia l'assetto che **massimizza |H(455k)|** sui nove passi sia quello il cui picco è più vicino a 455kHz. Non presuppone che i due criteri coincidano o che il vincitore 1k sia fabbricabile. Questa è la prima evidenza quantitativa direttamente legata al problema **accordo IF dopo scelta del carico**.

## Blocchi tecnici per l'approvazione

- Nessuna quantificazione OEM dell'ESR RF, della capacità effettiva della GKG50015, del Q reale o delle capacità parassite di KiCad, PCB e avvolgimento: la DCR 16.5Ω non equivale alla Rcoil a 455kHz.
- L'ottimo su soli 9 passi è uno screening nominale, non la taratura continua garantita su temperatura, tolleranze o tempi. Verificare capacità a reale rotazione, tolleranze, Q a 455kHz, auto-risonanza e precisione dei footprint.
- Recuperare la posizione di frequenza non implica recuperare `|H|`, e `|H|` non implica buono SNR/THD, sensibilità d'antenna, selettività AM/FM/SSB o AGC.
- Nessun master V2.6 modificato, nessuna vera PCB/DRC, nessuna interfaccia finale eletta, nessun transceiver funzionante. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
