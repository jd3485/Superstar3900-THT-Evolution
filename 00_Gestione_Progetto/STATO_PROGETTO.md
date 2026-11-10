# Stato corrente — V0.2, 10 novembre 2026

| Area | Stato |
|---|---|
| Piano RX | 270 posizioni con 30 ALFA, 25,615–28,305 MHz, calcolo e test statici PASS |
| CH9 | D/9 = 27,065 MHz AM prioritario |
| IF1 e LO | 10,695 MHz e 36,310–39,000 MHz, **candidati** |
| PLL matematico | REF 10,240 MHz, R=2048, /2, fPFD 5 kHz, N=3631..3900, tutti interi |
| PLL fisico | Due architetture THT in studio, componenti/pin/timing/sourcing non validati |
| Verifiche | V0.2: 24/24 PASS; V0.1: 12/12 PASS, solo software |
| KiCad, SPICE, EM, hardware | **NON ESEGUITI**, nessuna scheda |
| PCBWay | PCB nude e montaggio interno; nessun file di fabbricazione |
| TX e FAB | **INIBITI, NO FAB / NO TX** |

**Criticità:** approvvigionamento sintetizzatore MC145151P2 legacy, livelli al pin fIN, condizioni di clock del prescaler, VCO, rumore, spur e filtro loop, controllo fisico N e assenza di enable TX. **Prossima V0.3:** circuiti veri e verifica dei componenti prima di qualsiasi PCB.

---

# Stato attuale — V0.1 (10 novembre 2026)

**Fase:** definizione progettuale iniziale, non prototipo fabbricabile.

| Area | Stato |
|---|---|
| Requisiti e vincoli | Prima baseline V0.1 documentata |
| Piano dei moduli | Prima roadmap candidata |
| Frequenze 270 posizioni | Solo vincolo quantitativo; CSV dettagliato **da definire V0.2** |
| PLL/VCO tradizionale | Fattibilità e scelta architettura **aperte** |
| Mixer e filtri RF/IF | Architettura candidata, nessuno schema finalizzato |
| Modulazione TX/finale/antenna | Non progettati; TX bloccata |
| Accordatore manuale | Requisito approvato; rete LC e dimensionamento ancora aperti |
| KiCad ERC/DRC | **NON ESEGUITI**: progetto nativo da costruire |
| Simulazioni elettriche/SPICE/EM | **NON ESEGUITE** |
| PCB e Gerber | **NON CREATI** |
| Prototipi fisici e misure | **ZERO** |
| Assemblaggio | Interno; PCBWay solo fabbricazione PCB nude |
| Autorizzazione fabbricazione | **NO FAB** |
| Autorizzazione emissione RF | **NO TX** |

**Decisioni aperte fondamentali:** requisiti di sensibilità/selettività misurabili; gamma e piano RX completo; frequenze IF e oscillatori; topologia PLL THT e disponibilità componenti; potenza TX legale e obiettivi di prova; architettura singola PCB; dimensioni meccaniche; tensioni di alimentazione e dissipazione; accordatore manuale con limiti di impedenza e potenza da definire.

**Prossima revisione:** V0.2 Piano frequenze e studio PLL classico THT. Una simulazione corretta resta una simulazione: la validazione fisica viene dopo la progettazione e le verifiche necessarie.
