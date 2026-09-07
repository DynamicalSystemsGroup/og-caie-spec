"""ogc: navigate the OG-CAIE vocabulary graph. Deterministic, ontology-aware
retrieval; every command is a named query over the vocabulary, the sources,
the rulings, the essentials, the shapes and the crosswalk. First line of
every output: `# ogc <command> <args> @ <sha>` (the invocation in its canonical
form: --root and the global flags dropped, --model and --record last in that
order wherever they were typed, whitespace collapsed, newlines in an argument
escaped as \\n; for sparql the query and its sha256, or the @file and the
sha256 of its content); under --json the same triple is the `_ogc`
key of the one object printed (a list result sits under `rows`), and every
error is one object carrying `_ogc`, `error`, `hint` and `candidates`. Exit
0 success, 1 not found / ambiguous / bad filter value / refused / a failed
VERDICT, 2 usage. Read-only: no update forms, no federation, no named
graphs. Ids may be typed as the tool prints them: a local name, a CURIE
(term:probe, rul:R-16, run:mission-1, ogc:S0-Layers; the prefix in any case)
or a full IRI; a CURIE under a prefix the command does not read is refused
with the reader that does (rul: is read by ruling and concern, epo: by epo,
run: by record)."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

from . import api, text, views
from .graph import DOCTOR_FILES, PREFIXES, RUN, SPARQL_PREFIXES, find_root, git_sha, load

GLOBAL_FLAGS = ("--json", "--no-cache", "--wide")  # --model and --record change the answer, so they stay in the argstr that is printed and hashed
LOAD_CMDS = ("sparql", "record", "execute", "view", "views")  # the commands that read the model graph or the record; --model and --record apply only here
MODEL_CMDS = ("sparql", "execute", "view", "views")  # where --model changes (or names) what is read; elsewhere it is a usage error (round three, L2)
RECORD_CMDS = ("sparql", "record")  # where --record changes (or names) what is read
LOAD_HINT = ("--model and --record apply only to sparql, record, execute, view and views (the commands that read the model graph or the record): "
             "--model where the model graph is read (sparql, execute, view, views), --record where the record is read (sparql, record)")
MODEL_NS = ("sysml", "sysx", "elmt", "ogm")  # the model graph's prefixes; a query naming one is refused without --model (round three, M1)
READERS = {  # a CURIE's prefix names what it is and the reader for it; the hint when it is typed to another command (round three, M4)
    "term": ("a term", "ogc term {local}"), "rul": ("a ruling or concern", "ogc ruling {local}"), "epo": ("an EPO class, role or step", "ogc epo {local}"),
    "run": ("a record item", "ogc record {local}"), "src": ("a source", "ogc source {local}"), "tr": ("an essential", "ogc sci {local}"),
    "ogc": ("a shape (or the vocabulary itself)", "ogc shape {local}"), "xw": ("a Popper crosswalk row", "ogc crosswalk --popper"),
    **{k: ("the model graph, loaded by --model", "ogc --model sparql 'DESCRIBE {curie}'") for k in MODEL_NS}}
ECHO = 80  # an error line echoes at most this much of the argument, with three dots; the header keeps it whole (round three, L10)
PARAM_FLAGS = ("requirements", "criteria", "planned", "sessions", "populations")  # ogc execute: the executor's parameters, in the order printed
VERIFY_COLS = ["holder", "citation", "source", "posture", "locator", "status", "state", "where"]
VERIFY_STATUSES = ["machine", "human", "pending", "cite-only", "authors"]
VERIFY_STATES = ["verified", "digest", "human", "pending", "cite-only", "authors", "NOT FOUND"]
CLASSES = ["adopted", "refined", "coined"]
RANKS = ["1", "2", "3", "4", "reserve", "internal"]
PRECEDENCE_RANKS = ("1", "2", "3")  # the ranks a term's narrative definition is taken from, so a source there is cited (CLAUDE.md, precedence)
POSTURES = ["committed", "heldLocally", "citeOnly"]
STATUSES = ["open", "ruled", "closed"]
SEVERITIES = ["H", "M", "L"]
SCI_RANGE = "SCI-01..13"  # tests/test_ogc.py holds this against the graph
POPPER_ROWS = "seven"  # tests/test_ogc.py holds this against the graph
QUERY_MAX = 20_000
STEP_HINT = "a step by local name or label head (scope, 1 scope, C1 need, need)"
EXCLUDE = "these filters exclude each other"


def id_hint(example: str) -> str:
    """The id forms accepted, shown on an example of the right kind: R-16 gives (R-16, R16, r-016, 16)."""
    kind, num = example.split("-")
    return f"ids are case-insensitive; padded, unpadded and bare forms work ({example}, {kind}{num}, {kind.lower()}-0{num}, {int(num)})"


ID_HINT = id_hint("R-16")


class UsageError(Exception):
    """argparse's own usage errors, raised instead of printed so that --json can wrap them."""

    def __init__(self, message: str, usage_text: str = ""):
        super().__init__(message)
        self.usage_text = usage_text


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise UsageError(message, self.format_usage())


def argstr_of(argv: list[str], cmd: str) -> str:
    """The arguments as printed and hashed: without --root and the global flags,
    the command word dropped, --model and --record moved to the end in that
    order, newlines escaped as \\n so the line stays one line, other
    whitespace collapsed."""
    out, skip, loads = [], False, set()
    for a in argv:
        if skip:
            skip = False
            continue
        if a == "--root":
            skip = True
            continue
        if a.startswith("--root="):
            continue
        if a in ("--model", "--record"):
            loads.add(a)
            continue
        if a in GLOBAL_FLAGS or (a == cmd and not out):
            continue
        out.append(a.replace("\r\n", "\n").replace("\n", "\\n"))
    out += sorted(loads)  # --model before --record, wherever they were typed
    return re.sub(r"[ \t\f\v]+", " ", " ".join(out)).strip()


def prescan(argv: list[str], names: list[str]) -> SimpleNamespace:
    """What an error needs before argparse has spoken: --json, --root and the command word (`ogc` when none is known)."""
    root = None
    for i, a in enumerate(argv):
        if a == "--root" and i + 1 < len(argv):
            root = Path(argv[i + 1])
        elif a.startswith("--root="):
            root = Path(a.split("=", 1)[1])
    cmd = next((a for a in argv if a in names), "ogc")
    return SimpleNamespace(json="--json" in argv, root=(root or find_root()).resolve(), cmd=cmd, argstr=argstr_of(argv, cmd))


def stamp(args, cmd: str, argstr: str) -> dict:
    return {"command": cmd, "args": argstr, "sha": git_sha(args.root)}


def emit(args, cmd: str, argstr: str, data, lines_fn, summary=None) -> int:
    if args.json:
        out = {"_ogc": stamp(args, cmd, argstr)}
        if isinstance(data, list):
            out["rows"] = data
        else:
            out.update(data)
        if summary is not None:
            out["summary"] = summary
        print(json.dumps(out, indent=2, ensure_ascii=False, default=str))
        return 0
    print(text.head(cmd, argstr, git_sha(args.root)))
    for line in lines_fn():
        print(line)
    return 0


def envelope(args, error: str, hint: str, candidates=None) -> dict:
    """The one error object under --json: the invocation (`_ogc` with the real command), the error, a hint, the candidates."""
    return {"_ogc": stamp(args, args.cmd, args.argstr), "error": error, "hint": hint, "candidates": candidates or []}


def not_found(args, what: str, hint: str, candidates=None, state: str = "not found") -> int:
    """Exit 1: a name that did not resolve, a bad filter value, or a refused request; candidates are near misses, never the whole list."""
    what = text.short(what, ECHO)
    if args.json:
        print(json.dumps(envelope(args, f"{what} {state}", hint, candidates), indent=2, ensure_ascii=False))
    else:
        print(text.head(args.cmd, args.argstr, git_sha(args.root)))
        print(f"{what}: {state}. {hint}")
        for c in candidates or []:
            print(f"  candidate: {c}")
    return 1


def usage(args, msg: str, usage_text: str = "") -> int:
    """Exit 2: a usage error; `ogc: <msg>` on stderr (after argparse's usage line when it has one), or the one JSON object on stdout under --json."""
    if args.json:
        print(json.dumps(envelope(args, "usage", msg), indent=2, ensure_ascii=False))
    else:
        if usage_text:
            print(usage_text.rstrip(), file=sys.stderr)
        print(f"ogc: {msg}", file=sys.stderr)
    return 2


def refuse(args, msg: str) -> int:
    """Exit 1 with a hint on stderr (or the JSON envelope): the request is well formed but cannot be answered as asked."""
    if args.json:
        print(json.dumps(envelope(args, "refused", msg), indent=2, ensure_ascii=False))
    else:
        print(f"ogc: {msg}", file=sys.stderr)
    return 1


def namespace_hint(prefix: str, value: str) -> str:
    """What the prefix names and which reader takes it (round three, M4)."""
    local = api.bare(value)
    what, reader = READERS.get(prefix, ("a vocabulary the tool does not read by id", "ogc sparql 'DESCRIBE {curie}'"))
    if prefix == "rul" and local[:1].upper() == "C":
        reader = "ogc concern {local}"
    if prefix == "epo":
        return f"epo: classes and roles are read by `ogc epo {local}` (steps by `ogc quote {local}`)"
    return f"{prefix}: is {what}; try `{reader.format(local=local, curie=f'{prefix}:{local}')}`"


def foreign(args, value, what: str, accepted: tuple) -> int:
    """rc 1 with the right reader named when `value` is a CURIE or IRI under a prefix this command does not read; 0 otherwise."""
    p = api.prefix_of(value)
    if p is None or p in accepted:
        return 0
    return not_found(args, f"{what} '{api.norm(value)}'", namespace_hint(p, value))


def need(args, value, what: str) -> int:
    """rc 2 when a required id is missing, empty or blank; 0 otherwise."""
    if value is None or not value.strip():
        return usage(args, f"{what} is required and may not be empty or blank")
    return 0


def resolve(args, g, t: str, steps: bool = False):
    """A term IRI from a label, local name, CURIE or IRI; with steps=True also
    an EPO step (its local name or label head) when no term matches. Prints
    the not-found report itself; returns (iri, meta, rc)."""
    if need(args, t, "a term (a local name, prefLabel, altLabel, term: CURIE or IRI" + ("; or " + STEP_HINT + ")" if steps else ")")):
        return None, {}, 2
    rc = foreign(args, t, "term", ("term", "epo") if steps else ("term",))
    if rc:
        return None, {}, rc
    t = api.bare(t)
    iri, cands, meta = api.resolve_term(g, t)
    if iri is None and steps and not cands:
        st = api.resolve_step(g, t)
        if st is not None:
            return st, dict(via=f"step:{api.one(g, st, api.RDFS.label).split(':', 1)[0]}", step=True), 0
    if iri is None:
        found = [f"{p} ({l})" for p, l in cands] or api.candidates(g, t)
        hint = "ambiguous; use the local name" if cands else ("no exact label match; the candidates below are prefix, substring, quote or EPO label hits" if found else "no label or quote matches; try `ogc find <text>` with a shorter word, or `ogc list`")
        if steps and not cands:
            hint += "; " + STEP_HINT + " is also accepted"
        open_c = [c for c in api.concerns_mentioning(g, t) if c["status"] == "open"]
        if open_c:
            hint += "; open concerns mention the word: " + ", ".join(f"{c['id']} ({c['label']})" for c in open_c)
        return None, meta, not_found(args, f"term '{t}'", hint, found)
    return iri, meta, 0


def pick(value, allowed: list[str]):
    """The allowed spelling of a filter value, matched case-insensitively; None when it is not allowed."""
    if value is None:
        return None
    key = value.strip().lower()
    return next((a for a in allowed if a.lower() == key), None)


def check_filter(args, name: str, value, allowed: list[str]):
    """(canonical value, rc): rc is 1 and the allowed values are printed when the value is not one of them."""
    if value is None:
        return None, 0
    v = pick(value, allowed)
    if v is None:
        return None, not_found(args, f"--{name} value '{value}'", f"--{name} must be one of: {', '.join(allowed)} (case-insensitive)")
    return v, 0


def check_source(args, g, value):
    """(slug, rc): the registered slug for a --source value (a slug or src: CURIE, case-insensitive); rc 1 otherwise, with the near misses or, failing those, the allowed slugs (a filter value's allowed list, as the other filters print)."""
    if value is None:
        return None, 0
    rc = foreign(args, value, "--source value", ("src",))
    if rc:
        return None, rc
    src = api.resolve_source(g, api.bare(value))
    if src is None:
        slugs = api.source_slugs(g)
        return None, not_found(args, f"--source value '{value}'", "--source must be a registered slug (case-insensitive); see `ogc sources`", api.near(api.bare(value), slugs) or slugs)
    return api.local(src), 0


def build_parser() -> argparse.ArgumentParser:
    from .executor import CAP_NOTE, MUTATIONS, Params
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help="machine output: one object carrying the api result plus the `_ogc` key (command, args, sha); list results sit under `rows`; errors are one object with `_ogc`, `error`, `hint`, `candidates`")
    common.add_argument("--root", type=Path, default=argparse.SUPPRESS, help="repository checkout (default: found from cwd or OGC_ROOT)")
    common.add_argument("--no-cache", action="store_true", default=argparse.SUPPRESS, help="parse the Turtle afresh instead of reading the pickle cache under .cache/")
    common.add_argument("--wide", action="store_true", default=argparse.SUPPRESS, help="do not clip table cells at 80 characters")
    loads = argparse.ArgumentParser(add_help=False)
    loads.add_argument("--model", action="store_true", default=argparse.SUPPRESS, help="also load the canonical model graph model/og-caie.model.ttl (the OMG sysml: rendering of the structure; implied by view, views and execute); part of the printed and hashed args; " + LOAD_HINT)
    loads.add_argument("--record", action="store_true", default=argparse.SUPPRESS, help="also load the worked example's record track/measles-run.ttl (the run: namespace; implied by record); part of the printed and hashed args; " + LOAD_HINT)
    ap = Parser(prog="ogc", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter, parents=[common, loads],
                epilog="global flags may be placed before or after the subcommand; quote multi-word names.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    names = []

    def add(name, help_, *spec, **kw):
        names.append(name)
        p = sub.add_parser(name, help=help_, description=help_, parents=[common, loads] if name in LOAD_CMDS else [common], formatter_class=argparse.RawDescriptionHelpFormatter, **kw)
        for s in spec:
            p.add_argument(*s[0], **s[1])
        return p
    add("schema", "the map: classes and properties in use with counts, the pinned totals (shapes counted over every shape file, as `ogc shapes` does), the prefixes")
    add("find", "terms whose labels or quotes match: exact, then prefix, then substring", (["text"], dict(help="text to match against labels (and quotes unless --no-quotes)")),
        (["--no-quotes"], dict(action="store_true", help="labels only; part of the printed and hashed args")))
    add("term", "everything about one term", (["term"], dict(help="a local name, prefLabel, altLabel, term: CURIE or IRI (ids are case-insensitive, the prefix too)")))
    add("define", "the narrative definition and the canonical source (or who coined the term)", (["term"], dict(help="a local name, prefLabel, altLabel, term: CURIE or IRI (ids are case-insensitive, the prefix too)")))
    add("quote", "the verbatim quotes on a term or on an EPO step, with status", (["term"], dict(help="a term (label, local name, term: CURIE or IRI) or " + STEP_HINT)))
    add("list", "the term table (a coined term shows `(coined)` for its source)", (["--class"], dict(dest="klass", metavar="CLASS", help=f"one of {', '.join(CLASSES)} (case-insensitive)")),
        (["--source"], dict(metavar="SLUG", help="a registered source slug from `ogc sources` (case-insensitive; src: CURIE accepted)")))
    add("source", "one source and every citation of it", (["slug"], dict(help="a source slug from `ogc sources` (case-insensitive; src: CURIE or IRI accepted)")))
    add("sources", "the source register", (["--rank"], dict(help=f"one of {', '.join(RANKS)}")), (["--posture"], dict(help=f"one of {', '.join(POSTURES)} (case-insensitive)")),
        (["--uncited"], dict(action="store_true", help="only sources no citation names (not with --rank 1, 2 or 3: a source at a precedence rank is cited by the terms defined from it)")))
    add("ruling", "one ruling: the decision in the register's words, then the message as sent", (["id"], dict(help="R-16; " + ID_HINT + "; rul: CURIE or IRI accepted")))
    add("rulings", "the rulings log", (["--term"], dict(help="a term: rulings it derives from or that resolve a concern naming it")), (["--grep"], dict(metavar="TEXT", help="substring over the ruling text, the message as sent and the change note (non-empty)")))
    add("concern", "one concern", (["id"], dict(help="C-24; " + id_hint("C-24") + "; rul: CURIE or IRI accepted")))
    add("concerns", "the concern register", (["--open"], dict(action="store_true", help="only open concerns (the same as --status open; not with another --status)")), (["--status"], dict(help=f"one of {', '.join(STATUSES)}")),
        (["--severity"], dict(help=f"one of {', '.join(SEVERITIES)} (case-insensitive)")))
    add("sci", f"the essentials ({SCI_RANGE}): statement, tag, shapes, terms, sources", (["id"], dict(nargs="?", help=f"one essential, {SCI_RANGE}; " + id_hint("SCI-07") + "; tr: CURIE or IRI accepted; omitted: the table")))
    add("steps", "the twelve steps of the two cycles and the canon step each matches (R-31, R-32)")
    add("epo", "one EPO class or role (vocabulary/epo.ttl): label, superclasses (a role's types), subclasses and instances, the layer it is pinned at, the term it names with its headword, the disjointness axioms, and the shapes whose targets, paths or SPARQL bodies mention it",
        (["name"], dict(help="a class or role by local name, case-insensitive (StakeholderRepresentation, AuthorizedRepresentativeRole, accountExecutiveRole; epo: CURIE or IRI accepted); a step is read by `ogc quote`")))
    add("record", "the worked example's record (track/measles-run.ttl): its items by step, C1..C6 then 1..6, with who and when; then the items without a step and the parties; with a name, everything the record says about that one item (R-47, closes C-44)",
        (["name"], dict(nargs="?", help="an item's local name, case-insensitive (mission-1, attestation-1, annie; run: CURIE or IRI accepted); omitted: the listing")))
    add("execute", "execute the process from the model graph and run the checks over the emitted record (C-30); VERDICT: PASS when the record conforms, no item kind is missing and the traceback is non-empty, else FAIL and exit 1; " + CAP_NOTE,
        (["--mutate"], dict(action="append", metavar="NAME", help="break one thing in the emitted record before the checks; repeatable, applied in order; one of: " + ", ".join(sorted(MUTATIONS)))),
        (["--turtle"], dict(action="store_true", help="print the emitted record instead of the checks")),
        (["--requirements"], dict(type=int, metavar="N", help=f"requirements in the requirement set (positive; default {Params.requirements})")),
        (["--criteria"], dict(type=int, metavar="N", help=f"acceptance criteria per requirement (positive; requirements times criteria at most 100; default {Params.criteria_per_requirement})")),
        (["--planned"], dict(type=int, metavar="N", help=f"criteria the test plan exercises, the rest stay uncovered (positive, at most requirements times criteria; default {Params.planned})")),
        (["--sessions"], dict(type=int, metavar="N", help=f"sessions executed against the test item (positive, sessions at most 20; default {Params.sessions})")),
        (["--populations"], dict(type=int, metavar="N", help=f"affected populations, the first interviewed and the others represented (positive, at most 20; default {Params.populations})")),
        epilog="mutations:\n" + "\n".join(f"  {n:<32} {MUTATIONS[n][0]}" for n in sorted(MUTATIONS)))
    add("views", "the reusable views of the model graph: what each brings into focus and leaves out (R-38)")
    add("view", "one view of the model graph as mermaid, with the perspective it encodes (R-38)", (["name"], dict(help="one of " + ", ".join(sorted(views.VIEWS)) + " (case-insensitive)")))
    add("crosswalk", f"one row per term: class, anchor relation, canonical source and locator, binding; --popper for the {POPPER_ROWS} Popper rows",
        (["--class"], dict(dest="klass", metavar="CLASS", help=f"one of {', '.join(CLASSES)} (case-insensitive); not with --popper")), (["--source"], dict(metavar="SLUG", help="a registered source slug (case-insensitive); not with --popper")),
        (["--popper"], dict(action="store_true", help=f"the {POPPER_ROWS} Popper rows instead of the term table (they have no class or source, so --class and --source are refused)")))
    add("check-word", "is this word a registered label, of which term, or retired; what to write", (["words"], dict(nargs="+", help="one or more words or phrases (non-empty); quote multi-word ones")))
    add("verify", "per citation of a term, a source or a step (or --all): where the quote was found", (["what"], dict(nargs="?", help=STEP_HINT + "; or a term (label, local name, term: CURIE or IRI); or a source slug")),
        (["--all"], dict(action="store_true", help="every citation in the graph (the terms', the steps' and the crosswalk rows'), with a summary line; not together with a term")),
        (["--status"], dict(help=f"only citations whose quote status is one of {', '.join(VERIFY_STATUSES)} (`ogc verify --all --status pending`: the quotes awaiting a named verification)")),
        (["--state"], dict(help=f"only citations located in one of the states {', '.join(VERIFY_STATES)}")))
    add("shapes", "the SHACL node shapes with their targets, from every shape file")
    add("shape", "one node shape: target, property constraints (path, min, max, class, in, hasValue, datatype) and each SPARQL constraint's message with its sh:select body", (["id"], dict(help="a shape's local name, case-insensitive (S3-PlanApproval, m1-parties, RulingShape; ogc: CURIE or IRI accepted)")))
    add("sparql", "raw SPARQL (SELECT, ASK, CONSTRUCT, DESCRIBE) with the prefixes injected; @file.rq reads a file; --model adds the model graph, --record the record (a query naming run: or typing by a record class is refused without it)",
        (["query"], dict(help=f"the query text or @file.rq (at most {QUERY_MAX} characters); rows are sorted unless it has ORDER BY; no SERVICE, GRAPH or FROM")))
    add("doctor", "every file the tool reads parses, labels unambiguous, pins hold, quotes located; VERDICT line")
    ap.command_names = names
    return ap


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = build_parser()
    pre = prescan(argv, ap.command_names)
    if any((a == "--root" and (i + 1 >= len(argv) or not argv[i + 1].strip())) or (a.startswith("--root=") and not a[7:].strip()) for i, a in enumerate(argv)):
        return usage(pre, "--root needs a path and got none; give the checkout (or set OGC_ROOT), or omit it to find the checkout from the working directory")
    try:
        args, extras = ap.parse_known_args(argv)
    except UsageError as e:
        return usage(pre, str(e), e.usage_text)
    except SystemExit as e:  # --help
        return int(e.code) if isinstance(e.code, int) else 0
    for k, v in (("json", False), ("root", None), ("no_cache", False), ("wide", False), ("model", False), ("record", False)):
        if not hasattr(args, k):
            setattr(args, k, v)
    text.WIDE = args.wide
    args.root = (args.root or find_root()).resolve()
    c = args.cmd
    args.argv = argv
    args.argstr = argstr_of(argv, c)
    if extras:
        if any(x in ("--model", "--record") for x in extras) or ((args.model or args.record) and c not in LOAD_CMDS):
            return usage(args, LOAD_HINT)
        rest = list(argv)
        for x in extras:  # the stray arguments leave the printed args, so a query and what followed it stay apart (round three, L5)
            del rest[len(rest) - 1 - rest[::-1].index(x)]
        args.argstr = argstr_of(rest, c)
        words = [x for x in extras if not x.startswith("-")]
        flags = [x for x in extras if x.startswith("-")]
        hint = f'unrecognized arguments: {" ".join(extras)}'
        if words and not flags:
            hint += f'; quote multi-word names: ogc {c} "{text.short(" ".join([getattr(args, "term", None) or getattr(args, "text", None) or ""] + words).strip(), ECHO)}"'
        if flags:
            hint += f"; see `ogc {c} --help`"
        return usage(args, hint)
    if (args.model and c not in MODEL_CMDS) or (args.record and c not in RECORD_CMDS):
        return usage(args, LOAD_HINT)
    if not (args.root / "vocabulary" / "og-caie.ttl").exists():
        return usage(args, f"no og-caie-spec checkout at {args.root}; set --root or OGC_ROOT")
    argstr = args.argstr
    if c == "doctor":
        return doctor(args)
    if c in ("shapes", "shape"):
        return shapes(args, c, argstr)
    if c in ("view", "views", "execute"):
        args.model = True
    if c == "record":
        args.record = True
    g = load(args.root, model=args.model, cache=not args.no_cache, record=args.record)

    if c == "schema":
        d = api.schema(g, args.root)
        return emit(args, c, argstr, d, lambda: ["## counts"] + [f"{k}: {v}" for k, v in d["counts"].items()] + ["", "## classes"] + text.table(d["classes"], ["cls", "count"])
                    + ["", "## properties"] + text.table(d["properties"], ["prop", "uses"]) + ["", "## prefixes", SPARQL_PREFIXES.rstrip(),
                       "", 'note: labels and definitions are language-tagged ("probe"@en); match with STR(?l) = "probe" or LCASE(STR(?l)).'])

    if c == "find":
        if need(args, args.text, "text to match"):
            return 2
        if foreign(args, args.text, "text", ("term", "epo")):
            return 1
        key = api.bare(args.text)
        rows = api.find(g, key, quotes=not args.no_quotes)
        concerns = [x for x in api.concerns_mentioning(g, key) if x["status"] == "open"]
        if not rows:
            hint = "no label, quote or EPO label matches exactly, by prefix, or by substring; try `ogc list`"
            if concerns:
                hint += "; open concerns mention the word: " + ", ".join(f"{x['id']} ({x['label']})" for x in concerns)
            return not_found(args, f"'{args.text}'", hint)
        return emit(args, c, argstr, rows, lambda: text.table(rows, ["pref", "local", "match", "via", "class", "source"])
                    + (["(a hit via epo: is an EPO class or role, not a term; read it with `ogc epo <name>`)"] if any(r["via"].startswith("epo:") for r in rows) else [])
                    + [f"open concern mentioning the word: {x['id']} ({x['label']})" for x in concerns])

    if c == "verify":
        return verify(args, g, argstr)

    if c in ("term", "define", "quote"):
        iri, meta, rc = resolve(args, g, args.term, steps=(c == "quote"))
        if iri is None:
            return rc
        if meta.get("step"):
            head = meta["via"].split(":", 1)[1]
            q = api.step_citations(g, iri)
            return emit(args, c, argstr, dict(step=head, quotes=[x for x in q if x["quote"]], without_quote=[f"{x['source']} {x['locator']}" for x in q if not x["quote"]], resolved=meta),
                        lambda: quote_lines(f"step {head}", [x for x in q if x["quote"]], [f"{x['source']} {x['locator']}" for x in q if not x["quote"]]))
        t = api.term_record(g, iri)
        t["resolved"] = meta
        if c == "term":
            return emit(args, c, argstr, t, lambda: text.term(t, meta))
        if c == "define":
            cc = t["canonical"]
            coined = t["coined_by"] if t["class"] == "coined" and not cc else None
            d = dict(term=t["pref"], definition=t["definition"], **{"class": t["class"]}, canonical=f"{cc.get('source_label', '')}, {cc.get('locator', '')}" if cc else None,
                     coined_by=coined, status=cc.get("status") or None, resolved=meta)
            tail = f"coined by: {coined}" if coined else f"canonical: {d['canonical']}" + (f"   status: {d['status']}" if d["status"] else "")
            return emit(args, c, argstr, d, lambda: [f"## {t['pref']}"] + ([f"resolved via {meta['via']}"] if meta.get("via") else []) + [""] + text.wrap(t["definition"])
                        + ["", f"class: {t['class']}   {tail}"])
        q = [dict(citation="canonical", **{k: v for k, v in t["canonical"].items() if k != "node"})] if t["canonical"].get("quote") else []
        q += [dict(citation="seeAlso", **{k: v for k, v in x.items() if k != "node"}) for x in t["see_also"] if x["quote"]]
        noq = [f"{x['source']} {x['locator']}" for x in [t["canonical"], *t["see_also"]] if x and not x.get("quote")]
        return emit(args, c, argstr, dict(quotes=q, without_quote=noq), lambda: quote_lines(t["pref"], q, noq))

    if c == "list":
        klass, rc = check_filter(args, "class", args.klass, CLASSES)
        if rc:
            return rc
        source, rc = check_source(args, g, args.source)
        if rc:
            return rc
        rows = api.list_terms(g, klass, source)
        return emit(args, c, argstr, rows, lambda: text.table(rows, ["term", "local", "class", "source", "locator", "status"]))

    if c == "source":
        if need(args, args.slug, "a source slug"):
            return 2
        if foreign(args, args.slug, "source", ("src",)):
            return 1
        slug = api.bare(args.slug)
        d = api.source_record(g, slug)
        if d is None:
            return not_found(args, f"source '{args.slug}'", "slugs are case-insensitive; try `ogc sources`", api.near(slug, api.source_slugs(g)))

        def lines():
            L = [f"## {d['slug']}: {d['label']}", ""] + text.kv(d, ["rank", "kind", "posture", "url", "digest", "status", "retrieval", "licence", "permission"])
            if d["snapshots"]:
                L += ["snapshots:"] + [f"  {s['file']} {s['hash']}" for s in d["snapshots"]]
            L += ["", f"citations ({len(d['citations'])}):"]
            for x in d["citations"]:
                L.append(f"  {x['term']}  [{x['citation']}] {x['locator']}  [{x['status']}]")
                if x["quote"]:
                    L += text.wrap(f'"{x["quote"]}"', "      ")
            return L
        return emit(args, c, argstr, d, lines)

    if c == "sources":
        rank, rc = check_filter(args, "rank", args.rank, RANKS)
        if rc:
            return rc
        posture, rc = check_filter(args, "posture", args.posture, POSTURES)
        if rc:
            return rc
        if args.uncited and rank in PRECEDENCE_RANKS:
            return usage(args, f"{EXCLUDE}: --uncited and --rank {rank} (a source at rank 1, 2 or 3 is registered for the definitions terms take from it, so it is cited; uncited sources are found at rank 4, reserve or internal)")
        rows = api.sources_table(g, rank, posture, args.uncited)
        return emit(args, c, argstr, rows, lambda: text.table(rows, ["slug", "rank", "posture", "kind", "citations", "snapshots", "label"]))

    if c == "ruling":
        if need(args, args.id, "a ruling id"):
            return 2
        if foreign(args, args.id, "ruling", ("rul",)):
            return 1
        d = api.ruling_record(g, api.bare(args.id))
        if d is None:
            return not_found(args, f"ruling '{args.id}'", f"ids look like R-16 ({ID_HINT}); try `ogc rulings`")
        return emit(args, c, argstr, d, lambda: [f"## {d['id']}  (order {d['order']}, {d['date']}, attributed to {d['attributed']})", "",
                                                 "resolves: " + "; ".join(f"{i} ({l})" for i, l in zip(d["resolves"], d["resolves_labels"])), "", "text:"] + ["  " + l for l in d["text"].splitlines()]
                    + ["", "as sent:"] + ["  " + l for l in d["verbatim"].splitlines()]
                    + ["", "change:"] + text.wrap(d["change"]) + [f"terms deriving from it: {', '.join(d['derived_terms']) or '(none)'}"])

    if c == "rulings":
        if args.grep is not None and not args.grep.strip():
            return usage(args, "--grep needs a non-empty substring; omit it for the whole log")
        term_iri = None
        if args.term is not None:
            term_iri, meta, rc = resolve(args, g, args.term)
            if term_iri is None:
                return rc
        rows = api.rulings_table(g, term_iri, args.grep)
        if not args.grep:
            for r in rows:
                r.pop("matched", None)
                r.pop("snippet", None)
        cols = ["id", "date", "concern"] + (["matched", "snippet"] if args.grep else ["text"])
        return emit(args, c, argstr, rows, lambda: text.table(rows, cols))

    if c == "concern":
        if need(args, args.id, "a concern id"):
            return 2
        if foreign(args, args.id, "concern", ("rul",)):
            return 1
        d = api.concern_record(g, api.bare(args.id))
        if d is None:
            return not_found(args, f"concern '{args.id}'", f"ids look like C-24 ({id_hint('C-24')}); try `ogc concerns`")
        return emit(args, c, argstr, d, lambda: [f"## {d['id']}: {d['label']}", "", f"severity: {d['severity']}   status: {d['status']}   surfaced: {d['surfaced']} ({d['how']})",
                                                 f"terms: {', '.join(d['terms']) or '(none)'}", "", "problem:"] + text.wrap(d["problem"]) + ["", f"resolved by: {', '.join(d['resolved_by']) or '(open)'}"])

    if c == "concerns":
        status, rc = check_filter(args, "status", args.status, STATUSES)
        if rc:
            return rc
        severity, rc = check_filter(args, "severity", args.severity, SEVERITIES)
        if rc:
            return rc
        if args.open and status and status != "open":
            return usage(args, f"{EXCLUDE}: --open is --status open, not --status {status}; give one")
        rows = api.concerns_table(g, args.open, status, severity)
        return emit(args, c, argstr, rows, lambda: text.table(rows, ["id", "severity", "status", "terms", "resolved_by", "label"]))

    if c == "sci":
        if args.id is not None and need(args, args.id, "an essential's id (omit it for the table)"):
            return 2
        if args.id is not None and foreign(args, args.id, "essential", ("tr",)):
            return 1
        sid = api.bare(args.id) if args.id else None
        rows = api.sci_table(g, sid)
        if sid and not rows:
            return not_found(args, f"essential '{args.id}'", f"ids look like SCI-07, {SCI_RANGE} ({id_hint('SCI-07')}); try `ogc sci`")
        if sid:
            d = rows[0]
            return emit(args, c, argstr, d, lambda: [f"## {d['id']} {d['name']}  ({d['tag']})", ""] + text.wrap(d["statement"]) + ["", f"checked by: {', '.join(d['shapes'])}", f"terms: {', '.join(d['terms'])}", f"rests on: {', '.join(d['rests_on'])}"])
        return emit(args, c, argstr, rows, lambda: text.table(rows, ["id", "name", "tag", "shapes", "terms"]))

    if c == "execute":
        return execute(args, g, argstr)

    if c == "record":
        return record(args, g, argstr)

    if c == "views":
        rows = views.views_table()
        return emit(args, c, argstr, rows, lambda: [l for r in rows for l in ([f"## {r['name']}: {r['title']}"] + text.wrap(f"in focus: {r['focus']}", "  ") + text.wrap(f"leaves out: {r['leaves_out']}", "  ") + [""])])

    if c == "view":
        if need(args, args.name, "a view name"):
            return 2
        name = api.bare(args.name).lower()
        if name not in views.VIEWS:
            return not_found(args, f"view '{args.name}'", "names are case-insensitive; try `ogc views`", sorted(views.VIEWS))
        d = views.view_record(g, name)
        return emit(args, c, argstr, d, lambda: [f"## {d['name']}: {d['title']}"] + text.wrap(f"in focus: {d['focus']}", "  ") + text.wrap(f"leaves out: {d['leaves_out']}", "  ") + ["", "```mermaid", *d["mermaid"].splitlines(), "```"])

    if c == "epo":
        return epo(args, g, argstr)

    if c == "steps":
        rows = api.steps_table(g)
        return emit(args, c, argstr, rows, lambda: [l for r in rows for l in ([f"## {r['label']}", f"  matches: {r['source']} {r['locator']}  [{r['status']}]"] + text.wrap(f'"{r["quote"]}"', "    ") + [f"  also: {a['source']} {a['locator']}  [{a['status']}]" for a in r["also"]] + [""])])

    if c == "crosswalk":
        if args.popper and (args.klass is not None or args.source is not None):
            return usage(args, f"{EXCLUDE}: --popper prints the {POPPER_ROWS} Popper rows, which have no class or source; drop --popper or the filter")
        if args.popper:
            rows = api.popper(g)
            return emit(args, c, argstr, rows, lambda: [l for r in rows for l in ([f"## {r['order']} {r['concept']}"] + text.wrap(f'"{r["quote"]}"') + [f"  terms: {', '.join(r['terms'])}", f"  realized by: {', '.join(r['realized_by'])}"] + text.wrap(r["where"], "  where: ", "    ") + text.wrap(r["checkable"], "  checkable: ", "    ") + [""])])
        klass, rc = check_filter(args, "class", args.klass, CLASSES)
        if rc:
            return rc
        source, rc = check_source(args, g, args.source)
        if rc:
            return rc
        rows = api.crosswalk(g, klass, source)
        return emit(args, c, argstr, rows, lambda: text.table(rows, ["term", "class", "relation", "source", "locator", "status", "see_also", "binding"]))

    if c == "check-word":
        if any(not w.strip() for w in args.words):
            return usage(args, "check-word needs a word; empty or blank words are refused")
        for w in args.words:
            if foreign(args, w, "word", ("term",)):
                return 1
        rows = [api.check_word(g, api.bare(w)) for w in args.words]
        return emit(args, c, argstr, rows, lambda: [l for r in rows for l in text.check_word(r)])

    if c == "sparql":
        return sparql(args, g, argstr)
    return 2


def verify(args, g, argstr: str) -> int:
    if args.all and args.what:
        return usage(args, "give a term or --all, not both")
    status, rc = check_filter(args, "status", args.status, VERIFY_STATUSES)
    if rc:
        return rc
    state, rc = check_filter(args, "state", args.state, VERIFY_STATES)
    if rc:
        return rc

    def keep(rows):
        return [r for r in rows if (status is None or r["status"] == status) and (state is None or r["state"] == state)]
    if args.all:
        rows = keep(api.verify_all(g, args.root))
        states = dict(sorted(Counter(r["state"] for r in rows).items()))
        summary = dict(citations=len(rows), states=states)
        return emit(args, "verify", argstr, rows, lambda: text.table(rows, VERIFY_COLS) + [f"({len(rows)} citations" + ("; " + ", ".join(f"{n} {s}" for s, n in states.items()) if states else "") + ")"], summary=summary)
    if need(args, args.what, "a term, a source slug, a step, or --all"):
        return 2
    if foreign(args, args.what, "term, source or step", ("term", "src", "epo")):
        return 1
    what = api.bare(args.what)
    rows = api.verify_source(g, args.root, what) if re.fullmatch(r"[\w.-]+", what) else None
    if rows is not None:
        rows = keep(rows)
        return emit(args, "verify", argstr, rows, lambda: text.table(rows, VERIFY_COLS))
    iri, meta, rc = resolve(args, g, what, steps=True)
    if iri is None:
        return rc
    rows = keep(api.verify_term(g, args.root, iri))
    return emit(args, "verify", argstr, rows, lambda: text.table(rows, VERIFY_COLS))


def quote_lines(name: str, q: list[dict], noq: list[str]) -> list[str]:
    L = [f"{len(q)} verbatim quotes on {name}; {len(noq)} citations without a quote", ""]
    for x in q:
        L += [f"[{x['citation']}] {x['source']} {x['locator']}  [{x['status']}]" + (f" verified by {x['verified_by']} on {x['verified_on']}" if x.get("verified_by") else "")] + text.wrap(f'"{x["quote"]}"') + [""]
    if noq:
        L.append("citations without a quote (cite-only): " + "; ".join(noq))
    return L


def epo(args, g, argstr: str) -> int:
    if need(args, args.name, "an EPO class or role (a local name, epo: CURIE or IRI)"):
        return 2
    if foreign(args, args.name, "EPO class or role", ("epo",)):
        return 1
    name = api.bare(args.name)
    node, kind, cands = api.resolve_epo(g, name)
    if node is None:
        st = api.resolve_step(g, name)
        if st is not None:
            head = api.one(g, st, api.RDFS.label).split(":", 1)[0]
            return not_found(args, f"EPO class or role '{args.name}'", f"epo:{api.local(st)} is the step {head}, read by `ogc quote {api.local(st)}`, `ogc verify {api.local(st)}` and `ogc steps`", state="is a step")
        return not_found(args, f"EPO class or role '{args.name}'", "local names are case-insensitive; the candidates are near misses; `ogc find <text>` searches the labels", cands)
    d = api.epo_record(g, args.root, node, kind)

    def lines():
        L = [f"## {d['id']}  ({d['kind']})"] + text.wrap(d["label"])
        if d["comment"]:
            L += text.wrap(d["comment"], "  note: ", "    ")
        L.append("")
        L.append(f"superclasses: {', '.join(d['superclasses']) or '(none)'}" if d["kind"] == "class" else f"types: {', '.join(d['types']) or '(none)'}")
        if d["subclasses"]:
            L.append(f"subclasses: {', '.join(d['subclasses'])}")
        if d["instances"]:
            L.append(f"instances: {', '.join(d['instances'])}")
        L.append(f"pinned at: {d['pinned_at']['id']} ({d['pinned_at']['label']})" if d["pinned_at"] else "pinned at: (none)")
        L.append("term: " + ("; ".join(f"{t['headword']} ({t['local']})" for t in d["terms"]) if d["terms"] else "(none)"))
        L.append(f"disjoint with: {', '.join(d['disjoint_with']) or '(none)'}")
        L += ["", f"shapes mentioning it ({len(d['shapes'])}):"] + text.table(d["shapes"], ["id", "file", "where"])
        return L
    return emit(args, "epo", argstr, d, lines)


def who_cell(r: dict) -> str:
    """The who column of the listing: the agents, and the generating activity they were derived through (round three, L9)."""
    return ", ".join(r["who"] or []) + (f" (via {r['via']})" if r["via"] and r["who"] else "")


def record(args, g, argstr: str) -> int:
    if args.name is None:
        rows = api.record_rows(g)
        groups = {k: [dict(r, who=who_cell(r)) for r in rows if r["group"] == k] for k in ("record", "step", "no-step", "party")}
        return emit(args, "record", argstr, rows, lambda: [f"## the record ({len(groups['record'])})"] + text.table(groups["record"], ["item", "class", "label"])
                    + ["", f"## items by step ({len(groups['step'])}; C1..C6 then 1..6)"] + text.table(groups["step"], ["step", "item", "class", "who", "when"])
                    + ["", f"## items without a step ({len(groups['no-step'])})"] + text.table(groups["no-step"], ["item", "class", "who", "when"])
                    + ["", f"## parties and machines ({len(groups['party'])})"] + text.table(groups["party"], ["item", "class", "label"]))
    if need(args, args.name, "an item's local name (mission-1, attestation-1, annie; omit it for the listing)"):
        return 2
    if foreign(args, args.name, "record item", ("run",)):
        return 1
    iri, cands = api.resolve_record_item(g, api.bare(args.name))
    if iri is None:
        return not_found(args, f"record item '{args.name}'", "local names are case-insensitive; the candidates are near misses; try `ogc record` for the listing", cands)
    d = api.record_item(g, iri)

    def lines():
        L = [f"## {d['item']}  ({d['class']})" + (f"  step {d['step']}" if d["step"] else "")]
        if d["label"]:
            L += text.wrap(d["label"])
        L += ["", f"who: {', '.join(d['who'] or []) or '(none)'}   when: {d['when'] or '(none)'}" + (f"   (via {d['via']})" if d["via"] else ""), "", f"triples ({len(d['triples'])}):"]
        for t in d["triples"]:
            L += text.wrap(f"{t['predicate']} {t['object']}" + (f"  ({t['label']})" if t["label"] else ""), "  ", "      ")
        L += ["", f"referenced by ({len(d['referenced_by'])}):"] + ([f"  {t['subject']} {t['predicate']}" + (f"  ({t['label']})" if t["label"] else "") for t in d["referenced_by"]] or ["  (none)"])
        return L
    return emit(args, "record", argstr, d, lines)


def execute(args, g, argstr: str) -> int:
    from . import executor
    from rdflib import Graph
    names = []
    for m in args.mutate or []:
        key = m.strip().lower()
        if key not in executor.MUTATIONS:
            return not_found(args, f"mutation '{m}'", "--mutate takes one of the names below (case-insensitive) and may be repeated", sorted(executor.MUTATIONS))
        if key in names:
            return usage(args, f"mutation named twice: {key}; --mutate may be repeated with different names, each applied once in order")
        names.append(key)
    given = {k: getattr(args, k) for k in PARAM_FLAGS if getattr(args, k, None) is not None}
    params = executor.params_of(**given)
    reason = executor.validate(params)
    if reason:
        return not_found(args, "execute parameters " + ", ".join(f"{k} {v}" for k, v in given.items()), reason, state="refused")
    model = Graph()
    for t in g.triples((None, None, None)):
        model.add(t)
    shapes = Graph(); shapes.parse(args.root / "shapes" / "epo.shapes.ttl")
    epo = Graph(); epo.parse(args.root / "vocabulary" / "epo.ttl")
    rec = executor.execute(model, params)
    for n in names:
        executor.MUTATIONS[n][1](rec)
    pd = executor.params_dict(params)
    if args.turtle:
        return emit(args, "execute", argstr, {"mutations": names, "params": pd, "turtle": rec.serialize(format="turtle")}, lambda: rec.serialize(format="turtle").splitlines())
    d = executor.check(rec, model, shapes, epo)
    d["mutations"] = names
    d["params"] = pd
    ok = bool(d["conforms"]) and not d["missing"] and d["traceback"] > 0
    d["ok"] = ok
    d["verdict"] = f"VERDICT: {'PASS' if ok else 'FAIL'} (ogc execute{(' ' + argstr) if argstr else ''})"  # the parenthesis is the header's args
    cov = d["coverage"]
    emit(args, "execute", argstr, d, lambda: ["parameters: " + ", ".join(f"{k} {v}" for k, v in pd.items()), f"mutations: {', '.join(names) or 'none'}",
                                              f"conforms: {d['conforms']}" + (f"  (fired: {', '.join(d['fired'])})" if d["fired"] else ""),
                                              f"missing item kinds: {', '.join(d['missing']) or 'none'}",
                                              f"coverage: {cov['coverage']:.4f} (pass {cov['passRate']:.2f}, fail {cov['failRate']:.2f}, cannot tell {cov['cantTellRate']:.2f})",
                                              f"traceback rows: {d['traceback']}", d["verdict"]])
    return 0 if ok else 1


def shapes(args, c: str, argstr: str) -> int:
    if c == "shapes":
        rows = api.shapes_table(args.root)
        return emit(args, c, argstr, rows, lambda: text.table(rows, ["id", "target", "properties", "sparql", "file"]))
    if need(args, args.id, "a shape id"):
        return 2
    sid = api.bare(args.id)
    if api.prefix_of(args.id) not in (None, "ogc") and api.shape_record(args.root, sid) is not None:  # the shape exists, the prefix is wrong (round three, M4)
        return not_found(args, f"shape '{api.norm(args.id)}'", f"the shapes' IRIs are under ogc:, not {api.prefix_of(args.id)}:; try `ogc shape {sid}` or `ogc shape ogc:{sid}`")
    if foreign(args, args.id, "shape", ("ogc",)):
        return 1
    d = api.shape_record(args.root, sid)
    if d is None:
        return not_found(args, f"shape '{args.id}'", "shape ids are case-insensitive local names; the candidates are near misses; try `ogc shapes`", api.near(sid, [r["id"] for r in api.shapes_table(args.root)]))
    pcols = ["path", "min", "max", "class", "in", "hasValue", "datatype", "message"]

    def lines():
        L = [f"## {d['id']}  ({d['file']})", f"target: {', '.join(d['target']) or '(none)'}"]
        if d["message"]:
            L += text.wrap(d["message"], "message: ", "  ")
        if d["closed"]:
            L.append(f"closed: {d['closed']}")
        L += ["", f"property constraints ({len(d['properties'])}):"] + text.table(d["properties"], pcols)
        L += ["", f"sparql constraints ({len(d['sparql'])}):"]
        for x in d["sparql"]:
            L += text.wrap(x["message"], "  - ", "    ") + ["      " + l for l in x["select"].splitlines()] + [""]
        if not d["sparql"]:
            L.append("  (none)")
        return L
    return emit(args, c, argstr, d, lines)


def strip_comments(q: str) -> str:
    """The query without its comments (`#` to the end of the line, outside
    IRIs and string literals), so that a `run:` or a `sysml:` in a comment is
    not taken for a reference (round three, L1)."""
    out, i, n = [], 0, len(q)
    while i < n:
        ch = q[i]
        if ch == "<":
            j = q.find(">", i + 1)
            j = n if j < 0 or re.search(r"\s", q[i + 1:j]) else j + 1  # an IRI has no whitespace; otherwise it is the less-than operator
            if j == n:
                out.append(ch)
                i += 1
                continue
            out.append(q[i:j])
            i = j
        elif ch in "\"'":
            quote = q[i:i + 3] if q[i:i + 3] in ('"""', "\'\'\'") else ch
            j = i + len(quote)
            while j < n and not q.startswith(quote, j):
                j += 2 if q[j] == "\\" else 1
            j = min(n, j + len(quote))
            out.append(q[i:j])
            i = j
        elif ch == "#":
            j = q.find("\n", i)
            i = n if j < 0 else j
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def model_reference(q: str) -> str | None:
    """What in a query names the model graph: a `sysml:`, `sysx:`, `elmt:` or
    `ogm:` name, one of their namespaces, or a variable typed by a model
    class; None when the query stays within the graphs loaded by default.
    The mirror of record_reference for --model (round three, M1)."""
    m = re.search(r"(?:\ba|\brdf:type)\s+(?:(sysml:\w+)|<(" + re.escape(str(PREFIXES["sysml"])) + r"\w+)>)", q)
    if m:
        return m.group(1) or f"<{m.group(2)}>"
    m = re.search(r"\b(?:" + "|".join(MODEL_NS) + r"):[\w.-]*", q)
    if m:
        return m.group(0)
    for k in MODEL_NS:
        m = re.search(re.escape(str(PREFIXES[k])) + r"[\w.-]*", q)
        if m:
            return f"{k}: ({m.group(0)})"
    return None


def record_reference(g, q: str) -> str | None:
    """What in a query names the record: a `run:` name, the run namespace, or a
    variable typed by an EPO class whose instances live only in the record;
    None when the query stays within the graphs loaded by default."""
    m = re.search(r"\brun:[\w-]*", q) or re.search(re.escape(str(RUN)) + r"[\w-]*", q)
    if m:
        return m.group(0)
    kinds = api.record_classes(g)
    for m in re.finditer(r"(?:\ba|\brdf:type)\s+(?:epo:(\w+)|<" + re.escape(str(PREFIXES["epo"])) + r"(\w+)>)", q):
        name = m.group(1) or m.group(2)
        if name in kinds:
            return f"epo:{name}"
    return None


def sparql(args, g, argstr: str) -> int:
    from rdflib import BNode, Graph
    from rdflib.plugins.sparql import prepareQuery
    from rdflib.plugins.sparql.parserutils import CompValue
    q = args.query
    if q.startswith("@"):
        if not q[1:].strip():
            return usage(args, "no path after @; give the query file as @file.rq, or the query text itself")
        p = Path(q[1:])
        if p.is_dir():
            return usage(args, f"query file is a directory: {p}")
        if not p.exists():
            return usage(args, f"query file not found: {p}")
        try:
            q = p.read_text()
        except (OSError, UnicodeDecodeError) as e:
            return usage(args, f"query file cannot be read: {p} ({e})")
    if not q.strip():
        return usage(args, "sparql needs a query (or @file.rq)")
    if len(q) > QUERY_MAX:
        return usage(args, f"query too long: {len(q)} characters, the cap is {QUERY_MAX}")
    # The citation header: the query as typed (newlines escaped as \n by argstr_of, comments intact) and its sha256;
    # for @file, the path as typed and the sha256 of the file's content.
    digest = hashlib.sha256(q.encode()).hexdigest()[:12]
    header = args.argstr = f"{argstr} #sha256:{digest}"
    if re.search(r"\bSERVICE\b", q, re.I):
        return usage(args, "federation is disabled: SERVICE is refused; the tool is a read-only reader of the local graphs")
    for name, iri in re.findall(r"PREFIX\s+([\w-]*):\s*<([^>]*)>", q, re.I):
        if name in PREFIXES and str(PREFIXES[name]) != iri:
            return usage(args, f"PREFIX {name}: <{iri}> would shadow the injected prefix {name}: <{PREFIXES[name]}>; drop it or use a different name")
    bare_q = strip_comments(q)
    if not args.record:
        ref = record_reference(g, bare_q)
        if ref:
            return refuse(args, f"the query names the record ({ref}), which is not loaded; add --record to load track/measles-run.ttl (the run: namespace and the record's item kinds)")
    if not args.model:
        ref = model_reference(bare_q)
        if ref:
            return refuse(args, f"the query names the model graph ({ref}), which is not loaded; add --model to load model/og-caie.model.ttl (the sysml: vocabulary, the elmt: nodes, the ogm: and sysx: namespaces)")
    injected_lines = injected_chars = 0
    if "PREFIX" not in q.upper():
        injected_lines, injected_chars = SPARQL_PREFIXES.count("\n"), len(SPARQL_PREFIXES)
        q = SPARQL_PREFIXES + q
    try:
        pq = prepareQuery(q)
    except RecursionError:
        return usage(args, "query too deep to parse; simplify it")
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

    def nodes(n):
        if isinstance(n, CompValue):
            yield n
            for v in n.values():
                for x in (v if isinstance(v, list) else [v]):
                    if isinstance(x, CompValue):
                        yield from nodes(x)
    names = {n.name for n in nodes(pq.algebra)}
    if "Graph" in names or pq.algebra.get("datasetClause"):
        return usage(args, "named graphs are not exposed: the files are merged into one graph; drop GRAPH, FROM and FROM NAMED")
    # Determinism: without ORDER BY the engine's order is arbitrary, so a LIMIT
    # or OFFSET is lifted out of the query and applied after sorting the whole
    # answer (rows for SELECT, triples for CONSTRUCT and DESCRIBE).
    start = length = None
    top = pq.algebra
    if "OrderBy" not in names and isinstance(top.get("p"), CompValue) and top["p"].name == "Slice":
        sl = top["p"]
        def slice_part(key):  # a missing part comes back as its own name from the algebra (round three, machine H1: OFFSET without LIMIT)
            v = sl.get(key)
            return None if v is None or v == key else int(v)
        start, length = slice_part("start") or 0, slice_part("length")
        top["p"] = sl["p"]

    def window(seq):
        if start is None:
            return seq
        return seq[start:] if length is None else seq[start:start + int(length)]
    res = g.query(pq)
    labels = {}

    def label(b):
        if not labels:
            labels.update(api.bnode_labels(g))
        return labels.get(b)
    if kind == "AskQuery":
        return emit(args, "sparql", header, dict(ask=bool(res.askAnswer)), lambda: [str(bool(res.askAnswer)).lower()])
    if kind in ("ConstructQuery", "DescribeQuery"):
        out = res.graph
        fresh = {}
        nm = Graph(bind_namespaces="none")
        for k, v in PREFIXES.items():
            nm.bind(k, v, replace=True)

        def n3(x):
            if isinstance(x, BNode):
                if label(x) is None and not fresh:
                    fresh.update(api.bnode_labels(out))
                return "_:" + (label(x) or fresh.get(x, str(x)))
            return x.n3(nm.namespace_manager)
        triples = window(sorted(f"{n3(s)} {n3(p)} {n3(o)} ." for s, p, o in out))
        ttl = "\n".join([f"@prefix {k}: <{v}> ." for k, v in sorted(PREFIXES.items())] + [""] + triples) + "\n"
        return emit(args, "sparql", header, dict(triples=len(triples), turtle=ttl), lambda: ttl.rstrip("\n").splitlines() + [f"({len(triples)} triples)"])
    cols = [str(v) for v in res.vars] if res.vars else []

    def show(x):
        if x is None:
            return ""
        if isinstance(x, BNode):
            return "_:" + (label(x) or str(x))
        return str(x)
    rows = [dict(zip(cols, [show(x) for x in r])) for r in res]
    if "OrderBy" not in names:
        rows.sort(key=lambda r: tuple(r.get(c, "") for c in cols))
    rows = window(rows)
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
    for f in DOCTOR_FILES:
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
    located = api.verify_all(g, root)
    pending = [r for r in located if r["state"] == "pending"]
    add("ok" if not pending else "note", f"pending quotes: {len(pending)}" + (" (" + "; ".join(f"{r['holder']} {r['locator']}" for r in pending) + ")" if pending else ""))
    missing = [r for r in located if r["state"] == "NOT FOUND"]
    add("ok" if not missing else "BAD", "every machine quote is located in its snapshot or digest" + (": " + "; ".join(f"{r['holder']} {r['source']} {r['locator']} ({r['where']})" for r in missing) if missing else ""), bool(missing))
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
    verdict = f"VERDICT: {'PASS' if ok else 'FAIL'} (ogc doctor)"  # no path: the line is the same in every checkout
    if args.json:
        print(json.dumps({"_ogc": stamp(args, "doctor", ""), "checks": checks, "ok": ok, "verdict": verdict}, indent=2))
        return 0 if ok else 1
    print(text.head("doctor", "", git_sha(root)))
    for ch in checks:
        print(f"{ch['state']:<8}{ch['what']}")
    print(verdict)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
