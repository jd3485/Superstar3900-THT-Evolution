"""V0.2: test di aritmetica RX e coerenza file. NON test elettrici.
Eseguire da root: python3 -m unittest discover -s 03_Verifiche/V0.2 -p 'test_*.py' -v
"""
import csv,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'02_Piano_Frequenze/V0.2'))
from frequency_plan_v02 import (CHANNEL_D_KHZ,BAND_OFFSET_KHZ,ALPHAS,frequency_hz,rx_plan,all_rows,apply_ch9_priority,FPFD_HZ,R_REF,FREF_HZ,PRESCALER)
CSV=ROOT/'02_Piano_Frequenze/V0.2/PIANO_RX_PLL_270_V0.2.csv'
CFG=json.loads((ROOT/'01_Specifiche/CONFIGURAZIONE_V0.2.json').read_text(encoding='utf-8'))
class V02(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with CSV.open(newline='',encoding='utf-8') as f: cls.data=list(csv.DictReader(f))
    def test_01_table_270(self):
        self.assertEqual(len(self.data),270);self.assertEqual(len(all_rows()),270)
    def test_02_bands_45(self):
        self.assertEqual({b:sum(r['banda']==b for r in self.data) for b in 'ABCDEF'},dict.fromkeys('ABCDEF',45))
    def test_03_alphas_30(self):
        self.assertEqual(sum(int(r['alfa']) for r in self.data),30)
        self.assertEqual({r['canale'] for r in self.data if r['banda']=='D' and int(r['alfa'])},{'3A','7A','11A','15A','19A'})
    def test_04_grid_complete(self):
        freqs=sorted(int(r['rf_hz']) for r in self.data)
        self.assertEqual(freqs,list(range(25_615_000,28_305_000+1,10_000)))
    def test_05_source_fixed_ch23_24_25(self):
        self.assertEqual(CHANNEL_D_KHZ[22:25],(27255,27235,27245))
        self.assertEqual([frequency_hz('D',x) for x in (23,24,25)],[27_255_000,27_235_000,27_245_000])
    def test_06_ch9_priority(self):
        self.assertEqual(frequency_hz('D',9),27_065_000)
        self.assertEqual(apply_ch9_priority(ch9_pressed=True,band='F',channel=37,alpha=False,mode='FM'),('D',9,False,'AM'))
        self.assertEqual(sum(int(r['ch9_prioritario']) for r in self.data),1)
    def test_07_invalid_channel_band_alpha(self):
        for params in [('G',1,False),('D',0,False),('D',41,False),('D',4,True)]:
            with self.assertRaises(ValueError):frequency_hz(*params)
    def test_08_all_csv_vs_generator(self):
        exp=all_rows();self.assertEqual(len(exp),len(self.data))
        for a,b in zip(exp,self.data):
            self.assertEqual((a['banda'],str(a['ordine_banda']),a['canale'],str(a['alfa'])),(b['banda'],b['ordine_banda'],b['canale'],b['alfa']))
            for field,match in [('rf_hz','rf_hz'),('lo_hz','lo1_high_hz'),('image_hz','immagine1_hz'),('n','n_div'),('n_bin14','n_bin14'),('fin_hz','f_feedback_hz')]:
                self.assertEqual(str(a[field]),b[match])
    def test_09_lo_range(self):
        self.assertEqual((min(int(r['lo1_high_hz']) for r in self.data),max(int(r['lo1_high_hz']) for r in self.data)),(36_310_000,39_000_000))
    def test_10_lo_image_range(self):
        self.assertEqual((min(int(r['immagine1_hz']) for r in self.data),max(int(r['immagine1_hz']) for r in self.data)),(47_005_000,49_695_000))
    def test_11_int_n_all_points(self):
        for r in self.data:
            self.assertEqual(int(r['lo1_high_hz']),2*int(r['n_div'])*int(r['f_comparatore_hz']))
            self.assertEqual(int(r['lo1_high_hz'])//2,int(r['f_feedback_hz']))
            self.assertTrue(3<=int(r['n_div'])<=16383)
    def test_12_r_2048_to_5khz(self):
        self.assertEqual((FREF_HZ,R_REF,FPFD_HZ,PRESCALER),(10_240_000,2048,5_000,2))
        self.assertEqual({int(r['r_div']) for r in self.data},{2048})
    def test_13_n_range(self):
        self.assertEqual((min(int(r['n_div']) for r in self.data),max(int(r['n_div']) for r in self.data)),(3631,3900))
    def test_14_n_14bits(self):
        for r in self.data:
            self.assertEqual(len(r['n_bin14']),14);self.assertEqual(int(r['n_bin14'],2),int(r['n_div']))
    def test_15_feedback_range(self):
        self.assertEqual((min(int(r['f_feedback_hz']) for r in self.data),max(int(r['f_feedback_hz']) for r in self.data)),(18_155_000,19_500_000))
    def test_16_rx_only_fail_closed(self):
        self.assertTrue(all(r['tx_permitted']=='0' for r in self.data))
        self.assertFalse(CFG['radio']['tx_authorized']);self.assertFalse(CFG['radio']['fabrication_authorized'])
    def test_17_previous_v01_still_valid(self):
        self.assertTrue((ROOT/'01_Specifiche/CONFIGURAZIONE_V0.1.json').is_file())
        self.assertEqual(json.loads((ROOT/'01_Specifiche/CONFIGURAZIONE_V0.1.json').read_text())['revision'],'V0.1')
    def test_18_revision_v02_current(self):
        self.assertEqual(CFG['revision'],'V0.2')
        self.assertEqual(CFG['radio']['frequency_table_status'],'NUMERIC_RX_CANDIDATE_VERIFIED')
    def test_19_no_smd_or_auto_tuner(self):
        self.assertEqual(CFG['build']['technology'],'THT_ONLY')
        self.assertIn('automatic_antenna_tuner',CFG['excluded_features'])
        self.assertTrue(CFG['radio']['manual_tuner'])
    def test_20_legacy_pll_not_marked_approved(self):
        with (ROOT/'07_Componenti/BOM_PLL_CANDIDATI_V0.2.csv').open(newline='',encoding='utf-8') as f:components=list(csv.DictReader(f))
        self.assertEqual(len(components),6)
        self.assertTrue(all('APPROVATO' not in c['stato'] or 'NON APPROVATO' in c['stato'] for c in components))
    def test_21_out_of_range_source(self):
        self.assertEqual(len(CHANNEL_D_KHZ),40);self.assertEqual(tuple(sorted(ALPHAS)),ALPHAS)
    def test_22_ch9_false_keeps_state(self):
        self.assertEqual(apply_ch9_priority(ch9_pressed=False,band='C',channel=11,alpha=True,mode='LSB'),('C',11,True,'LSB'))
    def test_23_second_conversion_math(self):
        self.assertEqual(10_695_000-10_240_000,455_000);self.assertEqual(10_240_000-455_000,9_785_000)
    def test_24_consistent_csv_order_1_to_45(self):
        for b in 'ABCDEF':
            self.assertEqual([int(r['ordine_banda']) for r in self.data if r['banda']==b],list(range(1,46)))
if __name__=='__main__':unittest.main()
