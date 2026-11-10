"""V0.2: programma matematico RX-only, senza funzioni di trasmissione RF.
Sorgenti di confronto:
https://cbtricks.org/radios/superstar/3900/ss3900_band_chart_a.htm
https://cbtricks.org/radios/superstar/3900/ss3900_band_chart_b.htm
"""
CHANNEL_D_KHZ=(26965,26975,26985,27005,27015,27025,27035,27055,27065,27075,27085,27105,27115,27125,27135,27155,27165,27175,27185,27205,27215,27225,27255,27235,27245,27265,27275,27285,27295,27305,27315,27325,27335,27345,27355,27365,27375,27385,27395,27405)
BAND_OFFSET_KHZ={'A':-1350,'B':-900,'C':-450,'D':0,'E':450,'F':900}
ALPHAS=(3,7,11,15,19)
IF1_HZ=10_695_000
FREF_HZ=10_240_000
R_REF=2048
PRESCALER=2
FPFD_HZ=FREF_HZ//R_REF

def frequency_hz(band,channel,alpha=False):
    if band not in BAND_OFFSET_KHZ: raise ValueError("Banda inesistente")
    if type(channel) is not int or not 1<=channel<=40: raise ValueError("Canale invalido")
    if alpha and channel not in ALPHAS: raise ValueError("ALFA non valido")
    return (CHANNEL_D_KHZ[channel-1]+BAND_OFFSET_KHZ[band]+(10 if alpha else 0))*1000

def rx_plan(band,channel,alpha=False):
    rf=frequency_hz(band,channel,alpha)
    lo=rf+IF1_HZ
    if lo%(PRESCALER*FPFD_HZ): raise ValueError("NON INTEGER-N")
    n=lo//(PRESCALER*FPFD_HZ)
    if not 3<=n<=16383: raise ValueError("Divisore fuori intervallo")
    return dict(rf_hz=rf,lo_hz=lo,image_hz=rf+2*IF1_HZ,
                n=n,n_bin14=f'{n:014b}',fin_hz=lo//PRESCALER,
                f_pfd_hz=FPFD_HZ,tx_permitted=False)

def all_rows():
    data=[]
    for band in BAND_OFFSET_KHZ:
        pos=0
        for ch in range(1,41):
            for a in ((False,True) if ch in ALPHAS else (False,)):
                pos+=1
                data.append(dict(banda=band,ordine_banda=pos,
                                 canale=f'{ch}A' if a else str(ch),
                                 alfa=int(a),**rx_plan(band,ch,a)))
    return data

def apply_ch9_priority(*,ch9_pressed,band,channel,alpha,mode):
    if ch9_pressed: return ('D',9,False,'AM')
    if mode not in ('AM','FM','USB','LSB','CW'): raise ValueError("Modo RX invalido")
    frequency_hz(band,channel,alpha)
    return band,channel,alpha,mode

if __name__=="__main__":
    all_r=all_rows()
    print(f'{len(all_r)} posizioni RX; {min(x["rf_hz"] for x in all_r)}..{max(x["rf_hz"] for x in all_r)} Hz; TX=False')
