"""V0.1: controlli statici di continuità/requisiti. NON prove elettriche.
Eseguire da root: python3 -m unittest discover -s 03_Verifiche/V0.1 -p 'test_*.py' -v
"""
from pathlib import Path
import csv
import json
import unittest

ROOT = Path(__file__).resolve().parents[2]
C = json.loads((ROOT / "01_Specifiche/CONFIGURAZIONE_V0.1.json").read_text(encoding="utf-8"))

class BaselineV01(unittest.TestCase):
    def test_progetto_indipendente(self):
        self.assertTrue(C["independent_project"])
        self.assertEqual(C["slug"], "Superstar3900-THT-Evolution")
    def test_solo_tht_no_adattatori(self):
        b=C["build"]
        self.assertEqual(b["technology"],"THT_ONLY")
        self.assertFalse(b["allow_smd_components"])
        self.assertFalse(b["allow_smd_to_dip_adapters"])
    def test_pcbway_solo_schede_nude(self):
        b=C["build"]
        self.assertEqual(b["board_fabricator"],"PCBWay")
        self.assertEqual(b["board_order_type"],"BARE_PCB_ONLY")
        self.assertEqual(b["assembly"],"IN_HOUSE")
    def test_bande_e_270_posizioni_rx(self):
        r=C["radio"]
        self.assertEqual(r["bands"],list("ABCDEF"))
        self.assertEqual(r["total_rx_positions"],len(r["bands"])*(r["normal_positions_per_band"]+r["alpha_positions_per_band"]))
    def test_modes_and_comandi(self):
        r=C["radio"]
        self.assertEqual(r["rx_modes"],["AM","FM","USB","LSB","CW"])
        self.assertTrue(r["channel_9_priority"] and r["physical_alpha_control"])
    def test_tuner_manuale_e_pll_tradizionale(self):
        r=C["radio"]
        self.assertTrue(r["manual_tuner"] and r["tuner_bypass"])
        self.assertEqual(r["pll_approach"],"TRADITIONAL_THT_CANDIDATE")
    def test_esclusioni_concordate(self):
        self.assertEqual(set(C["excluded_features"]),{
            "advanced_audio_dsp","modern_integrated_rf_pll","dual_watch","ctcss_dcs","vox","automatic_antenna_tuner"})
    def test_fabbricazione_e_tx_bloccate(self):
        r=C["radio"]
        self.assertFalse(r["tx_authorized"])
        self.assertFalse(r["fabrication_authorized"])
        self.assertEqual(C["validation"]["hardware_prototypes"],0)
    def test_non_dichiarare_verifiche_non_fatte(self):
        for key in ("kicad_erc","kicad_drc","spice","rf_lab"):
            self.assertEqual(C["validation"][key],"NOT_RUN")
    def test_continuita_tra_chat(self):
        for name in ("README.md","RIPRENDI_IN_UNA_NUOVA_CHAT.md","00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md","00_Gestione_Progetto/REGISTRO_DECISIONI.md","00_Gestione_Progetto/STATO_PROGETTO.md"):
            self.assertTrue((ROOT/name).is_file(),name)
    def test_piano_freq_non_spacciato_per_completo(self):
        path=ROOT/"02_Piano_Frequenze/PIANO_FREQUENZE_RX_DA_COMPILARE_V0.2.csv"
        with path.open(newline="",encoding="utf-8") as f:
            self.assertEqual(len(list(csv.DictReader(f))),0)
        self.assertEqual(C["radio"]["frequency_table_status"],"NOT_DEFINED")
    def test_bom_non_inventata(self):
        path=ROOT/"07_Componenti/BOM_MASTER_V0.1.csv"
        with path.open(newline="",encoding="utf-8") as f:
            self.assertEqual(len(list(csv.DictReader(f))),0)

if __name__ == "__main__": unittest.main()
