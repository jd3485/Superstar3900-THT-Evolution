# Registro prove V0.9

**Evidenze su sottosistemi, non sulla radio completa**.

| Prova | Stato iniziale V0.9 | Nota |
|---|---|---|
| 33 nuovi test statici Python | NOT_RUN finché non esegue CI di PR | Suite cumulativa V0.1..V0.8 già 226 test |
| ngspice tre stati e leakage | NOT_RUN finché non esegue CI | Non modello vendor, non loop PLL |
| KiCad 9 native ERC sul solo sub-sheet | DA VERIFICARE SU RUN CI | Prima serie fallita per formato/generatori; correggere e distinguere |
| KiCad ERC completo radio | NOT_RUN | U401 U402, VCO e power supply non integrati |
| KiCad DRC PCB | NOT_RUN | Nessun PCB |
| RF/EMC/hardware | NOT_RUN | Nessun prototipo |
| Produzione e TX | BLOCKED | NO FAB / NO TX |

Run e risultati effettivi devono essere aggiornati **dopo** le verifiche GitHub.
