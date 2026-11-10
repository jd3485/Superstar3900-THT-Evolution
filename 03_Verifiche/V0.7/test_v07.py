"""V0.7: analytical THT VTUNE supply checks, historical snapshots and honest gates.
These checks do NOT validate actual MC34063, LM317 or RF emissions.
"""
import csv,json,math,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'02_Piano_Frequenze/V0.7'))
from vtune_power_design_v07 import (
 VIN_MIN_V,VIN_NOMINAL_V,VIN_MAX_V,BOOST_TARGET_V,BOOST_LOAD_DESIGN_A,
 SWITCH_HZ_ASSUMED,LM317_DROPOUT_DESIGN_ASSUMED_V,
 R_SENSE_OHM,L_BOOST_H,RC_FILTER_R_OHM,RC_FILTER_C_F,
 boost_point,booster_target_v,booster_tolerance_window,lm317_target_v,
 lm317_rough_window,ideal_rc_magnitude_db,inductor_energy_rate_w,
 rail_gates,summary)
def csv_read(p):
 with (ROOT/p).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
class V07(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
    cls.cfg=json.loads((ROOT/'01_Specifiche/CONFIGURAZIONE_CORRENTE.json').read_text())
    cls.old=json.loads((ROOT/'01_Specifiche/CONFIGURAZIONE_V0.6.json').read_text())
    cls.data=json.loads((ROOT/'03_Verifiche/V0.7/MISURE_BOOST_V0.7.json').read_text())
    cls.pins=csv_read('04_KiCad/V0.7/VTUNE_ALIMENTAZIONE_PINNET_V0.7.csv')
    cls.nets=csv_read('04_KiCad/V0.7/VTUNE_PASSIVI_NETS_V0.7.csv')
    cls.bom=csv_read('07_Componenti/BOM_VTUNE_ALIMENTAZIONE_V0.7.csv')
    cls.spice=(ROOT/'03_Verifiche/V0.7/BOOST_THT_BEHAVIORAL_V0.7.cir').read_text()
 def test_01_revision_current_v07(self):self.assertEqual(self.cfg['revision'],'V0.7')
 def test_02_previous_revision_v06_immutable_snapshot(self):self.assertEqual(self.old['revision'],'V0.6')
 def test_03_previous_v06_spice_evidence_intact(self):
    self.assertTrue((ROOT/'03_Verifiche/V0.6/VCO_COLPITTS_CANDIDATE_B_V0.6.cir').is_file())
 def test_04_pinnet_pin_count(self):self.assertEqual(len(self.pins),11)
 def test_05_all_pins_unique(self):
    self.assertEqual(len({(x['reference'],int(x['pin'])) for x in self.pins}),11)
 def test_06_u701_complete(self):
    self.assertEqual({int(x['pin']) for x in self.pins if x['reference']=='U701'},set(range(1,9)))
 def test_07_u702_complete(self):
    self.assertEqual({int(x['pin']) for x in self.pins if x['reference']=='U702'},{1,2,3})
 def test_08_boost_switch_and_sense_mapping(self):
    by={(x['reference'],int(x['pin'])):x['net'] for x in self.pins}
    self.assertEqual(by['U701',1],'SW_NODE')
    self.assertEqual(by['U701',7],'VIN_SENSE')
    self.assertEqual(by['U701',5],'BOOST_FB')
    self.assertEqual(by['U701',4],'GND')
 def test_09_lm317_tab_output(self):
    pin=next(x for x in self.pins if x['reference']=='U702' and x['pin']=='2')
    self.assertEqual(pin['net'],'VREG18_RAW');self.assertIn('TAB',pin['signal'])
 def test_10_all_ic_packages_tht(self):
    self.assertEqual({x['package'] for x in self.pins},{'DIP-8','TO-220-3'})
 def test_11_bom_tht_only(self):
    self.assertGreaterEqual(len(self.bom),16)
    for x in self.bom:
      self.assertTrue(any(y in x['package'] for y in ('DIP','TO-220','DO-41','THT','Radial','Axial')))
 def test_12_passive_pinnet(self):self.assertEqual(len(self.nets),16)
 def test_13_assumed_vin_range(self):self.assertEqual((VIN_MIN_V,VIN_NOMINAL_V,VIN_MAX_V),(11.,13.8,15.5))
 def test_14_duty_ratio_worst(self):
    w=boost_point(11);self.assertAlmostEqual(w.on_off_ratio,1.35,places=6)
    self.assertAlmostEqual(w.duty_nominal,1.35/2.35,places=6)
 def test_15_ton_and_toff(self):
    w=boost_point(11);self.assertAlmostEqual(w.on_time_us,14.3617,places=3)
    self.assertAlmostEqual(w.on_time_us+w.off_time_us,25.,places=6)
 def test_16_peak_current_small_margin(self):
    w=boost_point(11)
    self.assertTrue(0.30<w.inductor_delta_i_a<.31)
    self.assertTrue(0<w.sense_limit_a_typ-w.inductor_delta_i_a<.03)
 def test_17_duty_below_80_percent_three_points(self):
    self.assertTrue(all(boost_point(x).duty_nominal<.8 for x in (11,13.8,15.5)))
 def test_18_vout_divider(self):self.assertAlmostEqual(booster_target_v(),23.9583333333333,places=6)
 def test_19_boost_static_tolerances(self):
    lo,hi=booster_tolerance_window();self.assertTrue(23.0<lo<23.1 and 24.8<hi<25.0)
 def test_20_lm317_nominal(self):self.assertAlmostEqual(lm317_target_v(),18.287,places=4)
 def test_21_lm317_window(self):
    lo,hi=lm317_rough_window()
    self.assertAlmostEqual(lo,17.4,places=4);self.assertAlmostEqual(hi,19.174,places=4)
 def test_22_headroom_assumption_not_promotion(self):
    lo,_=booster_tolerance_window();_,hi=lm317_rough_window()
    self.assertGreater(lo-hi,LM317_DROPOUT_DESIGN_ASSUMED_V)
    self.assertFalse(summary()['regulation_verified'])
 def test_23_rc_frequency_at_40k(self):
    self.assertEqual((RC_FILTER_R_OHM,RC_FILTER_C_F),(10.0,100e-6))
    self.assertLess(ideal_rc_magnitude_db(40000),-47)
 def test_24_rc_loaded_drop(self):self.assertAlmostEqual(RC_FILTER_R_OHM*.015,.15,places=6)
 def test_25_lm358_worst_range_inadequate(self):
    min_reg=lm317_rough_window()[0]
    self.assertLess(min_reg-.15-3.0,15.)
 def test_26_analytical_energy_not_vendor_model(self):
    w=boost_point(11)
    self.assertGreater(inductor_energy_rate_w(w.inductor_delta_i_a),BOOST_TARGET_V*BOOST_LOAD_DESIGN_A)
    self.assertFalse(summary()['switch_model_vendor_verified'])
 def test_27_behavioral_model_flag(self):
    self.assertIn('NOT MC34063 transistor-level',self.spice)
    self.assertIn('BGATE GATE',self.spice)
    self.assertNotIn('.subckt mc34063',self.spice.lower())
 def test_28_three_real_ngspice_cases_recorded(self):
    self.assertEqual(len(self.data['vin_v']),3)
    self.assertTrue(all(23<v<25 for v in self.data['boost_average_v']))
 def test_29_noise_not_qualified(self):
    self.assertFalse(self.data['regulator_noise_ripple_qualified'])
    self.assertFalse(self.data['boost_device_validated'])
 def test_30_fail_closed(self):
    self.assertFalse(rail_gates(boost_ok=False,linear_reg_ok=True,vref_ok=True,pll_lock=True,retune_done=True)['rx_unmute_candidate'])
    self.assertTrue(rail_gates(boost_ok=True,linear_reg_ok=True,vref_ok=True,pll_lock=True,retune_done=True)['rx_unmute_candidate'])
 def test_31_no_fab_no_tx(self):
    self.assertFalse(self.cfg['radio']['tx_authorized'])
    self.assertFalse(self.cfg['radio']['fabrication_authorized'])
    self.assertFalse(self.data['fab_authorized'])
 def test_32_kicad_not_executed(self):
    self.assertEqual(self.cfg['validation']['kicad_erc'],'NOT_RUN')
    self.assertEqual(self.cfg['validation']['kicad_drc'],'NOT_RUN')
 def test_33_reports_and_handoff(self):
    self.assertTrue((ROOT/'03_Verifiche/V0.7/RAPPORTO_TECNICO_V0.7.md').is_file())
    self.assertTrue((ROOT/'01_Specifiche/V0.7/ALIMENTAZIONE_VTUNE_THT_V0.7.md').is_file())
    self.assertIn('V0.7',(ROOT/'RIPRENDI_IN_UNA_NUOVA_CHAT.md').read_text()[:300])
if __name__=='__main__':unittest.main()
