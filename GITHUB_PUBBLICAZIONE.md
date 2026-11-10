# Nota cumulativa V0.2

La V0.2 **non rigenera ZIP** né sostituisce la V0.1: il commit su `main` conserva il progetto completo e i file invariati. Per ricostruire la V0.2 usare lo SHA del commit; `MANIFEST_SHA256_V0.1.csv` riguarda esclusivamente la V0.1 e non va applicato al `main` aggiornato. Un tag v0.2 non è dichiarato finché non creato e verificato. A ogni futura revisione aggiungere/modificare soltanto i percorsi necessari.

---

# GitHub — pubblicazione e gestione cumulativa V0.1

**Repository privata:** `jd3485/Superstar3900-THT-Evolution`  
**URL:** https://github.com/jd3485/Superstar3900-THT-Evolution  
**Branch di riferimento:** `main`.

## Regola permanente
GitHub conserva l'intero albero cumulativo a ogni commit. **Non rigenerare e non caricare ZIP completi per ogni revisione.** Aggiungere soltanto file nuovi o modificati; gli altri restano invariati. I commit storici e gli eventuali tag permettono di recuperare le baseline precedenti. Uno ZIP di una revisione, se necessario, si scarica dal suo commit/tag.

## Per ogni revisione «Continua»
1. Controllare HEAD `main`, tag, PR, CI e leggere i file di continuità.
2. Studiare il modulo successivo e produrre documenti, BOM, schemi, calcoli e test pertinenti.
3. Eseguire verifiche reali e registrare PASS/FAIL/SKIP/NON ESEGUITO senza promuovere simulazioni a misure hardware.
4. Aggiornare solo i percorsi nuovi o modificati, incluso rapporto di revisione, README/stato, registro decisioni e `RIPRENDI_IN_UNA_NUOVA_CHAT.md`.
5. Integrare la revisione coerente in `main`; non forzare risultati bloccanti.
6. Non sovrascrivere né spostare tag preesistenti; i manifest SHA-256 delle vecchie baseline valgono solo per la versione a cui si riferiscono.

## Stato V0.1
Baseline documentale, 12/12 test statici; nessuna simulazione circuitale, nessun ERC/DRC o prototipo. NO FAB / NO TX.

## Stato del tag
La presenza di `main` e dei file va verificata su GitHub. Un tag `v0.1` è utile ma non deve essere dichiarato esistente prima della sua effettiva creazione.
