# Audit passivi THT V2.6 — lotto 2: ceramici PLL, VCO e bypass 5V (12 novembre 2026)

## Sintesi e limiti della prova
Dopo il merge [PR #48](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/48), SHA `9d714b41e223eb7e940b0d533ec7dc401acb6ed1`, CI #43248555956 tutti e 3 i job PASS, si sono esaminate **otto ulteriori posizioni fisiche**. Nessuna qualifica di produzione OEM è stata riconosciuta; **6/138 ATTIVO_CONFERMATO; 132/138 DA_VERIFICARE**. Nessuna modifica KiCad o ai blocchi release.

Fonte primaria: cross-reference [Vishay 45177, revisione 23 agosto **2012**](https://www.vishay.com/docs/45177/crmllccspraguevsbcc.pdf). Il timestamp di pubblicazione nei motori di ricerca non modifica la data del documento originale. È una prova di corrispondenza commerciale storica, **non** che i codici esatti siano fabbricati oggi. Per la gamma di prodotto e i parametri generali vedere anche [datasheet Vishay K Series](https://www.vishay.com/docs/45171/kseries.pdf), anch'esso non sufficiente a certificare ogni codice d'ordine.

| Riferimenti CAD | Valore CAD e impronta | Codice candidato nella cross-reference OEM | Dati tabella | Gate non superati |
|---|---|---|---|---|
| C403, C404 PLL | 22 pF, C_Disc_D3.0mm_W1.6mm_P2.50mm | **K220J15C0GF53L2** | 22 pF, 50 V, C0G, ±5%, passo **2.54 mm** | Fabbricazione SKU attuale, CL quarzo/capacità parassite, precisione, temperatura, dimensioni corpo e passo vs CAD |
| C507, C510 VCO | 100 pF, stesso footprint | **K101J15C0GF53L2** | 100 pF, 50 V, C0G, ±5%, passo **2.54 mm** | Fabbricazione, Q/potenze RF, TC, microfonicità, geometria, tolleranze su sintonia |
| C602, C614, C615, C616 distribuzione +5V | 100 nF 25 V nominale CAD, stesso footprint | **K104K15X7RF53L2** | 100 nF, **50 V**, X7R, ±10%, passo **2.54 mm** | Fabbricazione, fattore DC-bias, invecchiamento, ESR/ESL, tempera, compatibilità sagoma e ruolo di ogni decoupler |

## Risultati tecnici
1. **Separazione C0G da X7R obbligatoria.** Per i picofarad del PLL/VCO non sostituire indiscriminatamente con classe 2: la deriva e non-linearità altererebbero il comportamento RF. Per i bypass 100nF X7R è un candidato ma la capacità effettiva varia con tensione continua e temperatura.
2. **Differenza di passo**: il dato tabellare 2.54 mm non coincide letteralmente con il pad pitch 2.50 mm CAD (differenza 0.04 mm). Non affermiamo che sia meccanicamente impossibile, ma **nemmeno un match esatto**: sagoma, lead, fori e criteri IPC da verificare e documentare sulla dimensione reale. Inoltre Ø3.0/W1.6 dell'impronta potrebbe risultare incompatibile con il corpo del candidato.
3. **Anche per una famiglia nominale comune, il MPN OEM e la qualifica restano individuali**; i condensatori C403/C404 richiedono analisi del carico reale del quarzo PLL, C507/C510 analisi del VCO. Quattro bypass C602/C614/C615/C616 richiedono valutazione dell'ambiente +5V e dei transitori.
4. Non è stata svolta una verifica quantitativa della capacità di carico del quarzo, della catena RF/VCO, né una simulazione vendor o DRC/layout PCB. Queste restano attività distinte, non sottintese dal gate GitHub documentale.
5. Per trovare componenti THT **davvero attivi** non bastano una tabella OEM del 2012 o stock di distributore: richiedere stato di ordinabilità/produzione nuovi lotti presso Vishay o selezionare gamma attuale con dati ufficiali sullo SKU preciso, e completare le prove elettriche/meccaniche.

## Decisione di rilascio
**Nessuna nuova posizione qualificata; nessuna sostituzione elettrica approvata.** Conservare `INVENTARIO_MPN_V26.csv` con tutti i 138 riferimenti, `--release` intenzionalmente bloccato. Fino al superamento del gate OEM e del blocco sicurezza Issue #27: STOP V2.7, NO PCB/GERBER/FAB, NO TX, NO batteria/veicolo. La PCB-FRONT resta da progettare e richiederà verifica dei suoi nuovi componenti THT.
