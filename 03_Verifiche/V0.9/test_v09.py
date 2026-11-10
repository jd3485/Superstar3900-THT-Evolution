"""V0.9: static engineering consistency tests only; vendor PFD/VCO loop NOT QUALIFIED."""
import csv,json,math,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"02_Piano_Frequenze/V0.9"))
import pll_tristate_budget_v09 as m
class V09(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
    cls.cfg=json.loads((ROOT/"01_Specifiche/CONFIGURAZIONE_CORRENTE.json").read_text())
    cls.prev=json.loads((ROOT/"01_Specifiche/CONFIGURAZIONE_V0.8.json").read_text())
    cls.data=json.loads((ROOT/"03_Verifiche/V0.9/MISURE_TRISTATE_V0.9.json").read_text())
    cls.deck=(ROOT/"03_Verifiche/V0.9/PDOUT_TRISTATE_SURROGATE_V0.9.cir").read_text()
    cls.doc=(ROOT/"01_Specifiche/V0.9/PDOUT_TRISTATE_FILTRO_V0.9.md").read_text()
    with (ROOT/"04_KiCad/V0.9/PLL_PDOUT_FILTRI_CANDIDATI_V0.9.csv").open(newline="",encoding="utf-8") as f:
        cls.net=list(csv.DictReader(f))
 def test_01_revision(self):self.assertEqual(self.cfg["revision"],"V0.9")
 def test_02_snapshot_v08(self):self.assertEqual(self.prev["revision"],"V0.8")
 def test_03_history_unchanged(self):self.assertTrue((ROOT/"03_Verifiche/V0.8/RAPPORTO_TECNICO_V0.8.md").is_file())
 def test_04_pfd_pin(self):self.assertEqual(m.PDOUT_PIN_ML145151,4)
 def test_05_three_logic_states(self):
    self.assertEqual({x["mode"] for x in self.data["cases"]},{"UP","DOWN","HOLD"})
 def test_06_six_simulated_cases(self):self.assertEqual(len(self.data["cases"]),6)
 def test_07_two_candidate_resistors(self):self.assertEqual(m.R_OPTIONS_OHM,(10000.0,47000.0))
 def test_08_c_known(self):self.assertEqual(m.C_OPTION_F,1e-6)
 def test_09_tau_10ms(self):self.assertAlmostEqual(m.time_constant_s(10000),.01)
 def test_10_tau_47ms(self):self.assertAlmostEqual(m.time_constant_s(47000),.047)
 def test_11_fcorner10k(self):self.assertAlmostEqual(m.corner_hz(10000),15.91549430919)
 def test_12_fcorner47k(self):self.assertAlmostEqual(m.corner_hz(47000),3.38627538493)
 def test_13_attn_10k(self):self.assertTrue(-50<m.attenuation_db(5000,10000)<-49)
 def test_14_attn_47k(self):self.assertTrue(-64<m.attenuation_db(5000,47000)<-63)
 def test_15_pulse_up_moves_positive(self):
    for x in self.data["cases"]:
      if x["mode"]=="UP": self.assertGreater(x["after_first_v"],x["before_v"])
 def test_16_pulse_down_moves_negative(self):
    for x in self.data["cases"]:
      if x["mode"]=="DOWN": self.assertLess(x["after_first_v"],x["before_v"])
 def test_17_hiz_retains_short_term_only(self):
    for x in self.data["cases"]:
      if x["mode"]=="HOLD":self.assertLess(abs(x["final_v"]-x["before_v"]),.002)
 def test_18_rlarger_slower(self):
    values={(x["mode"],x["r_filter_ohm"]):x for x in self.data["cases"]}
    a=values["UP",10000];b=values["UP",47000]
    self.assertGreater(a["after_first_v"]-a["before_v"],b["after_first_v"]-b["before_v"])
 def test_19_leak_not_real_bom(self):
    self.assertEqual(self.data["leak_resistor_ohm"],100e6)
    self.assertIn("DO_NOT_PURCHASE",(ROOT/"07_Componenti/BOM_FILTRO_PLL_V0.9.csv").read_text())
 def test_20_vendor_qualification_false(self):
    self.assertFalse(self.data["vendor_pd_model"])
    self.assertFalse(self.data["closed_pll_loop"])
 def test_21_bias_current_significant(self):
    self.assertAlmostEqual(m.bias_input_drift_v(1),.02,places=5)
 def test_22_kvco_sample_average(self):
    self.assertTrue(.44<m.vco_slope_mhz_v_sampled()<.46)
 def test_23_synthetic_switches(self):
    self.assertIn("S_UP PLL_PD_RAW",self.deck)
    self.assertIn("S_DN PLL_PD_RAW",self.deck)
    self.assertIn(".ic v(PD_FILTER)=2.5",self.deck)
 def test_24_doc_high_z(self):
    self.assertIn("alta impedenza",self.doc)
    self.assertIn("pin 4",self.doc)
 def test_25_pinnet_and_fabrication_gate(self):
    self.assertEqual({x["ref"] for x in self.net},{"U401","R901","C901","R902","U803"})
    self.assertFalse(self.cfg["radio"]["tx_authorized"])
    self.assertFalse(self.cfg["radio"]["fabrication_authorized"])
 def test_26_erc_not_run(self):
    self.assertEqual(self.cfg["validation"]["kicad_erc"],"NOT_RUN")
    self.assertFalse(self.cfg["validation"]["schematic_complete"])
 def test_27_fabrication_off_on_model(self):
    self.assertFalse(m.require_physical_pll_gates()["fabrication_authorized"])
    self.assertFalse(self.data["fabrication_authorized"])
 def test_28_handoff(self):
    self.assertIn("V0.9",(ROOT/"RIPRENDI_IN_UNA_NUOVA_CHAT.md").read_text()[:350])
    self.assertTrue((ROOT/"03_Verifiche/V0.9/RAPPORTO_TECNICO_V0.9.md").is_file())
if __name__=="__main__":unittest.main()
