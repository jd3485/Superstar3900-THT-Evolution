# V2.7 — PMOS anti-serie source comuni: un solo driver guasto apre un percorso direzionale

**16 novembre 2026 — finding di topologia sulla netlist nativa KiCad9; non è una misura, un modello SPICE OEM né una qualifica di sicurezza.** Banco isolato #327 con Q804/Q805 PMOS source comuni, drain rispettivamente ingresso e uscita, gate separati Q806/Q807, doppi Zener 1N4106-1 per gate.

## Dimostrazione di raggiungibilità elettrica idealizzata
In un P-channel IRF9540N il diodo parassita conduce idealmente da **DRAIN a SOURCE**. Con source Q804 e Q805 uniti e gate indipendenti:

| Q804 gate | Q805 gate | Raggiungibilità ingresso→uscita | Raggiungibilità uscita→ingresso |
| --- | --- | --- | --- |
| OFF | OFF | NO | NO |
| ON | OFF | NO | **SÌ**, via diodo Q805 e canale Q804 |
| OFF | ON | **SÌ**, via diodo Q804 e canale Q805 | NO |
| ON | ON | SÌ | SÌ |

I valori **SÌ** indicano solo esistenza di un percorso topologico orientato ideale, **non corrente reale garantita**, tensione soglia, corrente disponibile, dissipazione o prestazione protettiva. La polarizzazione dei diodi, la tensione ai morsetti e il guasto fisico devono essere considerati nel progetto reale.

**Controesempio safety fondamentale:** con entrambi gli ENABLE esterni OFF, un unico guasto Q807 C–E SHORT forza ON il gate Q805, lasciando Q804 OFF; il diodo intrinseco Q804 può collegare l'ingresso alla source comune e Q805 ON può condurre dalla source all'uscita. Quindi l'indipendenza dei due comandi **non** equivale a due interruzioni fisiche indipendenti nella direzione INPUT→OUTPUT. Il caso speculare Q806 C–E SHORT lascia un percorso inverso OUTPUT→INPUT. Quattro Zener, anche perfettamente funzionanti, non chiudono il bypass del body diode.

## Verifica automatizzata
`03_Verifiche/V2.7/verify_twin_gate_directional_body_diode_native.py` esporta la **netlist reale KiCad9 44 pin / 12 reti**, verifica fisicamente drain, source e gate separati, enumera 16 combinazioni idealizzate (ENABLE A/B e C–E SHORT A/B) e vincola il controesempio direzionale. La verifica è registrata in FULL. Nessuna curva OEM né topologia di carico/supervisore è assimilata al test.

## Gate di progettazione successivo
Concretizzare due **interruttori completi bidirezionali** distinti in serie, ciascuno formato da due MOSFET in anti-serie e dotato di proprio pilotaggio/rete di gate, oppure valutare contattori THT/meccanici normalmente aperti adeguatamente qualificati (senza dichiarare safety automatica). Prima scegliere architettura che garantisca assenza di percorso alimentato in entrambe le direzioni per ogni singolo driver ON indebito, verificando diodi, isolamento dei tab TO220, pilotaggio flottante, gate clamps, energia SOA, termico, surge, reference/supply/return comuni, carico reale e guasti single/double. **Nessun collegamento a VIN reale e nessuna PCB finché #27 non chiusa su evidenze OEM e hardware.**

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
