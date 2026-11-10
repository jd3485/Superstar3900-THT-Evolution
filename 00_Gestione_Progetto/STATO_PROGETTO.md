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
