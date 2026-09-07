#!/usr/bin/env bash
# Regenerate every derived fragment from the graphs, in the gate's order:
# the site fragments, the command-line blocks, the figures, the explorer, the sample report and the toolchain review.
# The gate runs this and then diffs generated/, explorer/ and report/ byte for byte.
set -euo pipefail
cd "$(dirname "$0")/.."
uv run python scripts/render.py
uv run python scripts/render_cli.py
uv run python scripts/render_diagrams.py
uv run python scripts/render_explorer.py
uv run python scripts/render_report.py
uv run python scripts/render_toolchain.py
uv run python scripts/render_bib.py
uv run python scripts/render_version.py
