# V2.7 — due stadi THT, clamp Zener SHORT/OPEN e stress di pilotaggio (non qualificante)

**17 novembre 2026.** Analisi ancorata ai pin della netlist nativa KiCad9 del banco isolato a 24 componenti THT, 54 pin e 14 reti. Il verificatore `03_Verifiche/V2.7/verify_two_stage_zener_short_open_driver_stress_native.py` è collegato alla FULL CI ed esamina separatamente gli stadi A e B, ciascuno con due 1N4106-1 in parallelo gate–source, Rgs 47k e resistore serie driver 10k.

In ciascuno stadio: 6 sorgenti ipotetiche (0/13,8/20/24/36/48V), 3 corner ±5% per ciascuna R, tre stati driver (DISABLED, ENABLED, C–E SHORT) e due estremi di clamp (entrambi Zener OPEN, uno Zener corto ideale), per **324 corner per stadio; 648 complessivi**. Non è una prova transistor: il driver è idealizzato come sink rigido, i due tipi di guasto sono mutuamente esclusivi nel modello e non sono coperti i transitori.

* Con **entrambi Zener OPEN** e sink attivo, `|Vgs|=Vs*Rgs/(Rgs+Rserie)`. Su 324 corner/stadio, **38** superano 20V (limite assoluto ipotizzato nel banco); massimo **40,251487V** al corner 48V/49,35kΩ/9,5kΩ. Lo stesso estremo con driver C–E SHORT significa comando OFF non rispettato, ma la capacità di attivare il MOSFET *reale* non è provata.
* Con **uno Zener ideale in corto** gate–source, `Vgs=0` e il resistore serie dissiperebbe `Vs²/Rserie`: massimo **0,242526W** al corner 48V/9,5kΩ; nominale 48V/10kΩ **0,2304W**. La corrente nel driver, resistenza reale di guasto e dissipazione a impulsi non sono state qualificate. Questo caso non dimostra isolamento in ogni guasto.
* Quando il driver sano è DISABLED, il solo modello ohmico impone Vgs=0 tramite Rgs; non dimostra ritorno sicuro durante perdita massa, carico o reference.

Le reti SOURCE_A/B, GATE_A/B e SINK_A/B sono verificate distinte fisicamente nello schema nativo; alimentazioni, returns e comandi esterni restano non qualificati. La combinazione di due stadi non fornisce immunità ai guasti di causa comune. I corner 36/48V sono esclusivamente ipotetici e non autorizzano l'impiego a tali tensioni. Nessun modello OEM Zener I–V, transistor SOA, termica, capacità gate, protezione input, PCB o hardware è stato validato. Restano aperti issue #27 e i gate CAD/produzione.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
