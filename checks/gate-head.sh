#!/usr/bin/env bash
# Run the gate on the committed HEAD, not on the working tree: a detached
# worktree of HEAD is checked out under .cache/gate-head, the pinned toolchain
# binaries are copied in, and checks/run-checks.sh runs there. This is what
# the lambda discipline needs (Z, 2026-09-06): the slow bar judges the commit
# while editing continues in the checkout. The verdict line is the gate's own.
set -uo pipefail
cd "$(git rev-parse --show-toplevel)"
WT=.cache/gate-head
mkdir -p .cache
git worktree remove --force "$WT" >/dev/null 2>&1 || true
rm -rf "$WT"
git worktree add -q --detach "$WT" HEAD || exit 2
if [ -d toolchain/bin ]; then mkdir -p "$WT/toolchain" && cp -R toolchain/bin "$WT/toolchain/"; fi
if [ -d sources/local ]; then mkdir -p "$WT/sources" && cp -R sources/local "$WT/sources/"; fi
( cd "$WT" && bash checks/run-checks.sh )
RC=$?
mkdir -p checks/out && cp "$WT/checks/out/last.log" checks/out/last.log 2>/dev/null; cp "$WT/checks/out/report.json" checks/out/report.json 2>/dev/null
git worktree remove --force "$WT" >/dev/null 2>&1 || true
exit $RC
