# S-meter FRONT: carico sulla sorgente di tensione candidata, con buffer MAIN ancora assente

**16 novembre 2026. Studio teorico non qualificato.**

Il percorso KiCad9 FRONT J1801/1, potenziometro RV1801 da 10 kΩ, resistori seriali R1801/R1802 da 100 kΩ e carico ipotetico J1802 è stato verificato tramite netlist nativa KiCad9. La corrente del movimento non coincide con la corrente che il driver di tensione deve erogare: la pista RV1801 assorbe corrente anche quando il movimento è scarico o il cursore viene ruotato.

Il verificatore `verify_smeter_passive_source_loading_native.py` esplora **675 scenari**: tensioni ideali a vuoto 5/9/11/15/20 V, resistenze di uscita del driver ipotetiche 0/100/1000 Ω, carichi ipotetici 1 kΩ/20 kΩ/40 kΩ, zero/uno/due resistori di protezione in corto, cinque posizioni cursore 0/10/50/90/100%. Calcola indipendentemente per ciascun caso la tensione terminale, corrente richiesta alla sorgente, corrente verso movimento e corrente verso il ramo inferiore del potenziometro, mediante partitore caricato Thévenin e KCL nodale a due nodi; confronta e obbliga la conservazione delle correnti.

| Caso ipotetico | Risultato teorico |
|---|---|
| Fonte ideale 11 V, Rcoil 20 kΩ, 2×100 kΩ intatti, cursore al massimo | I metro 50 µA; I pista RV1801 1,10 mA; I sorgente 1,15 mA |
| Come sopra, dissipazione della pista a 11 V | 12,1 mW, **non** limite PVT/MPN |
| Fonte ideale 5 V, Rcoil 20 kΩ, cursore al massimo | I metro 22,727 µA; I pista 0,50 mA; I sorgente 0,522727 mA |
| Fonte a vuoto 11 V con 1 kΩ in serie al driver | Tensione terminale ridotta, corrente metro inferiore a 50 µA |

**Rischi/limiti:** nessuna tensione MAIN prodotta da uno stadio hardware, impedenza o massimo corrente driver approvati, classe termica del potenziometro, FSD reale, cable shield/return, guasti di cursore e transitori. I due resistori 100 kΩ appartengono alla rete passiva storica e **non** sono il driver a corrente 5 V di studio; non fonderli automaticamente. Esito della CI nativa obbligatorio prima del merge. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
