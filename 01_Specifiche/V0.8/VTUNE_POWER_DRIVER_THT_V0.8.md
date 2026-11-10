# V0.8 — boost 27 V, LM317 20 V e driver analogico VTUNE in tecnologia THT

**Tipo:** progettazione candidata, conti con limiti dichiarati e simulazione SPICE **solo comportamentale** del driver. NON è un PLL agganciato, né un progetto fabbricabile.

## 1. Perché cambiamo V0.7

Il VCO candidata B V0.6 usa nel modello VTUNE 8–15 V con LO 36,31–39 MHz. La sorgente V0.7 boost24/LM31718,3V mostrava due problemi: sense R701=1Ω vicino alla soglia minima del MC34063, e margine d'uscita non garantito per il LM358N.

ST pubblica la soglia MC34063 di limitazione di corrente **250mV minimo, 300mV tipico, 350mV max** e il timing oscillator per C_T=1nF a 25°C **24–42kHz, tipico33kHz**. Di conseguenza **C_T=470pF non significa automaticamente 40kHz**. Nota di dimensionamento TI: https://www.ti.com/product/MC34063A; documento ST https://www.st.com/resource/en/datasheet/mc34063ab.pdf .

### Nuova soluzione scelta per la sola fase di studio
- U701 MC34063ABN PDIP8: target **27V** da rail protetta **11–15,5V**, design Iboost **25mA** (include la corrente minima LM317 e carichi previsti; carichi worst-case da provare).
- R701 **0,47Ω THT 0,5W** invece di1Ω, L701 **470µH THT** candidato **Bourns RLB0914-471KL** (Irms 0,56A, Isat 1A *tipici*, DCR fino1,3Ω, non schermato). Non ordinato; il margine reale dipende da CCM, ripple e temperatura.
- D701 Schottky **Vishay SB160-E3/54 60V 1A DO-41** invece del 1N5819 40V: più spazio nominale rispetto a 27V output e spike, **non certificato** sul layout.
- R702 24,7k / R7031,2k → **VBOOST nominale 26,979V** con Vref tipico1,25V. ±2% Vref e ±1% resistori → **25,94–28,05V** nel modello *illustrativo*, non limiti assoluti del datasheet e non regolazione reale.
- U702 LM317 TO-220 con R710240Ω R7113,57kΩ → **20,02225V** nominali (Iadj50µA), gamma assunta Vref1,2..1,3V Iadj0..100µA → **19,05–20,9945V**.
- **R713 2,4kΩ 0,5W** VREG20_RAW→GND aggiunge un carico minimo. A Vreg19,05V scarica7,94mA; la resistenza programmazione R710 vale ≥5mA in condizioni analoghe, quindi corrente totale minimo di studio **12,94mA** contro 10mA richiesta massima di LM317 in una configurazione conservativa. Potenza massima nel modello 20,9945²/2400≈**0,184W**; resistenza0,5W con verifica temperatura/derating prima del PCB. TI raccomanda garantire minimo carico quando necessario: https://www.ti.com/product/LM317
- R71210Ω C712100µF da VREG20_RAW a VANA20_FILT. A Iload=25mA caduta di0,25V (caso di studio conservativo, carico reale a valle inferiore o variabile). L'attenuazione ideale a40kHz è ~−48dB SOLO a impedenza infinita/ESR nullo; nel circuito reale non è dimostrata.

### Corrente / ciclo con parametri assunti

A VIN11V, Vboost27V, Vf0,5V, Vsat1V e f_switch40kHz *assunta*: tON/tOFF=(27,5−11)/(11−1)=1,65; duty 62,264%; tON=15,566µs; incremento di corrente 470µH ~0,3312A. Soglia **minima** con Rsc0,47Ω: 0,25/0,47≈0,532A: differenza da `deltaI` ≈**0,201A**. **Non è garanzia di margine a Ipeak in CCM**, include ipotesi di risalita da zero e ignora induttanza -10%, perdite e transitori. Vin15,5V ha altra corrente da controllare. Sostituire la frequenza ideale con range reale (Ct / Icharge / temperature) nel prossimo dimensionamento. Il design non è autorizzato alla fabbricazione.

## 2. Driver LM358N in DIP8 per un primo contratto dei segnali

U803 **LM358N** (2 amplificatori nel package PDIP8), usiamo solo amplificatore A per un buffer a guadagno fisso non invertente:
- pin1 `OPA_OUT_A`, pin2 `OPA_FB_A`, pin3 `PD_FILTER`, pin4 GND, pin8 VANA20_FILT;
- R80330k tra pin1 e pin2, R80410k pin2→GND; **gain ideale 4**.
- R805220Ω pin1→VTUNE_RAIL, C805100nF VTUNE_RAIL→GND, interfaccia con varicap e filtro RF. **C805 potrebbe duplicare C505 VCO: non collegare entrambi senza analisi del loop**.
- canale B inutilizzato: pin5=GND, pin6=pin7 (follower a zero), nessun output verso il PLL.
- `PD_FILTER` **non è PDout direttamente**: occorrono phase-detector output reale U401, compensazione PLL, mute e clamp/limiti da progettare. Alimentazione VANA20_FILT non esiste ancora come circuito fisico; GND RF separazione/layout non definito.
- Input necessari per modello VTUNE 8,10,15V = **2,00 / 2,50 / 3,75V** su PD_FILTER. L'uscita reale dipende da Vhigh, tolleranze, swing, slew, capacità vista e phase margin.
- La prima stima VANA20 minima19,05V, caduta RC 0,25V e uscita headroom **assunta3V** produce massimo ~15,80V, quindi un possibile margine 0,8V su15V. Se headroom effettivo fosse 4V o più, il margine si riduce o sparisce. Il datasheet LM358 mostra swing verso V+ limitato, non rail-to-rail; non promuovere il solo modello a garanzia.

`04_KiCad/V0.8/VTUNE_PINNET_V0.8.csv` contiene **19/19 pin** dei tre IC; `04_KiCad/V0.8/VTUNE_RETI_PASSIVE_V0.8.csv` nuove reti a due terminali; componenti scelti o ipotizzati in `07_Componenti/BOM_VTUNE_V0.8.csv`. Sono reti candidate documentali, non schematico KiCad integrato né PCB.

## 3. Simulazione vera di un modello LIMITATO

`03_Verifiche/V0.8/VTUNE_DRIVER_BEHAVIORAL_V0.8.cir`: ngspice esegue una sorgente comportamentale con saturazione `rail - headroom`, guadagno DC elevato, feedback resistivo 30k/10k, R220/C100n del nodo VTUNE. Sono vere transienti elettriche **del modello semplificato**, non un macromodello fisico del LM358, né prove del loop PLL.

Tre valori PD_FILTER 2/2,5/3,75V a rail19,05V e headroom3V danno circa 8/10/15V di VTUNE. Caso perturbato headroom4,3V raggiunge solo ~14,75V (**FAIL MARGINE**). Nessun phase-margin, tuning RF, EMI o hardware qualificato.

## 4. Bloccanti ora più chiari
1. Oscillatore MC34063 vero non ancora simulato con macro-modello del costruttore e timing worst-case; L701 e sense reali non qualificati né EMC.
2. LM317 reale con precarico, protezioni LM317 e temperatura ancora non testato; rail ~20V ipotesi su boost~27V.
3. Driver LM358N ha swing/rumore reali non simulati, riferimenti U401 PDOUT e filtro loop non progettati. La retroazione del PLL può essere instabile; **NO PLL LOCK AFFIRMATO**.
4. Varicap BB204G storico non fornito e non caratterizzato a 37MHz; accuratezza quarzo SSB ancora non accettabile.
5. Alimentazione ingresso protezioni, rail powergood, hard mute, separazione EMI, schematici KiCad completi, ERC/DRC, layout RF e test su banco non eseguiti.

**GATE:** NO FAB / NO TX. Prossima V0.9: validazione con macro-modelli dispositivi o circuito SPICE fisicamente rappresentativo con worst-case Ct/Ipk/ESR, circuiti di protezione/mute e PD loop; schema KiCad nativo revisionato prima di PCBWay.

## Fonti primarie e package
- ST MC34063ABN: https://www.st.com/resource/en/datasheet/mc34063ab.pdf
- TI MC34063: https://www.ti.com/product/MC34063A
- TI LM317: https://www.ti.com/product/LM317
- TI LM358 PDIP: https://www.ti.com/product/LM358
- Bourns RLB0914-471KL: https://www.bourns.com/docs/product-datasheets/rlb.pdf
- Vishay SB160-E3/54: https://www.vishay.com/doc?88715
