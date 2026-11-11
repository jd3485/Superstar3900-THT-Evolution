#!/usr/bin/env python3
"""V2.6 dual-2N3904 ideal DC network WITHOUT the existing D803 Zener.\n48V overdrive here describes an open-D803 fault, not the healthy KiCad circuit.\n"""
from itertools import product
import json
states=[(a,b,a and b) for a,b in product((False,True),repeat=2)]
assert states==[(False,False,False),(False,True,False),(True,False,False),(True,True,True)]
rows=[(v,s,1000*(v-s)/57000,(s+10000*(v-s)/57000)-v) for v,s in product((10.,11.5,13.8,18.,24.,48.),(.2,.4,.6))]
ib=(2.5-.85)/22000-.85/100000
assert ib>0
sinks=[r[2] for r in rows if r[0]==13.8]
assert max(sinks)/(1000*ib)<4
assert all(abs(r[3])<20 for r in rows if r[0]==18)
assert all(abs(r[3])>20 for r in rows if r[0]==48)
print(json.dumps({"gate":"PASS_IDEAL_SERIES_INTERLOCK_STUDY_ONLY","states":states,"sink_13p8_mA":[round(min(sinks),4),round(max(sinks),4)],"Q802_base_ideal_mA":round(1000*ib,4),"stack_sat_assumed_V":[.2,.4,.6],"48V_gate_stress_if_D803_OPEN":True,"vendor_spice":False,"hardware_qualified":False,"cad_not_checked_by_ideal_screen":True,"NO_FAB":True,"NO_TX":True},sort_keys=True))
