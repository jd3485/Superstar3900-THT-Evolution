# V1.8 — interruttore high-side OVP THT reale su KiCad9, NON qualificato

## Circuito nuovo, collegato nel sesto foglio nativo
Nella V1.7 il fusibile F701, TVS D702 e diodo Schottky D701 erano collegati senza disconnessione contro tensione sostenuta. In `04_KiCad/V1.8/INPUT_FUSE_REVERSE_TVS_OVP_V1.8.kicad_sch` è stato fisicamente inserito **Q801 Infineon IRF9540NPBF** P-MOSFET TO-220-3 con **pin3 SOURCE** su FUSED_RAW, **pin2 DRAIN** su OVP_SWITCHED e poi **D701 anodo pin2**, e **pin1 GATE** comandato. Non esiste più una netlist diretta F701 pin2→D701 pin2.

`U801 LM393N PDIP8` comparatore A: VCC pin8 da FUSED_RAW (a monte del MOSFET), GND pin4, input meno pin2 `SENSE_RAW`, input più pin3 `CMP_PLUS`, uscita open collector pin1 `CMP_OUT`. Canale B inutilizzato: pin5 GND, pin6 a VREF2V5, **pin7 esplicitamente NC**, non lasciato in floating. `U802 TI TL431BCLP TO-92`: pin1 CATHODE e pin3 REF uniti alla rete `VREF2V5`, anodo pin2 GND. Datasheet TI TL431 2024 [pinout](https://www.ti.com/lit/ds/symlink/tl431.pdf), versione B ±0,5% a 25°C, temperatura/variazioni ulteriori da verificare.

`R1001` 3,3kΩ alimenta il riferimento; `R1002` 56,2kΩ /`R1003` 10kΩ rilevano la tensione; `R1004` 100kΩ/`R1005` 1MΩ forniscono feedback e isteresi, `R1006` 2,2kΩ pullup da VREF a CMP_OUT; `R1007` 22kΩ pilota `Q802` 2N3904 TO-92; `R1008` 47kΩ GATE-SOURCE pullup OFF, `R1009` 10kΩ tra gate e collettore Q802; `R1010` 100kΩ base-GND per spegnimento. `D803` 1N4742A 12V zener con catodo su source e anodo su gate, SOLO clamp candidata. `PWR801` è flag ERC-only a monte del MOSFET, **non** una sorgente hardware o segnale powergood.

L'uscita LM393 open collector **va LOW quando SENSE_RAW supera CMP_PLUS**: Q802 si spegne, R1008 porta il gate al source e apre Q801. L'isteresi impedisce idealmente il ricongiungimento fino a una tensione più bassa, ma tempi e soglie devono essere dimostrati.

## Valori nominali, non garanzie
- soglia ideale senza carico uscita: `2,495 × (56,2k+10k)/10k ≈ 16,52V`; l'uscita comparator HIGH caricata dal BJT può ridurre la soglia a circa 16,4V;
- reset indicativo con uscita LOW ~0,2V: circa **15,1V**; il comportamento reale dipende da offset, riferimenti, tolleranze, gate-charge e carichi;
- script `screen_ovp_v18.py` esegue corner analitici ±0,5% VREF a 25°C, ±1% resistori e ±5mV offset LM393 **assunti**, e stima caduta RDS(on) IRF9540 a carico (valore garantito al test Vgs=-10V, non sempre valido nei transitori).
- D803 1N4742A è Zener 12V 1W DO-41, ma **12 V specificati a Izt ≈21mA** mentre il pilot gate assorbe corrente molto inferiore. Nessuna tenuta Vgs max ±20V provata in transitorio.

## Datasheet verificati
- TI [LM393-N](https://www.ti.com/product/LM393-N) comparator 2–36V PDIP8, output open collector.
- TI [TL431/TL432 rev S](https://www.ti.com/lit/ds/symlink/tl431.pdf): TO-92 LP pin1 K, pin2 A, pin3 REF; `TL431BCLP` candidato 0,5% a 25°C.
- Infineon [IRF9540N](https://www.infineon.com/part/IRF9540N), TO-220 G1 D2 S3 e tab D, VDS=-100V, VGS max ±20 V, Rds(on) max 117mΩ a Vgs=-10V.
- onsemi [1N4742A](https://www.digikey.it/en/products/detail/onsemi/1N4742A/977257) zener 12V ±5% 1W DO-41.
- Tutti nuovi componenti THT; fixture e BOM con R1001–R1010 senza conflitto con R803–R805 della V0.x.

## Limiti e gate
**Questa revisione fornisce un circuito di interruzione contro sovratensione continua dal punto di vista topologico, NON un'apparecchiatura qualificata.** Alimentazione LM393 rimane su `FUSED_RAW`: **oltre 36 V prolungati possono danneggiarla anche quando Q801 è aperto**. Reference start-up, reset, body diode MOS, stadio BJT, termica, inrush, ripple, EMI, transitori auto, soglie worst-case su temperatura, freeze, single-point failures e fail-safe di sistema non testati. Il fusibile F701 0,5A non è coordinato con la sorgente, il TVS D702 non è qualificato e i loro footprint restano vuoti. Interfaccia J701 solo laboratorio. **NON collegare a veicolo/batteria**, NO FAB / NO TX.

Criterio CI: KiCad9 ERC zero, 6 pagine SVG, librerie simboli esportabili, determinismo generator, netlist original V1.7 54 reti → V1.8 attese **63** gruppi KiCad (**62 reti connesse + 1 pin U801/7 No Connect**) con pin D701 anodo2 unica connessione legacy spezzata; verifiche dei nuovi nodi gate/feedback e controllo ref univoci. Analisi corner aritmetica NON qualifica RF e OVP. ERC KiCad9 dopo correzione del nome del child: **0 violazioni**, esportata la netlist. Verifica delle partizioni-pin in corso. Un gruppo isolato `unconnected-(U801-OUT_B-Pad7)` è il pin 7 **esplicitamente NC**, non un cortocircuito o errore di progetto.
