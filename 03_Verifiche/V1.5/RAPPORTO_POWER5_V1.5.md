# V1.5 — Sottoblocco reale KiCad 5V THT, indipendente fino al gate di integrazione
Data 10 novembre 2026. Radio solo THT, senza modificare la SMD. Questa è una **prima scheda di alimentazione nello schema KiCad**, NON un PCB e non è ancora nel master.

## CAD fisico creato
- **U601 ST L7805CV** package TO-220, pin1 VIN, pin2 GND/tab, pin3 VOUT: input `+13V8_PROTECTED` **fornito da protezione esterna NON disegnata**, nodo +5V_REG.
- **C600 330nF** e **C602 100nF**, secondo circuito tipico ST L7800. C601 47µF / 35V input e C603 47µF /16V output **candidati aggiuntivi**, da qualificare per ESR, ripple, esatto package e scarica.
- **D601 1N4007 DO-41** con catodo pin1 verso ingresso VIN e anodo pin2 verso uscita +5V_REG, solo percorso di scarica dell'uscita al collasso dell'ingresso. **NON protegge** da inversione dell'alimentazione o sovratensione.
- R611/R612/R613 1Ω THT 1/4W su tre rami `+5V_PLL`, `VCC_VCO5`, `VCC_BUF5`; C611–C613 10µF e C614–C616 100nF THT dopo ciascuna resistenza. I tre rami non garantiscono isolamento RF o regolazione esatta; caduta di tensione funzione della corrente.
- J601 ingresso, J602–J604 uscite, J605 nodo test; PWR601/602 flag di alimentazione esterna usati esclusivamente per ERC. **Tutte le uscite temporanee da test non sono la PCB principale**.

## Vincoli meccanici e termici
- Datasheet ST [L7800 series](https://www.rf-microwave.com/resources/products_attachments/5a438715b5a2b.pdf), rev 13: TO-220 RthJA circa **50°C/W** e junction-case **5°C/W** (scenario senza dissipatore, dipende da montaggio); dimensionare corrente e dissipatore con dati verificati di tutti i sottoblocchi. L7805 è lineare: `P_D≈(VIN−5)·I_OUT + VIN·I_Q`.
- Lo script `screen_power5_thermal_v15.py` esamina VIN 11/13.8/15.5V, carichi 30–250mA, Tamb 50°C, Iq=6mA **tipico ipotizzato**, segnala casi termicamente rischiosi; non è una prova reale o un calcolo garantito per prodotto.
- **Sorgente +13V8_PROTECTED assunta, NON presente nel CAD**, non comprendente fusibile/polarity-guard/TVS. Non collegare direttamente a batteria o ingresso veicolo prima del progetto completo e degli stress test. Tab TO-220 = GND: attenzione all'isolamento da chassis.
- La V1.4 richiede VCO 5V stabile; la scelta 1Ω/branch modifica il riferimento rispetto al modello ngspice da 5,000V, quindi richiede analisi di tuning, carichi, power sequencing, bias e brown-out.
- Le alimentazioni `VANA20_FILT` e `VTUNE_RAIL` restano **fuori**: nessun boost MC34063/LM317 reale nella V1.5. L501 ancora senza MPN/footprint; VCO/74AC14 non hardware qualificati.

## Gate
- GitHub Actions `cad_native_v15.yml`: rigenerazione bit-per-bit, ERC KiCad 9 nativo, export netlist con sei reti distinte e pin corretti, export SVG, script budget termico.
- Evidenza PENDING sino a CI. L'ERC non prova la stabilità del 7805, ripple/PSRR, temperatura, capacità di avviamento di VCO o le emissioni.
- **NO FAB / NO TX**. Prima di portare questa sezione nel master servono load budget reale, valore meccanico di C e R, verifica scelta di protezioni, rielaborazione carico e KiCad integrazione.
