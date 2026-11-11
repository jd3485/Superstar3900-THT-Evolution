# Rapporto V2.2 — footprint fisico candidato L920 (NON QUALIFICATO)

Baseline di PR #20 V2.1 (sette fogli); il master V2.2 conserva **tutte le reti**
e modifica **solo** la proprietà Footprint di L920. Pubblicazione e ogni eventuale merge
dipendono da test KiCad9 nativi eseguiti sul commit finale e dalla PR base #20.
Non confondere un check statico con ERC/DRC o misura fisica.

## Riferimento tecnico originale

Bourns RLB series, RLB0914-681KL:
https://www.bourns.com/docs/product-datasheets/rlb.pdf (pagina geometria e tabella serie RLB0914).
680uH ±10%, DCR max 1.6 ohm, Irms 0.49A typ, Isat 0.90A typ, SRF >=1.6MHz,
dimensioni corpo 8.7 ±0.5mm diametro, 12 ±1mm altezza, passo 5.0 ±0.8mm,
terminali Ø0.65mm nominali. In un boost unshielded, verificare spur switching e
interazioni VCO PLL e filtri IF.

## Impronta candidata (non approvata)

`THT_V22:Inductor_Bourns_RLB0914_681KL_P5.00mm`, pad 1 a x=-2.5mm,
pad 2 a x=+2.5mm, drill 1.0mm, pad Ø2.0mm (anello 0.5mm nominale),
corpo F.Fab Ø9.2mm, F.CrtYd Ø10.4mm. La fascia di tolleranza ±0.8mm
del passo richiede verifica fisica e montaggio; nessun footprint universale garantito.

## Screen elettrico preliminare

A I_RMS=0.49A, Pdc <=(0.49A)^2*(1.6Ω)=0.38416W nel modello RDC fisso;
a 0.9A energia nominale L*I²/2=0.2754mJ *prima di perdita di induttanza*.
Valori ipotetici a temperatura costante: nessun modello termico,
nessun vendor SPICE, nessuna prova di banco; Isat e Irms sono **tipici**,
non soglie assolute garanti. Corrente di picco MC34063 e stress EMI ancora ignoti.

## Gate tecnico ancora obbligatorio

V2.1 e V2.2 ERC0, 72 partizioni nette identiche per ogni pin, 7 SVG,
footprint SVG generato dal CLI, copertura BOM e generatore --check.
Non esiste PCB: DRC non applicabile. L501 resta MPN/footprint/qualifica RF irrisolti;
F701/D702 richiedono qualifica fusibile/TVS e montaggio; LM393 36V,
reverse battery, load dump e ogni rail restano non qualificati.

**NO FAB / NO TX**. Nessuna integrazione con CI non eseguita o fallita.
