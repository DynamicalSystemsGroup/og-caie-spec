"""ogc: navigate the OG-CAIE vocabulary graph. Deterministic, ontology-aware
retrieval; every command is a named query over the vocabulary, the sources,
the rulings, the essentials and the crosswalk. First line of every output:
`# ogc <command> <args> @ <sha>` (the invocation; for sparql the query on one
line and its sha256). Exit 0 success, 1 not found / ambiguous / bad filter
value, 2 usage. Read-only: no update forms, no federation."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from . import api, text
from .graph import MODEL_FILE, PREFIXES, SOURCE_FILES, SPARQL_PREFIXES, find_root, git_sha, load

GLOBAL_FLAGS = ("--json", "--no-cache", "--wide", "--model")
VERIFY_COLS = ["term", "holder", "source", "posture", "locator", "status", "state", "where"]


def argstr_of(argv: list[str], cmd: str) -> str:
    out = []
    skip = False
    for a in argv:
        if skip:
            skip = False
            continue
        if a == "--root":
            skip = True
            continue
        if a.startswith("--root="):
            continue
        if a in GLOBAL_FLAGS or (a == cmd and not out):
            continue
        out.append(a)
    return re.sub(r"\s+", " ", " ".join(out)).strip()


def emit(args, cmd: str, argstr: str, data, lines_fn) -> int:
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
        return 0
    print(text.head(cmd, argstr, git_sha(args.root)))
    for line in lines_fn():
        print(line)
    return 0


def not_found(args, what: str, hint: str, candidates=None) -> int:
    payload = dict(error=f"{what} not found", hint=hint, candidates=candidates or [])
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(text.head("error", what, git_sha(args.root)))
        print(f"{what}: not found. {hint}")
        for c in candidates or []:
            print(f"  candidate: {c}")
    return 1


def usage(args, msg: str) -> int:
    if args.json:
        print(json.dumps(dict(error="usage", hint=msg), indent=2))
    else:
        print(f"ogc: {msg}", file=sys.stderr)
    return 2


def resolve(args, g, t: str):
    if not t.strip():
        return None, {}, usage(args, "a term is required (a local name, prefLabel or altLabel)")
    iri, cands, meta = api.resolve_term(g, t)
    if iri is None:
        found = [f"{p} ({l})" for p, l in cands] or api.candidates(g, t)
        hint = "ambiguous; use the local name" if cands else ("no exact label match; the candidates below are prefix, substring or quote hits" if found else "no label or quote matches; try `ogc find <text>` with a shorter word, or `ogc list`")
        open_c = [c for c in api.concerns_mentioning(g, t) if c["status"] == "open"]
        if open_c:
            hint += "; open concerns mention the word: " + ", ".join(f"{c['id']} ({c['label']})" for c in open_c)
        return None, meta, not_found(args, f"term '{t}'", hint, found)
    return iri, meta, 0


def check_filter(args, name: str, value, allowed: list[str], what: str) -> int:
    if value is None or value in allowed:
        return 0
    return not_found(args, f"--{name} value '{value}'", f"{what} must be one of: {', '.join(allowed)}")


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help="machine output (the api result, unchanged)")
    common.add_argument("--root", type=Path, default=argparse.SUPPRESS, help="repository checkout (default: found from cwd or OGC_ROOT)")
    common.add_argument("--no-cache", action="store_true", default=argparse.SUPPRESS)
    common.add_argument("--wide", action="store_true", default=argparse.SUPPRESS, help="do not clip table cells at 80 characters")
    common.add_argument("--model", action="store_true", default=argparse.SUPPRESS, help="also load the canonical model graph (sparql)")
    ap = argparse.ArgumentParser(prog="ogc", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter, parents=[common],
                                 epilog="global flags may be placed before or after the subcommand; quote multi-word names.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, help_, *spec):
        p = sub.add_parser(name, help=help_, parents=[common])
        for s in spec:
            p.add_argument(*s[0], **s[1])
        return p
    add("schema", "the map: classes and properties in use with counts, the pinned totals, the prefixes")
    add("find", "terms whose labels or quotes match: exact, then prefix, then substring", (["text"], {}), (["--no-quotes"], dict(action="store_true", help="labels only")))
    add("term", "everything about one term", (["term"], {}))
    add("define", "the narrative definition and the canonical source", (["term"], {}))
    add("quote", "the verbatim quotes on a term, with status", (["term"], {}))
    add("list", "the term table", (["--class"], dict(dest="klass")), (["--source"], {}))
    add("source", "one source and every citation of it", (["slug"], {}))
    add("sources", "the source register", (["--rank"], {}), (["--posture"], {}), (["--uncited"], dict(action="store_true")))
    add("ruling", "one ruling, text verbatim", (["id"], {}))
    add("rulings", "the rulings log", (["--term"], dict(help="a term: rulings it derives from or that resolve a concern naming it")), (["--grep"], dict(help="substring over text and change note")))
    add("concern", "one concern", (["id"], {}))
    add("concerns", "the concern register", (["--open"], dict(action="store_true")), (["--status"], {}), (["--severity"], {}))
    add("sci", "the essentials (SCI-01..12): statement, tag, shapes, terms, sources", (["id"], dict(nargs="?")))
    add("steps", "the seven EPO steps and the canon step each matches (R-31)")
    add("crosswalk", "one row per term: class, anchor relation, canonical source and locator, binding; --popper for the Popper rows", (["--class"], dict(dest="klass")), (["--source"], {}), (["--popper"], dict(action="store_true")))
    add("check-word", "is this word a registered label, of which term, or retired; what to write", (["words"], dict(nargs="+")))
    add("verify", "per citation of a term or source (or --all): where the quote was found", (["what"], dict(nargs="?")), (["--all"], dict(action="store_true")))
    add("sparql", "raw SPARQL (SELECT, ASK, CONSTRUCT, DESCRIBE) with the prefixes injected; @file.rq reads a file; --model adds the model graph", (["query"], {}))
    add("doctor", "files parse, labels unambiguous, pins hold, quotes located; VERDICT line")
    return ap


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = build_parser()
    try:
        args, extras = ap.parse_known_args(argv)
    except SystemExit as e:
        return int(e.code) if isinstance(e.code, int) else 2
    for k, v in (("json", False), ("root", None), ("no_cache", False), ("wide", False), ("model", False)):
        if not hasattr(args, k):
            setattr(args, k, v)
    text.WIDE = args.wide
    if extras:
        words = [x for x in extras if not x.startswith("-")]
        flags = [x for x in extras if x.startswith("-")]
        hint = f'unrecognized arguments: {" ".join(extras)}'
        if words and not flags:
            hint += f'; quote multi-word names: ogc {args.cmd} "{" ".join([getattr(args, "term", None) or getattr(args, "text", None) or ""] + words).strip()}"'
        if flags:
            hint += f"; see `ogc {args.cmd} --help`"
        return usage(args, hint)
    args.root = (args.root or find_root()).resolve()
    if not (args.root / "vocabulary" / "og-caie.ttl").exists():
        return usage(args, f"no og-caie-spec checkout at {args.root}; set --root or OGC_ROOT")
    c = args.cmd
    argstr = argstr_of(argv, c)
    if c == "doctor":
        return doctor(args)
    g = load(args.root, model=args.model, cache=not args.no_cache)

    if c == "schema":
        d = api.schema(g)
        return emit(args, c, argstr, d, lambda: ["## counts"] + [f"{k}: {v}" for k, v in d["counts"].items()] + ["", "## classes"] + text.table(d["classes"], ["cls", "count"])
                    + ["", "## properties"] + text.table(d["properties"], ["prop", "uses"]) + ["", "## prefixes", SPARQL_PREFIXES.rstrip(),
                       "", 'note: labels and definitions are language-tagged ("probe"@en); match with STR(?l) = "probe" or LCASE(STR(?l)).'])

    if c == "find":
        if not args.text.strip():
            return usage(args, "find needs text to match")
        rows = api.find(g, args.text, quotes=not args.no_quotes)
        concerns = [x for x in api.concerns_mentioning(g, args.text) if x["status"] == "open"]
        if not rows:
            hint = "no label or quote matches exactly, by prefix, or by substring; try `ogc list`"
            if concerns:
                hint += "; open concerns mention the word: " + ", ".join(f"{x['id']} ({x['label']})" for x in concerns)
            return not_found(args, f"'{args.text}'", hint)
        return emit(args, c, argstr, rows, lambda: text.table(rows, ["pref", "local", "match", "via", "class", "source"]) + [f"open concern mentioning the word: {x['id']} ({x['label']})" for x in concerns])

    if c == "verify":
        if args.all:
            rows = api.verify_all(g, args.root)
            return emit(args, c, argstr, rows, lambda: text.table(rows, VERIFY_COLS) + [f"({len(rows)} citations; " + ", ".join(f"{n} {s}" for s, n in sorted(__import__('collections').Counter(r['state'] for r in rows).items())) + ")"])
        if not args.what:
            return usage(args, "verify needs a term, a source slug, or --all")
        rows = api.verify_source(g, args.root, args.what) if re.fullmatch(r"[\w.-]+", args.what) else None
        if rows is not None:
            return emit(args, c, argstr, rows, lambda: text.table(rows, VERIFY_COLS))
        iri, meta, rc = resolve(args, g, args.what)
        if iri is None:
            return rc
        rows = api.verify_term(g, args.root, iri)
        return emit(args, c, argstr, rows, lambda: text.table(rows, VERIFY_COLS))

    if c in ("term", "define", "quote"):
        iri, meta, rc = resolve(args, g, args.term)
        if iri is None:
            return rc
        t = api.term_record(g, iri)
        t["resolved"] = meta
        if c == "term":
            return emit(args, c, argstr, t, lambda: text.term(t, meta))
        if c == "define":
            cc = t["canonical"]
            d = dict(term=t["pref"], definition=t["definition"], **{"class": t["class"]}, canonical=f"{cc.get('source_label', '')}, {cc.get('locator', '')}", resolved=meta)
            return emit(args, c, argstr, d, lambda: [f"## {t['pref']}"] + ([f"resolved via {meta['via']}"] if meta.get("via") else []) + [""] + text.wrap(t["definition"])
                        + ["", f"class: {t['class']}   canonical: {d['canonical']}" + (f"   status: {cc.get('status')}" if cc.get("status") else "")])
        q = [dict(holder="canonical", **{k: v for k, v in t["canonical"].items() if k != "node"})] if t["canonical"].get("quote") else []
        q += [dict(holder="seeAlso", **{k: v for k, v in x.items() if k != "node"}) for x in t["see_also"] if x["quote"]]
        noq = [f"{x['source']} {x['locator']}" for x in [t["canonical"], *t["see_also"]] if x and not x.get("quote")]

        def lines():
            L = [f"{len(q)} verbatim quotes on {t['pref']}; {len(noq)} citations without a quote", ""]
            for x in q:
                L += [f"[{x['holder']}] {x['source']} {x['locator']}  [{x['status']}]" + (f" verified by {x['verified_by']} on {x['verified_on']}" if x.get("verified_by") else "")] + text.wrap(f'"{x["quote"]}"') + [""]
            if noq:
                L.append("citations without a quote: " + "; ".join(noq))
            return L
        return emit(args, c, argstr, dict(quotes=q, without_quote=noq), lines)

    if c == "list":
        if (rc := check_filter(args, "class", args.klass, ["adopted", "refined", "coined"], "--class")):
            return rc
        rows = api.list_terms(g, args.klass, args.source)
        return emit(args, c, argstr, rows, lambda: text.table(rows, ["term", "local", "class", "source", "locator", "status"]))

    if c == "source":
        d = api.source_record(g, args.slug)
        if d is None:
            return not_found(args, f"source '{args.slug}'", "try `ogc sources`", [r["slug"] for r in api.sources_table(g) if args.slug.lower() in r["slug"]][:8])

        def lines():
            L = [f"## {d['slug']}: {d['label']}", ""] + text.kv(d, ["rank", "kind", "posture", "url", "digest", "status", "retrieval", "licence", "permission"])
            if d["snapshots"]:
                L += ["snapshots:"] + [f"  {s['file']} {s['hash']}" for s in d["snapshots"]]
            L += ["", f"citations ({len(d['citations'])}):"]
            for x in d["citations"]:
                L.append(f"  {x['term']}  [{x['holder']}] {x['locator']}" + (f"  [{x['status']}]" if x["status"] else "  (no quote)"))
                if x["quote"]:
                    L += text.wrap(f'"{x["quote"]}"', "      ")
            return L
        return emit(args, c, argstr, d, lines)

    if c == "sources":
        if (rc := check_filter(args, "rank", args.rank, ["1", "2", "3", "4", "reserve", "internal"], "--rank")):
            return rc
        if (rc := check_filter(args, "posture", args.posture, ["committed", "heldLocally", "citeOnly"], "--posture")):
            return rc
        rows = api.sources_table(g, args.rank, args.posture, args.uncited)
        return emit(args, c, argstr, rows, lambda: text.table(rows, ["slug", "rank", "posture", "kind", "citations", "snapshots", "label"]))

    if c == "ruling":
        d = api.ruling_record(g, args.id)
        if d is None:
            return not_found(args, f"ruling '{args.id}'", "ids look like R-05 (case-insensitive); try `ogc rulings`")
        return emit(args, c, argstr, d, lambda: [f"## {d['id']}  (order {d['order']}, {d['date']}, attributed to {d['attributed']})", "",
                                                 "resolves: " + "; ".join(f"{i} ({l})" for i, l in zip(d["resolves"], d["resolves_labels"])), "", "text (verbatim):"] + ["  " + l for l in d["text"].splitlines()]
                    + ["", "change:"] + text.wrap(d["change"]) + [f"terms deriving from it: {', '.join(d['derived_terms']) or '(none)'}"])

    if c == "rulings":
        term_iri = None
        if args.term is not None:
            term_iri, meta, rc = resolve(args, g, args.term)
            if term_iri is None:
                return rc
        rows = api.rulings_table(g, term_iri, args.grep)
        cols = ["id", "date", "concern"] + (["matched", "snippet"] if args.grep else ["text"])
        return emit(args, c, argstr, rows, lambda: text.table(rows, cols))

    if c == "concern":
        d = api.concern_record(g, args.id)
        if d is None:
            return not_found(args, f"concern '{args.id}'", "ids look like C-07 (case-insensitive); try `ogc concerns`")
        return emit(args, c, argstr, d, lambda: [f"## {d['id']}: {d['label']}", "", f"severity: {d['severity']}   status: {d['status']}   surfaced: {d['surfaced']} ({d['how']})",
                                                 f"terms: {', '.join(d['terms']) or '(none)'}", "", "problem:"] + text.wrap(d["problem"]) + ["", f"resolved by: {', '.join(d['resolved_by']) or '(open)'}"])

    if c == "concerns":
        if (rc := check_filter(args, "status", args.status, ["open", "ruled", "closed"], "--status")):
            return rc
        if (rc := check_filter(args, "severity", args.severity, ["H", "M", "L"], "--severity")):
            return rc
        rows = api.concerns_table(g, args.open, args.status, args.severity)
        return emit(args, c, argstr, rows, lambda: text.table(rows, ["id", "severity", "status", "terms", "resolved_by", "label"]))

    if c == "sci":
        rows = api.sci_table(g, args.id)
        if args.id and not rows:
            return not_found(args, f"essential '{args.id}'", "ids look like SCI-07; try `ogc sci`")
        if args.id:
            d = rows[0]
            return emit(args, c, argstr, d, lambda: [f"## {d['id']} {d['name']}  ({d['tag']})", ""] + text.wrap(d["statement"]) + ["", f"checked by: {', '.join(d['shapes'])}", f"terms: {', '.join(d['terms'])}", f"rests on: {', '.join(d['rests_on'])}"])
        return emit(args, c, argstr, rows, lambda: text.table(rows, ["id", "name", "tag", "shapes", "terms"]))

    if c == "steps":
        rows = api.steps_table(g)
        return emit(args, c, argstr, rows, lambda: [l for r in rows for l in ([f"## {r['label']}", f"  matches: {r['source']} {r['locator']}  [{r['status']}]"] + text.wrap(f'"{r["quote"]}"', "    ") + [f"  also: {a['source']} {a['locator']}" + (f"  [{a['status']}]" if a["status"] else "  (cite-only)") for a in r["also"]] + [""])])

    if c == "crosswalk":
        if args.popper:
            rows = api.popper(g)
            return emit(args, c, argstr, rows, lambda: [l for r in rows for l in ([f"## {r['order']} {r['concept']}"] + text.wrap(f'"{r["quote"]}"') + [f"  terms: {', '.join(r['terms'])}", f"  realized by: {', '.join(r['realized_by'])}"] + text.wrap(r["where"], "  where: ", "    ") + text.wrap(r["checkable"], "  checkable: ", "    ") + [""])])
        if (rc := check_filter(args, "class", args.klass, ["adopted", "refined", "coined"], "--class")):
            return rc
        rows = api.crosswalk(g, args.klass, args.source)
        return emit(args, c, argstr, rows, lambda: text.table(rows, ["term", "class", "relation", "source", "locator", "status", "see_also", "binding"]))

    if c == "check-word":
        rows = [api.check_word(g, w) for w in args.words]
        return emit(args, c, argstr, rows, lambda: [l for r in rows for l in text.check_word(r)])

    if c == "sparql":
        return sparql(args, g, argstr)
    return 2


def sparql(args, g, argstr: str) -> int:
    from rdflib.plugins.sparql import prepareQuery
    q = args.query
    if q.startswith("@"):
        p = Path(q[1:])
        if not p.exists():
            return usage(args, f"query file not found: {p}")
        q = p.read_text()
    if not q.strip():
        return usage(args, "sparql needs a query (or @file.rq)")
    if re.search(r"\bSERVICE\b", q, re.I):
        return usage(args, "federation is disabled: SERVICE is refused; the tool is a read-only reader of the local graphs")
    for name, iri in re.findall(r"PREFIX\s+([\w-]*):\s*<([^>]*)>", q, re.I):
        if name in PREFIXES and str(PREFIXES[name]) != iri:
            return usage(args, f"PREFIX {name}: <{iri}> would shadow the injected prefix {name}: <{PREFIXES[name]}>; drop it or use a different name")
    injected_lines = injected_chars = 0
    if "PREFIX" not in q.upper():
        injected_lines, injected_chars = SPARQL_PREFIXES.count("\n"), len(SPARQL_PREFIXES)
        q = SPARQL_PREFIXES + q
    try:
        pq = prepareQuery(q)
    except Exception as e:
        msg = str(e).splitlines()[0]
        msg = re.sub(r"\(at char (\d+)\)", lambda m: f"(at char {max(0, int(m.group(1)) - injected_chars)})", msg)
        m = re.search(r"\(line:(\d+), col:(\d+)\)", msg)
        if m:
            msg = msg[:m.start()] + f"(line:{int(m.group(1)) - injected_lines}, col:{m.group(2)}; positions are into your query)"
        return usage(args, f"query does not parse: {msg}")
    kind = pq.algebra.name
    if kind not in ("SelectQuery", "AskQuery", "ConstructQuery", "DescribeQuery"):
        return usage(args, f"only SELECT, ASK, CONSTRUCT, and DESCRIBE are accepted (got {kind}); the tool is read-only")
    digest = hashlib.sha256(args.query.encode()).hexdigest()[:12]
    header = f"{argstr} #sha256:{digest}"
    res = g.query(pq)
    if kind == "AskQuery":
        return emit(args, "sparql", header, dict(ask=bool(res.askAnswer)), lambda: [str(bool(res.askAnswer)).lower()])
    if kind in ("ConstructQuery", "DescribeQuery"):
        out = res.graph
        for k, v in PREFIXES.items():
            out.bind(k, v, replace=True)
        ttl = out.serialize(format="turtle")
        return emit(args, "sparql", header, dict(triples=len(out), turtle=ttl), lambda: ttl.rstrip("\n").splitlines() + [f"({len(out)} triples)"])
    cols = [str(v) for v in res.vars] if res.vars else []
    rows = [dict(zip(cols, [str(x) if x is not None else "" for x in r])) for r in res]
    rows.sort(key=lambda r: tuple(r.get(c, "") for c in cols))
    return emit(args, "sparql", header, rows, lambda: text.table(rows, cols) + [f"({len(rows)} rows)"])


def doctor(args) -> int:
    from rdflib import Graph, RDF
    from .graph import OGC, SKOS
    root = args.root
    ok = True
    checks = []

    def add(state, what, bad=False):
        nonlocal ok
        checks.append(dict(state=state, what=what))
        if bad:
            ok = False
    for f in SOURCE_FILES + [MODEL_FILE]:
        p = root / f
        if not p.exists():
            add("MISSING", f, True)
            continue
        try:
            add("ok", f"{f} ({len(Graph().parse(p))} triples)")
        except Exception as e:
            add("BROKEN", f"{f}: {e}", True)
    g = load(root, cache=not args.no_cache)
    amb = api.ambiguous_labels(g)
    add("ok" if not amb else "BAD", "every label resolves to one term" + ("" if not amb else ": " + "; ".join(f"'{a['label']}' -> {', '.join(a['terms'])}" for a in amb)), bool(amb))
    coined = [api.one(g, t, SKOS.prefLabel) for t in api.concepts(g) if api.one(g, t, OGC["class"]) == "coined"]
    add("ok" if len(coined) == 4 else "BAD", f"coinage is exactly four ({', '.join(sorted(coined))})", len(coined) != 4)
    noq = [api.one(g, t, SKOS.prefLabel) for t in api.concepts(g) if api.one(g, t, OGC["class"]) in ("adopted", "refined") and not api.one(g, g.value(t, OGC.canonical), OGC.quote)]
    add("ok" if not noq else "BAD", "every adopted or refined term carries a verbatim canonical quote" + (": missing on " + ", ".join(noq) if noq else ""), bool(noq))
    pending = [r for r in api.verify_all(g, root) if r["state"] == "pending"]
    add("ok" if not pending else "note", f"pending quotes: {len(pending)}" + (" (" + "; ".join(f"{r['term']} {r['locator']}" for r in pending) + ")" if pending else ""))
    missing = [r for r in api.verify_all(g, root) if r["state"] == "NOT FOUND"]
    add("ok" if not missing else "BAD", "every machine quote is located in its snapshot or digest" + (": " + "; ".join(f"{r['term']} {r['source']} {r['locator']} ({r['where']})" for r in missing) if missing else ""), bool(missing))
    bad = sorted(api.local(c) for c in g.subjects(RDF.type, OGC.Concern) if api.one(g, c, OGC.status) == "open" and (None, OGC.resolves, c) in g)
    add("ok" if not bad else "BAD", "no open concern has a resolving ruling" + (f": {', '.join(bad)}" if bad else ""), bool(bad))
    orders = sorted(int(api.one(g, r, OGC.order)) for r in g.subjects(RDF.type, OGC.Ruling))
    add("ok" if orders == list(range(1, len(orders) + 1)) else "BAD", f"ruling orders are 1..{len(orders)} with no gap", orders != list(range(1, len(orders) + 1)))
    open_c = api.concerns_table(g, open_only=True)
    add("note", f"open concerns: {', '.join(c['id'] for c in open_c) or '(none)'}")
    key = root / "generated" / "key-terms.md"
    if key.exists():
        try:
            sys.path.insert(0, str(root / "scripts"))
            from render import render_key_terms
            add("ok" if render_key_terms() == key.read_text() else "STALE", "generated/key-terms.md is current", render_key_terms() != key.read_text())
        except SystemExit as e:
            add("BAD", f"{{term}} roles: {e}", True)
    cache = sorted((root / ".cache").glob("ogc-graph-*.pkl")) if (root / ".cache").exists() else []
    add("cache", cache[0].name if cache else "(none)")
    verdict = f"VERDICT: {'PASS' if ok else 'FAIL'} (ogc doctor at {root})"
    if args.json:
        print(json.dumps(dict(sha=git_sha(root), checks=checks, ok=ok, verdict=verdict), indent=2))
        return 0 if ok else 1
    print(text.head("doctor", "", git_sha(root)))
    for ch in checks:
        print(f"{ch['state']:<8}{ch['what']}")
    print(verdict)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
