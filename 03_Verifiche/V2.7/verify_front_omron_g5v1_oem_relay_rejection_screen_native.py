#!/usr/bin/env python3
"""Omron G5V-1 DC5 5V-coil OEM data screen against current unqualified driver.

Source: https://components.omron.com/eu-en/system/files/2023-01/datasheet_pdf/K048-E1.pdf
OEM PDF p1: G5V-1 5V coil 30 mA/167 ohm (±10% at 23C), pickup
80% max. p2: reference contact failure-rate load 1mA at 5VDC, which
does NOT qualify µV/µA line-audio dry contact. Current driver candidate
is STILL generic/unassigned. THIS SCRIPT MUST *PASS* WHEN IT DETECTS
SCREEN FAILURES; it MUST NOT certify this combination or assign MPN.
"""
from __future__ import annotations
from pathlib import Path
from itertools import product
from verify_interboard_audio_contract_native import exported_nets,require
import tempfile
ROOT=Path(__file__).resolve().parents[2]
DRIVER=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_MUTE_COIL_DRIVER/FRONT_NC_MUTE_DUAL_ENABLE_COIL_DRIVER_V2_7_DRAFT.kicad_sch"
CONTACT=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_MUTE_NC_RELAY/FRONT_NC_MUTE_CONTACT_THT_V2_7_DRAFT.kicad_sch"
OEM="https://components.omron.com/eu-en/system/files/2023-01/datasheet_pdf/K048-E1.pdf"
RCOIL_OHM=167.0
RCOIL_TOL=0.10
MUST_PICKUP_FRACTION=0.80
RBASE_OHM=1500.
RPULL_OHM=10000.
VBE_ASSUMED=.8
FORCED_BETA_TARGET=10.
def main():
    assert OEM.endswith("K048-E1.pdf")
    assert RCOIL_OHM==167. and MUST_PICKUP_FRACTION==.80
    raw=DRIVER.read_text(encoding="utf-8")
    assert raw.count("1k5_THT_BASERES")==2
    assert raw.count("10k_THT_PULLDOWN")==2
    assert "G5V-1" not in raw and "G5V-1" not in CONTACT.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="tht_omron_oem_screen_") as td:
        d=Path(td)
        drv=exported_nets(DRIVER,d/"driver.net")
        relay=exported_nets(CONTACT,d/"contact.net")
    require(drv,"COIL_PLUS_LAB",("J1914","1"),("D1911","1"))
    require(drv,"COIL_MINUS_LAB",("J1914","2"),("D1911","2"),("Q1911","1"))
    require(drv,"DRIVE1_BASE",("Q1911","2"),("R1911","2"),("R1913","1"))
    require(drv,"SERIES_MID",("Q1911","3"),("Q1912","1"),("R1913","2"))
    require(drv,"DRIVE2_BASE",("Q1912","2"),("R1912","2"))
    require(relay,"COIL_PLUS_LAB",("K1901","4"),("J1903","1"))
    require(relay,"COIL_MINUS_LAB",("K1901","5"),("J1903","2"))
    total=0; current_fail=0; pickup_not_guaranteed=0; release_unqualified=0
    examples=[]
    for vrail,vlogic,rcoil,vcesat in product(
        (4.5,5.,5.5),(4.5,5.),(RCOIL_OHM*(1-RCOIL_TOL),RCOIL_OHM,
        RCOIL_OHM*(1+RCOIL_TOL)),(.15,.30)):
        # Assumed VCEsat and VBE are engineering test corners, NOT
        # Omron or transistor maximum values / vendor SPICE models.
        vcoil=vrail-2*vcesat
        icoil=vcoil/rcoil
        ibu=(vlogic-(VBE_ASSUMED+vcesat))/RBASE_OHM-VBE_ASSUMED/RPULL_OHM
        ibl=(vlogic-VBE_ASSUMED)/RBASE_OHM-VBE_ASSUMED/RPULL_OHM
        sufficient_drive=min(ibu,ibl)>=icoil/FORCED_BETA_TARGET
        pickup_guaranteed_at_23C=vcoil>=5.*MUST_PICKUP_FRACTION
        current_fail+=int(not sufficient_drive)
        pickup_not_guaranteed+=int(not pickup_guaranteed_at_23C)
        total+=1
        if not sufficient_drive or not pickup_guaranteed_at_23C:
            examples.append((vrail,vlogic,round(rcoil,2),vcesat,
                             round(1000*icoil,3),round(1000*min(ibu,ibl),3),
                             sufficient_drive,pickup_guaranteed_at_23C))
    assert total==36 and current_fail>=20 and pickup_not_guaranteed>=1
    # 5V nominal OEM coil is >250-ohm floor excluded from original
    # generic 48-case screen. This component MUST NOT be accepted
    # under that old screen's assumptions.
    assert RCOIL_OHM*(1+RCOIL_TOL)<250.
    assert (4.5-.3-.3)<.8*5.  # 4.5V rail with two 0.3V switches = 3.9V
    # Switching reliability reference is 1mA @ 5VDC, whereas input
    # amplitude & actual contact-current minimum are not yet quantified.
    minimum_qualified_audio_current_mA=None
    assert minimum_qualified_audio_current_mA is None
    assert release_unqualified==0  # not a test of flyback/release timing
    print("OMRON_G5V1_DC5_THT_CANDIDATE_REJECTION_SCREEN",{
        "OEM_datasheet_url":OEM,
        "THT_SPDT_product_family_production_status_online":"listed in production",
        "coil_ohm_nominal_23C":RCOIL_OHM,
        "coil_ohm_tolerance_23C":RCOIL_TOL,
        "coil_current_mA_nominal_5V":30.,
        "coil_must_pickup_fraction_23C_max":MUST_PICKUP_FRACTION,
        "OEM_contact_reference_failure_rate_load":"1mA @ 5VDC",
        "audio_actual_min_current_unknown":True,
        "DC_cases":total,"forced_beta10_margin_failed":current_fail,
        "coil_pickup_not_assured":pickup_not_guaranteed,
        "hypothetical_drive_and_VCEsat_corners":True,
        "OEM_contact_qualifies_real_AF_audio":False,
        "actual_NPN_diode_OEM_qualified":False,
        "relay_selected_for_product":False,
        "NO_FAB_NO_TX":True},flush=True)
    print("OMRON_G5V1_FIRST_UNQUALIFIED_CASES",examples[:6],flush=True)
    print("PASS_NATIVE_KICAD9_OMRON_G5V1_36_OEM_SCREEN_EXPECTED_FAIL_NOT_RELEASE",flush=True)
if __name__=="__main__":main()
