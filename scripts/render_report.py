#!/usr/bin/env python3
"""Render the sample report (ruling R-51, sheet 10 item 10-44): the concrete
report of the synthetic measles evaluation, as a dashboard the sponsor reads.
It answers the question the sponsor asked and nothing else: the explorer
(Appendix B) holds everything the report leaves out.

Reads the record and the EPO vocabulary (for the class and value labels)
through one function, record_graph, and writes:

- report/report.json: a small, flat, deterministic JSON holding exactly what
  the dashboard shows: the sponsor and its mission, the question (the need),
  the test item and its version, the recommendation, the outcome per
  acceptance criterion with its requirement, weight, outcome, sufficiency
  and appropriateness, the coverage and the three rates recomputed by
  queries/coverage.rq (never copied from the stored report; the two must
  agree or the renderer refuses), the attestations with who attested on
  what evidence and when, the determinations behind them, the evidence with
  the probe and the response it derives from, the DSO release and the
  operational environment, the approval and the conformance verdict, the
  delivery and the acceptance, the parties, the chain of custody as dated
  events, and the synthetic-case note;
- report/index.html: one self-contained d3 dashboard (inline CSS and JS,
  d3 loaded from the explorer's vendored copy by a relative path, no
  network) that fetches report.json by a relative path and renders it.

Deterministic: same record, same bytes. Keys are sorted, lists are sorted
by what they hold, and nothing is stamped at render time; every date in the
JSON is a date the record holds. The page carries no IRI, no prefix and no
shape name; the record's items are found by type, never by name, so the
record may be renamed without touching this file.
"""
from __future__ import annotations

import json
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
TITLE = "Evaluation report"
OUTCOME_WORDS = {"passed": "passed", "failed": "failed", "cantTell": "cannot tell"}
NOT_PLANNED = "not planned"
NOT_ATTESTED = "not attested"
# The chain of custody: one event per item of these kinds, dated by the item's own stamp and
# attributed to whoever the record attributes it to; only the kinds the record holds appear.
EVENTS = [
    (EPO.ServiceAgreement, EPO.signedBy),
    (EPO.TestItemAccess, PROV.wasAttributedTo),
    (EPO.RequirementSet, PROV.wasAttributedTo),
    (EPO.AppropriatenessAssessment, EARL.assertedBy),
    (EPO.PlanApproval, EARL.assertedBy),
    (EPO.Session, PROV.wasAssociatedWith),
    (EPO.Attestation, EARL.assertedBy),
    (EPO.ConformanceVerdict, EARL.assertedBy),
    (EPO.ReportApproval, EARL.assertedBy),
    (EPO.Delivery, PROV.wasAttributedTo),
    (EPO.Acceptance, PROV.wasAttributedTo),
]


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


def labels(g: Graph, s, p) -> list[str]:
    return sorted(label(g, o) for o in g.objects(s, p))


def stamp(g: Graph, s, p) -> str | None:
    """A date as the record writes it (UTC, Z), not as rdflib normalises it."""
    v = g.value(s, p)
    if v is None:
        return None
    dt = v.toPython()
    if isinstance(dt, datetime):
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return str(v)


def when(g: Graph, s) -> str | None:
    return stamp(g, s, PROV.generatedAtTime) or stamp(g, s, PROV.endedAtTime) or stamp(g, s, PROV.startedAtTime)


def by(g: Graph, s) -> list[str]:
    """Who the record credits with an item: the asserter of an assertion, else whom it is attributed to."""
    return labels(g, s, EARL.assertedBy) or labels(g, s, PROV.wasAttributedTo)


def of_type(g: Graph, cls) -> list[URIRef]:
    return sorted((s for s in g.subjects(RDF.type, cls) if isinstance(s, URIRef)), key=str)


def one(g: Graph, cls) -> URIRef:
    items = of_type(g, cls)
    if len(items) != 1:
        raise RuntimeError(f"the record holds {len(items)} items of kind {local(cls)}; the report needs exactly one")
    return items[0]


def kind(g: Graph, cls) -> str:
    """The plain name of an item kind: the head of the EPO class label, before its gloss and without a parenthesis."""
    head = label(g, cls).split(":", 1)[0]
    return head.split(" (", 1)[0].strip()


def result(g: Graph, assertion) -> tuple[str | None, str | None]:
    res = g.value(assertion, EARL.result)
    if res is None:
        return None, None
    o = g.value(res, EARL.outcome)
    return (local(o) if o is not None else None), text(g, res, EARL.info)


def assertion(g: Graph, s) -> dict:
    outcome, note = result(g, s)
    return {"by": by(g, s), "date": when(g, s), "outcome": OUTCOME_WORDS.get(outcome, outcome), "note": note}


# --- the parts of the report ------------------------------------------------

def coverage(g: Graph, report) -> dict:
    """Coverage and the three rates by queries/coverage.rq; the stored report must agree."""
    row = next(iter(g.query(COVERAGE_QUERY.read_text())))
    computed = {"coverage": float(row.coverage), "pass_rate": float(row.passRate),
                "fail_rate": float(row.failRate), "cant_tell_rate": float(row.cantTellRate)}
    stored = {"coverage": g.value(report, EPO.coverage), "pass_rate": g.value(report, EPO.passRate),
              "fail_rate": g.value(report, EPO.failRate), "cant_tell_rate": g.value(report, EPO.cantTellRate)}
    for k, v in computed.items():
        if stored[k] is None or abs(float(stored[k]) - v) > 1e-9:
            raise RuntimeError(f"the stored report's {k} ({stored[k]}) disagrees with queries/coverage.rq ({v})")
    computed["covered_count"] = int(row.coveredCount)
    return computed


def evidence_item(g: Graph, ev) -> dict:
    response = g.value(ev, PROV.wasDerivedFrom)
    turn = g.value(response, PROV.wasGeneratedBy) if response is not None else None
    probe = g.value(turn, PROV.used) if turn is not None else None
    session = g.value(turn, EPO.inSession) if turn is not None else None
    item = {"label": label(g, ev), "by": by(g, ev), "date": when(g, ev)}
    if response is not None:
        item["response"] = {"text": text(g, response, EPO.text), "by": labels(g, response, PROV.wasAttributedTo)}
    if probe is not None:
        item["probe"] = {"text": text(g, probe, EPO.text), "date": when(g, probe)}
    if session is not None:
        item["session"] = {"label": label(g, session), "started": stamp(g, session, PROV.startedAtTime),
                           "ended": stamp(g, session, PROV.endedAtTime),
                           "turn": int(g.value(turn, EPO.turnIndex)) if g.value(turn, EPO.turnIndex) is not None else None}
    return item


def determination_item(g: Graph, d) -> dict:
    item = assertion(g, d)
    item["evidence"] = [evidence_item(g, ev) for ev in sorted(g.objects(d, PROV.used), key=str)
                        if (ev, RDF.type, EPO.Evidence) in g]
    return item


def attestation_item(g: Graph, a) -> dict:
    item = assertion(g, a)
    item["appropriateness"] = local(g.value(a, EPO.appropriateness)) if g.value(a, EPO.appropriateness) is not None else None
    item["sufficiency"] = local(g.value(a, EPO.sufficiency)) if g.value(a, EPO.sufficiency) is not None else None
    item["determinations"] = [determination_item(g, d) for d in sorted(g.objects(a, PROV.used), key=str)
                              if (d, RDF.type, EPO.Determination) in g]
    return item


def criterion_outcome(attestations: list[dict], planned: bool) -> str:
    """The rule of queries/coverage.rq: failed if any attestation failed, else passed if any passed, else cannot tell;
    a criterion without an attestation is not covered, and is not planned when no test plan names it."""
    outcomes = {a["outcome"] for a in attestations}
    for word in ("failed", "passed", "cannot tell"):
        if word in outcomes:
            return word
    return NOT_ATTESTED if planned else NOT_PLANNED


def criteria(g: Graph) -> list[dict]:
    planned = {a for plan in of_type(g, EPO.TestPlan) for a in g.objects(plan, EPO.objective)}
    out = []
    for a in of_type(g, EPO.AcceptanceCriterion):
        atts = [attestation_item(g, t) for t in of_type(g, EPO.Attestation) if g.value(t, EARL.test) == a]
        requirement = g.value(a, PROV.wasDerivedFrom)
        out.append({
            "id": local(a),
            "requirement": text(g, requirement, EPO.text) if requirement is not None else None,
            "text": text(g, a, EPO.text),
            "expected": text(g, a, EPO.expectedResult),
            "weight": float(g.value(a, EPO.weight)),
            "min_pass_rate": float(g.value(a, EPO.minPassRate)) if g.value(a, EPO.minPassRate) is not None else None,
            "planned": a in planned,
            "outcome": criterion_outcome(atts, a in planned),
            "appropriateness": sorted({t["appropriateness"] for t in atts if t["appropriateness"]}),
            "sufficiency": sorted({t["sufficiency"] for t in atts if t["sufficiency"]}),
            "attested_by": sorted({who for t in atts for who in t["by"]}),
            "attestations": atts,
        })
    return out


def verdict(coverage_row: dict) -> str:
    """One word for the badge, by the same rule as the criteria: failed if any covered criterion failed, passed
    only if every criterion is covered and passed, otherwise cannot tell."""
    if coverage_row["fail_rate"] > 0:
        return "failed"
    if coverage_row["coverage"] == 1 and coverage_row["pass_rate"] == 1:
        return "passed"
    return "cannot tell"


def timeline(g: Graph) -> list[dict]:
    events = []
    for cls, who in EVENTS:
        for s in of_type(g, cls):
            date = when(g, s)
            if date is None:
                continue
            detail = None
            if cls in (EPO.Attestation,):
                detail = "on criterion " + local(g.value(s, EARL.test))
            elif cls in (EPO.Session,):
                detail = label(g, s)
            events.append({"what": kind(g, cls), "who": labels(g, s, who), "date": date, "detail": detail})
    return sorted(events, key=lambda e: (e["date"], e["what"], e["who"]))


def parties(g: Graph) -> dict:
    orgs = [label(g, s) for s in of_type(g, PROV.Organization)]
    people = [{"name": label(g, s), "for": labels(g, s, PROV.actedOnBehalfOf)} for s in of_type(g, PROV.Person)]
    populations = [label(g, s) for s in of_type(g, EPO.Population)]
    return {"organizations": sorted(orgs), "people": sorted(people, key=lambda p: p["name"]), "populations": sorted(populations)}


def build(g: Graph) -> dict:
    approval = one(g, EPO.ReportApproval)
    report = g.value(approval, EPO.approvesReport) or one(g, EPO.Report)
    recommendation = one(g, EPO.Recommendation)
    delivery = one(g, EPO.Delivery)
    acceptance = one(g, EPO.Acceptance)
    conformance = one(g, EPO.ConformanceVerdict)
    requirement_set = one(g, EPO.RequirementSet)
    test_item = g.value(requirement_set, EPO.systemUnderTest)
    dso = one(g, EPO.DsoRelease)
    mission = one(g, EPO.Mission)
    need = one(g, EPO.Need)
    agreement = one(g, EPO.ServiceAgreement)
    assessment = [assertion(g, s) for s in of_type(g, EPO.AppropriatenessAssessment) if g.value(s, EARL.subject) == requirement_set]
    record = [s for s in g.subjects(SKOS.note) if (s, RDF.type, PROV.Entity) in g and not any(
        (s, RDF.type, c) in g for c in (PROV.Agent, EPO.Population))]
    cov = coverage(g, report)
    return {
        "title": TITLE,
        "record": {"label": label(g, record[0]) if record else None, "note": text(g, record[0], SKOS.note) if record else None},
        "sponsor": {"name": labels(g, mission, PROV.wasAttributedTo), "mission": label(g, mission), "need": label(g, need)},
        "agreement": {"label": label(g, agreement), "signed_by": labels(g, agreement, EPO.signedBy), "date": when(g, agreement)},
        "test_item": {"name": label(g, test_item), "version": text(g, test_item, EPO.version),
                      "provider": labels(g, test_item, PROV.actedOnBehalfOf)},
        "recommendation": {"text": text(g, recommendation, EPO.text), "by": by(g, recommendation), "date": when(g, recommendation),
                           "targets_guardrail": text(g, recommendation, EPO.targetsGuardrail)},
        "verdict": verdict(cov),
        "coverage": cov,
        "criteria": criteria(g),
        "assumptions": {
            "dso": {"label": label(g, dso), "version": text(g, dso, EPO.version), "approved_by": labels(g, dso, EPO.approvedBy), "date": when(g, dso)},
            "environment": text(g, requirement_set, EPO.environment),
            "requirement_set": {"label": label(g, requirement_set), "by": by(g, requirement_set), "date": when(g, requirement_set),
                                "assessment": assessment},
        },
        "conformance": {k: v for k, v in assertion(g, conformance).items() if k != "note"},  # the note names the shapes; the page does not
        "approval": assertion(g, approval),
        "delivery": {"label": label(g, delivery), "by": by(g, delivery), "to": labels(g, delivery, EPO.deliveredTo), "date": when(g, delivery)},
        "acceptance": {"label": label(g, acceptance), "by": by(g, acceptance), "date": when(g, acceptance)},
        "timeline": timeline(g),
        "parties": parties(g),
    }


# --- the page ----------------------------------------------------------------

PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
  :root{color-scheme:light dark;
    --bg:#ffffff;--fg:#1a1a1a;--muted:#5b6470;--line:#d9dde3;--panel:#f4f6f8;
    --passed:#1b7f3b;--failed:#c62828;--canttell:#d97706;--notplanned:#6b7280;--accent:#1d4ed8}
  @media (prefers-color-scheme:dark){:root{
    --bg:#121417;--fg:#e8eaed;--muted:#a0a8b3;--line:#2e343d;--panel:#1b1f25;
    --passed:#34a853;--failed:#ef5350;--canttell:#f59e0b;--notplanned:#9aa4b2;--accent:#7aa2ff}}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
  main{max-width:960px;margin:0 auto;padding:24px 20px 48px}
  h1{font-size:1.6rem;line-height:1.25;margin:8px 0 12px;font-weight:650}
  h2{font-size:1.05rem;margin:40px 0 12px;font-weight:650;letter-spacing:.01em}
  p{margin:6px 0}
  .muted{color:var(--muted)}
  .eyebrow{font-size:.85rem;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
  .badge{display:inline-block;padding:4px 12px;border-radius:999px;color:#fff;font-weight:700;font-size:.9rem;letter-spacing:.04em;text-transform:uppercase;vertical-align:middle}
  .passed{background:var(--passed)}.failed{background:var(--failed)}.canttell{background:var(--canttell)}.notplanned{background:var(--notplanned)}
  .dot{display:inline-block;width:.75em;height:.75em;border-radius:50%;margin-right:.4em;vertical-align:baseline}
  .question{background:var(--panel);border-left:4px solid var(--accent);padding:10px 14px;border-radius:0 8px 8px 0;margin:14px 0}
  .lead{font-size:1.1rem;margin:0 0 12px}
  .byline{font-size:.95rem}
  .chart{display:grid;grid-template-columns:minmax(0,1fr) 260px;gap:20px;align-items:start}
  @media (max-width:640px){.chart{grid-template-columns:1fr}}
  .tiles{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px}
  .tile{background:var(--panel);border-radius:8px;padding:10px 12px}
  .tile.big{grid-column:1 / -1}
  .tile .n{font-size:1.4rem;font-weight:700;line-height:1.1}
  .tile.big .n{font-size:2.2rem}
  .tile .l{font-size:.78rem;color:var(--muted);line-height:1.3}
  svg{display:block;width:100%;height:auto;overflow:visible}
  .bar-label{font-size:13px;fill:var(--fg)}
  .bar-value{font-size:13px;fill:var(--fg);font-weight:600}
  .axis text{font-size:12px;fill:var(--muted)}
  .axis line,.axis path{stroke:var(--line)}
  table{width:100%;border-collapse:collapse;font-size:.92rem}
  th,td{text-align:left;vertical-align:top;padding:9px 8px;border-top:1px solid var(--line)}
  th{font-size:.8rem;color:var(--muted);font-weight:600;border-top:0}
  tr.row{cursor:pointer}
  tr.row:hover td{background:var(--panel)}
  tr.row td:first-child::before{content:"▸ ";color:var(--muted)}
  tr.row.open td:first-child::before{content:"▾ "}
  tr.fold td{background:var(--panel);border-top:0;padding:4px 8px 16px}
  .fold-inner{display:grid;grid-template-columns:1fr 1fr;gap:14px}
  @media (max-width:640px){.fold-inner{grid-template-columns:1fr}}
  .fold h4{margin:8px 0 4px;font-size:.8rem;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
  blockquote{margin:4px 0 8px;padding:8px 12px;border-left:3px solid var(--line);font-style:italic}
  @media (max-width:760px){
    table thead{display:none}
    table tr{display:block;border-top:1px solid var(--line);padding:6px 0}
    table td{display:block;border-top:0;padding:3px 8px}
    table td[data-h]::before{content:attr(data-h) ": ";color:var(--muted);font-size:.8rem}
    tr.fold td{padding:4px 8px 12px}
  }
  .lines p{margin:8px 0}
  .lines b{font-weight:650}
  .timeline .t-label{font-size:12px;fill:var(--fg)}
  .timeline .t-date{font-size:11px;fill:var(--muted)}
  .timeline .t-line{stroke:var(--line);stroke-width:2}
  .timeline .t-tick{stroke:var(--muted)}
  .timeline .t-dot{fill:var(--accent)}
  ol.custody{list-style:none;padding:0;margin:0;border-left:2px solid var(--line)}
  ol.custody li{position:relative;padding:2px 0 10px 16px;font-size:.92rem}
  ol.custody li::before{content:"";position:absolute;left:-6px;top:.55em;width:10px;height:10px;border-radius:50%;background:var(--accent)}
  .parties{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px;font-size:.92rem}
  .parties ul{margin:4px 0;padding-left:18px}
  footer{margin-top:44px;padding-top:16px;border-top:1px solid var(--line);font-size:.9rem;color:var(--muted)}
  #error{color:var(--failed)}
</style></head>
<body><main>
<div class="eyebrow">A sample report for a synthetic case</div>
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
  const pct = x => Math.round(x * 100) + "%";
  const cls = o => ({"passed":"passed","failed":"failed","cannot tell":"canttell"}[o] || "notplanned");
  const colour = o => getComputedStyle(document.documentElement).getPropertyValue("--" + cls(o)).trim();
  const join = xs => xs.length <= 1 ? xs.join("") : xs.slice(0, -1).join(", ") + " and " + xs[xs.length - 1];
  const esc = s => String(s == null ? "" : s);

  // (a) the headline
  const head = root.append("section").attr("id", "headline");
  const sentences = R.recommendation.text.match(/[^.]+\.?/g) || [R.recommendation.text];
  head.append("h1").html(`<span class="badge ${cls(R.verdict)}">${esc(R.verdict)}</span> ${esc(R.test_item.name)} ${esc(R.test_item.version)}: ${esc(sentences[0].trim())}`);
  if (sentences.length > 1) head.append("p").attr("class", "lead").text(sentences.slice(1).join("").trim());
  head.append("div").attr("class", "question").html(`<b>The question the sponsor asked.</b> ${esc(R.sponsor.need)}.`);
  head.append("p").attr("class", "byline").html(
    `Recommended by ${esc(join(R.recommendation.by))} on ${fmt(R.recommendation.date)}; the report approved by ${esc(join(R.approval.by))} on ${fmt(R.approval.date)}; ` +
    `delivered by ${esc(join(R.delivery.by))} to ${esc(join(R.delivery.to))} on ${fmt(R.delivery.date)}; accepted on ${fmt(R.acceptance.date)}.`);
  head.append("p").attr("class", "byline muted").html(`For ${esc(join(R.sponsor.name))}. Its mission: ${esc(R.sponsor.mission)}.`);

  // (b) the chart: one bar per criterion, weighted, coloured by outcome; coverage and the rates beside it
  const chartSec = root.append("section");
  chartSec.append("h2").text("The criteria, by weight and outcome");
  const chart = chartSec.append("div").attr("class", "chart");
  const barsBox = chart.append("div");
  const tiles = chart.append("div").attr("class", "tiles");
  const C = R.coverage;
  const totalW = d3.sum(R.criteria, d => d.weight), coveredW = d3.sum(R.criteria.filter(d => !["not planned", "not attested"].includes(d.outcome)), d => d.weight);
  tiles.append("div").attr("class", "tile big").html(`<div class="n">${pct(C.coverage)}</div><div class="l">coverage by weight: ${coveredW} of ${totalW}, ${C.covered_count} of ${R.criteria.length} criteria attested</div>`);
  for (const [k, w] of [["pass_rate", "passed"], ["fail_rate", "failed"], ["cant_tell_rate", "cannot tell"]])
    tiles.append("div").attr("class", "tile").html(`<div class="n" style="color:${colour(w)}">${pct(C[k])}</div><div class="l">${w}, of the criteria attested</div>`);
  function drawBars(){
    barsBox.selectAll("*").remove();
    const width = Math.max(280, barsBox.node().getBoundingClientRect().width), rowH = 34, left = 44, right = 150, top = 6;
    const height = top + rowH * R.criteria.length + 24;
    const x = d3.scaleLinear().domain([0, d3.max(R.criteria, d => d.weight)]).range([0, width - left - right]);
    const svg = barsBox.append("svg").attr("viewBox", `0 0 ${width} ${height}`).attr("width", width).attr("height", height).attr("role", "img")
      .attr("aria-label", "one bar per acceptance criterion, its length the criterion's weight, its colour the attested outcome");
    const g = svg.selectAll("g.row").data(R.criteria).join("g").attr("class", "row").attr("transform", (d, i) => `translate(0,${top + i * rowH})`);
    g.append("text").attr("class", "bar-label").attr("x", 0).attr("y", rowH / 2).attr("dy", ".35em").text(d => d.id);
    g.append("rect").attr("x", left).attr("y", 6).attr("height", rowH - 12).attr("width", d => x(d.weight)).attr("rx", 3).attr("fill", d => colour(d.outcome));
    g.append("text").attr("class", "bar-value").attr("x", d => left + x(d.weight) + 8).attr("y", rowH / 2).attr("dy", ".35em").text(d => `${d.outcome}, weight ${d.weight}`);
    const axis = svg.append("g").attr("class", "axis").attr("transform", `translate(${left},${top + rowH * R.criteria.length})`).call(d3.axisBottom(x).ticks(d3.max(R.criteria, d => d.weight)).tickFormat(d3.format("d")));
    axis.append("text").attr("x", x.range()[1] + 8).attr("y", 0).attr("dy", ".35em").attr("text-anchor", "start").text("weight");
  }
  drawBars();

  // (c) the criteria table; a row unfolds into its evidence
  const tabSec = root.append("section");
  tabSec.append("h2").text("Each criterion, and what it was judged on");
  tabSec.append("p").attr("class", "muted").text("Click a row to see the probe, the response, the determination and who made it.");
  const heads = ["Requirement", "Criterion", "Expected result", "Outcome", "Sufficiency", "Appropriateness", "Attested by", "Evidence"];
  const table = tabSec.append("table");
  table.append("thead").append("tr").selectAll("th").data(heads).join("th").text(d => d);
  const tbody = table.append("tbody");
  for (const c of R.criteria) {
    const evidence = c.attestations.flatMap(a => a.determinations.flatMap(d => d.evidence));
    const row = tbody.append("tr").attr("class", "row").attr("tabindex", 0);
    const cells = [
      c.requirement, `${c.id}: ${c.text}`, c.expected,
      `<span class="dot ${cls(c.outcome)}"></span>${esc(c.outcome)}`,
      c.sufficiency.length ? c.sufficiency.join(", ") : "no attestation",
      c.appropriateness.length ? c.appropriateness.join(", ") : "no attestation",
      c.attested_by.length ? join(c.attested_by) : "no one",
      evidence.length ? join(evidence.map(e => e.label)) : (c.planned ? "none collected" : "none: the plan did not exercise it")
    ];
    cells.forEach((v, i) => row.append("td").attr("data-h", heads[i]).html(i === 3 ? v : esc(v)));
    const fold = tbody.append("tr").attr("class", "fold").attr("hidden", true);
    const inner = fold.append("td").attr("colspan", heads.length).append("div").attr("class", "fold");
    if (!c.attestations.length) {
      inner.append("p").text(c.planned ? "No attestation was made on this criterion." : "The test plan did not exercise this criterion, so there is no evidence and no attestation; the coverage above counts it as not covered.");
    }
    for (const a of c.attestations) {
      inner.append("p").html(`<b>Attestation</b> by ${esc(join(a.by))} on ${fmt(a.date)}: <span class="dot ${cls(a.outcome)}"></span>${esc(a.outcome)}, the context ${esc(a.appropriateness)}, the evidence ${esc(a.sufficiency)}. ${esc(a.note || "")}`);
      for (const d of a.determinations) {
        inner.append("p").html(`<b>Determination</b> by ${esc(join(d.by))} on ${fmt(d.date)}: <span class="dot ${cls(d.outcome)}"></span>${esc(d.outcome)}. ${esc(d.note || "")}`);
        for (const e of d.evidence) {
          const grid = inner.append("div").attr("class", "fold-inner");
          const l = grid.append("div"), r = grid.append("div");
          l.append("h4").text("The probe");
          l.append("blockquote").text(e.probe ? e.probe.text : "not recorded");
          if (e.session) l.append("p").attr("class", "muted").text(`${e.session.label}; turn ${e.session.turn}, ${fmt(e.session.started)}.`);
          r.append("h4").text("The response");
          r.append("blockquote").text(e.response ? e.response.text : "not recorded");
          if (e.response) r.append("p").attr("class", "muted").text(`By ${join(e.response.by)}; collected as evidence by ${join(e.by)} on ${fmt(e.date)}.`);
        }
      }
    }
    const toggle = () => { const open = !row.classed("open"); row.classed("open", open); fold.attr("hidden", open ? null : true); };
    row.on("click", toggle).on("keydown", ev => { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); toggle(); } });
  }

  // (d) the assumptions: the DSO release and the operational environment
  const asm = root.append("section").attr("class", "lines");
  asm.append("h2").text("What the judgments assume");
  const A = R.assumptions;
  asm.append("p").html(`<b>The domain knowledge.</b> ${esc(A.dso.label)} (version ${esc(A.dso.version)}), approved by ${esc(join(A.dso.approved_by))} on ${fmt(A.dso.date)}.`);
  const assessed = A.requirement_set.assessment.map(s => `judged ${s.outcome === "passed" ? "appropriate" : s.outcome} by ${join(s.by)} on ${fmt(s.date)}${s.note ? ": " + s.note : ""}`).join("; ");
  asm.append("p").html(`<b>The operational environment.</b> ${esc(A.environment)} Declared by ${esc(join(A.requirement_set.by))} on ${fmt(A.requirement_set.date)}${assessed ? "; " + esc(assessed) : ""}.`);

  // (e) the chain of custody
  const cust = root.append("section").attr("class", "timeline");
  cust.append("h2").text("The chain of custody");
  cust.append("p").attr("class", "muted").text(`The agreement, the access, the requirement set and its assessment, the plan approval, the sessions, the attestations, the machine check of the record, the approval, the delivery and the acceptance, each on its date. The record's construction was checked by ${join(R.conformance.by)} on ${fmt(R.conformance.date)}: ${R.conformance.outcome}.`);
  const strip = cust.append("div");
  function drawTimeline(){
    strip.selectAll("*").remove();
    const width = Math.max(280, strip.node().getBoundingClientRect().width);
    const events = R.timeline.map(e => ({...e, t: new Date(e.date)}));
    if (width < 700) {
      const ol = strip.append("ol").attr("class", "custody");
      ol.selectAll("li").data(events).join("li").html(e => `<b>${esc(e.what)}</b>${e.detail ? ", " + esc(e.detail) : ""}, ${esc(join(e.who))}. <span class="muted">${fmt(e.date)}</span>`);
      return;
    }
    const left = 20, right = 20, mid = 120, height = 250;
    const x = d3.scaleUtc().domain(d3.extent(events, e => e.t)).range([left, width - right]);
    const svg = strip.append("svg").attr("viewBox", `0 0 ${width} ${height}`).attr("width", width).attr("height", height).attr("role", "img").attr("aria-label", "the dated events of the evaluation on one time line");
    svg.append("line").attr("class", "t-line").attr("x1", left).attr("x2", width - right).attr("y1", mid).attr("y2", mid);
    // events on the same day stack; labels alternate above and below the line
    const byDay = d3.groups(events, e => e.date.slice(0, 10));
    byDay.forEach(([d, es], i) => {
      const cx = x(new Date(d + "T12:00:00Z")), up = i % 2 === 0, dir = up ? -1 : 1;
      const g = svg.append("g").attr("transform", `translate(${cx},${mid})`);
      g.append("circle").attr("class", "t-dot").attr("r", 5);
      g.append("line").attr("class", "t-tick").attr("y1", 0).attr("y2", dir * 14);
      const t = g.append("text").attr("text-anchor", cx < width / 2 ? "start" : "end").attr("x", cx < width / 2 ? -4 : 4);
      t.append("tspan").attr("class", "t-date").attr("x", cx < width / 2 ? -4 : 4).attr("y", dir * (up ? 22 : 30)).text(fmt(d));
      const names = d3.groups(es, e => e.what).map(([w, xs]) => xs.length > 1 ? `${xs.length} ${w}s` : w);
      names.forEach((n, j) => t.append("tspan").attr("class", "t-label").attr("x", cx < width / 2 ? -4 : 4).attr("y", dir * (up ? 22 + 15 * (j + 1) : 30 + 15 * (j + 1))).text(n));
    });
  }
  drawTimeline();
  const cl = cust.append("details");
  cl.append("summary").attr("class", "muted").text("Every event, with who did it");
  cl.append("ol").attr("class", "custody").style("margin-top", "10px").selectAll("li").data(R.timeline).join("li")
    .html(e => `<b>${esc(e.what)}</b>${e.detail ? ", " + esc(e.detail) : ""}, ${esc(join(e.who))}. <span class="muted">${fmt(e.date)}</span>`);

  // the parties
  const par = root.append("section");
  par.append("h2").text("Who was party to it");
  const pg = par.append("div").attr("class", "parties");
  const col = (title, items) => { const d = pg.append("div"); d.append("b").text(title); d.append("ul").selectAll("li").data(items).join("li").text(t => t); };
  col("Organizations", R.parties.organizations);
  col("People, within the testing organization", R.parties.people.map(p => `${p.name}, for ${join(p.for)}`));
  col("Affected populations", R.parties.populations);
  par.append("p").attr("class", "muted").text(`${R.agreement.label}; signed by ${join(R.agreement.signed_by)} on ${fmt(R.agreement.date)}. Test item provided by ${join(R.test_item.provider)}.`);

  // (f) the footer
  const foot = root.append("footer");
  foot.append("p").html(`<b>A sample report for a synthetic case.</b> ${esc(R.record.note)}`);
  foot.append("p").text("Everything on this page is read from the evaluation record; the coverage and the rates are recomputed from it by the coverage query, never copied from the stored report. The record holds more than this page shows; the knowledge graph explorer opens all of it.");

  let raf = null;
  window.addEventListener("resize", () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(() => { drawBars(); drawTimeline(); }); });
})();
</script>
</body></html>
"""


def render() -> str:
    return PAGE.replace("__TITLE__", TITLE).replace("__D3__", D3)


def main() -> int:
    OUT.mkdir(exist_ok=True)
    model = build(record_graph())
    (OUT / "report.json").write_text(json.dumps(model, ensure_ascii=False, sort_keys=True, indent=1) + "\n")
    (OUT / "index.html").write_text(render())
    print(f"report: {len(model['criteria'])} criteria, coverage {model['coverage']['coverage']:.2f}, verdict {model['verdict']}, {len(model['timeline'])} events")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
