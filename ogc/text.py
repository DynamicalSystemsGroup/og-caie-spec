"""Deterministic text rendering of api results. No timestamps; sorted input assumed."""
from __future__ import annotations

import textwrap

WIDE = False
CLIP = 80


def head(cmd: str, args: str, sha: str) -> str:
    return f"# ogc {cmd} {args} @ {sha}".replace("  @", " @")


def clip(s: str, n: int = CLIP) -> str:
    return s if WIDE or len(s) <= n else s[: n - 1] + "…"


def cell(v) -> str:
    s = ", ".join(str(x) for x in v) if isinstance(v, (list, tuple)) else str(v)
    lines = s.splitlines()
    if len(lines) > 1:
        s = f"{lines[0]} [+{len(lines) - 1} lines]"
    return clip(s)


def table(rows: list[dict], cols: list[str]) -> list[str]:
    if not rows:
        return ["(none)"]
    cells = [{c: cell(r.get(c, "")) for c in cols} for r in rows]
    widths = {c: max(len(c), *(len(r[c]) for r in cells)) for c in cols}
    out = ["  ".join(c.ljust(widths[c]) for c in cols), "  ".join("-" * widths[c] for c in cols)]
    for r in cells:
        out.append("  ".join(r[c].ljust(widths[c]) for c in cols).rstrip())
    if not WIDE and any(len(r[c]) >= CLIP for r in cells for c in cols):
        out.append("(cells clipped at 80 characters; --wide or --json for the whole text)")
    return out


def wrap(s: str, indent: str = "  ", rest: str | None = None) -> list[str]:
    return textwrap.wrap(s, width=96, initial_indent=indent, subsequent_indent=indent if rest is None else rest) or [indent]


def cite_lines(c: dict, indent: str) -> list[str]:
    if not c:
        return [f"{indent}(none)"]
    L = [f"{indent}{c['source']} (rank {c['rank']}, {c['posture']}) {c['locator']}  [{c['status']}]"]
    if c["quote"]:
        L += wrap(f'"{c["quote"]}"', indent + "  ")
    if c.get("verified_by"):
        L.append(f"{indent}  verified by {c['verified_by']} on {c['verified_on']}" + (f" against {c['file']}" if c.get("file") else ""))
    return L


def term(t: dict, meta: dict | None = None) -> list[str]:
    L = [f"## {t['pref']}  ({t['local']})"]
    if meta and meta.get("via"):
        L.append(f"resolved via {meta['via']}")
    L += ["", *wrap(t["definition"])]
    L += ["", f"class: {t['class']}" + (f" ({t['anchor_relation']})" if t["anchor_relation"] else "")]
    if t["alts"]:
        L.append("also: " + "; ".join(t["alts"]))
    L.append("canonical:")
    if t.get("coined_by"):
        L.append(f"coined by: {t['coined_by']}")
    else:
        L += cite_lines(t["canonical"], "  ")
    if t["see_also"]:
        L.append("see also:")
        for c in t["see_also"]:
            L += cite_lines(c, "  ")
    if t["scope_note"]:
        L += ["scope note:"] + wrap(t["scope_note"])
    if t["binding"]:
        L.append(f"binding: {t['binding']}")
    if t["rulings"]:
        L.append("derives from rulings: " + "; ".join(f"{r['id']} ({r['label']})" if r["label"] else r["id"] for r in t["rulings"]))
    if t["concerns"]:
        L.append("concerns naming it: " + "; ".join(f"{c['id']} ({c['status']}) {c['label']}" for c in t["concerns"]))
    if t["sci"]:
        L.append("essentials stated in it: " + ", ".join(t["sci"]))
    if t["crosswalk"]:
        L.append("Popper crosswalk: " + ", ".join(t["crosswalk"]))
    return L


def check_word(r: dict) -> list[str]:
    if r["retired"]:
        L = [f"{r['word']}: RETIRED ({r['retired']})"]
    elif not r["registered"]:
        L = [f"{r['word']}: not registered"]
    else:
        L = [f"{r['word']}: registered as {r['matched_as']} label '{r['label']}' of '{r['term']}' ({r['local']}); class {r['class']}",
             f"  sense: {r['sense']}", f"  canonical: {r['canonical']}"]
        for a in r["also"]:
            L.append(f"  also: {a['term']} ({a['local']}) via {a['matched_as']} label '{a['label']}'")
    for q in r.get("quote_hits", []):
        L.append(f"  carried in a quote on: {q['term']} ({q['source']})")
    for c in r["concerns"]:
        L.append(f"  concern: {c['id']} ({c['status']}) {c['label']}")
    L.append(f"  -> {r['advice']}")
    return L


def kv(d: dict, keys: list[str]) -> list[str]:
    out = []
    for k in keys:
        v = d.get(k)
        if v in (None, "", []):
            continue
        lines = str(v).splitlines()
        out.append(f"{k}: {lines[0]}")
        out += ["  " + l for l in lines[1:]]
    return out
