"""Execute the nested process from the model graph (concern C-30).

The executor walks the contracting lifecycle in succession order as the
canonical model graph states it, drills into the step typed by the
evaluation process, and at each step emits the items the step's out
parameters name, each attributed to the part whose port supplies that item
kind in the wiring, timestamped in step order, and linked to the items that
flowed into the step. What comes from the model: the steps, their order,
the nesting, which item kinds each step produces and consumes, and who
produces them. What comes from here: one template per step saying which
fields a conformant item of each kind carries, written against the record
shapes (R-22: value rules live in the shapes; the executor states an item,
the shapes judge it). The executor refuses to run if a template's declared
outputs disagree with the model's step signature, so the two cannot drift.

Then the checks the site claims are run over the emitted record: SHACL
conformance (S0 to S9), completeness (every item kind the process produces
is present), coverage recomputed by query, and the traceback from every
recommendation to what it rests on. Mutations remove a wire, skip a step,
put the wrong actor on an activity or break the time order; each is
expected to be caught by a named check, and the table says by which.
Deterministic: same model, same parameters, same graph.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

from rdflib import RDF, RDFS, BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import XSD

from . import views
from .views import SYS

EPO = Namespace("https://w3id.org/og-caie/epo#")
OGC = Namespace("https://w3id.org/og-caie/")
PROV = Namespace("http://www.w3.org/ns/prov#")
EARL = Namespace("http://www.w3.org/ns/earl#")
RUN = Namespace("https://w3id.org/og-caie/run/executed#")
SH = Namespace("http://www.w3.org/ns/shacl#")

OPTIONAL_KINDS = {"Strategy"}  # a plan's means are probes or a strategy (S3-TestPlan); probes here
START = datetime(2026, 9, 1, 9, 0, tzinfo=timezone.utc)


@dataclass(frozen=True)
class Params:
    requirements: int = 1
    criteria_per_requirement: int = 3
    planned: int = 2          # criteria the plan exercises; the rest stay uncovered
    sessions: int = 1
    turns: int | None = None   # turns per session; None applies every probe once
    populations: int = 2      # the first is interviewed, the others represented
    outcomes: tuple = ("failed", "passed")   # cycled over the covered criteria


@dataclass
class Run:
    g: Graph
    agents: dict
    items: dict = field(default_factory=lambda: {})   # kind -> [nodes], in emission order
    clock: int = 0

    def at(self, step_index: int, j: int = 0) -> Literal:
        return Literal((START + timedelta(days=step_index, minutes=10 * j)).isoformat().replace("+00:00", "Z"), datatype=XSD.dateTime)

    def new(self, kind: str, tag: str, step_index: int, j: int = 0, timed: str = "generatedAtTime"):
        n = RUN[f"{tag}-{len(self.items.get(kind, [])) + 1}"]
        self.g.add((n, RDF.type, EPO[kind]))
        if timed:
            self.g.add((n, PROV[timed], self.at(step_index, j)))
        self.items.setdefault(kind, []).append(n)
        return n


# --- what the model says ----------------------------------------------------

def process_steps(g: Graph) -> list[tuple[str, str]]:
    """(process, step) pairs in execution order, the typed step replaced by its process's steps."""
    out = []
    for step in views.steps(g, views.OUTER_PROCESS):
        proc = views.definitions(g, SYS.ActionDefinition)[views.OUTER_PROCESS]
        u = next(x for x in g.subjects(SYS.owner, proc) if (x, RDF.type, SYS.ActionUsage) in g and views.name(g, x) == step)
        typ = g.value(u, SYS.type)
        if typ is not None and (typ, RDF.type, SYS.ActionDefinition) in g:
            out += [(views.name(g, typ), s) for s in views.steps(g, views.name(g, typ))]
        else:
            out.append((views.OUTER_PROCESS, step))
    return out


def step_signature(g: Graph, proc_name: str, step: str) -> tuple[set[str], set[str]]:
    """(input kinds, output kinds) of one step, from its parameters."""
    proc = views.definitions(g, SYS.ActionDefinition)[proc_name]
    u = next(x for x in g.subjects(SYS.owner, proc) if (x, RDF.type, SYS.ActionUsage) in g and views.name(g, x) == step)
    ins, outs = set(), set()
    for p in g.subjects(SYS.owner, u):
        t = g.value(p, SYS.type)
        if t is None:
            continue
        (outs if str(g.value(p, SYS.direction)) == "out" else ins).add(views.name(g, t))
    return ins, outs


def suppliers(g: Graph) -> dict[str, list[str]]:
    """item kind -> the part kinds whose output port carries it, from the wiring."""
    out: dict[str, list[str]] = {}
    for pd in g.subjects(RDF.type, SYS.PortDefinition):
        item = views.item_of_port_def(g, pd)
        parts = sorted({views.name(g, g.value(p, SYS.owner)) for p in g.subjects(SYS.type, pd)
                        if (p, RDF.type, SYS.PortUsage) in g and g.value(p, SYS.isConjugated) is None and g.value(p, SYS.isEnd) is None
                        and (g.value(p, SYS.owner), RDF.type, SYS.PartDefinition) in g})
        out[item] = parts
    return out


# --- the run -----------------------------------------------------------------

def parties(r: Run, params: Params):
    g = r.g
    def agent(tag, label, *types, **props):
        n = RUN[tag]
        for t in (PROV.Agent, *types):
            g.add((n, RDF.type, t))
        g.add((n, RDFS.label, Literal(label)))
        for k, v in props.items():
            g.add((n, EPO[k] if k not in ("actedOnBehalfOf",) else PROV[k], v))
        return n
    a = r.agents
    a["SponsorOrganization"] = agent("sponsor", "sponsor organization", PROV.Organization, role=EPO.sponsorRole, isAccountable=Literal(False))
    a["AccountableOrganization"] = agent("accountable", "accountable organization", PROV.Organization, role=EPO.accountableOrganizationRole)
    a["TestingOrganization"] = agent("testing-org", "testing organization", PROV.Organization, role=EPO.testingOrganizationRole, independentOfAccountable=Literal(True))
    a["AccountExecutive"] = agent("executive", "account executive", PROV.Person, role=EPO.accountExecutiveRole, actedOnBehalfOf=a["TestingOrganization"])
    a["DomainExpert"] = agent("expert", "domain expert", PROV.Person, role=EPO.domainExpertRole, actedOnBehalfOf=a["TestingOrganization"])
    a["EvaluationOperator"] = agent("operator", "evaluation operator", PROV.Person, role=EPO.evaluationOperatorRole, actedOnBehalfOf=a["TestingOrganization"])
    a["TestItem"] = agent("test-item", "test item", PROV.SoftwareAgent, EARL.TestSubject, version=Literal("1"), actedOnBehalfOf=a["AccountableOrganization"])
    a["ProbeDeriver"] = agent("probe-deriver", "probe deriver", PROV.SoftwareAgent, version=Literal("1"), actedOnBehalfOf=a["TestingOrganization"])
    a["ConformanceChecker"] = agent("checker", "conformance checker", PROV.SoftwareAgent, version=Literal("1"), actedOnBehalfOf=a["TestingOrganization"])
    a["CoverageCalculator"] = agent("calculator", "coverage calculator", PROV.SoftwareAgent, version=Literal("1"), actedOnBehalfOf=a["TestingOrganization"])
    a["AffectedPopulation"] = []
    for i in range(params.populations):
        p = agent(f"population-{i + 1}", f"affected population {i + 1}", EPO.Population)
        if i > 0:
            g.add((p, EPO.representedBy, a["DomainExpert"]))
        a["AffectedPopulation"].append(p)


def by(r: Run, n, kind: str, pred=PROV.wasAttributedTo):
    """Attribute an item to the one part kind the wiring says supplies it."""
    who = r.agents[r.supplier[kind][0]]
    r.g.add((n, pred, who))
    return who


def result(g: Graph, n, outcome: str, info: str = ""):
    res = BNode()
    g.add((n, EARL.result, res)); g.add((res, RDF.type, EARL.TestResult)); g.add((res, EARL.outcome, EARL[outcome]))
    if info:
        g.add((res, EARL.info, Literal(info)))


# one template per step: declares the kinds it emits (checked against the model's step signature)
def t_need(r, i, p):
    g = r.g
    m = r.new("Mission", "mission", i)
    for pop in r.agents["AffectedPopulation"]:
        g.add((m, EPO.regards, pop))
    g.add((m, RDFS.label, Literal("the sponsor's purpose and its obligations towards the affected populations"))); g.add((m, EPO.step, EPO.need)); by(r, m, "Mission")
    n = r.new("Need", "need", i, 1)
    g.add((n, EPO.underMission, m)); g.add((n, RDFS.label, Literal("the sponsor's stated need"))); g.add((n, EPO.step, EPO.need)); by(r, n, "Need")
    return {"Mission", "Need"}


def t_propose(r, i, p):
    n = r.new("Proposal", "proposal", i)
    r.g.add((n, EPO.respondsTo, r.items["Need"][0])); r.g.add((n, EPO.step, EPO.propose)); r.g.add((n, RDFS.label, Literal("the provider's proposal"))); by(r, n, "Proposal")
    return {"Proposal"}


def t_agree(r, i, p):
    g = r.g
    n = r.new("ServiceAgreement", "agreement", i)
    g.add((n, EPO.signedBy, r.agents["SponsorOrganization"])); g.add((n, EPO.signedBy, r.agents["AccountExecutive"]))
    g.add((n, EPO.step, EPO.agree)); g.add((n, RDFS.label, Literal("the service agreement")))
    sow = r.new("StatementOfWork", "statement-of-work", i, 1)
    g.add((sow, EPO.step, EPO.agree)); g.add((sow, RDFS.label, Literal("the scope of work: the first population interviewed, the others represented"))); by(r, sow, "StatementOfWork")
    for k, pop in enumerate(r.agents["AffectedPopulation"]):
        d = RUN[f"engagement-{k + 1}"]
        g.add((d, RDF.type, EPO.EngagementDecision)); g.add((d, EPO.population, pop))
        g.add((d, EPO.engagement, EPO.interview if k == 0 else EPO.representation)); g.add((sow, EPO.decides, d))
    return {"ServiceAgreement", "StatementOfWork"}


def t_access(r, i, p):
    n = r.new("TestItemAccess", "access", i)
    r.g.add((n, EPO.grantsAccessTo, r.agents["TestItem"])); r.g.add((n, EPO.step, EPO.access)); by(r, n, "TestItemAccess")
    return {"TestItemAccess"}


def t_scope(r, i, p):
    g = r.g
    s = r.new("StakeholderInput", "input", i)
    g.add((s, PROV.wasAttributedTo, r.agents["AffectedPopulation"][0])); g.add((s, EPO.step, EPO.scope)); g.add((s, RDFS.label, Literal("interview notes")))
    d = r.new("DsoRelease", "dso", i, 1)
    g.add((d, EPO.version, Literal("r1"))); g.add((d, EPO.approvedBy, r.agents["DomainExpert"])); g.add((d, EPO.step, EPO.scope)); by(r, d, "DsoRelease")
    return {"StakeholderInput", "DsoRelease"}


def t_declare(r, i, p):
    g = r.g
    rs = r.new("RequirementSet", "requirements", i)
    g.add((rs, EPO.environment, Literal("the declared operational environment"))); g.add((rs, EPO.systemUnderTest, r.agents["TestItem"]))
    g.add((rs, EPO.underAgreement, r.items["ServiceAgreement"][0])); g.add((rs, EPO.step, EPO.declareRequirements)); by(r, rs, "RequirementSet")
    for q in range(p.requirements):
        req = r.new("Requirement", "requirement", i, 0, timed="")
        g.add((req, EPO.partOf, rs)); g.add((req, EPO.text, Literal(f"requirement {q + 1}")))
        for c in range(p.criteria_per_requirement):
            a = r.new("AcceptanceCriterion", "criterion", i, 0, timed="")
            g.add((a, PROV.wasDerivedFrom, req)); g.add((a, EPO.text, Literal(f"criterion {q + 1}.{c + 1}")))
            g.add((a, EPO.expectedResult, Literal(f"expected result {q + 1}.{c + 1}"))); g.add((a, EPO.weight, Literal(1))); g.add((a, EPO.minPassRate, Literal(0.95)))
    ass = r.new("AppropriatenessAssessment", "assessment", i, 1, timed="endedAtTime")
    g.add((ass, EARL.subject, rs)); g.add((ass, EARL.mode, EARL.manual)); g.add((ass, EARL.assertedBy, r.agents["DomainExpert"]))
    g.add((ass, PROV.used, r.items["StakeholderInput"][0])); g.add((ass, EPO.appropriateness, EPO.appropriate)); g.add((ass, EPO.step, EPO.declareRequirements))
    result(g, ass, "passed")
    return {"RequirementSet", "AcceptanceCriterion", "AppropriatenessAssessment"}


def t_plan(r, i, p):
    g = r.g
    dso, rs = r.items["DsoRelease"][0], r.items["RequirementSet"][0]
    der = r.new("ProbeDerivation", "derivation", i, 0, timed="endedAtTime")
    g.add((der, PROV.used, dso)); g.add((der, PROV.used, rs)); g.add((der, PROV.wasAssociatedWith, r.agents["ProbeDeriver"])); g.add((der, EPO.step, EPO.plan))
    plan = r.new("TestPlan", "plan", i, 1)
    g.add((plan, PROV.wasDerivedFrom, rs)); g.add((plan, PROV.wasDerivedFrom, dso)); g.add((plan, PROV.wasGeneratedBy, der)); g.add((plan, EPO.step, EPO.plan)); by(r, plan, "TestPlan")
    covered = r.items["AcceptanceCriterion"][:p.planned]
    for a in covered:
        g.add((plan, EPO.objective, a))
        pr = r.new("Probe", "probe", i, 1)
        g.add((pr, EPO.text, Literal(f"probe for {g.value(a, EPO.text)}"))); g.add((pr, EPO.exercises, a)); g.add((pr, EPO.derivedFromDso, dso))
        g.add((pr, PROV.wasGeneratedBy, der)); g.add((plan, EPO.means, pr))
        chk = r.new("ConsistencyCheck", "check", i, 2, timed="endedAtTime")
        g.add((chk, EARL.subject, pr)); g.add((chk, EARL.test, dso)); g.add((chk, EARL.mode, EARL.automatic)); g.add((chk, EARL.assertedBy, r.agents["ConformanceChecker"]))
        g.add((chk, PROV.wasAssociatedWith, r.agents["ConformanceChecker"])); result(g, chk, "passed")
    ap = r.new("PlanApproval", "approval", i, 3, timed="endedAtTime")
    g.add((ap, EPO.approves, plan)); g.add((ap, EARL.subject, plan)); g.add((ap, EARL.mode, EARL.manual)); g.add((ap, EARL.assertedBy, r.agents["DomainExpert"]))
    g.add((ap, PROV.wasAssociatedWith, r.agents["DomainExpert"])); g.add((ap, EPO.step, EPO.plan)); result(g, ap, "passed")
    return {"TestPlan", "Probe", "PlanApproval"}


def t_execute(r, i, p):
    g = r.g
    plan = r.items["TestPlan"][0]
    probes = r.items["Probe"]
    for s in range(p.sessions):
        ses = r.new("Session", "session", i, s, timed="startedAtTime")
        g.add((ses, PROV.wasAssociatedWith, r.agents["TestItem"])); g.add((ses, PROV.wasAssociatedWith, r.agents["EvaluationOperator"]))
        g.add((ses, PROV.endedAtTime, r.at(i, s + 1))); g.add((ses, EPO.step, EPO.execute))
        turns = p.turns or len(probes)
        traj = r.new("Trajectory", "trajectory", i, s, timed="")
        g.add((traj, PROV.wasGeneratedBy, ses)); g.add((traj, EPO.turns, Literal(turns)))
        for t in range(turns):
            pr = probes[t % len(probes)]
            turn = r.new("Turn", "turn", i, s, timed="startedAtTime")
            g.add((turn, EPO.inSession, ses)); g.add((turn, EPO.turnIndex, Literal(t + 1))); g.add((turn, PROV.used, pr))
            resp = r.new("Response", "response", i, s, timed="")
            g.add((resp, EPO.text, Literal(f"response of session {s + 1} turn {t + 1}"))); g.add((resp, PROV.wasGeneratedBy, turn)); g.add((resp, PROV.wasAttributedTo, r.agents["TestItem"]))
            for a in g.objects(pr, EPO.exercises):
                ev = r.new("Evidence", "evidence", i, s + 1)
                g.add((ev, EPO.bearsOn, a)); g.add((ev, EPO.underPlan, plan)); g.add((ev, PROV.wasDerivedFrom, resp)); by(r, ev, "Evidence")
    return {"Session", "Response", "Evidence"}


def t_determine(r, i, p):
    g = r.g
    covered = [a for a in r.items["AcceptanceCriterion"] if (r.items["TestPlan"][0], EPO.objective, a) in g]
    determiners = r.supplier["Determination"]
    for k, a in enumerate(covered):
        evs = [e for e in r.items["Evidence"] if (e, EPO.bearsOn, a) in g]
        outcome = p.outcomes[k % len(p.outcomes)]
        det = r.new("Determination", "determination", i, k, timed="endedAtTime")
        who = r.agents[determiners[k % len(determiners)]]
        g.add((det, EARL.test, a)); g.add((det, EARL.subject, r.agents["TestItem"])); g.add((det, EARL.mode, EARL.manual)); g.add((det, EARL.assertedBy, who))
        g.add((det, PROV.wasAssociatedWith, who)); g.add((det, EPO.step, EPO.determineAndAttest))
        for e in evs:
            g.add((det, PROV.used, e))
        result(g, det, outcome)
        att = r.new("Attestation", "attestation", i, k + 1, timed="endedAtTime")
        g.add((att, EARL.test, a)); g.add((att, EARL.subject, r.agents["TestItem"])); g.add((att, EARL.mode, EARL.manual)); g.add((att, EARL.assertedBy, r.agents["DomainExpert"]))
        g.add((att, PROV.wasAssociatedWith, r.agents["DomainExpert"])); g.add((att, PROV.used, det)); g.add((att, EPO.appropriateness, EPO.appropriate))
        g.add((att, EPO.sufficiency, EPO.sufficient)); g.add((att, EPO.step, EPO.determineAndAttest)); result(g, att, outcome)
    return {"Determination", "Attestation"}


def t_report(r, i, p):
    g = r.g
    comp = r.new("CoverageComputation", "coverage", i, 0, timed="endedAtTime")
    g.add((comp, PROV.used, r.items["RequirementSet"][0])); g.add((comp, PROV.wasAssociatedWith, r.agents["CoverageCalculator"])); g.add((comp, EARL.mode, EARL.automatic)); g.add((comp, EPO.step, EPO.report))
    for att in r.items["Attestation"]:
        g.add((comp, PROV.used, att))
    rep = r.new("Report", "report", i, 1, timed="")
    g.add((rep, PROV.wasGeneratedBy, comp))
    row = next(iter(g.query((views_root() / "queries" / "coverage.rq").read_text())))
    for k in ("coverage", "passRate", "failRate", "cantTellRate"):
        g.add((rep, EPO[k], Literal(round(float(getattr(row, k)), 6))))
    rec = r.new("Recommendation", "recommendation", i, 2)
    g.add((rec, EPO.text, Literal("the recommendation"))); g.add((rec, EPO.step, EPO.report)); by(r, rec, "Recommendation")
    for att in r.items["Attestation"]:
        g.add((rec, PROV.wasDerivedFrom, att))
        for det in g.objects(att, PROV.used):
            for e in g.objects(det, PROV.used):
                g.add((rec, PROV.wasDerivedFrom, e))
    g.add((rec, PROV.wasDerivedFrom, r.items["TestPlan"][0])); g.add((rec, PROV.wasDerivedFrom, r.items["DsoRelease"][0])); g.add((rec, PROV.wasDerivedFrom, rep))
    return {"Report", "Recommendation"}


def t_deliver(r, i, p):
    d = r.new("Delivery", "delivery", i)
    g = r.g
    g.add((d, PROV.wasDerivedFrom, r.items["Report"][0])); g.add((d, PROV.wasDerivedFrom, r.items["Recommendation"][0]))
    g.add((d, EPO.deliveredTo, r.agents["SponsorOrganization"])); g.add((d, EPO.step, EPO.deliver)); by(r, d, "Delivery")
    return {"Delivery"}


def t_accept(r, i, p):
    a = r.new("Acceptance", "acceptance", i)
    r.g.add((a, EPO.accepts, r.items["Delivery"][0])); r.g.add((a, EPO.step, EPO.acceptDelivery)); by(r, a, "Acceptance")
    return {"Acceptance"}


TEMPLATES = {"need": t_need, "propose": t_propose, "agree": t_agree, "access": t_access, "scope": t_scope,
             "declareRequirements": t_declare, "plan": t_plan, "execute": t_execute, "determineAndAttest": t_determine,
             "report": t_report, "deliver": t_deliver, "acceptDelivery": t_accept}


def views_root() -> Path:
    from .graph import find_root
    return find_root()


def execute(model: Graph, params: Params = Params()) -> Graph:
    """Walk the process the model states and emit one conformant record."""
    g = Graph()
    for k, v in (("epo", EPO), ("prov", PROV), ("earl", EARL), ("run", RUN), ("rdfs", RDFS), ("xsd", XSD)):
        g.bind(k, v)
    r = Run(g=g, agents={})
    r.supplier = suppliers(model)
    parties(r, params)
    for i, (proc, step) in enumerate(process_steps(model)):
        ins, outs = step_signature(model, proc, step)
        emitted = TEMPLATES[step](r, i, params)
        if not (emitted <= outs and (outs - emitted) <= OPTIONAL_KINDS):
            raise RuntimeError(f"step {step}: template emits {sorted(emitted)} but the model declares {sorted(outs)}")
        for kind in ins:
            if kind not in r.items:
                raise RuntimeError(f"step {step}: input {kind} was never produced by an earlier step")
    return g


# --- mutations: each breaks one thing a check must catch ---------------------

def m_skip_assessment(g):
    for a in list(g.subjects(RDF.type, EPO.AppropriatenessAssessment)):
        g.remove((a, None, None))


def m_skip_approval(g):
    for a in list(g.subjects(RDF.type, EPO.PlanApproval)):
        g.remove((a, None, None))


def m_skip_access(g):
    for a in list(g.subjects(RDF.type, EPO.TestItemAccess)):
        g.remove((a, None, None))


def m_unwire_evidence(g):
    for e in list(g.subjects(RDF.type, EPO.Evidence)):
        g.remove((e, EPO.underPlan, None))


def m_executive_attests(g):
    ex = next(g.subjects(EPO.role, EPO.accountExecutiveRole))
    for a in g.subjects(RDF.type, EPO.Attestation):
        g.remove((a, EARL.assertedBy, None)); g.add((a, EARL.assertedBy, ex))


def m_attest_without_determination(g):
    for a in g.subjects(RDF.type, EPO.Attestation):
        g.remove((a, PROV.used, None))


def m_requirements_before_agreement(g):
    ag = next(g.subjects(RDF.type, EPO.ServiceAgreement))
    rs = next(g.subjects(RDF.type, EPO.RequirementSet))
    t = g.value(ag, PROV.generatedAtTime)
    g.remove((rs, PROV.generatedAtTime, None)); g.add((rs, PROV.generatedAtTime, Literal(str(t).replace("2026-09-03", "2026-08-30"), datatype=XSD.dateTime)))


def m_engagement_mismatch(g):
    """The statement of work said the first population would be interviewed; the decision is flipped to representation, which the record does not realize."""
    d = next(d for d in g.subjects(RDF.type, EPO.EngagementDecision) if (d, EPO.engagement, EPO.interview) in g)
    g.remove((d, EPO.engagement, None)); g.add((d, EPO.engagement, EPO.representation))


MUTATIONS = {
    "skip-assessment": ("skip the appropriateness assessment (a step's output missing)", m_skip_assessment),
    "skip-approval": ("skip the plan approval", m_skip_approval),
    "skip-access": ("skip the access grant (a contracting step missing)", m_skip_access),
    "unwire-evidence": ("cut the wire binding evidence to its plan", m_unwire_evidence),
    "executive-attests": ("the account executive attests instead of the domain expert", m_executive_attests),
    "attest-without-determination": ("attestations aggregate no determination", m_attest_without_determination),
    "requirements-before-agreement": ("the requirement set dated before the agreement", m_requirements_before_agreement),
    "engagement-mismatch": ("the statement of work decides representation for a population the record only interviewed", m_engagement_mismatch),
}


# --- the checks ---------------------------------------------------------------

def conformance(record: Graph, shapes: Graph, epo: Graph) -> tuple[bool, list[str]]:
    from pyshacl import validate
    data = Graph()
    for t in record:
        data.add(t)
    for t in epo:
        data.add(t)
    ok, rg, _ = validate(data, shacl_graph=shapes, advanced=True)
    fired = set()
    for s in rg.objects(None, SH.sourceShape):
        if isinstance(s, BNode):  # a property shape: name the node shape that owns it
            s = next((ns for ns in shapes.subjects(SH.property, s)), s)
        fired.add(str(s).rsplit("/", 1)[-1])
    return bool(ok), sorted(fired)


def completeness(record: Graph, model: Graph) -> list[str]:
    """Item kinds the process produces (out parameters of its steps) that the record lacks."""
    produced = set()
    for proc, step in process_steps(model):
        produced |= step_signature(model, proc, step)[1]
    present = {str(c).rsplit("#", 1)[-1] for c in record.objects(None, RDF.type) if str(c).startswith(str(EPO))}
    return sorted(k for k in produced - present if k not in OPTIONAL_KINDS)


def coverage(record: Graph, epo: Graph) -> dict:
    data = Graph()
    for t in record:
        data.add(t)
    for t in epo:
        data.add(t)
    row = next(iter(data.query((views_root() / "queries" / "coverage.rq").read_text())))
    return {k: round(float(getattr(row, k)), 4) for k in ("coverage", "passRate", "failRate", "cantTellRate")}


def traceback_rows(record: Graph, epo: Graph) -> int:
    data = Graph()
    for t in record:
        data.add(t)
    for t in epo:
        data.add(t)
    return len(list(data.query((views_root() / "queries" / "traceback.rq").read_text())))


def check(record: Graph, model: Graph, shapes: Graph, epo: Graph) -> dict:
    ok, fired = conformance(record, shapes, epo)
    return {"conforms": ok, "fired": fired, "missing": completeness(record, model), "coverage": coverage(record, epo), "traceback": traceback_rows(record, epo)}


VARIANTS = {
    "planned 2 of 3": Params(),
    "planned 3 of 3": Params(planned=3),
    "two sessions, two requirements": Params(requirements=2, criteria_per_requirement=2, planned=4, sessions=2),
}


def demonstrate(model: Graph, shapes: Graph, epo: Graph, params: Params = Params()) -> dict:
    """The run, the parameter variants, and every mutation of the run, each with its checks."""
    base = execute(model, params)
    out = {"run": check(base, model, shapes, epo), "variants": {}, "mutations": {}}
    for name, pv in VARIANTS.items():
        out["variants"][name] = check(execute(model, pv), model, shapes, epo)
    for name, (desc, fn) in MUTATIONS.items():
        g = Graph()
        for t in base:
            g.add(t)
        fn(g)
        out["mutations"][name] = {"description": desc, **check(g, model, shapes, epo)}
    return out
