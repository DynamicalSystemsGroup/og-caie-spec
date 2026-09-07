#!/usr/bin/env bash
# Put the knowledge graph explorer (ruling R-39) and the sample report
# (ruling R-51, sheet 10 item 10-44) next to the built site.
# Run after `myst build --html`, from the repository root; the gate and the
# deploy workflow both call it, so the two builds cannot drift.
#
# The explorer lives at <site>/explorer/ and the appendix embeds it with the
# relative src `explorer/index.html`. The appendix page is served as
# appendix-explorer/index.html, so its URL is seen both without a trailing
# slash (the site's own links and client-side navigation) and with one
# (GitHub Pages redirects a directory URL to the slash form on a full load).
# Without the slash the src resolves to <site>/explorer/index.html; with it,
# to <site>/appendix-explorer/explorer/index.html. A one-line stub at that
# second location sends the frame to the real copy, so one relative src
# works at the site root and under a BASE_URL alike, with a single copy of
# the explorer's data and vendor files. The report follows the same pattern
# at <site>/report/ with its stub at appendix-report/report/; it loads d3
# from the explorer's vendored copy by the relative path ../explorer/vendor/.
set -euo pipefail
cd "$(dirname "$0")/.."
test -d _build/html
rm -rf _build/html/explorer _build/html/appendix-explorer/explorer
cp -R explorer _build/html/explorer
mkdir -p _build/html/appendix-explorer/explorer
printf '%s\n' '<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=../../explorer/index.html"><title>the explorer</title><a href="../../explorer/index.html">the knowledge graph explorer</a>' \
  > _build/html/appendix-explorer/explorer/index.html
test -f _build/html/explorer/index.html
test -f _build/html/explorer/graph.json
rm -rf _build/html/report _build/html/appendix-report/report
cp -R report _build/html/report
mkdir -p _build/html/appendix-report/report
printf '%s\n' '<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=../../report/index.html"><title>the sample report</title><a href="../../report/index.html">the sample report</a>' \
  > _build/html/appendix-report/report/index.html
test -f _build/html/report/index.html
test -f _build/html/report/report.json
test -f _build/html/explorer/vendor/d3.v7.min.js
echo "explorer copied to _build/html/explorer/ (stub at appendix-explorer/explorer/); report copied to _build/html/report/ (stub at appendix-report/report/)"
