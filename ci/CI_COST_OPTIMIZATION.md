# Cost-optimized continuous verification — Superstar 3900 THT Evolution

## Principles and merge controls
- ChatGPT identifies and corrects electronics/EDA errors directly. GitHub stores revisions.
- 21 historical workflows are **retained verbatim apart from their triggers** and remain
  available via manual `workflow_dispatch`. They no longer run separately for every
  push, PR, or administrative change, avoiding simultaneous KiCad installations.
- `.github/workflows/ci_optimized.yml` is the single automatic PR gate:
  - **Fast:** original V0.1 through V1.0 Python unittest suites on all PRs,
    even documentation-only (to preserve handoff continuity).
  - **Full:** for electrical, non-allowlisted script, YAML, library, BOM, layout, testing or
    unrecognized changes, a single job in the **official KiCad9 Docker image**
    executes **all 20 remaining historical workflows' original PR-applicable run steps in
    order**, including actual native KiCad9 ERC, netlists, footprint SVG,
    partition audits, screenings and ngspice. Only repeated bootstrap
    installation steps and per-workflow checkout/upload steps are deduplicated.
    Python manifest asserts expected run-step count; unknown new workflows fail.
  - **Gate:** fails if fast fails, or if full was required and was not successful.
- Changes to native/electrical test scripts or CI policy always force FULL; only the four narrowly allowed standalone analytical Python/CSV files below may run FAST-only.
- `workflow_dispatch` on optimized gate allows a manual FULL revalidation.
- `concurrency` cancels obsolete **PR** runs when new commits arrive; a
  manually dispatched run is not automatically cancelled.
- Merge only after the **final HEAD SHA** has the required green CI gate.
  Do not merge on skipped/missing gate or broken full native checks.
- No automated `push: main` CI rerun after an already validated PR merge.
- No branch-protection setting changed; if historical checks are required by
  external rulesets, update protections **only with owner's explicit action**
  after inspection. The GitHub connector cannot read branch protection.
- KiCad CLI 9.0 official Docker image is supported by the manufacturer:
  https://www.kicad.org/download/docker/
  The official KiCad 9.0.9 image is **pinned to tested digest**
  `sha256:e638b79b0321f29395a5b783e94bb9f3c73303e8da15da27b8f5cb4b67a37729` from real native ERC0 pilot [run 43054348749](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43054348749).
- **Local execution**: `python3 -B ci/ci_scope.py --selftest`,
  `python3 -B ci/fast_regressions.py`; when KiCad9/ngspice and PyYAML are
  present `python3 -B ci/full_regressions.py`. Never declare a PASS on the
  basis of an unavailable local KiCad.
- Archive only short-lived recent native evidence, not every historical
  repetitive SVG. GitHub Actions costs depend on official billed minutes;
  reduction is structural, not a fabricated measured saving.
- Not a safety or fabrication qualification. No PCB/DRC until a real PCB.
  **NO FAB / NO TX / NO BATTERY / VEHICLE**, no change to SMD repository.

## Rollout caution
The old 22 workflows are the source of truth for all original test commands.
The optimized runner extracts each `run` step and executes its shell text
under `bash -e -o pipefail`. Any changed legacy step count or a new unknown
workflow fails the manifest. Manually inspect evidence for status and technical
correctness. No tests silently classified as success.

The five V0.6 exploratory steps formerly restricted to a historical feature
push were **not** part of PR checks. They now run on standalone V0.6
`workflow_dispatch`, and on manual optimized full dispatch when
`include_v06_exploration=true`; normal PR runs retain their original
conditional skip. The script asserts exactly these five conditional steps.

V2.4 adds `cad_native_v24.yml` as the 20th native/SPICE workflow in
`ci/full_regressions.py`, now **21 historical workflows in total** including
the ten-suite Python workflow. The original V2.4 KiCad gate is not skipped;
its 6 original `run` steps (minus only KiCad installation) are executed
by the common container for each changed-CAD PR.


## 2026-11-11 update for V2.5 candidate (PR #28 DRAFT)
The historical workflow set now includes a V2.5 manual KiCad9 workflow. The consolidated runner tracks **21 native/SPICE** workflows plus the same historical Python regression workflow, and the single automatic PR gate continues to execute all native tests only once in its pinned KiCad9 container. No parallel installation fan-out is reintroduced. The new V2.5 native ERC/netlist/7 SVG and PVT screen must pass on the new final HEAD. Previous V2.4 PASS does not transfer. No PCB or safety qualification. NO FAB/NO TX.

## 13 novembre 2026 — eccezione FAST-only strettamente delimitata

La CI spendeva minuti di container KiCad9 anche per modifiche a due calcolatori audio **puramente numerici**, già eseguiti obbligatoriamente ad ogni PR in `ci/fast_regressions.py`. Aggiunta in `ci/ci_scope.py` una **allowlist esatta** (non generica per estensione o cartella) di quattro file:

- `03_Verifiche/V2.7/verify_audio_load_envelope.py`
- `03_Verifiche/V2.7/AUDIO_LOAD_ENVELOPE_LM386_6V.csv`
- `03_Verifiche/V2.7/verify_audio_rail_current_graph_v27.py`
- `03_Verifiche/V2.7/LM386_GRAPH_6V_RAIL_CURRENT_BRACKETS.csv`

Solo diff con **documentazione e/o questi quattro file** possono passare senza FULL, a condizione che FAST termini **SUCCESS** con i test numerici realmente eseguiti e il required gate sia SUCCESS. Ogni modifica a `ci/ci_scope.py`, `ci/fast_regressions.py`, altri verificatori, `.github/workflows/`, CAD/footprint/simboli, SPICE/ngspice, BOM, YAML o file nuovo/sconosciuto **richiede FULL**. Un diff che combina uno dei quattro file con una modifica elettrica richiede FULL senza eccezioni. La modalità manuale `workflow_dispatch` continua a lanciare FULL. `ci/ci_scope.py --selftest` verifica la matrice dei casi misti, dei nuovi file non consentiti e della modalità manuale.

**Non sono stati ridotti i test KiCad9/ngspice per nessuna modifica elettrica.** L'eccezione elimina l'avvio di un container pesante solo per numeri già validati in FAST; non prova che tutte le modifiche siano prive di effetti elettronici, quindi il gruppo dei file è intenzionalmente piccolo e richiede revisione umana quando si cambia natura ai calcolatori. La PR di adozione modifica la policy `ci/ci_scope.py` e quindi **deve essa stessa eseguire FULL**, con i gate verdi sullo SHA finale. Non si dichiara un risparmio in euro senza dati di fatturazione GitHub. NO FAB/NO TX.
