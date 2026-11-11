# Gate produttivo obbligatorio — 138 componenti THT della KiCad V2.6

**Audit in data 12 novembre 2026. Esito: BOM NON APPROVATA.**

L'utente chiede di non riprendere il progetto elettrico finché tutti i componenti siano **effettivamente in produzione**, THT, con MPN esatto. L'inventario V2.6 contiene **138 posizioni fisiche**: 45 resistori, 42 condensatori, 22 connettori, 11 diodi, 9 integrati, 5 transistor, 2 induttori, 1 fusibile, 1 quarzo. Non sono 138 MPN diversi: molti Value sono generici. **L'inventario è del solo CAD MAIN parziale, non della PCB FRONT non ancora progettata**.

## Confermati da fonti ORIGINALI sul codice esatto

| Ref | MPN THT | Stato produttore | Fonte |
|---|---|---|---|
| Q801 | Infineon IRF9540NPBF TO-220 | Active | https://www.infineon.com/part/IRF9540N |
| U802 | TI TL431BCLP TO-92 | ACTIVE | https://www.ti.com/product/TL431/part-details/TL431BCLP |
| U520 | TI SN74AC14N PDIP14 | ACTIVE | https://www.ti.com/product/SN74AC14/part-details/SN74AC14N |
| U601 | ST L7805CV TO-220 | Active Product is in volume production, riga MPN esatta | https://www.st.com/en/power-management/l78.html |
| U911 | ST MC34063ABN DIP8 | Active Product is in volume production, riga MPN esatta; precedente contrasto su pagine categoria non prevale su scheda SKU | https://www.st.com/en/power-management/mc34063ab.html |
| D806 | Diotec 1N5352B DO-201 | Life Cycle active; **Lead-free No, RoHS exemption 7(a)-I**: compliance prodotto ancora da esaminare | https://diotec.com/en/product/1N5352B.html |

**6/138 posizioni confermate attive sul MPN effettivo CAD; 132/138 DA_VERIFICARE.** Nessuna delle rimanenti posizioni è stata dichiarata EOL senza dati.

## Candidati attivi ufficiali, ma NON lo stesso codice CAD

- U801: TI LM393N/NOPB PDIP8 ACTIVE, https://www.ti.com/lit/ds/symlink/lm393-n.pdf. Il Value CAD `LM393N_DIP8_DUAL` non definisce /NOPB; verificare pinout e margini 36 V, temperatura.
- U803: TI LM358N/NOPB PDIP8 ACTIVE, https://www.ti.com/lit/ds/symlink/lm358-n.pdf. Nel CAD è `LM358N` senza suffisso e fabbricante.
- U912: TI LM317T/NOPB TO-220 ACTIVE, https://www.ti.com/product/LM317-N/part-details/LM317T/NOPB. In CAD figura **onsemi LM317T**: diversa origine, serve qualificare tab VOUT, limitazioni termiche e pinout.
- U402: Toshiba TC74AC74P(F), DIP14, pagina ufficiale elenca codice ordinabile rappresentativo, https://toshiba.semicon-storage.com/eu/semiconductor/product/general-purpose-logic-ics/detail.TC74AC74P.html: non prova definitivamente produzione continuativa SKU.

## Blocchi critici alla certezza richiesta

1. **U401 ML145151YP PLL DIP28:** Lansdale pubblica il datasheet specifico https://lansdale.com/datasheets/ML145151_ML145152_ML145155_ML145156_ML145157_ML145158_revA.pdf, ma non abbiamo conferma produttiva **attuale sul codice preciso**, distinguendo fabbricazione e NOS/die banking.
2. **L501 Coilcraft 150-05J08L**: conferma lifecycle esatto e proprietà RF ancora mancanti. **L920 Bourns RLB0914-681KL**: la serie e il valore compaiono nel datasheet ufficiale https://www.bourns.com/docs/product-datasheets/rlb.pdf; il datasheet non è una dichiarazione esplicita di stato attivo SKU. Non considerare sufficiente stock dei distributori.
3. **D804/D805 1N5819 40 V, D702 P6KE20CA, D803 1N4742A, F701 0251.500MXL e R1011 Vishay PR03:** confermare MPN specifico, produttore attuale, tensioni/fault/temperatura e RoHS; lo stato di produzione non rende il circuito sicuro.
4. I **45 resistori, 42 condensatori, 22 connettori e X401 quarzo** includono molti soli valori nominali: scegliere per ciascuno MPN THT ancora prodotto, con tolleranze, potenza/dielettrico, RF, passo, coefficiente termico. Anche i codici presenti nella stringa Value devono essere verificati presso il fabbricante.
5. **C805** è annotato DNI: decidere se davvero non verrà montato; posizione simbolica e BOM di montaggio non vanno confuse.

## Controllo di rilascio

Lo script `03_Verifiche/V2.6/verify_mpn_inventory_v26.py` controlla i 138 componenti. In uso normale verifica l'integrità della distinta, non la qualifica. Con argomento `--release` si **blocca** finché anche una singola riga ha lifecycle non confermato. Il gate BOM **NON** è verde e non deve essere descritto come verde anche se KiCad ERC è verde.

**Decisione operativa:** sospendere nuove revisioni elettriche V2.7 e la progettazione PCB finché tutti i componenti attuali (o equivalenti THT realmente prodotti e correttamente sostituiti nello schema) non siano certificati; quindi ripetere il gate anche su tutti i nuovi componenti V2.7 e sulla PCB-FRONT futura. Preservare ADR-001, S-meter analogico, Issue #27 sicurezza, **NO FAB / NO TX / NO BATTERIA/VEICOLO**.
