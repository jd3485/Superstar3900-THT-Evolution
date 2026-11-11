#!/usr/bin/env python3
"""V2.5 OVP/UVLO shared feedback screen, NOT a hardware safety qualification."""
from itertools import product
import json
r4=100000.; r5=1000000.; top=56200.; bot=10000.
def threshold(ref,out,a=r4,b=r5,c=top,d=bot):
    plus=(ref/a+out/b)/(1/a+1/b)
    return plus*(c+d)/d
low=threshold(2.5,0.25)
released=threshold(2.5,2.5)
deltas=[threshold(v,v,a,b,c,d)-threshold(v,l,a,b,c,d) for v,l,a,b,c,d in product((2.45,2.5,2.55),(.1,.25,.5),(r4*.99,r4*1.01),(r5*.95,r5*1.05),(top*.99,top*1.01),(bot*.99,bot*1.01))]
assert len(deltas)==144 and min(deltas)>1.0
assert 1.30<released-low<1.40
print(json.dumps(dict(gate="PASS_SHARED_CMP_OUT_COUPLING_DETECTED_NOT_SAFETY_APPROVAL",uvlo_nominal_v=11.5,ovp_low_v=round(low,4),ovp_released_ideal_v=round(released,4),ovp_approx_shift_v=round(released-low,4),range_shift_v=[round(min(deltas),4),round(max(deltas),4)],cases=len(deltas),assumption="Vout released=Vref; no output load or Q802 modeling",uvlo_hysteresis_separate=False,failed_components_qualified=False,NO_FAB=True,NO_TX=True),sort_keys=True))
