# V2.7 — due Zener THT in parallelo sul gate Q804/Q805: laboratorio isolato

**16 novembre 2026. Candidato KiCad9; NO qualifica hardware e NO autorizzazione VIN48V.**

## Circuito elettrico effettivamente aggiunto

Nuovo schematico **isolato**: `04_KiCad/V2.7_DRAFT/MAIN_SECONDARY_OVP_Q804_Q805_Q806_DUAL_ZENER/MAIN_SECONDARY_OVP_Q804_Q805_Q806_DUAL_ZENER_LAB_V2_7_DRAFT.kicad_sch`, derivato dal banco Q804/Q805 e driver KSP42BU Q806 (PR #303). I circuiti originali restano immutati; nessuna modifica al master MAIN V2.6.

Il nuovo **D2102 1N4742A candidato THT DO-41** è in **parallelo** al precedente D2101: entrambi i **catodi pin1** sul `FLOATING_COMMON_SOURCE_LAB` (Q804/3, Q805/3, R2101/1) e entrambi gli **anodi pin2** su `COMMON_GATE_LAB` (Q804/1, Q805/1, R2101/2, R2102/2). R2101 47k, R2102 10k, Q806 KSP42BU e la rete di enable restano identici. Biblioteche e footprint KiCad THT generici; MPN/derating/meccanica, tolleranze Zener e termica non verificati.

## Rischio OEM appena verificato — impedisce qualsiasi claim di clamp

Il [datasheet originale onsemi 1N4736AT/D Rev.10](https://www.onsemi.com/pdf/datasheet/1n4736at-d.pdf), tabella **1N4742A** a 25°C, dichiara **Vz min11,4V / tip12V / max12,6V solo a IZT=21mA**, impedenza dinamica massima **ZZT=9Ω a IZT=21mA**, impedenza al ginocchio massima **ZZK=700Ω a IZK=0,25mA**. Il dato ZZT=9Ω non è un modello utilizzabile arbitrariamente a pochi mA; il dato ZZK non definisce da solo un limite DC del gate nell'intero intervallo di corrente.

Con Vsource ipotetico massimo **48V**, resistore serie R2102 al minimo **9,5kΩ** e soglia Zener 11,4V, **la corrente assoluta massima del ramo serie è ≤48/9500 ≈5,053mA** anche senza supporre un ginocchio Zener, ossia ben **inferiore alla corrente IZT=21mA** alla quale è garantita la tensione nominale; in caso di due Zener paralleli ciascuno può riceverne una porzione diversa. I modelli precedenti **0,1/1/10Ω con knee a 11/12/13V sono esclusivamente ipotesi sintetiche** e il loro risultato <20V con un singolo Zener OPEN **non fornisce prova di tenuta VGS** su hardware reale. Dimensionamento del resistore, famiglia di clamp a bassa corrente o vera curva di conduzione OEM devono essere rivalutati prima di integrare il circuito o autorizzare hardware. **Finding bloccante addizionale sulla issue #27.**

## Verificatore nativo

`03_Verifiche/V2.7/verify_q806_dual_zener_clamp_native.py`, nella FULL, richiede **ERC KiCad9 0 errori/0 warning**, export netlist reale **27 terminali fisici su 8 reti** senza corto fra source flottante e return. Modello idealizzato con **1.944 condizioni**: ingresso source imposto 0/13,8/20/24/36/48V, R2101/R2102 ±5%, Zener nominale 11/12/13V, resistenza dinamica sintetica 0,1/1/10Ω, stati HEALTHY, D2101 OPEN, D2102 OPEN, BOTH OPEN.

Due Zener uguali `(Vz,Rz)` sono ipotizzati elettricamente identici nel modello: con uno OPEN resta il ramo sano e il gate rimane sotto 20V **solo nelle ipotesi del test**. Se entrambi OPEN la tensione gate segue `Vsource × 47k/(47k+10k)`, ~39,58V a source48V nominale e supera |VGS|20V. **L'eguaglianza dei due Zener non è realisticamente garantita:** possibile squilibrio di corrente per Vz/temperatura/tolleranze, guasto comune per sovratensione, termica e cablaggio. Un corto Zener potrebbe impedire la conduzione anziché creare protezione qualificata. Se il transistor Q806 C-E va in corto la rete di driver può accendere i PMOS indipendentemente da ENABLE: il secondo Zener non risolve questo guasto.

L'attuale `KSP42BU` resta candidato e NON fornisce alcuna alimentazione protetta o supervisore indipendente; il corpo diodo, tab TO220, fault F701/D702, limiti LM393 upstream, reverse, startup, load-dump, SOA, EMC e safety fisica sono aperti. L'ERC dimostra solo coerenza CAD.

**Prossimo requisito:** modello OEM I/V Zener, verifica energia/derating/thermal/latched faults, vero supervisore indipendente con supply immune ai guasti primari, power-good/mute fail-closed, layout THT/PCB reale e review di sicurezza prima di produrre o alimentare.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
