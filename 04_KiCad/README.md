# KiCad — metodo CAD-first V1.0 (stato attuale)

Prima del nuovo pilot, `main` aveva un solo schematico nativo parziale V0.4 e **zero PCB KiCad**. La PR #5 (KiCad parziale) aveva fallito l'esportazione della libreria e non è stata integrata. Il nuovo circuito parziale `V1.0/PLL_FILTER_DRIVER_CAD_V1.0.kicad_sch` è uno **studio isolato** con U803 LM358N DIP8, R/C THT, 3 connettori di test e alimentazioni esterne marcate; reali connessioni e pin/simboli documentati nel file nativo. **Non contiene U401, mixer, VCO, boost, FI o intera radio.**

Il workflow nativo `cad_native_v10.yml` (GitHub Actions, KiCad CLI 9) verifica simboli, ERC e netlist. Se FAIL, il circuito resta su branch e non è validato. Qualsiasi eventuale PASS vale **solo per questo sottocircuito isolato**, non per il sistema RF.

R901=22k C901=100n **sono varianti CAD non approvate**, diverse dal precedente modello ngspice V0.9 R90110k/47k e C9011µF. Non usare il valore dell'esempio per produrre PCB. Il target è un progetto integrato multi-sheet KiCad e successivamente `.kicad_pcb` con DRC reale; gerarchia/processo in `00_Gestione_Progetto/METODO_CAD_FIRST_V1.0.md`. **NO FAB / NO TX**.

---

# KiCad — stato V0.1

**Non esiste ancora** un progetto KiCad nativo o uno schematico con pin numerati. Per non simulare un progresso inesistente, questa cartella non contiene file `.kicad_sch` o `.kicad_pcb` fittizi.

Nella fase di progettazione saranno creati schematici reali, gerarchie coerenti, librerie/footprint THT verificati su datasheet e, successivamente, PCB con regole di fabbricazione PCBWay.

Conservare la separazione fra controlli statici, ERC, DRC, refill zone e verifica della parità/schema-PCB. **Non produrre Gerber finché i gate non risultano chiusi.**
