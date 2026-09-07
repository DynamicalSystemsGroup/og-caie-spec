#!/usr/bin/env python3
"""Render the sample report (ruling R-51, sheet 10 items 10-44 and 10-48): the
report the sponsor's executive reads at the end of an evaluation, for a
reader who knows the domain and little about AI. It answers the question
the sponsor asked and nothing else: the explorer (Appendix B) holds
everything the report leaves out.

Reads the record and the EPO vocabulary through one function, record_graph,
and writes:

- report/report.json: a small, flat, deterministic JSON holding exactly what
  the page shows, in the record's own words and in plain ones: the answer
  (the recommendation, a badge, who approved the report and who wrote the
  recommendation, the date), the question (the need), the item tested (its
  name and version, whom it serves, where it is used, what the judgments
  rest on), one row per requirement with a result word and one line of why
  and its criteria beneath, the share of criteria tested recomputed by
  queries/coverage.rq (the stored report must agree or the renderer
  refuses), what the report rests on (who tested and declared independence,
  who judged, the machine check of the record and its date), what to do
  next (the recommendation's remaining sentences), and the synthetic-case
  note;
- report/index.html: one self-contained page (inline CSS and JS, d3 loaded
  from the explorer's vendored copy by a relative path, no network) that
  fetches report.json by a relative path and renders the six sections.

Plain language: no word the record and the specification use among
themselves reaches the page (tests/test_report.py lists them); the page says
"tested" where the record says coverage, "met" where it says passed, and
names no machine but the item tested. Terse: a cell is one sentence of at
most 25 words.

Honest: the report is final when a delivery derives from it and its
approval passed; the evaluation is complete when the report is final and
every criterion was tested. Otherwise the badge reads "not complete", the
headline says so and the page shows what was tested. When complete, the
badge reads "fit to deploy" if every requirement was met, else "not fit"
when the recommendation's first sentence opens with "not", else "fit with
conditions".

Deterministic: same record, same bytes. Keys are sorted, lists are sorted
by what they hold, and nothing is stamped at render time; every date in the
JSON is a date the record holds (the approval's and the machine check's).
The page carries no IRI, no prefix and no shape name; the record's items
are found by type, never by name, so the record may be renamed without
touching this file.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from rdflib import RDF, RDFS, Graph, URIRef

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ogc.graph import EARL, EPO, PROV, RECORD_FILE, SKOS  # noqa: E402

OUT = ROOT / "report"
EPO_FILE = "vocabulary/epo.ttl"
COVERAGE_QUERY = ROOT / "queries" / "coverage.rq"
D3 = "../explorer/vendor/d3.v7.min.js"  # the explorer's vendored copy, one file for both pages
EXPLORER = "../explorer/index.html"  # the one link to everything the report leaves out
TITLE = "Evaluation report"
MAX_WORDS = 25
RESULT_WORDS = {"passed": "met", "failed": "not met", "cantTell": "could not tell"}
NOT_TESTED = "not fully tested"
CHECK_WORDS = {"passed": "passed", "failed": "failed", "cantTell": "could not tell"}
PRECEDENCE = ("not met", "could not tell", NOT_TESTED, "met")  # a requirement's word is its worst criterion's
BADGE_NOT_COMPLETE = "not complete"
BADGE_FIT = "fit to deploy"
BADGE_CONDITIONS = "fit with conditions"
BADGE_NOT_FIT = "not fit"


def record_graph() -> Graph:
    """The one place the record is read: the file ogc.graph.RECORD_FILE names, with the EPO for its labels.
    Nothing else in this script names the record's file or its namespace."""
    g = Graph()
    g.parse(ROOT / EPO_FILE)
    g.parse(ROOT / RECORD_FILE)
    return g


# --- small readers ----------------------------------------------------------

def local(node) -> str:
    return str(node).rsplit("#", 1)[-1]


def text(g: Graph, s, p) -> str | None:
    v = g.value(s, p)
    return str(v) if v is not None else None


def label(g: Graph, s) -> str:
    return text(g, s, RDFS.label) or local(s)


def plain(g: Graph, s) -> str:
    """A party's name as the record labels it, before the parenthesis that glosses its role."""
    return label(g, s).split(" (", 1)[0].strip()


def gloss(g: Graph, s) -> str | None:
    """What the record says of a party in the parenthesis after its name: for a person, the expertise it gives."""
    m = re.search(r"\(([^)]*)\)", label(g, s))
    return m.group(1).strip() if m else None


def names(g: Graph, s, p) -> list[str]:
    return sorted(plain(g, o) for o in g.objects(s, p))


def stamp(g: Graph, s, p) -> str | None:
    """A date as the record writes it (UTC, Z), not as rdflib normalises it."""
    v = g.value(s, p)
    if v is None:
        return None
    dt = v.toPython()
    if isinstance(dt, datetime):
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return str(v)


def when(g: Graph, s) -> str:
    return stamp(g, s, PROV.generatedAtTime) or stamp(g, s, PROV.endedAtTime) or stamp(g, s, PROV.startedAtTime) or ""


def by(g: Graph, s) -> list[str]:
    """Who the record credits with an item: the asserter of an assertion, else whom it is attributed to."""
    return names(g, s, EARL.assertedBy) or names(g, s, PROV.wasAttributedTo)


def of_type(g: Graph, cls) -> list[URIRef]:
    return sorted((s for s in g.subjects(RDF.type, cls) if isinstance(s, URIRef)), key=str)


def latest(g: Graph, items: list[URIRef]) -> URIRef | None:
    """The most recent of several items by the record's own stamps, the IRI order breaking ties."""
    return max(items, key=lambda s: (when(g, s), str(s))) if items else None


def one(g: Graph, cls) -> URIRef:
    items = of_type(g, cls)
    if len(items) != 1:
        raise RuntimeError(f"the record holds {len(items)} items of kind {local(cls)}; the report needs exactly one")
    return items[0]


def result(g: Graph, assertion) -> tuple[str | None, str | None]:
    res = g.value(assertion, EARL.result)
    if res is None:
        return None, None
    o = g.value(res, EARL.outcome)
    return (local(o) if o is not None else None), text(g, res, EARL.info)


def sentences(s: str) -> list[str]:
    return [p.strip() for p in re.split(r"(?<=[.!?])\s+", s.strip()) if p.strip()]


def line(s: str | None) -> str:
    """One line for a cell: the first sentence, at most MAX_WORDS words, ending in a full stop."""
    if not s:
        return ""
    first = sentences(" ".join(s.split()))[0]
    words = first.split()
    if len(words) > MAX_WORDS:
        first = " ".join(words[:MAX_WORDS]).rstrip(",;:") + "…"
    first = first[0].upper() + first[1:]
    return first if first[-1] in ".!?…" else first + "."


def join(xs: list[str]) -> str:
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1] if xs else ""


# --- the parts of the report ------------------------------------------------

def the_report(g: Graph) -> tuple[URIRef, URIRef, bool]:
    """The report the page reads and its approval: the delivered report when a delivery derives from one,
    else the approved one, else the only one; the latest by approval when several. Final when a delivery
    derives from it and its approval passed."""
    reports = of_type(g, EPO.Report)
    delivered = [r for r in reports if any((d, PROV.wasDerivedFrom, r) in g for d in of_type(g, EPO.Delivery))]

    def approval_of(r):
        return latest(g, [a for a in of_type(g, EPO.ReportApproval) if g.value(a, EPO.approvesReport) == r])

    approved = [r for r in reports if approval_of(r) is not None and result(g, approval_of(r))[0] == "passed"]
    candidates = delivered or approved or reports
    if not candidates:
        raise RuntimeError("the record holds no report")
    report = max(candidates, key=lambda r: (when(g, approval_of(r)) if approval_of(r) is not None else "", str(r)))
    approval = approval_of(report)
    if approval is None:
        raise RuntimeError("the report the page reads has no approval")
    return report, approval, report in delivered and report in approved


def share_tested(g: Graph, report) -> dict:
    """The share of criteria tested, by queries/coverage.rq; the stored report must agree."""
    row = next(iter(g.query(COVERAGE_QUERY.read_text())))
    computed = {"share": float(row.coverage), "tested": int(row.coveredCount)}
    stored = g.value(report, EPO.coverage)
    if stored is None or abs(float(stored) - computed["share"]) > 1e-9:
        raise RuntimeError(f"the stored report's coverage ({stored}) disagrees with queries/coverage.rq ({computed['share']})")
    return computed


def criterion_row(g: Graph, a, planned: set) -> dict:
    """One criterion: its text, its result word by the rule of queries/coverage.rq (not met if any attestation failed,
    else met if any passed, else could not tell) and one line of why from the latest attestation's note, else
    from the evidence the record holds on it, else that it was not tested."""
    attestations = [t for t in of_type(g, EPO.Attestation) if g.value(t, EARL.test) == a]
    outcomes = {result(g, t)[0] for t in attestations}
    word = next((RESULT_WORDS[o] for o in ("failed", "passed", "cantTell") if o in outcomes), NOT_TESTED)
    why = None
    if attestations:
        deciding = [t for t in attestations if RESULT_WORDS.get(result(g, t)[0]) == word]
        why = result(g, latest(g, deciding or attestations))[1]
    if not why:
        evidence = [e for e in of_type(g, EPO.Evidence) if g.value(e, EPO.bearsOn) == a]
        why = label(g, latest(g, evidence)) if evidence else None
    if not why:
        why = "Not yet judged." if a in planned else "Not tested."
    return {"text": line(text(g, a, EPO.text)), "result": word, "why": line(why)}


def results(g: Graph) -> tuple[list[dict], list[str]]:
    """One row per requirement, its criteria beneath; the untested criteria named."""
    planned = {a for plan in of_type(g, EPO.TestPlan) for a in g.objects(plan, EPO.objective)}
    rows, untested = [], []
    for q in of_type(g, EPO.Requirement):
        criteria = [criterion_row(g, a, planned) for a in of_type(g, EPO.AcceptanceCriterion) if g.value(a, PROV.wasDerivedFrom) == q]
        untested += [c["text"] for c in criteria if c["result"] == NOT_TESTED]
        words = {c["result"] for c in criteria}
        word = next((w for w in PRECEDENCE if w in words), NOT_TESTED)
        deciding = next((c for c in criteria if c["result"] == word), None)
        rows.append({"requirement": line(text(g, q, EPO.text)), "result": word,
                     "why": deciding["why"] if deciding else "No criterion was set.", "criteria": criteria})
    return rows, untested


def tested_line(share: dict, untested: list[str], total: int) -> str:
    if share["share"] == 1 and not untested:
        return "Every criterion was tested"
    return (f"{share['tested']} of {total} criteria were tested, {round(share['share'] * 100)}% by weight. "
            f"Not tested: {' '.join(untested)}")


def badge(complete: bool, rows: list[dict], recommendation: str) -> str:
    if not complete:
        return BADGE_NOT_COMPLETE
    if all(r["result"] == "met" for r in rows):
        return BADGE_FIT
    return BADGE_NOT_FIT if sentences(recommendation)[0].lower().startswith("not") else BADGE_CONDITIONS


def person(g: Graph, s) -> dict:
    return {"name": plain(g, s), "expertise": gloss(g, s)}


def organizations_with(g: Graph, role) -> list[URIRef]:
    return [o for o in of_type(g, PROV.Organization) if (o, EPO.role, role) in g]


def build(g: Graph) -> dict:
    report, approval, final = the_report(g)
    recommendation = latest(g, [r for r in of_type(g, EPO.Recommendation) if (r, PROV.wasDerivedFrom, report) in g]) or one(g, EPO.Recommendation)
    check = latest(g, [v for v in of_type(g, EPO.ConformanceVerdict) if (v, EARL.subject, report) in g] or of_type(g, EPO.ConformanceVerdict))
    requirement_set = one(g, EPO.RequirementSet)
    test_item = g.value(requirement_set, EPO.systemUnderTest)
    dso = one(g, EPO.DsoRelease)
    mission = one(g, EPO.Mission)
    need = one(g, EPO.Need)
    record = [s for s in g.subjects(SKOS.note) if (s, RDF.type, PROV.Entity) in g and not any(
        (s, RDF.type, c) in g for c in (PROV.Agent, EPO.Population))]
    share = share_tested(g, report)
    rows, untested = results(g)
    total = len(of_type(g, EPO.AcceptanceCriterion))
    complete = final and share["share"] == 1 and not untested
    rec_text = text(g, recommendation, EPO.text) or ""
    rec_sentences = sentences(rec_text)
    if complete:
        headline = rec_sentences[0]
    elif not final:
        headline = "This evaluation is not complete: its report is not final."
    else:
        headline = f"This evaluation is not complete: {share['tested']} of {total} criteria were tested."
    testers = organizations_with(g, EPO.testingOrganizationRole)
    providers = organizations_with(g, EPO.accountableOrganizationRole) or list(g.objects(test_item, PROV.actedOnBehalfOf))
    independent = any(str(g.value(t, EPO.independentOfAccountable)).lower() == "true" for t in testers)
    judges = sorted({p for t in of_type(g, EPO.Attestation) for p in g.objects(t, EARL.assertedBy) if (p, RDF.type, PROV.Person) in g}, key=str)
    check_outcome, _ = result(g, check)
    return {
        "title": TITLE,
        "answer": {
            "badge": badge(complete, rows, rec_text),
            "complete": complete,
            "headline": headline,
            "recommendation": rec_text,
            "recommended_by": by(g, recommendation),
            "approved_by": [person(g, p) for p in sorted(g.objects(approval, EARL.assertedBy), key=str)],
            "date": when(g, approval),
        },
        "question": {"text": label(g, need), "asked_by": names(g, need, PROV.wasAttributedTo) or names(g, mission, PROV.wasAttributedTo)},
        "item": {
            "name": plain(g, test_item), "version": text(g, test_item, EPO.version),
            "purpose": label(g, mission),
            "environment": text(g, requirement_set, EPO.environment),
            "assumptions": label(g, dso), "assumptions_by": names(g, dso, EPO.approvedBy),
        },
        "results": rows,
        "criteria": {**share, "of": total, "untested": untested, "line": tested_line(share, untested, total)},
        "rests_on": {
            "tested_by": [plain(g, t) for t in testers],
            "independent_of": [plain(g, p) for p in providers] if independent else [],
            "judged_by": [person(g, p) for p in judges],
            "checked": {"outcome": CHECK_WORDS.get(check_outcome, check_outcome), "date": when(g, check)},
            "approved": when(g, approval),
        },
        "next": rec_sentences[1:],
        "note": text(g, record[0], SKOS.note) if record else "",
    }


# --- the page ----------------------------------------------------------------

PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
  :root{color-scheme:light dark;
    --bg:#ffffff;--fg:#1a1a1a;--muted:#5b6470;--line:#d9dde3;--panel:#f4f6f8;
    --met:#1b7f3b;--notmet:#c62828;--canttell:#b45309;--untested:#5b6470;--accent:#1d4ed8}
  @media (prefers-color-scheme:dark){:root{
    --bg:#121417;--fg:#e8eaed;--muted:#a0a8b3;--line:#2e343d;--panel:#1b1f25;
    --met:#3fb457;--notmet:#f06060;--canttell:#f2a33a;--untested:#a0a8b3;--accent:#8ab4ff}}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;overflow-wrap:anywhere}
  main{max-width:760px;margin:0 auto;padding:28px 20px 40px}
  section{margin:0 0 44px}
  h1{font-size:1.7rem;line-height:1.25;margin:10px 0 14px;font-weight:650}
  h2{font-size:.85rem;margin:0 0 12px;font-weight:650;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
  p{margin:8px 0}
  a{color:var(--accent)}
  .muted{color:var(--muted)}
  .badge{display:inline-block;padding:5px 14px;border-radius:999px;color:#fff;font-weight:700;font-size:.85rem;letter-spacing:.05em;text-transform:uppercase}
  .met{background:var(--met)}.notmet{background:var(--notmet)}.canttell{background:var(--canttell)}.untested{background:var(--untested)}
  .dot{display:inline-block;width:.7em;height:.7em;border-radius:50%;margin-right:.45em;vertical-align:baseline}
  .word{font-weight:650;white-space:nowrap}
  .word.met{color:var(--met);background:none}.word.notmet{color:var(--notmet);background:none}
  .word.canttell{color:var(--canttell);background:none}.word.untested{color:var(--untested);background:none}
  .question{background:var(--panel);border-left:4px solid var(--accent);padding:10px 14px;border-radius:0 8px 8px 0;margin:16px 0 0}
  .lines p{margin:10px 0}
  .lines b{font-weight:650}
  table{width:100%;border-collapse:collapse}
  th,td{text-align:left;vertical-align:top;padding:10px 8px;border-top:1px solid var(--line)}
  th{font-size:.8rem;color:var(--muted);font-weight:600;border-top:0;text-transform:uppercase;letter-spacing:.05em}
  td.result{white-space:nowrap}
  button.fold-toggle{background:none;border:0;color:var(--muted);font:inherit;cursor:pointer;padding:0 6px 0 0;line-height:1}
  button.fold-toggle[aria-expanded="true"]{color:var(--fg)}
  tr.fold td{background:var(--panel);border-top:0;padding:4px 8px 14px}
  tr.fold ul{margin:6px 0 0;padding-left:20px}
  tr.fold li{margin:6px 0}
  @media (max-width:640px){
    table thead{display:none}
    table tr{display:block;border-top:1px solid var(--line);padding:8px 0}
    table td{display:block;border-top:0;padding:3px 8px}
    table td[data-h]::before{content:attr(data-h) ": ";color:var(--muted);font-size:.8rem;text-transform:uppercase;letter-spacing:.05em}
    td.result{white-space:normal}
    tr.fold{border-top:0;padding:0}
  }
  ol.next{padding-left:22px;margin:8px 0}
  ol.next li{margin:6px 0}
  footer{margin-top:8px;padding-top:16px;border-top:1px solid var(--line);font-size:.92rem;color:var(--muted)}
  #error{color:var(--notmet)}
</style></head>
<body><main>
<div id="report"><p id="error" hidden></p></div>
</main>
<script src="__D3__"></script>
<script>
(async function(){
  const root = d3.select("#report");
  let R;
  try {
    const res = await fetch(new URL("report.json", location.href).href);
    if(!res.ok) throw new Error(res.status);
    R = await res.json();
  } catch(e) {
    root.select("#error").attr("hidden", null).text("The report could not be read: this page fetches report.json next to it, so serve the folder over http.");
    return;
  }
  const day = d3.utcFormat("%-d %B %Y");
  const fmt = iso => iso ? day(new Date(iso)) : "undated";
  const cls = w => ({"met":"met","not met":"notmet","could not tell":"canttell","fit to deploy":"met","fit with conditions":"canttell","not fit":"notmet"}[w] || "untested");
  const join = xs => xs.length <= 1 ? xs.join("") : xs.slice(0, -1).join(", ") + " and " + xs[xs.length - 1];
  const who = ps => join(ps.map(p => p.expertise ? `${p.name}, ${p.expertise}` : p.name));
  const esc = s => String(s == null ? "" : s);
  const section = title => { const s = root.append("section"); s.append("h2").text(title); return s; };

  // 1. the answer
  const A = R.answer;
  const head = section("The answer");
  head.append("div").append("span").attr("class", "badge " + cls(A.badge)).text(A.badge);
  head.append("h1").text(A.headline);
  if (!A.complete && A.recommendation) head.append("p").text("The recommendation so far, in the record's words: " + A.recommendation);
  head.append("p").text(`Approved by ${who(A.approved_by)}, who is accountable for its words; the recommendation written by ${join(A.recommended_by)}. ${fmt(A.date)}.`);
  head.append("p").attr("class", "question").text(`The question ${join(R.question.asked_by)} asked: ${R.question.text}.`);

  // 2. what was tested
  const I = R.item;
  const item = section("What was tested").attr("class", "lines");
  item.append("p").html(`<b>${esc(I.name)}</b>, version ${esc(I.version)}.`);
  item.append("p").html(`<b>Whom it serves.</b> ${esc(I.purpose)}.`);
  item.append("p").html(`<b>Where it is used.</b> ${esc(I.environment)}`);
  item.append("p").html(`<b>What the judgments rest on.</b> ${esc(I.assumptions)}, approved by ${esc(join(I.assumptions_by))}.`);

  // 3. how it did: one row per requirement, its criteria folded beneath
  const how = section("How it did");
  const heads = ["Requirement", "Result", "Why"];
  const table = how.append("table");
  table.append("thead").append("tr").selectAll("th").data(heads).join("th").text(d => d);
  const tbody = table.append("tbody");
  let n = 0;
  for (const row of R.results) {
    const id = "fold-" + (++n);
    const tr = tbody.append("tr");
    const first = tr.append("td");
    const toggle = first.append("button").attr("class", "fold-toggle").attr("aria-expanded", "false").attr("aria-controls", id).attr("title", "the criteria beneath this requirement").text("▸");
    first.append("span").text(row.requirement);
    tr.append("td").attr("class", "result").attr("data-h", heads[1]).html(`<span class="dot ${cls(row.result)}"></span><span class="word ${cls(row.result)}">${esc(row.result)}</span>`);
    tr.append("td").attr("data-h", heads[2]).text(row.why);
    const fold = tbody.append("tr").attr("class", "fold").attr("id", id).attr("hidden", true);
    const ul = fold.append("td").attr("colspan", heads.length).append("ul");
    for (const c of row.criteria)
      ul.append("li").html(`${esc(c.text)} <span class="dot ${cls(c.result)}"></span><span class="word ${cls(c.result)}">${esc(c.result)}</span>: ${esc(c.why)}`);
    toggle.on("click", () => { const open = toggle.attr("aria-expanded") !== "true"; toggle.attr("aria-expanded", open).text(open ? "▾" : "▸"); fold.attr("hidden", open ? null : true); });
  }
  how.append("p").attr("class", "muted").text(R.criteria.line + (R.criteria.line.endsWith(".") ? "" : "."));

  // 4. what it rests on
  const W = R.rests_on;
  const rests = section("What it rests on").attr("class", "lines");
  rests.append("p").html(`<b>Who tested.</b> ${esc(join(W.tested_by))}, ` + (W.independent_of.length
    ? `which declared its independence from ${esc(join(W.independent_of))}.`
    : `which did not declare its independence from the maker of what was tested.`));
  rests.append("p").html(`<b>Who judged.</b> ${esc(who(W.judged_by))}.`);
  rests.append("p").html(`<b>Checked by machine.</b> The record of this evaluation was checked against the process it had to follow: ${esc(W.checked.outcome)}, ${fmt(W.checked.date)}, before the report was approved on ${fmt(W.approved)}.`);

  // 5. what to do next
  const next = section("What to do next");
  if (R.next.length) next.append("ol").attr("class", "next").selectAll("li").data(R.next).join("li").text(d => d);
  else next.append("p").text("None.");

  // 6. the footer
  const foot = root.append("footer");
  foot.append("p").html(`<b>A sample report for a synthetic case.</b> ${esc(R.note)}`);
  foot.append("p").html(`Everything this report leaves out is in <a href="__EXPLORER__">the explorer</a>.`);
})();
</script>
</body></html>
"""


def render() -> str:
    return PAGE.replace("__TITLE__", TITLE).replace("__D3__", D3).replace("__EXPLORER__", EXPLORER)


def main() -> int:
    OUT.mkdir(exist_ok=True)
    model = build(record_graph())
    (OUT / "report.json").write_text(json.dumps(model, ensure_ascii=False, sort_keys=True, indent=1) + "\n")
    (OUT / "index.html").write_text(render())
    c = model["criteria"]
    print(f"report: {len(model['results'])} requirements, {c['tested']} of {c['of']} criteria tested, {model['answer']['badge']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
