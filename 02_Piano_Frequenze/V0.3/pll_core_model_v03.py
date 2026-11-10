"""V0.3: modello RX-only aritmetico, NON simulazione elettrica."""
import math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'02_Piano_Frequenze/V0.2'))
from frequency_plan_v02 import rx_plan
PLL='ML145151YP'
DIV2='TC74AC74P(F)'
FREF=10_240_000
R=2048
PRESCALER=2
FPFD=FREF//R
N_TO_PIN={0:11,1:12,2:13,3:14,4:15,5:16,6:17,7:18,8:19,9:20,10:24,11:25,12:22,13:23}
LO_MIN=36_310_000
LO_MAX=39_000_000
FF_CLK_MIN_GUARANTEED_5V=100_000_000
PLL_FIN_DATASHEET_LIMIT_5V_85C_SQUARE=22_000_000

def channel_state(band,channel,alpha=False):
    p=rx_plan(band,channel,alpha)
    n=p['n']
    bits={i:(n>>i)&1 for i in range(14)}
    if bits[12] or bits[13]:raise ValueError('N12/N13 must be zero')
    return dict(n=n,n_bits=bits,pin_levels={N_TO_PIN[b]:v for b,v in bits.items()},
                fref_hz=FREF,fcompare_hz=FPFD,lo_hz=p['lo_hz'],fin_hz=p['fin_hz'],
                ra2_ra1_ra0=(1,0,1),tx_permitted=False)

def crystal_load_pf(c1=22,c2=22,cin=5,cout=6,ca=1,cholder=3):
    if min(c1,c2,cin,cout,ca,cholder)<0 or not c1+c2 or not cin+cout:raise ValueError('invalid capacitance')
    return cin*cout/(cin+cout)+ca+cholder+c1*c2/(c1+c2)

def tank_ceff_pf(f_hz,L_h=220e-9):
    if f_hz<=0 or L_h<=0:raise ValueError('invalid LC')
    return 1e12 / ((2*math.pi*f_hz)**2 * L_h)

def error_hz(f_hz,ppm):
    if f_hz<=0 or ppm<0:raise ValueError('invalid error')
    return f_hz*ppm/1_000_000

def gate_model(*,pll_locked,clock_ok,code_valid,power_ok):
    rx_allowed=all((pll_locked,clock_ok,code_valid,power_ok))
    return dict(rx_audio_allowed=rx_allowed,tx_permitted=False,fabrication_authorized=False)

if __name__=='__main__':
    d=channel_state('D',9)
    print('CH9 N:',d['n'],'LO:',d['lo_hz'],'fIN:',d['fin_hz'])
    print('crystal CL pF:',round(crystal_load_pf(),3))
    print('LC ideal pF:',round(tank_ceff_pf(LO_MIN),3),round(tank_ceff_pf(LO_MAX),3))
