# V2.7 — audit OEM Vishay 1N4148-TAP e gate DC per modelli DGENERIC (15 novembre 2026)

## Fonte primaria, identificazione e condizioni

Fonte ufficiale: [Vishay 1N4148, documento 81857, revisione 1.6 del 7 novembre 2024](https://www.vishay.com/docs/81857/1n4148.pdf), pagine 1–2. Identificazione ordinabile **1N4148-TAP**, corpo in vetro **DO-35/DO-204AH**, terminale catodo identificato dalla fascia **nera**; 1N4148TR è un'altra opzione di confezionamento. Pagina [prodotto Vishay](https://www.vishay.com/en/product/81857/) e [tabella qualifiche Vishay](https://www.vishay.com/en/product/81857/tab/quality/) riportano `1N4148-TAP` e qualificazione **non-automotive**. La pagina OEM corrente con ordini/campioni supporta la plausibilità commerciale, ma **non documenta da sola un impegno di produzione continua o un test di vita sul prodotto**. MPN candidato, NON componente finale autorizzato.

| Grandezza OEM | Valore datasheet | Condizioni (vincolanti) |
|---|---:|---|
| Tensione diretta VF max | 1,0 V | IF = 10 mA, Tamb 25 °C |
| Corrente inversa IR max | 25 nA | VR = 20 V, Tamb 25 °C |
| Corrente inversa IR max | 50 µA | VR = 20 V, Tj = 150 °C |
| Capacità CD max | 4 pF | VR = 0 V, f = 1 MHz, segnale 50 mV |
| Tempo recupero inverso trr max | 8 ns | IF=IR=10mA, iR=1mA |
| Tempo recupero inverso trr max | 4 ns | IF=10mA, VR=6V, iR=0,1 IR, RL=100Ω |
| Tensione inversa continuativa VR | 75 V | limite assoluto, non condizione di prova |
| Tensione di picco ripetitivo inversa VRRM | 100 V | limite assoluto |
| Dissipazione | 440/500 mW | dipende da lunghezza terminali e temperatura, **non** potenza garantita su PCB |

Questi dati OEM non identificano `Is`, `N`, `Rs`, `Cjo`, `Tt` univoci né autorizzano a tradurre un numero di leakage massima (VR=20 V) in `Is` di ngspice per ogni bias o temperatura. Le curve tipiche di VF e leakage non diventano min/max garantiti. L'orientamento fisico/pin-pad di D1501 deve essere riesaminato sul footprint definitivo con fascetta catodo e assemblaggio.

## Verifica nuova: ngspice su 9 modelli numerici

Il file `03_Verifiche/V2.7/verify_am455_1n4148_vishay_datasheet_model_screen_native.py` riusa **esattamente** Is e Cjo dello screening a 54 transienti, non inventa un modello vendor, ed esegue per ciascuna delle **3×3=9 coppie** una vera soluzione ngspice `.op`: corrente diretta forzata **10 mA** per ricavare VF e tensione inversa forzata **20 V** per IR. I valori vengono classificati rispetto ai limiti OEM alle relative condizioni a 25 °C; i modelli sintetici fuori limite sono **segnalati come non conformi** anziché autorizzati o nascosti. Esporta anche la netlist nativa KiCad9 AM455 per identificare il lato ingresso del diodo J1501/1 e il nodo inviluppo D1501/1 e dimostrare che l'audit riguarda il componente della bozza CAD.

**Ulteriore scostamento sperimentale identificato:** l'operating point del modello con `Is=25n` produce **IR≈25,020 nA** a VR≈20 V/T=25°C, cioè supera il limite Vishay **25,000 nA max**. Non è corretto accettare questa curva come corner OEM solo perché l'eccedenza è piccola. Il gate deve classificare come **fuori specifica tutti e tre gli scenari Is=25n**, insieme ai tre Cjo=8p; un caso combina entrambe le esclusioni. **Solo 4/9 varianti non superano quei limiti puntuali del modello**, e neppure esse sono qualificate come macromodelli OEM. La misura simulata di IR usa uno shunt 100kΩ e lettura della sua caduta amplificata, per non perdere nanoampere nell'arrotondamento della stampa SPICE.

**Distinzione critica:** lo screening precedente variava `Cjo=2/4/8 pF`. **8 pF supera il massimo OEM dichiarato di CD=4 pF** a VR=0 e f=1MHz. È legittimo solo come *stress sintetico fuori specifica*, **non corner accettabile della 1N4148-TAP**. `Cjo` non è di per sé una misura completa `CD` di dispositivo reale: il gate segnala il superamento numerico conservativo, senza fingere di misurare la capacità totale. Lo script respinge qualsiasi regressione che rietichetti i tre casi a 8 pF come corner OEM.

Questa verifica **non** prova che il modello DGENERIC rappresenti la 1N4148 in RF455, alla temperatura elevata o a basse ampiezze; VF/IR 25 °C sono due sole prove puntuali e non vincolano non linearità di giunzione, trr, leakage vs temperatura, degradazione o rumore. Il valore `Tt=4ns` del deck precedente non è il test `trr=4ns` datasheet: **due grandezze non equivalenti**. Nessun modello SPICE ufficiale Vishay 1N4148 è stato scaricato o validato qui.

## Decisioni bloccanti prima di CAD integrato/PCB

1. Mantenere il diodo D1501 candidato e il MAIN radio a fogli IF/AF **elettricamente separati**; non trasformare prove di simulazione in qualificazione progettuale.
2. Acquisire/validare un modello produttore ufficiale identificato e applicabile oppure caratterizzare 1N4148-TAP reale nel circuito, includendo temperature PVT, carico del volume, condizione RF 455kHz e bassa ampiezza IF.
3. Verificare produzione OEM esatta, marcatura catodo→pad, corrente/termica, ritorni di massa e cavi. La qualifica non-automotive è un dato del produttore che impedisce di trattare la parte come già verificata in ambiente veicolare.
4. Il gate su branch deve superare FAST/FULL/required sul **final SHA**; fino a esito verificato, risultati numerici non attribuibili alla CI.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.** Nessuna PCB MAIN/FRONT radio definitiva o DRC prodotto.
