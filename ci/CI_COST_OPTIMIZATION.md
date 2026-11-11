# Cost-optimized continuous verification — Superstar 3900 THT Evolution

## Principles and merge controls
- ChatGPT identifies and corrects electronics/EDA errors directly. GitHub stores revisions.
- 20 historical workflows are **retained verbatim apart from their triggers** and remain
  available via manual `workflow_dispatch`. They no longer run separately for every
  push, PR, or administrative change, avoiding simultaneous KiCad installations.
- `.github/workflows/ci_optimized.yml` is the single automatic PR gate:
  - **Fast:** original V0.1 through V1.0 Python unittest suites on all PRs,
    even documentation-only (to preserve handoff continuity).
  - **Full:** for electrical, script, YAML, library, BOM, layout, testing or
    unrecognized changes, a single job in the **official KiCad9 Docker image**
    executes **all 19 remaining historical workflows' original PR-applicable run steps in
    order**, including actual native KiCad9 ERC, netlists, footprint SVG,
    partition audits, screenings and ngspice. Only repeated bootstrap
    installation steps and per-workflow checkout/upload steps are deduplicated.
    Python manifest asserts expected run-step count; unknown new workflows fail.
  - **Gate:** fails if fast fails, or if full was required and was not successful.
- All changes to test scripts or the CI itself force FULL, not just structural CAD.
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
The old 20 workflows are the source of truth for all original test commands.
The optimized runner extracts each `run` step and executes its shell text
under `bash -e -o pipefail`. Any changed legacy step count or a new unknown
workflow fails the manifest. Manually inspect evidence for status and technical
correctness. No tests silently classified as success.

The five V0.6 exploratory steps formerly restricted to a historical feature
push were **not** part of PR checks. They now run on standalone V0.6
`workflow_dispatch`, and on manual optimized full dispatch when
`include_v06_exploration=true`; normal PR runs retain their original
conditional skip. The script asserts exactly these five conditional steps.
