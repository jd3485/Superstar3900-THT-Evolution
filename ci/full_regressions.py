#!/usr/bin/env python3
"""Run ALL original 22 KiCad9/ngspice legacy suites in ONE verified KiCad9 container.

The additional original workflow (verifica_v02) is ALWAYS run in ci/fast_regressions.py.
No ERC/DRC waiver, no best-effort test skipping, and no fake pass on failure.
Only separate installation steps and GitHub artifact/checkout steps are deduplicated.
"""
from __future__ import annotations
import os,re,subprocess,sys
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
RUN_COUNTS={
 "cad_native_v10.yml":8,"cad_native_v11.yml":6,"cad_native_v12.yml":6,
 "cad_native_v13.yml":6,"cad_native_v14.yml":7,"cad_native_v15.yml":6,
 "cad_native_v16.yml":6,"cad_native_v17.yml":8,"cad_native_v18.yml":9,
 "cad_native_v19.yml":7,"cad_native_v20.yml":9,"cad_native_v21.yml":7,
 "cad_native_v22.yml":7,"cad_native_v23.yml":7,"cad_native_v24.yml":6,"cad_native_v25.yml":6,"cad_native_v26.yml":6,
 "boost_v07.yml":2,"ngspice_v14_vco_frontend.yml":2,
 "pll_tristate_v09.yml":2,"vco_spice_v06.yml":8,"vtune_driver_v08.yml":2,
}
EXPECTED_ALL_WORKFLOWS=23
ALLOWED_USES=("actions/checkout@v4","actions/upload-artifact@v4")
INSTALL_NGSPICE_RE=re.compile(r"^\s*sudo\s+.*apt-get\s+install\s+.*\bngspice\b.*$",re.MULTILINE)

def normalized_command(cmd:str) -> str|None:
    if "add-apt-repository" in cmd:
        assert "kicad-cli version" in cmd and "apt-get" in cmd, "Unexpected KiCad install step"
        return None
    if "apt-get" in cmd:
        lines=cmd.splitlines()
        kept=[]
        for line in lines:
            if "apt-get update" in line or ("apt-get install" in line and "ngspice" in line):
                continue
            kept.append(line)
        cleaned="\n".join(kept)
        assert "apt-get" not in cleaned and "add-apt-repository" not in cleaned, "Unreviewed installer"
        return cleaned if cleaned.strip() else None
    return cmd

def load_steps(name:str) -> list[tuple[str,str|None]]:
    yml=ROOT/".github/workflows"/name
    raw=yaml.safe_load(yml.read_text(encoding="utf-8"))
    assert isinstance(raw,dict) and "jobs" in raw, name
    jobs=raw["jobs"]
    assert isinstance(jobs,dict) and len(jobs)==1, "Unexpected extra job in "+name
    job=next(iter(jobs.values()))
    assert job.get("runs-on"), "Missing original runner metadata: "+name
    steps=job["steps"]
    seen_run=0
    commands=[]
    for st in steps:
        assert isinstance(st,dict), "Invalid legacy step"
        if "uses" in st:
            assert st["uses"] in ALLOWED_USES and "run" not in st, (name,st)
            continue
        assert "run" in st, f"Missing original run step {name}: {st}"
        seen_run+=1
        condition=st.get("if")
        if condition:
            assert name=="vco_spice_v06.yml" and condition=="github.event_name == 'workflow_dispatch'", (name,condition)
            # Original five v06 exploratory steps were push-only, never part of PR checks.
            # Keep explicitly executable for manual full-run and standalone dispatch.
            if os.getenv("ENABLE_HISTORICAL_EXPLORATORY")!="true":
                commands.append((st.get("name","v06 exploratory"),"__ORIGINAL_PR_CONDITION_FALSE__"))
                continue
        cmd=st["run"]
        assert isinstance(cmd,str) and cmd.strip(),(name,st)
        commands.append((st.get("name","Unnamed legacy step"),normalized_command(cmd)))
    assert seen_run==RUN_COUNTS[name],f"{name}: {seen_run} commands not {RUN_COUNTS[name]}"
    return commands

def main()->None:
    assert len(RUN_COUNTS)==22
    workflow_dir=ROOT/".github/workflows"
    actual={p.name for p in workflow_dir.glob("*.yml")}
    expected=set(RUN_COUNTS)|{"verifica_v02.yml"}
    # The unified gate and one obsolete pilot do not count as legacy; reject other untracked workflow.
    unknown={name for name in actual-expected
             if not name.startswith("ci_") and not name.startswith("zz_pilot_")}
    assert not unknown, "New unreviewed workflow lacks CI coverage: "+str(unknown)
    compiled={name:load_steps(name) for name in RUN_COUNTS}
    total=sum(len(st) for st in compiled.values())
    assert total==sum(RUN_COUNTS.values())
    print("CI_FULL_MANIFEST_VERIFIED",{"workflows":len(compiled),"legacy_run_steps":total,
         "plus_fast_suites":10,"deduplicated_install_steps":sum(c is None for steps in compiled.values() for _,c in steps),
         "original_v06_conditional_skips":sum(c=="__ORIGINAL_PR_CONDITION_FALSE__" for steps in compiled.values() for _,c in steps)},flush=True)
    if "--audit-only" in sys.argv: return
    v=subprocess.run(["kicad-cli","version"],capture_output=True,text=True,check=True).stdout.strip()
    assert re.match(r"^9\.0\.\d+",v), "Wrong KiCad CLI version: "+v
    subprocess.run(["ngspice","--version"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
    subprocess.run(["node","--version"],check=True)
    executed=0
    for name,steps in compiled.items():
        print("::group::"+name,flush=True)
        for label,cmd in steps:
            if cmd is None:
                print("DEDUPED_INSTALL_ONLY",name,label,flush=True)
                continue
            if cmd=="__ORIGINAL_PR_CONDITION_FALSE__":
                print("ORIGINAL_PR_CONDITION_FALSE",name,label,flush=True)
                continue
            print("RUN_REAL_LEGACY_STEP",name,label,flush=True)
            subprocess.run(["bash","-e","-o","pipefail","-c",cmd],cwd=ROOT,
                          env=os.environ.copy(),check=True)
            executed+=1
        print("::endgroup::",flush=True)
    # New standalone V2.7 audio draft: fail the FULL gate on any native
    # schematic ERC violation or missing pin/net in the exported netlist.
    pilot=ROOT/"04_KiCad/V2.7_DRAFT/AUDIO_RX_MONO_LM386_V2_7_DRAFT.kicad_sch"
    if pilot.exists():
        print("::group::V2.7 RX AUDIO THT PILOT NATIVE KIcad9",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_audio_draft_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    front=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_VOLUME/FRONT_VOLUME_THT_V2_7_DRAFT.kicad_sch"
    if front.exists():
        print("::group::V2.7 FRONT_VOLUME THT NATIVE KiCad9",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_front_volume_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    if (ROOT/"04_KiCad/V2.7_DRAFT/FRONT_VOLUME/FRONT_VOLUME_THT_V2_7_DRAFT.kicad_sch").exists():
        print("::group::V2.7 MAIN-FRONT AUDIO INTERBOARD NATIVE PIN CONTRACT",flush=True)
        subprocess.run([sys.executable, "-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_interboard_audio_contract_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # Independent 6V audio lab regulator, not connected to the master V2.6.
    psu=ROOT/"04_KiCad/V2.7_DRAFT/AUDIO_PSU_6V/AUDIO_PSU_LM317_6V_LAB_DRAFT.kicad_sch"
    if psu.exists():
        print("::group::V2.7 THT LAB-ONLY AUDIO PSU LM317 NATIVE",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_audio_psu_lm317_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    if (ROOT/"04_KiCad/V2.7_DRAFT/AUDIO_PSU_6V/AUDIO_PSU_LM317_6V_LAB_DRAFT.kicad_sch").exists():
        print("::group::V2.7 AUDIO 6V PSU TO LM386 NATIVE PIN CONTRACT",flush=True)
        subprocess.run([sys.executable, "-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_audio_6v_supply_contract_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # New ngspice behavioral rail-step study. This exercises REAL transient
    # simulation, not LM317/LM386 vendor semiconductor models. No PCB release.
    spice=ROOT/"03_Verifiche/V2.7/spice/audio_6v_lab_rail_step_behavioral.cir"
    if spice.exists():
        print("::group::V2.7 AUDIO 6V LAB RAIL STEP NATIVE NGSPICE BEHAVIORAL",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_audio_rail_step_ngspice.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # 455kHz AM-only THT diode envelope pilot: real native KiCad9 schematic,
    # not an SSB/FM detector or integrated receiver board.
    am455=ROOT/"04_KiCad/V2.7_DRAFT/AM455_ENVELOPE/AM455_ENVELOPE_THT_V2_7_DRAFT.kicad_sch"
    if am455.exists():
        print("::group::V2.7 AM455 ENVELOPE THT BENCH NATIVE KICAD9",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_am455_bench_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # Bench 455kHz AM envelope behavior with a deliberately GENERIC diode model.
    # This does NOT replace the native KiCad ERC, IF gain or OEM qualification.
    am455_spice=ROOT/"03_Verifiche/V2.7/spice/am455_envelope_1khz_generic_diode_bench.cir"
    if am455_spice.exists():
        print("::group::V2.7 AM455 1KHZ AM DEMOD GENERIC DIODE NATIVE NGSPICE",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_am455_generic_diode_spice.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # IF455 1mH/122.2pF passive THT lab tank, with PROVISIONAL coil mechanics.
    # Real KiCad9 ERC and pin-net exports; no receiver passband certification.
    tank=ROOT/"04_KiCad/V2.7_DRAFT/IF455_TANK/IF455_TANK_THT_V2_7_DRAFT.kicad_sch"
    if tank.exists():
        print("::group::V2.7 IF455 PASSIVE THT LC TANK NATIVE KICAD9",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_if455_tank_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # IF455 coil-loss/coupling load and retuning comparison: actual ngspice AC.
    # Behavioral RLC only (not OEM Q/SRF or production filter qualification).
    if (ROOT/"03_Verifiche/V2.7/spice/if455_loaded_tank_ac_comparison.cir").exists():
        print("::group::V2.7 IF455 LOADED LC 455K NATIVE NGSPICE AC SWEEP",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_if455_loaded_ac_ngspice.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # OEM Delevan active candidate 2500-28J, RF Q at 455k not qualified.
    # Actual native ngspice +/-5% inductance & illustrative SRF parasitic
    # shows why fixed IF tank must NOT be released for manufacturing.
    if (ROOT/"03_Verifiche/V2.7/spice/if455_delevan_2500_28j_tolerance_ac.cir").exists():
        print("::group::V2.7 IF455 DELEVAN CANDIDATE TOLERANCE NATIVE NGSPICE",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_if455_delevan_tolerance_ngspice.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # THT IF455 active EW GKG50015 10-50pF trimmer candidate: real ngspice
    # range coverage, not a claim of Q/ESR, mechanical footprint or RF release.
    if (ROOT/"03_Verifiche/V2.7/spice/if455_trimmer_gkg50015_tuning_envelope.cir").exists():
        print("::group::V2.7 IF455 VARIABLE 10TO50PF TRIM THT NATIVE NGSPICE",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_if455_trimmer_range_ngspice.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # Verify candidate IF455 LC -> diode AM455 bench cable pin1 signal/pin2 GND
    # against BOTH native KiCad9 exported netlists. No physical harness.
    if (ROOT/"03_Verifiche/V2.7/verify_if455_am455_interface_native.py").exists():
        print("::group::V2.7 IF455 TANK TO AM455 DETECTOR 2WIRE NATIVE KICAD9",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_if455_am455_interface_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # Real ngspice downstream load-sensitivity study; the separate
    # native KiCad9 IF455→AM455 pin contract is already merged (PR #89).
    # 10k and 1k are shunt SURROGATES, not nonlinear 1N4148 RF input.
    if (ROOT/"03_Verifiche/V2.7/spice/if455_downstream_input_load_ac.cir").exists():
        print("::group::IF455 DOWNSTREAM OUTPUT LOAD NATIVE NGSPICE AC",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_if455_downstream_load_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # Nonlinear 455kHz AM generic-diode transient; NOT OEM 1N4148 or hardware validation.
    # Reuse the existing FULL container/job; no extra GitHub Actions workflow.
    nonlinear=ROOT/"03_Verifiche/V2.7/spice/if455_am455_nonlinear_transient_generic.cir"
    if nonlinear.exists():
        print("::group::IF455 AM455 GENERIC NONLINEAR TRANSIENT NGSPICE",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_if455_am455_nonlinear_transient_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # RF signal amplitude corner check using the existing generic IF455+AM455 deck.
    # This does not qualify a real diode or IF amplifier. No extra Actions job.
    if (ROOT/"03_Verifiche/V2.7/spice/if455_am455_nonlinear_transient_generic.cir").exists():
        print("::group::IF455 AM455 GENERIC NONLINEAR INPUT LEVEL SWEEP",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_if455_am455_input_level_sweep_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # Follow-up to PR95: source impedance × input amplitude matrix with the same
    # generic diode deck. Native ngspice only; no vendor IF driver or 1N4148 model.
    if (ROOT/"03_Verifiche/V2.7/verify_if455_source_impedance_matrix_native.py").exists():
        print("::group::IF455 AM455 ZSOURCE AND INPUT LEVEL NATIVE NGSPICE MATRIX",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_if455_source_impedance_matrix_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # KSP10BU active THT candidate: native ERC and pin/net mapping for
    # physically isolated IF455 emitter follower laboratory draft.
    if (ROOT/"04_KiCad/V2.7_DRAFT/IF455_KSP10_FOLLOWER/IF455_KSP10_FOLLOWER_THT_V2_7_DRAFT.kicad_sch").exists():
        print("::group::IF455 KSP10BU THT NATIVE KiCad9 ERC NETLIST",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_if455_ksp10_follower_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # 9 native ngspice corners of candidate KSP10 THT emitter follower
    # using generic BJT model only; separate from OEM qualification.
    if (ROOT/"03_Verifiche/V2.7/spice/if455_ksp10_generic_bjt_bias_ac.cir").exists():
        print("::group::IF455 KSP10 GENERIC BJT NATIVE NGSPICE BIAS AND AC CORNERS",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_if455_ksp10_generic_bjt_bias_ac.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # End-to-end nonlinear AM path with THT KSP10 candidate and generic BJT/diode:
    # identical independent IF455 tanks, direct diode versus common-collector
    # followed by diode; native ngspice, no OEM semiconductor qualification.
    if (ROOT/"03_Verifiche/V2.7/spice/if455_ksp10_am455_combined_generic_transient.cir").exists():
        print("::group::IF455 TANK KSP10 AM455 GENERIC NONLINEAR CASCADE NGSPICE",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_if455_ksp10_am455_combined_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # Nonlinear diode peak resolution: comparative 50/25/12.5ns transients
    # for the complete generic tank-BJT-detector chain at two AM levels.
    # Record numerical nonconvergence as evidence: NOT a hardware gate.
    if (ROOT/"03_Verifiche/V2.7/verify_if455_ksp10_cascade_timestep_convergence_native.py").exists():
        print("::group::IF455 KSP10 AM455 NONLINEAR TIMESTEP CONVERGENCE NGSPICE",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_if455_ksp10_cascade_timestep_convergence_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # Experiment: 8 generic BJT coupling/bias variants at 2 AM levels,
    # each with direct LC+diode reference at 25 ns; does NOT qualify OEM.
    if (ROOT/"03_Verifiche/V2.7/verify_if455_highz_bias_coupling_screen_native.py").exists():
        print("::group::IF455 GENERIC HIGH-Z FOLLOWER COUPLING BIAS MATRIX NATIVE NGSPICE",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_if455_highz_bias_coupling_screen_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # onsemi-only J113 TO92 pin1D/2S/3G: vendor-specific KiCad9 source
    # follower BENCH schematic, nine THT refs / six nets, no production.
    if (ROOT/"04_KiCad/V2.7_DRAFT/IF455_J113_SOURCE_FOLLOWER/IF455_J113_SOURCE_FOLLOWER_THT_V2_7_DRAFT.kicad_sch").exists():
        print("::group::IF455 ONSEMI J113 TO92 NATIVE KICAD9 ERC PIN NET",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_if455_j113_source_follower_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # Generic depletion NJF models, not vendor macromodel: 12 RF AM nonlinear
    # runs comparing direct diode with high-Z J113 gate source follower.
    if (ROOT/"03_Verifiche/V2.7/spice/if455_j113_am455_generic_jfet_transient.cir").exists():
        print("::group::IF455 J113 GENERIC NJF FULL CASCADE 12 CORNERS NATIVE NGSPICE",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_if455_j113_generic_njf_full_cascade_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # onsemi J113 worst generic VTO/IDSS scenario: 3 input couplings x 3
    # source resistors x 2 RF levels. Diagnose gain/loading/forward gate;
    # avoid claiming these generic results represent OEM yield/linearity.
    if (ROOT/"03_Verifiche/V2.7/verify_if455_j113_worst_corner_coupling_source_native.py").exists():
        print("::group::IF455 J113 GENERIC WORST CORNER COUPLING SOURCE 18 NGSPICE",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_if455_j113_worst_corner_coupling_source_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # Probe generic 455 kHz envelope detector sensitivity to IF stimulus
    # 100uV..500mV (generator, NOT aerial sensitivity); direct and J113 path.
    # No physical noise or OEM diode/JFET model: never label AFpp as SINAD.
    if (ROOT/"03_Verifiche/V2.7/verify_if455_lowlevel_envelope_native.py").exists():
        print("::group::IF455 GENERIC J113 DIODE LOW LEVEL NATIVE NGSPICE",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_if455_lowlevel_envelope_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # Four genuinely executed native ngspice transfer/Zport experiments on
    # the standalone passive IF455 tank: unloaded reference, 10k/1k shunts,
    # and an explicitly non-OEM JFET gate RC input surrogate. No receiver Q claim.
    if (ROOT/"03_Verifiche/V2.7/verify_if455_passive_port_impedance_selectivity_native.py").exists():
        print("::group::IF455 PASSIVE FILTER COMPLEX ZOUT BANDWIDTH NATIVE NGSPICE",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_if455_passive_port_impedance_selectivity_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # EW GKG50015 passive 10..50pF trimmer AC retuning: 4 output-load
    # surrogates x 9 settings = 36 native ngspice runs (not OEM RF Q test).
    if (ROOT/"03_Verifiche/V2.7/verify_if455_loaded_trimmer_retune_native.py").exists():
        print("::group::IF455 TRIMMER LOAD RETUNE 36 NATIVE NGSPICE AC",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_if455_loaded_trimmer_retune_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # Native SPICE superposition of physically independent Johnson noise
    # sources in passive IF455 RGEN / RCOIL / RDAMP / RLOAD / optional R_GATE.
    # 2 load cases x 5-ish AC probe runs; 290K and 8kHz RF band assumptions.
    if (ROOT/"03_Verifiche/V2.7/verify_if455_passive_resistor_noise_budget_native.py").exists():
        print("::group::IF455 NATIVE PASSIVE RF RESISTOR JOHNSON NOISE BUDGET",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_if455_passive_resistor_noise_budget_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # Resistor-noise/455k transfer trade-off: 3 damping R values x 2 output
    # R values, each signal plus 4 native ngspice Johnson transfer probes.
    if (ROOT/"03_Verifiche/V2.7/verify_if455_passive_resistor_noise_load_tradeoff_native.py").exists():
        print("::group::IF455 RESISTOR NOISE VS PORT LOAD 30 NATIVE NGSPICE",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_if455_passive_resistor_noise_load_tradeoff_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # Independent 6-case full-frequency native AC check of the same
    # 47/100/220k damping × 100/220k output resistance configurations
    # previously evaluated by Johnson noise source superposition.
    if (ROOT/"03_Verifiche/V2.7/verify_if455_resistor_noise_bandwidth_crosscheck_native.py").exists():
        print("::group::IF455 RESISTOR NOISE TRADEOFF 6 AC BW NATIVE",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_if455_resistor_noise_bandwidth_crosscheck_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # KiCad J1601/J1602 passive IF455 upstream interface contract:
    # 3 hypothetical source impedances x 2 downstream loads plus 2 native
    # complex Zin probes. No mixer gain, NF or OEM impedance inferred.
    if (ROOT/"03_Verifiche/V2.7/verify_if455_two_port_source_impedance_native.py").exists():
        print("::group::IF455 TWO PORT UPSTREAM SOURCE Z AND LOAD NATIVE",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_if455_two_port_source_impedance_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # Mini-Circuits actual A06 THT mixer symbol native KiCad9 parser + OEM
    # eight-pin port mapping; +7dBm 50-ohm LO drive is a budget only.
    # No A06 footprint or mixer electrical performance is approved.
    if (ROOT/"03_Verifiche/V2.7/verify_sbl1_mixer_oem_symbol_lo_contract_native.py").exists():
        print("::group::SBL1 OEM A06 CANDIDATE NATIVE KICAD9 SYMBOL LO CONTRACT",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_sbl1_mixer_oem_symbol_lo_contract_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # OEM pin 3+4 tied externally: isolated four-net native KiCad9 mixer
    # schematic proof, with 3 THT connector ports; no A06 footprint approval.
    if (ROOT/"04_KiCad/V2.7_DRAFT/MIXER_SBL1_CANDIDATE/MIXER_SBL1_BENCH_THT_V2_7_DRAFT.kicad_sch").exists():
        print("::group::SBL1 THT MIXER BENCH SCHEMATIC ERC0 AND 4 NATIVE NETS",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_sbl1_mixer_bench_kicad_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # V2.7 mixer LO contract: exported KiCad9 native VCO+SBL-1+ nets and
    # ideal 50-ohm sine power envelope. No claim of physical LO drive.
    if (ROOT/"03_Verifiche/V2.7/verify_sbl1_lo_drive_budget_native.py").exists():
        print("::group::SBL1 LO LEVEL7 VCO NATIVE PORT AND 50OHM ENVELOPE",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_sbl1_lo_drive_budget_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # SBL-1+ IF3/4 physically tied -> IF455 passive input: independent
    # native KiCad9 exported ports, NOT a matched or connected PCB.
    if (ROOT/"03_Verifiche/V2.7/verify_mixer_if455_interface_native.py").exists():
        print("::group::SBL1 MIXER TO IF455 FILTER TWO PORT NATIVE KICAD9",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_mixer_if455_interface_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # C1601 input series coupling: 15 real ngspice AC cases across five
    # experimental values and three hypothetical source resistances.
    # No KiCad/BOM edit and no vendor mixer impedance asserted.
    print("::group::IF455 C1601 NATIVE SOURCE AND CAPACITANCE SWEEP",flush=True)
    subprocess.run([sys.executable,"-B",
                    str(ROOT/"03_Verifiche/V2.7/verify_if455_c1601_source_sweep_native.py")],
                   cwd=ROOT,check=True)
    print("::endgroup::",flush=True)
    # C1601 455kHz coupling tradeoff must also evaluate full response shape,
    # not just nominal scalar amplitude. Hypothetical source Rs only.
    print("::group::IF455 C1601 PASSBAND SOURCE DEPENDENCE",flush=True)
    subprocess.run([sys.executable,"-B",
                    str(ROOT/"03_Verifiche/V2.7/verify_if455_c1601_bandwidth_native.py")],
                   cwd=ROOT,check=True)
    print("::endgroup::",flush=True)
    # OEM mixer IF termination is NOT currently implemented in native KiCad.
    # Nine 455kHz test-only loading cases; no nonlinear SBL-1+ mixer model.
    print("::group::MIXER IF 50OHM TERMINATION PORT CONTRACT AND TEST LOAD",flush=True)
    subprocess.run([sys.executable,"-B",
                    str(ROOT/"03_Verifiche/V2.7/verify_mixer_if_termination_native.py")],
                   cwd=ROOT,check=True)
    print("::endgroup::",flush=True)
    # Three-frequency RF-facing IF port shunt sensitivity; native KiCad
    # netlists + twelve ngspice complex-admittance checks only. No diplexer.
    print("::group::SBL1 IF PORT TEST SHUNT 12 COMPLEX ADMITTANCE CASES",flush=True)
    subprocess.run([sys.executable,"-B",
                    str(ROOT/"03_Verifiche/V2.7/verify_if_port_shunt_frequency_native.py")],
                   cwd=ROOT,check=True)
    print("::endgroup::",flush=True)
    # L1601 assumed ideal 1mH: explore hypothetical winding capacitance
    # at 455kHz/1MHz/30MHz, with 12 ngspice vs nodal complex-Z checks.
    print("::group::IF455 COIL PARASITIC SRF SENSITIVITY NATIVE",flush=True)
    subprocess.run([sys.executable,"-B",
                    str(ROOT/"03_Verifiche/V2.7/verify_if455_coil_parasitic_srf_native.py")],
                   cwd=ROOT,check=True)
    print("::endgroup::",flush=True)
    # Delevan 2500-28J DCR max 16.5Ω is not AC-loss @455kHz.
    # Eight native AC sensitivity runs, real KiCad9 port contract.
    print("::group::IF455 2500-28J Q790 VS DCR RF LOSS SENSITIVITY",flush=True)
    subprocess.run([sys.executable,"-B",
                    str(ROOT/"03_Verifiche/V2.7/verify_if455_2500_28j_q_vs_dcr_native.py")],
                   cwd=ROOT,check=True)
    print("::endgroup::",flush=True)
    # Real KiCad9 IF455 standalone port plus four native AC test cases.
    # Compare both sides of ±3/5/10/20/40 kHz offsets, NOT receiver masks.
    print("::group::IF455 SINGLE TANK CHANNEL OFFSET NATIVE SELECTIVITY",flush=True)
    subprocess.run([sys.executable,"-B",
                    str(ROOT/"03_Verifiche/V2.7/verify_if455_channel_selectivity_native.py")],
                   cwd=ROOT,check=True)
    print("::endgroup::",flush=True)
    # NextGen 5-pin FB455 Case11070, OEM bottom-view to temporary
    # KiCad9 THT pad map and native footprint SVG parser; no PCB release.
    print("::group::NEXTGEN FB455 5PIN PROVISIONAL NATIVE FOOTPRINT NO FAB",flush=True)
    subprocess.run([sys.executable,"-B",
                    str(ROOT/"03_Verifiche/V2.7/verify_fb455_case11070_provisional_native.py")],
                   cwd=ROOT,check=True)
    print("::endgroup::",flush=True)
    print("PASS_FULL_HISTORICAL_22_WORKFLOWS_AND_ALL_NATIVE_KICAD9_GATES",{"executed_commands":executed},flush=True)

if __name__=="__main__":
    main()
