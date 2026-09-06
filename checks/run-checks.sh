#!/usr/bin/env bash
# The gate. Every step runs; the only summary is the CHECKS: line and
# checks/out/report.json; each step's full output is in checks/out/last.log.
# No step is optional and nothing here fails quietly. CI runs exactly this.
set -uo pipefail
cd "$(dirname "$0")/.."
mkdir -p checks/out
LOG=checks/out/last.log
: > "$LOG"
SHA=$(git rev-parse --short HEAD 2>/dev/null || echo none)
DIRTY=$(test -n "$(git status --porcelain 2>/dev/null)" && echo true || echo false)
declare -a STEPS=()
FAIL=0

step() { # step <name> <expected-exit> <cmd...>
  local name="$1" expect="$2"; shift 2
  echo "== $name ==" | tee -a "$LOG"
  "$@" >> "$LOG" 2>&1
  local got=$?
  if [ "$got" -eq "$expect" ]; then
    STEPS+=("\"$name\": \"pass\""); echo "   pass"
  else
    STEPS+=("\"$name\": \"FAIL\""); echo "   FAIL (exit $got, expected $expect; see checks/out/last.log)"; FAIL=1
  fi
}

step "toolchain: pinned sysml v0.4.3, digest-verified" 0 bash toolchain/get-sysml.sh
step "model: validate -strict (authoring view and model counterexamples)" 0 toolchain/bin/sysml model/og-caie.sysml counterexamples/model/unwired-port.sysml counterexamples/model/expert-administers-tests.sysml counterexamples/model/missing-accountable.sysml counterexamples/model/no-obligation.sysml -validate -strict

regen_model() {
  uv run python scripts/prune_model.py && git diff --quiet -- model/og-caie.model.ttl model/model_manifest.json
}
step "model graph: convert, prune, byte-identical to the committed canonical graph" 0 regen_model
step "ogc: doctor (labels unambiguous, quotes located, record consistent)" 0 uv run -q ogc doctor --no-cache
step "tests: full suite" 0 uv run pytest -q

regen() {
  uv run python scripts/render.py && uv run python scripts/render_diagrams.py && git diff --quiet -- generated/
}
step "generated/: regenerates byte-identically" 0 regen
step "site: myst build --html" 0 uv run myst build --html

RESULT=$([ "$FAIL" -eq 0 ] && echo PASS || echo FAIL)
printf '{"sha":"%s","dirty":%s,"time":"%s","steps":{%s},"result":"%s"}\n' \
  "$SHA" "$DIRTY" "$(date -u +%FT%TZ)" "$(IFS=,; echo "${STEPS[*]}")" "$RESULT" > checks/out/report.json
echo "CHECKS: $RESULT (sha=$SHA dirty=$DIRTY)"
exit "$FAIL"
