# V2.7 — SPDT NC mute, 64 stati di guasto del contatto

**Candidato TOPologico solamente, nessuna qualifica di relè o sicurezza fisica.**

Dopo la PR #261 (merge `acfae8f0041d90b8bd9b398adb6832a3e5632480`),
lo schematico `FRONT_NC_MUTE_CONTACT_THT_V2_7_DRAFT.kicad_sch` contiene
K1901: COM pin1 verso amplificatore, NC pin2 verso AF_GND, NO pin3
verso volume; la bobina pin4/5 resta su interfaccia LAB isolata.
La PR #261 ha PASSATO CI finale [#43760083956](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43760083956):
FAST/FULL/Required 3/3, ERC0 e netlist nativa dei cinque nodi.
Due run iniziali FULL failed per libreria locale non risolta; correzioni
vere `TH_MUTE.kicad_sym`, `sym-lib-table` e `.kicad_pro` hanno portato
alla verifica finale verde senza waiver.

## Nuova matrice fail-closed

Nuovo script obbligatorio FULL:
`03_Verifiche/V2.7/verify_front_nc_relay_contact_fault_matrix_native.py`.
Le connessioni pin KiCad9 vengono esportate, poi sono enumerate
**64 condizioni**:
- comando MUTE / AUDIO (2);
- bobina disponibile / interrotta (2);
- contatto libero / saldato su NO / saldato su NC / aperto (4);
- massa esterna valida / aperta (2);
- cursore di volume valido / aperto (2).

Due formalizzazioni indipendenti (grafo delle connessioni e logica
booleana) verificano la raggiungibilità di `GROUND` e `WIPER`
dall'input amplificatore, con invariante di non corto
simultaneo GND/wiper. In tutti i quattro casi `NO saldato`
con volume collegato e richiesta MUTE, il percorso audio rimane
attivo. `NC` e GND integri + bobina diseccitata chiudono
idealmente su massa, **ma** massa esterna aperta / contatto aperto
possono lasciare l'ingresso **flottante**. La bobina mantenuta
involontariamente eccitata non è evitata con il solo contatto.

La matrice **non rappresenta** degrado reale in µV, velocità
meccanica, bounce, film sui contatti, weld probabilities,
ciclo termico, vibrazioni, elettromagnetismo, reale forma d'onda
di bobina e capacità parassite. Di conseguenza **NON prova**
fail-safe rispetto a un singolo guasto, protezione uditiva,
IEC/EN o conformità automobilistica.

## Priorità vera successiva

Progettare/validare un driver coil normalmente OFF con controllo
power-good che **non** possa bypassare il mute a rail spenti,
dimensionare carico e flyback, e soprattutto studiare metodi
indipendenti per disabilitare il guadagno LM386 in caso di
massa/front-cable aperti o contatto saldato sul NO.
OEM relè prodotto attivamente, dry contacts low-level,
corrente/tensione contatti e derating sono BLOCCANTI.
Nessuna modifica PCB FRONT 13THT/28pad/12reti/35 piste.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
