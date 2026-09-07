"""Shared fixtures: repository root, graph loaders, quote normalisation."""
import re
from pathlib import Path

import pytest
from rdflib import Graph, Namespace

ROOT = Path(__file__).resolve().parents[1]
OGC = Namespace("https://w3id.org/og-caie/")
RUL = Namespace("https://w3id.org/og-caie/rulings#")
SRC = Namespace("https://w3id.org/og-caie/sources#")
TERM = Namespace("https://w3id.org/og-caie/terms#")
EPO = Namespace("https://w3id.org/og-caie/epo#")


def load(*paths: str) -> Graph:
    g = Graph()
    for p in paths:
        g.parse(ROOT / p)
    return g


import sys as _sys
_sys.path.insert(0, str(ROOT))
from ogc.verify import normalized  # noqa: E402  (one normalisation, shared with `ogc verify`)

# The version line is written at render time and never committed (sheet 10-38);
# a fresh checkout has none, so the tests that resolve includes render it first.
if not (ROOT / "generated" / "version.md").exists():
    _sys.path.insert(0, str(ROOT / "scripts"))
    import render_version as _rv  # noqa: E402
    _rv.OUT.write_text(_rv.render())



@pytest.fixture(scope="session")
def rulings() -> Graph:
    return load("rulings/adjudications.ttl")
