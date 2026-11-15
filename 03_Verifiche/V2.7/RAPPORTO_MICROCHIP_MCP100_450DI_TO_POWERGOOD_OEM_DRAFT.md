# V2.7 — supervisore THT Microchip MCP100-450DI/TO, candidato reale a tre pin

**15/11/2026 · prototipo concettuale KiCad9 standalone, MPN NON rilasciato**

## Fonte OEM e pinout

[Microchip MCP100/101, datasheet originale DS11187F](https://ww1.microchip.com/downloads/en/devicedoc/11187f.pdf),
pagine 1–2, figura package e tabella DC/AC (visti).
Dispositivo **MCP100-450DI/TO**: TO-92 a **bondout D** e
uscita RESET attiva-bassa **push-pull**. Nel disegno del package OEM
D-bondout, vista come illustrata, i tre pin numerati sono
**1 RESET_N, 2 VDD, 3 VSS**. La variante H-bondout e il modello MCP101
hanno pin/funzioni differenti; non usare footprint generico
senza confronto **meccanico + pin1**. La famiglia è ancora elencata
da distributori come active (verificare stato produttore dell'MPN esatto
prima della BOM finale).

Specifiche OEM da non confondere con misure:
- threshold `-450`: **4,25 ≤ VTRIP ≤ 4,50 V**, nominale 4,375V;
- RESET release **150–700 ms** (typ 350ms) dopo salita VDD;
- output HIGH garantito **≥VDD−0,7V** a **IOH=3mA**
  soltanto se VDD maggiore di VTRIPMAX;
- funzionamento RESET fino a **VDD=1,0V**, non garantito
  a rail più bassa; VDD massimo raccomandato **5,5V**,
  massimo assoluto 7V NON operativo;
- reset durante discesa tipicamente 10µs con condizioni OEM,
  **non** tempo massimo garantito né protezione da dip di durata
  arbitraria; immunità a transitori e fissaggio cablaggi da provare.

## CAD THT originale e relazione col driver

`04_KiCad/V2.7_DRAFT/FRONT_MUTE_MCP100/FRONT_MCP100_450_POWER_GOOD_THT_V2_7_DRAFT.kicad_sch`:
U2101 supervisory TO92 **footprint vuoto**, C2101 100n,
J2101 rail 5V+GND, J2102 output power-good + driver GND.
Tre net `PGOOD_5V_LAB`, `DRIVER_GND`, `POWER_GOOD_LAB`,
con J2102/1 ↔ J1913/1 del precedente doppio NPN.
Questa è una **alternativa** allo schema LM393/TL431 della PR #267
(merge su main `640de1d16c1b5c3e42dd4212051635b0fd803441`),
non un secondo supervisore parallelo e non un cambio hardware al PCB.
Il reset push-pull fornisce un'uscita logica migliore rispetto
all'open collector caricato da 1k5 ma **non garantisce** 4,5V ai livelli
inferiori della rail.

## Verifica e screening reale

`verify_front_mcp100_450_oem_powergood_native.py` esegue
ERC KiCad9 nativo e netlist sulle **tre reti esatte**. Il test
incrocia 54 casi (rail 3,5/4,25/4,5/4,6/5/5,5V
× 3 Rcoil 150,3/167/183,7Ω
× 3 VCEsat ipotizzate 0,15/0,2/0,3V).
Nei 27 casi sopra VTRIPMAX, l'uscita OEM garantisce
minimo VDD−0,7V a 3mA. Con il downstream
`R1912=1k5` e pull-down 10k, VBE ipotizzata 0,8 V,
si calcola `Ibase_min=(VDD−0,7−0,8)/1500−0,8/10000`.
Per la bobina Omron G5V-1 DC5 (167Ω±10%) selezionata solo
per confronto, **tutti e 27 i corner sopra soglia restano
insufficienti** all'ipotesi forced β10 di due NPN in serie.
Sotto 4,5V NON è garantito il rilascio RESET:
il controllo non dichiara HIGH, richiede mute e resta
un modello di limiti, non un proof di sicurezza hardware.

Una CI verde dimostra soltanto che
l'ingegneria di esclusione e le connessioni KiCad sono
**correttamente rilevate**, non che si possa integrare
questo MPN in K1901/PCB o sostituire l'alimentazione.


## Screening addizionale dei guasti, 216 casi (branch successivo a PR #268)

Il verificatore nativo ora esegue una matrice separata di **216 stati logici**:
6 tensioni di ingresso × 3 resistenze bobina × 3 cadute ipotetiche ×
4 modalità (nominale, uscita bloccata HIGH, uscita bloccata LOW,
massa del segnale aperta). Attesi **27** casi HIGH erroneo sotto/o
alla soglia massima per guasto stuck-HIGH, **27** casi di consenso
non disponibile sopra soglia con stuck-LOW e **54** riferimenti
indefiniti con massa aperta. La zona di soglia 4,25–4,50 V non
viene classificata arbitrariamente come livello OEM garantito.
I risultati sono classificazioni logiche dei guasti, non simulazione
transitoria SPICE/vendor, né verifica dell'effettiva energizzazione
di bobina o posizione di contatto. **Output stuck-HIGH e apertura
di massa impediscono di proclamare fail-closed**; restano esclusi
collasso sotto 1 V, saldatura del contatto NO, tempi di release e
dati di dispersione/carichi AF. Il blocco di fabbricazione resta invariato.


## Verifica aggiuntiva della corrente massima garantita dall'uscita OEM

La specifica `VOH >= VDD-0.7V` è caratterizzata solo a 3mA di source corrente. Con il modello **illustrativo** di bobina 167Ω ±10%, due VCEsat ipotetiche e beta forzato 10, la corrente richiesta al supervisore è `Icoil/10 + 0.8V/10kΩ` (la seconda componente alimenta la pull-down del driver). Dei 27 stati sopra VTRIPMAX, **9 superano 3mA**: non esiste una semplice riduzione della resistenza di base che mantenga simultaneamente questa garanzia di carico OEM e l'ipotesi di beta10 in tutti gli stati. Gli altri 18 non sono automaticamente compatibili: il resistore da 1k5 resta insufficiente negli stati già documentati, VBE è ipotizzata, NPN/coil pickup/temperatura/transitori non qualificati. Non confondere 3mA di corrente di prova del VOH con un massimo assoluto di corrente ammissibile: il risultato è un limite alla **garanzia disponibile dal datasheet**, non prova di danneggiamento. Richiesta alternativa con buffer/driver THT qualificato oppure relè compatibile con carico e contatti audio.

## Problemi ancora aperti

Scegliere relè THT SPDT con vera specifica dry-contact audio
e bobina più alta impedenza (o riprogettare in modo
dimensionato NPN/base-drive), supervisionare l'ingresso
`ENABLE_AUDIO_LAB` e la reale rail (non usare
GND cavo frontale come unica massa), testare tempo
release relè con clamp, contatti NO weld/NC open, AF_GND
interrotta, transistor stuck-on, output reset stuck-high,
ESD e transitori reali. Prove di banco indipendenti obbligatorie.
PCB FRONT 13THT/28pad/12net/35 piste e MAIN intatti.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

## Gate analitico aggiuntivo: resistenza minima bobina, 9 corner (16/11/2026)

Con `R1912=1k5`, `R1914=10k`, `VBE=0,8V` **illustrativa**, VOH garantito `VDD−0,7V` a prova OEM `IOH=3mA` e forced β10, la condizione **necessaria** per il driver esistente è `Rcoil >= (VDD−2·VCEsat)/(10·[(VDD−0,7−0,8)/1500−0,8/10000])`. Su 3 rail sopra soglia (4,6/5/5,5V) e 3 cadute ipotetiche (0,15/0,2/0,3V), il peggiore limite è **216,443Ω**. La bobina Omron nominale da 167Ω non supera nessuno dei nove corner; una bobina idealizzata da 220Ω supera **soltanto questa disuguaglianza**, non la qualifica OEM né le condizioni di pickup, dropout, temperatura, transistor, flyback, contatti microsegnale o PVT. Non è una distinta componenti né proposta di collegamento hardware; `NO FAB / NO TX / NO BATTERIA / NO VEICOLO`.

## Screening incrociato OEM Omron DC5/DC6 — 54 corner (16/11/2026)

Fonte primaria [Omron G5V-1](https://omronfs.omron.com/en_US/ecb/products/pdf/en-g5v_1.pdf), tabella bobine: G5V-1 DC5 **167Ω** e DC6 **240Ω**, resistenza **±10% a 23°C**; tensione *must operate* **80% massimo** della nominale (4,0V per DC5, 4,8V per DC6, solo a 23°C). Il modello attraversa 3 rail MCP100 rilasciate (4,6/5/5,5V), 3 cadute ipotetiche **per ciascuno dei due NPN** (0,15/0,2/0,3V) e 3 resistenze bobina (90/100/110%): **27 stati per MPN, 54 totali**. Con Rbase1k5, pull-down10k, VBE0,8V e beta10 ipotetici:

- **DC5**: pilotaggio base insufficiente in **27/27**; bobina al di sotto dei 4,0V di pickup OEM in **3/27**.
- **DC6**: base insufficiente in **1/27**, nonostante 240Ω nominali oltre il limite analitico di 216,443Ω, perché il minimo di tolleranza è **216Ω**; bobina al di sotto dei **4,8V** minimi richiesti per garantire il pickup in **18/27**.
- La variante a 6V non è una sostituzione qualificata a rail 5V. **Il superamento della condizione di resistenza non garantisce energizzazione né contatto NO.** Le grandezze VCEsat, beta e VBE sono illustrative; temperatura, pickup effettivo, correnti minime dei contatti audio, interconnessione e transitori non sono validati. Nessun circuito rilasciato; **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.
