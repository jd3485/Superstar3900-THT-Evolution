"""V0.9: independent static engineering checks for 3-state PDout THT loop sheet.
These tests do NOT imply phase lock, ERC of the whole radio or RF qualification.
Native ERC is a SEPARATE GitHub Actions job on the partial sheet.
"""
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'02_Piano_Frequenze/V0.9'))
from pll_loop_model_v09 import (
 F_PFD_HZ,PD_VDD_V,PD_PIN,LD_PIN,PDOUT_ON_LOCK,LOOP_R_OHM,LOOP_C_F,
 LOOP_GAIN_ASSUMED,BIAS_CURRENT_ASSUMED_A,REF_FREQUENCY_HZ,R_DIVIDER,PRESCALER,
 source_points,linear_segments,rc_5khz_attenuation_db,
 nominal_hold_voltage_drift,max_frequency_drift_assumed_hz,
 rx_unmute_contract,summary)
SCHEM=ROOT/'04_KiCad/V0.9/PLL_LOOP_RX_PARTIAL_V0.9.kicad_sch'
class V09(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
    cls.cfg=json.loads((ROOT/'01_Specifiche/CONFIGURAZIONE_CORRENTE.json').read_text())
    cls.prev=json.loads((ROOT/'01_Specifiche/CONFIGURAZIONE_V0.8.json').read_text())
    cls.deck=(ROOT/'03_Verifiche/V0.9/PLL_TRISTATE_HOLD_V0.9.cir').read_text()
    cls.design=(ROOT/'01_Specifiche/V0.9/PLL_TRISTATE_LOOP_THT_V0.9.md').read_text()
    cls.sch=SCHEM.read_text() if SCHEM.exists() else ''
 def test_01_revision(self):self.assertEqual(self.cfg['revision'],'V0.9')
 def test_02_old_snapshot(self):self.assertEqual(self.prev['revision'],'V0.8')
 def test_03_previous_bench_retained(self):
    self.assertTrue((ROOT/'03_Verifiche/V0.8/VTUNE_DRIVER_BEHAVIORAL_V0.8.cir').is_file())
 def test_04_three_state_pin_correct(self):
    self.assertEqual((PD_PIN,LD_PIN),(4,28))
 def test_05_pdout_high_z(self):self.assertEqual(PDOUT_ON_LOCK,'HIGH_IMPEDANCE')
 def test_06_pfd_clock(self):
    self.assertEqual(REF_FREQUENCY_HZ/R_DIVIDER,F_PFD_HZ)
    self.assertEqual((F_PFD_HZ,PRESCALER),(5000.,2))
 def test_07_load_vco_real_sim_data_not_new_estimate(self):
    p=source_points();self.assertEqual(len(p),5)
    self.assertEqual([x[0] for x in p],[8.,9.,10.,12.,15.])
 def test_08_vco_coverage_sample(self):
    p=source_points();self.assertLess(p[0][1],36.31e6)
    self.assertGreater(p[-1][1],39e6)
 def test_09_monotonic_vco_in_model(self):
    ps=source_points();self.assertTrue(all(a[1]<b[1] for a,b in zip(ps,ps[1:])))
 def test_10_segments(self):self.assertEqual(len(linear_segments()),4)
 def test_11_worst_kvco(self):
    rows=linear_segments()
    self.assertTrue(.75e6<rows[0].sample_kvco_hz_per_v<.77e6)
 def test_12_low_kvco(self):self.assertTrue(.30e6<linear_segments()[-1].sample_kvco_hz_per_v<.32e6)
 def test_13_total_divider_includes_prescaler(self):
    for d in linear_segments():
       self.assertTrue(7000<d.total_divider_nominal<8000)
 def test_14_loop_values(self):self.assertEqual((LOOP_R_OHM,LOOP_C_F),(22_000.,100e-9))
 def test_15_linear_fn(self):
    rows=linear_segments()
    self.assertTrue(100<rows[0].natural_frequency_hz<115)
    self.assertTrue(60<rows[-1].natural_frequency_hz<75)
 def test_16_zeta_low(self):
    self.assertTrue(.30<linear_segments()[0].damping_factor<.35)
 def test_17_zeta_changes_with_vco_gain(self):
    rows=linear_segments()
    self.assertGreater(rows[-1].damping_factor,rows[0].damping_factor)
 def test_18_damping_not_sufficiently_qualified(self):
    self.assertTrue(all(d.damping_factor<.55 for d in linear_segments()))
    self.assertFalse(summary()['verified_phase_margin'])
 def test_19_small_signal_overshoot_risk(self):
    self.assertTrue(all(x.overshoot_fraction_ideal>.1 for x in linear_segments()))
 def test_20_5khz_filter_rejection_ideal(self):
    self.assertTrue(-38<rc_5khz_attenuation_db()<-36)
 def test_21_hold_bias_assumption(self):
    self.assertEqual(BIAS_CURRENT_ASSUMED_A,20e-9)
    self.assertAlmostEqual(nominal_hold_voltage_drift(),.012,places=6)
 def test_22_hold_frequency_error_illustration(self):
    self.assertGreater(max_frequency_drift_assumed_hz(),8000)
    self.assertFalse(summary()['full_vco_closed_loop_model'])
 def test_23_data_from_legacy_not_hardware(self):
    self.assertFalse(summary()['frequency_accuracy_hardware_verified'])
 def test_24_pulse_deck_no_vendor_model(self):
    self.assertIn('S_TRI',self.deck)
    self.assertIn('SUP PLL_PDOUT',self.deck)
    self.assertIn('SDN PLL_PDOUT',self.deck)
    self.assertNotIn('.subckt ML145151',self.deck.lower())
 def test_25_pulse_deck_hold_cap(self):
    self.assertIn('R901 PLL_PDOUT PD_FILTER 22k',self.deck)
    self.assertIn('C901 PD_FILTER 0 100n IC=2.5',self.deck)
 def test_26_kicad_native_file_present(self):
    self.assertTrue(SCHEM.is_file())
    self.assertIn('(kicad_sch (version 20250114)',self.sch)
 def test_27_embedded_tht_lm358_and_rc(self):
    for tok in ('THT_V09:LM358N_PDIP8','(lib_id "THT_V09:Resistor")','"PD_FILTER"','"VTUNE_RAIL"'):
        self.assertIn(tok,self.sch)
 def test_28_c805_explicitly_dni(self):
    self.assertIn('C805',self.sch)
    self.assertIn('(dnp yes)',self.sch)
 def test_29_erc_gate_separate_from_software(self):
    wf=(ROOT/'.github/workflows/kicad_erc_v09.yml').read_text()
    self.assertIn('kicad-cli sch erc',wf)
    self.assertIn('--exit-code-violations',wf)
    self.assertFalse(self.cfg['validation']['schematic_complete'])
 def test_30_mute_fail_closed(self):
    defaults=dict(supply_ok=True,ref_ok=True,ld_stable=False,channel_stable=True,settling_elapsed=True)
    self.assertFalse(rx_unmute_contract(**defaults)['rx_unmute_allowed'])
    defaults['ld_stable']=True
    self.assertTrue(rx_unmute_contract(**defaults)['rx_unmute_allowed'])
    self.assertFalse(rx_unmute_contract(**defaults)['rf_tx_enable'])
 def test_31_no_tx_no_fab(self):
    self.assertFalse(self.cfg['radio']['tx_authorized'])
    self.assertFalse(self.cfg['radio']['fabrication_authorized'])
 def test_32_full_erc_not_run(self):
    self.assertEqual(self.cfg['validation']['kicad_drc'],'NOT_RUN')
    self.assertEqual(summary()['kicad_full_radio_erc'],'NOT_RUN')
 def test_33_reports_and_handoff(self):
    self.assertTrue((ROOT/'03_Verifiche/V0.9/RAPPORTO_TECNICO_V0.9.md').is_file())
    self.assertIn('V0.9',(ROOT/'RIPRENDI_IN_UNA_NUOVA_CHAT.md').read_text()[:300])
if __name__=='__main__':unittest.main()
