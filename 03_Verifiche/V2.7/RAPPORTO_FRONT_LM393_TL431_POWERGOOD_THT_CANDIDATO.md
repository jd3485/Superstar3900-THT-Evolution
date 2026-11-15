# V2.7 — supervisore THT power-good LM393 + TL431: CAD reale ma NON qualificato

**15 novembre 2026 · schema standalone DA BANCO · NO FAB / NO TX / NO BATTERIA / NO VEICOLO**

## Obiettivo tecnico

A differenza del precedente `POWER_GOOD_LAB` passivo nella PR #264,
questa revisione aggiunge una topologia **reale KiCad9** per derivare
un consenso da una rail candidata da 5 V, senza inserirla ancora
nel master MAIN né nella PCB FRONT.

Schema:
`04_KiCad/V2.7_DRAFT/FRONT_MUTE_POWER_GOOD/FRONT_LM393_TL431_POWER_GOOD_THT_V2_7_DRAFT.kicad_sch`.

U2001 è un comparatore duale TI LM393 candidato **PDIP-8 THT**,
U2002 una reference shunt TI TL431 candidata **TO-92 LP THT**.
Pinout primario [TI LM393 datasheet, sezione 4 pag.3](https://www.ti.com/lit/ds/symlink/lm393.pdf):
1 OUTA, 2 INA−, 3 INA+, 4 GND, 5 INB+, 6 INB−, 7 OUTB, 8 VCC.
[TI TL431 datasheet, sezione 5 pag.4](https://www.ti.com/lit/ds/symlink/tl431.pdf):
TO-92 LP **1 cathode / 2 anode / 3 REF** (NON generalizzare il pinout a TL432
o packaging alternativi). Il TL431 TO92 mantiene footprint **vuoto**
finché esatto MPN/pacchetto/quota fisica sono qualificati.

R2001 1kΩ polarizza TL431 cathode e REF collegate a `VREF2V5`;
U2002 anode a `PGOOD_GND`. U2001 INA− segue la reference,
INA+ `SENSE_DIV`: R2002 10kΩ verso `PGOOD_5V_LAB`,
R2003 12kΩ verso GND; soglia ideale
`Vthreshold = Vref × (1+10k/12k) = 4,574 V`.
U2001 OUTA open collector con R2004 1,5kΩ a rail:
`POWER_GOOD_LAB`, J2002/1 verso il driver J1913/1.
C2001 100nF di disaccoppiamento vicino al comparatore è
solo da schema: posizionamento/ESR reale non validati.
Seconda sezione inutilizzata: INB+=GND, INB−=VREF,
OUTB=GND (open collector), per evitare pin flottanti.
Nessuna isteresi, latch, timer o evento startup validato.

## Gate reale e limiti analitici

`verify_front_tl431_lm393_powergood_native.py` eseguito da
`ci/full_regressions.py` usa ERC KiCad9 **senza waiver**,
esporta netlist e verifica le **5 reti complete** e i pin 1–8 U2001
e 1–3 U2002, J2002/1 ↔ J1913/1 via la stessa interfaccia logica
candidata. I 35 segmenti PCB FRONT restano intatti.

La matrice **135 condizioni illustrate**:
VIN 3,5/4/4,5/5/5,5V × Vref 2,44/2,495/2,55V
× Rtop 9,5/10/10,5kΩ × Rbottom 11,4/12/12,6kΩ,
conteggia automaticamente quando sono violate:
- **TL431**: IKA almeno 1mA per riferimento valido (dato OEM
  per una famiglia specifica, non prova startup).
- **LM393 legacy**: ingressi <= VCC−2 V nel range di temperatura
  garantito; a VIN basso la reference 2,5V può risultare **fuori
  common-mode**, il comparatore potrebbe essere indeterminato,
  quindi non può essere dichiarato rail-fail-closed.
- **OUT open collector 1,5kΩ**: la base a valle
  R1912 1,5kΩ e pull-down R1914 10kΩ non vede VIN ideale.
  Ipotesi VBE0,8V e base già attiva:
  `Vout≈(VIN+0,8)/2` (3,15V anche a VIN 5,5V):
  il consenso **non** eroga il precedente livello LAB
  ipotetico 4,5V; saturazione e corrente bobina non garantite.
  Anche con R2004 1,5k la corrente sink ideale < 4mA @5,5V,
  ma la conformità VOL a temperatura, EMI/ESD e transitori va
  misurata e confrontata con l'MPN esatto.

**Importante:** CI PASS su questo gate significa
**identificare e proteggere contro una falsa qualifica**, non
significa che il supervisore sia fail-safe/adeguato alla bobina.

## Gate prima di qualunque release

1. Definire architettura di uscita buffer e tempi/power-good con
   prove startup, brownout profondo, doppio guasto e ritorno massa.
2. Dimensionare isteresi e filtri senza compromettere dropout
   rapido (relè e diodo ricircolo possono ritardare il mute).
3. Qualificare TL431 e LM393 MPN/temperatura, reference current
   a fine rail, offset, input CM, dinamica, pinout package,
   dissipazione e stabilità con i passivi e prototipo.
4. Confermare corrente di uscita a valle, coil, base drive
   e contatti AF piccoli segnali tramite datasheet OEM.
5. Coprire open AF_GND, saldatura NO, comando incollato,
   output comparator stuck-high, perdita reference e bobina;
   una catena seriale non è automaticamente redundante.
6. Prima di toccare MAIN/FRONT PCB, completare verifica
   KiCad9 gerarchica, ERC, integrità pin-pad-net e DRC
   solo di una PCB prodotto reale.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

## Primo gate nativo CI e correzione CAD (15/11/2026)

La prima [Actions #43766197158](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43766197158) sullo SHA `75dbc7b48cb2c5abe429909f7a1295bdd21f2612` ha FAST **SUCCESS**, ma FULL/required **FAILED**: KiCad9 `ERC Found 12 violations`, **0 errori / 12 warning** `endpoint_off_grid`, concentrati sui pin/fili R2002, R2003, R2004 e J2002. Corretti *nello schematico* i centri/pin di queste quattro posizioni ai multipli di **1,27 mm** (grid connection), senza waiver o modifica di net/pin-intent. Deve essere rieseguita la FULL sul nuovo HEAD; non assimilare la prima CI fallita a una qualifica.

Correzione CAD integrativa sullo stesso branch: 12 segmenti di collegamento pin disegnati diagonalmente dal generatore (senza significato elettrico aggiuntivo) sono stati ortogonalizzati; i due endpoint J2002 residui a X=207,645 mm riallineati a X=208,28 mm. Verifica statica preventiva: **0 endpoint wire XY fuori multipli di 1,27 mm** sullo schematico aggiornato. Verifica KiCad9/ERC FULL sullo SHA finale rimane obbligatoria.
