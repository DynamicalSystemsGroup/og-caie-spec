"""The site's version line (sheet 10-38, R-50): the nearest tag and the commit
the site was rendered at, written to generated/version.md for the front
page's footer. The file is not committed (it would change with every
commit and break byte-identical regeneration); the regen script, the
gate and the test conftest write it before anything reads it."""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated" / "version.md"


def describe() -> tuple[str, str]:
    def git(*args: str) -> str:
        try:
            return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return ""
    tag = git("describe", "--tags", "--abbrev=0")
    sha = git("rev-parse", "--short", "HEAD")
    dirty = git("status", "--porcelain") != ""
    return tag or "unreleased", (sha or "unknown") + ("+" if dirty else "")


def render() -> str:
    tag, sha = describe()
    return f"*Version {tag}, rendered at commit `{sha}`: the specification's version is its git tag and its commit (sheet 10-38).*\n"


if __name__ == "__main__":
    OUT.write_text(render())
    print(f"version: {OUT.read_text().strip()}")
