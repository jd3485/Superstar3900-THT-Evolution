# V2.7 FRONT — collegamento bobina tra due fogli gerarchici KiCad9 (candidato laboratorio, NO FAB)

Data: 16 novembre 2026. Revisione di progetto, non approvazione di relè o hardware.

## Variazione elettrica reale

Nel master `04_KiCad/V2.7_DRAFT/FRONT_CONTROL_PARTIAL_V2_7_DRAFT.kicad_sch`, i child `FRONT_MUTE_NC_RELAY` e `FRONT_MUTE_COIL_DRIVER` espongono due pin gerarchici passivi ciascuno. Due nuovi fili nel master collegano le porte omonime:
- `COIL_PLUS_LAB`: `K1901/4`, `J1903/1` ↔ `J1911/1`, `D1911/1 (catodo)`, `J1914/1`, `C1911/1`, `C1912/1`.
- `COIL_MINUS_LAB`: `K1901/5`, `J1903/2` ↔ `J1914/2`, `D1911/2 (anodo)`, `Q1911/1 (collettore)`.

Il collegamento è nello schema del master, **non** un cablaggio reale assemblato e non una PCB prodotta. I connettori di laboratorio J1903/J1914 rimangono rappresentati e non sono un'interfaccia qualificata; evitare doppi collegamenti o alimentazioni parallele in qualunque futura implementazione. Nessuna modifica alle reti del master MAIN V2.6/V2.7.

## Verifica obbligatoria e isolamento

`verify_front_partial_hierarchy_native.py` richiede ERC0 e netlist nativa di cinque fogli, 32 riferimenti fisici, **22 reti** anziché 24, invariati **71 endpoint**. Verifica quattro unioni fisiche (due audio e due bobina), l'identità esatta dei pin e l'assenza di corti tra `COIL_PLUS_LAB`, `COIL_MINUS_LAB`, `DRIVER_GND`, `AF_GND` e `ILLUM_RETURN_LAB`. I test standalone dei child ora invocano ERC sul parent, come richiesto da KiCad9 quando esistono hierarchical labels; continuano a esportare la netlist dei child per mantenere il controllo endpoint.

## Limiti non risolti

La connessione non prova tensione/bobina, resistenza di pickup/release, capacità dei contatti su segnale audio, saturazione Q1911/Q1912 a PVT, safety in presenza di transistor stuck-on, saldatura contatti NO, AF_GND interrotta, transitori, reverse/hotplug, dissipazione dei condensatori, protezione ESD, MPN attivo OEM, pinout fisico e impronta K1901. `POWER_GOOD_LAB` è un ingresso esterno, non una supervisione qualificata. `COIL_PLUS_LAB` non è automaticamente un rail MAIN/FRONT sicuro. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**. Non usare questo schema per collaudo con alimentazione reale senza qualifiche/autorizzazioni.

Evidenza definitiva: solo CI FAST/FULL/Required verde sullo SHA finale della PR, con log KiCad9 ERC e netlist (non si afferma pass anticipatamente).