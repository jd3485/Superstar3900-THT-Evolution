"""Riferimento logico RX V0.5 (Python). NON firmware PIC18 compilabile."""
from dataclasses import dataclass
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"02_Piano_Frequenze/V0.2"))
from frequency_plan_v02 import rx_plan,apply_ch9_priority

@dataclass
class RxState:
    code_n: int | None = None
    mode: str = "AM"
    band: str = "D"
    channel: int = 9
    alpha: bool = False
    muted: bool = True
    stable_ticks: int = 0
    tx_enabled: bool = False

class RxController:
    """Uno switch canale imposta subito mute; solo lock e servizi continuativi sbloccano RX."""
    def __init__(self,qualify_ticks=100):
        if qualify_ticks<1:raise ValueError("invalid lock qualify ticks")
        self.qualify_ticks=qualify_ticks
        self.state=RxState()
        self._target_valid=False

    def request(self,band,channel,alpha=False,mode="AM",ch9=False):
        self.state.muted=True
        self.state.stable_ticks=0
        self._target_valid=False
        self.state.code_n=None
        try:
            b,ch,a,m=apply_ch9_priority(ch9_pressed=ch9,band=band,channel=channel,alpha=alpha,mode=mode)
            p=rx_plan(b,ch,a)
            if not (0<=p["n"]<4096):raise ValueError("word not representable")
        except (ValueError,TypeError,KeyError):
            return False
        self.state.band,self.state.channel,self.state.alpha,self.state.mode=b,ch,a,m
        self.state.code_n=p["n"]
        self._target_valid=True
        return True

    def tick(self,*,power_good,ref_ok,pll_lock,code_bus_stable):
        if not all((power_good,ref_ok,pll_lock,code_bus_stable)) or not self._target_valid:
            self.state.muted=True
            self.state.stable_ticks=0
        else:
            self.state.stable_ticks=min(self.qualify_ticks,self.state.stable_ticks+1)
            self.state.muted=self.state.stable_ticks < self.qualify_ticks
        self.state.tx_enabled=False
        return not self.state.muted

    def reset(self):
        self.state=RxState()
        self._target_valid=False
