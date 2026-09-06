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


def normalized(text: str) -> str:
    """Whitespace-collapsed, quote-and-dash-folded, lowercase; the one
    normalisation shared by locate.py and the citation tests."""
    t = text.replace("’", "'").replace("‘", "'")
    t = t.replace("“", '"').replace("”", '"')
    t = t.replace("–", "-").replace("—", "-").replace("­", "")
    t = t.replace("ﬁ", "fi").replace("ﬂ", "fl")
    return re.sub(r"\s+", " ", t).strip().lower()


@pytest.fixture(scope="session")
def rulings() -> Graph:
    return load("rulings/adjudications.ttl")
