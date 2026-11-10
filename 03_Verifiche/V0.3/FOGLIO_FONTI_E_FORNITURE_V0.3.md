# Sorgenti e stato approvvigionamento — V0.3

## Componenti chiave e alternative
| Referenza | MPN / contenitore | Documento verificabile | Disponibilità e limite |
|---|---|---|---|
| U401 | **Lansdale ML145151YP / PDIP28** | https://www.lansdale.com/datasheets/ML145151_ML145152_ML145155_ML145156_ML145157_ML145158_revA.pdf | Il fabbricante propone quote via https://www.lansdale.com/order_info.php. **Non equivale a stock/disponibilità accertati.** Richiede richiesta offerta e autenticità. |
| U402 | **Toshiba TC74AC74P(F) / DIP14** | https://toshiba.semicon-storage.com/info/docget.jsp?did=3156&prodName=TC74AC74P | Datasheet ufficiale documenta famiglia e package. Reale fornitura ai distributori italiani da verificare al momento dell'ordine. |
| X401 | **Citizen HC-49/U-S10240000ABJB / HC-49US THT** | https://www.digikey.com/en/products/detail/citizen-finedevice-co-ltd/HC-49-U-S10240000ABJB/284210 | Scheda commerciale attiva ma precisione troppo modesta come riferimento SSB finale. Solo bench candidata. |
| Alternativa B | **CD74HC4046AE / DIP16**, contatori **TC74AC161P** DIP16 | https://www.ti.com/product/CD74HC4046A ; https://toshiba.semicon-storage.com/us/semiconductor/product/general-purpose-logic-ics/detail.TC74AC161P.html | Soluzione non disegnata né temporizzata; più circuiteria, non sostituisce direttamente U401. |

## Azioni tecniche non concluse
- Richiedere preventivo `ML145151YP` in quantità piccole, prezzo, lead-time, conformità RoHS e tracciabilità; nessun ordine effettuato.
- Definire target di deriva/accuratezza RX SSB e identificare riferimento quarzo/TCXO **effettivamente THT** o oscillatore discreto compensato regolabile.
- Verificare timing/drive per `TC74AC74P(F)` con clock CMOS 36,31–39,00MHz, incluso massimo fanout, temperatura, margini e commutazione.
- Definire filtri RF del clock e alimentazioni con soppressione spurie e separazione massa. PCB solo dopo KiCad/ERC/DRC e gates.
