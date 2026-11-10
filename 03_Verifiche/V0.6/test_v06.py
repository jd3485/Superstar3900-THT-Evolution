"""V0.6 static coherence of real SPICE evidence. 21 checks.
SPICE runs are separate GitHub Actions jobs; these tests do NOT simulate RF.
"""
import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CONFIG=ROOT/'01_Specifiche/CONFIGURAZIONE_CORRENTE.json'
DATA=ROOT/'03_Verifiche/V0.6/MISURE_SPICE_V0.6.json'
class V06(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
    cls.c=json.loads(CONFIG.read_text())
    cls.d=json.loads(DATA.read_text())
    cls.old=(ROOT/'03_Verifiche/V0.5/VCO_COLPITTS_CANDIDATE_V0.5.cir').read_text()
    cls.new=(ROOT/'03_Verifiche/V0.6/VCO_COLPITTS_CANDIDATE_B_V0.6.cir').read_text()
 def test_01_revisions(self):self.assertEqual((self.c['revision'],self.d['revision']),('V0.6','V0.6'))
 def test_02_history_v05_config_preserved(self):
    self.assertEqual(json.loads((ROOT/'01_Specifiche/CONFIGURAZIONE_V0.5.json').read_text())['revision'],'V0.5')
 def test_03_history_v05_netlist_unchanged(self):
    self.assertIn('L501 V9 TANK 150n',self.old)
    self.assertIn('C504 TANK VAR_A 1n',self.old)
 def test_04_first_real_spice_three_points(self):
    v=self.d['historical_v05_rejected'];self.assertEqual(len(v['bias_v']),3)
    self.assertEqual(v['status'],'FAIL_FORWARD_BIAS_AND_TUNING_RANGE')
 def test_05_v05_diode_forward_fails(self):
    self.assertTrue(all(x>0.5 for x in self.d['historical_v05_rejected']['max_diode_forward_v']))
 def test_06_old_vco_cannot_span_band(self):
    a=self.d['historical_v05_rejected']['frequency_mhz']
    self.assertLess(max(a)-min(a),.05)
 def test_07_true_spice_in_workflow(self):
    wf=(ROOT/'.github/workflows/vco_spice_v06.yml').read_text()
    self.assertIn('sudo apt-get install -y -qq ngspice',wf)
    self.assertIn('run_selected_v06.py',wf)
 def test_08_candidate_b_tht(self):
    self.assertIn('Q501 TANK BASE1 EMIT1',self.new)
    self.assertIn('D501A VAR_A VTUNE_RAIL',self.new)
    self.assertIn('D501B VAR_A VTUNE_RAIL',self.new)
 def test_09_new_vco_values(self):
    for line in ('VCC V9 0 PWL(0 0 100n 5)','R503 EMIT1 0 1200',
                 'L501 V9 TANK 166n','C504 TANK VAR_A 470p'):
       self.assertIn(line,self.new)
 def test_10_no_artificial_uic_seed(self):
    self.assertNotIn(' uic',self.new.lower());self.assertNotIn('.ic ',self.new)
 def test_11_bench_has_5_bias_points(self):
    c=self.d['candidateB'];self.assertEqual(len(c['vtune_v']),5)
    self.assertEqual(c['vtune_v'],[8,9,10,12,15])
 def test_12_model_covers_rx_LO(self):
    c=self.d['candidateB'];self.assertLess(min(c['frequency_mhz']),36.310)
    self.assertGreater(max(c['frequency_mhz']),39.000)
 def test_13_varactor_stays_reverse_five_points(self):
    self.assertTrue(all(v<0 for v in self.d['candidateB']['max_anode_minus_cathode_v']))
 def test_14_monotonic_five_samples(self):
    a=self.d['candidateB']['frequency_mhz']
    self.assertTrue(all(x<y for x,y in zip(a,a[1:])))
 def test_15_coarse_36_variants(self):
    self.assertEqual(self.d['exploration']['coarse']['ngspice_runs'],108)
 def test_16_power_ramp_80_transients(self):
    self.assertEqual(self.d['exploration']['ramp_scan']['ngspice_runs'],80)
    self.assertEqual(self.d['exploration']['ramp_scan']['safe_and_cover_screened_model'],4)
 def test_17_need_real_vendor_spice(self):
    self.assertTrue(len(self.d['candidateB']['not_qualified'])>=7)
 def test_18_no_fab_no_tx(self):
    self.assertFalse(self.c['radio']['tx_authorized'])
    self.assertFalse(self.c['radio']['fabrication_authorized'])
    self.assertFalse(self.d['gates']['hardware_validated'])
 def test_19_kicad_not_run(self):
    self.assertEqual(self.d['gates']['kicad_erc'],'NOT_RUN')
    self.assertEqual(self.c['validation']['kicad_drc'],'NOT_RUN')
 def test_20_handoff_and_report(self):
    self.assertTrue((ROOT/'03_Verifiche/V0.6/RAPPORTO_TECNICO_V0.6.md').is_file())
    self.assertTrue((ROOT/'01_Specifiche/V0.6/VCO_SIMULAZIONE_E_CORREZIONI_V0.6.md').is_file())
 def test_21_constraints(self):
    self.assertEqual(self.c['build']['technology'],'THT_ONLY')
    self.assertEqual(self.c['build']['assembly'],'IN_HOUSE')
    self.assertEqual(self.c['build']['board_order_type'],'BARE_PCB_ONLY')
if __name__=='__main__':unittest.main()
