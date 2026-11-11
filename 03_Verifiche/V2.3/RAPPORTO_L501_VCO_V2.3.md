# V2.3 — candidatura RF VCO L501: Coilcraft 150-05J08L THT regolabile, NON ancora qualificata

**Baseline reale:** PR #24 V2.2 su PR #20 V2.1, sette fogli KiCad9.
Nuovi sette sorgenti V2.3 riproducibili. Unica modifica intenzionale è l'assegnazione dei
metadati Value e Footprint della bobina **L501**; nessun filo/pin modificato.
La funzionalità RF NON è provata da KiCad ERC0 o da un footprint.

## Produttore, geometria, specifiche
Datasheet originale Coilcraft 7mm tunable, documento 109-1 e 109-2:
https://www.coilcraft.com/getmedia/aaa9fcd2-5ef1-4ee2-b9b8-0ec1aa8c8db0/uni7.pdf

**150-05J08L (unshielded)**: L nominale CON nucleo regolato 165nH, range dichiarato
137..193nH; il modello storico era 166nH (entro intervallo). Q minimo 114
a 50 MHz, SRF minima 650MHz **SENZA nucleo**, DCR max13.2mΩ, Irms8.7A
a condizioni del vendor; -40..+85°C. I numeri vendor a 50MHz / senza nucleo
NON garantiscono stessi Q/SRF a 36..39 MHz con nucleo/in cabinet e carichi reali.
Core regolabile carbonyl J, serve fissaggio/locking, aging/drift, EMC.
Verificare acquisto campioni, disponibilità MPN esatta e tool di taratura.

Corpo massimale 6.81±0.13mm quadro (max6.94), lunghezza con corpo 11.43±0.51mm,
passo reofori **4.5±0.13 mm per ciascun asse** (diagonali in bottom view),
Ø terminali 0.51±0.05mm. Footprint candidato
`THT_V23:Inductor_Coilcraft_150-05J08L_Uni7_Tunable_THT` ha
pad1 (-2.25,-2.25), pad2 (+2.25,+2.25), drill0.80mm, pad1.80mm, corpo
F.Fab 6.94mm quadro e courtyard 8.50mm quadro. È una scelta di processo THT
preliminare; verificare tolleranze drill, lead forming e campioni reali.
La variante **senza schermatura** può subire accoppiamenti dal boost 20V; rafforzare
la separazione EM e considerare variante schermata a 4 connessioni (inclusi tabs GND).

## Limiti gate
Il filtro PLL, varicap BB204G, carico AC14, KVCO, phase noise, pull-range,
27 MHz e 270 canali, jitter e margini RF 36..39MHz PVT NON sono qualificati;
il modello ideale `1/sqrt(L)` è solo uno screen e NON una simulazione vendor.
Nessuna produzione o connessione alimentata permessa. Rimangono:
qualifica 5V/20V OVP LM393 36V TVS/fusibile, EMI, RF/IF/audio/controller e
PCB assente (DRC non eseguito).

**Gate merge:** prima #20 V2.1 integrata con CI verde su HEAD finale;
poi #24 V2.2 validata/integrata; poi questa V2.3 con KiCad9 ERC0,
72 partizioni pin-net identiche, BOM 129/129 footprint compilati,
SVG footprint e sette schemi, tutti i workflow finali verdi.
**NO FAB / NO TX**.
