# S-meter passivo FRONT: tensione sorgente necessaria al fondo scala (solo analisi)

Data: 16 novembre 2026. Candidato indipendente dal driver S-meter a corrente di laboratorio. **Nessun fondo scala, sorgente MAIN o movimento approvato.**

Il foglio KiCad9 `FRONT_SMETER_THT_V2_7_DRAFT.kicad_sch` collega J1801/1 alla pista alta RV1801 (10 kΩ), il cursore alla serie R1801+R1802 (100 kΩ ciascuno) e al J1802/1 movimento; J1802/2 e pista bassa tornano a J1801/2. Il verificatore `verify_smeter_passive_source_fsd_compliance_native.py` controlla **tutte le cinque reti** e le connessioni per pin dalla netlist KiCad9, poi esegue 675 condizioni: 5 tensioni sorgente, 3 resistenze di movimento ipotetiche, 3 stati di cortocircuito dei limitatori, 5 posizioni cursore, 3 ipotesi FSD. Il modello del potenziometro è un partitore **caricato**, non un semplice partitore a vuoto. L'assenza di resistenza di bobina con entrambi i limitatori in corto produce **15 condizioni senza limite ohmico finito** quando il cursore è al 100% del potenziometro e V sorgente è non nulla (5 tensioni × 3 FSD). Negli altri 45 casi con bobina ipoteticamente da 0Ω e doppio corto, la porzione superiore della pista da 10kΩ limita la corrente: il calcolo fornisce un limite superiore conservativo, non la corrente effettiva nella bobina. A cursore 0, il riparto fra pista inferiore e ramo bobina, entrambi di resistenza nulla nell'idealizzazione, è indeterminato; non va interpretato come misura.

| Condizione ipotetica | Corrente massima a 5 V, cursore massimo |
|---|---:|
| Due 100 kΩ nominali e bobina 20 kΩ | 22,727 µA |
| Due 100 kΩ nominali, bobina trascurabile | 25,000 µA |
| Un 100 kΩ nominale in corto, bobina 20 kΩ | 41,667 µA |
| Entrambi i 100 kΩ in corto, bobina 20 kΩ | 250,000 µA |
| Entrambi in corto, bobina ipotetica 0Ω, cursore al massimo | Nessun limite finito |
| Entrambi in corto, bobina ipotetica 0Ω, cursore al 50% | ≤ 1 mA (limite superiore dal tratto superiore 5 kΩ) |

Per un movimento ipotetico **FSD=50µA e 20 kΩ**, servirebbero **almeno 11 V** al massimo del cursore se R1801/R1802 restassero entrambi a 100 kΩ; ipotizzandoli entrambi -5%, **10,5 V**. Per un singolo cortocircuito e una resistenza residua -5%, l'ipotesi FSD richiederebbe 5,75 V; non è un punto di funzionamento valido da scegliere, bensì un esempio di sensibilità ai guasti. All'aumentare della temperatura, con tensione sorgente non ideale, sul cavo e sul driver reale i risultati possono differire. Né la rete storica a 2×100k né il progetto separato di driver active-sink possono essere approvati senza scegliere la vera bobina, limite di corrente hardware e interfaccia MAIN/FRONT.

Questa analisi NON dimostra accuratezza scala S1–S9/+dB, robustezza a guasti o conformità EMC. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
