"""myst.yml names only files that exist; every included fragment exists."""
import re

import yaml

from conftest import ROOT


def _files(entries):
    for e in entries:
        if "file" in e:
            yield e["file"]
        yield from _files(e.get("children", []))


def test_toc_files_exist():
    cfg = yaml.safe_load((ROOT / "myst.yml").read_text())
    for f in _files(cfg["project"]["toc"]):
        assert (ROOT / f).exists(), f


def test_includes_resolve():
    for md in [ROOT / "index.md", *(ROOT / "docs").glob("*.md")]:
        for inc in re.findall(r"```\{include\}\s+(\S+)", md.read_text()):
            assert (md.parent / inc).resolve().exists(), f"{md.name} includes missing {inc}"
