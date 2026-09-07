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

The emitted record follows sheet 10 (R-50): it is a prov:Bundle every item
and agent is a member of, tagged synthetic; the sponsor's signatory signs,
declares the user interest, approves the requirement set and accepts; the
authorized representative declares independence; the operator's
determinations are paired with a second by the expert (independence at the
person level); the attestations' judgments cycle over a parameter; the
checker's verdict on the record precedes the final report and carries the
digests of what it ran; no item asserts a step (the checks load the model
graph, through which the step is derived).
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
RUN = Namespace("https://w3id.org/og-caie/evaluation/executed#")  # the executed record's own namespace (prefix ex:), apart from the measles evaluation's ev:
SH = Namespace("http://www.w3.org/ns/shacl#")

OPTIONAL_KINDS = {"Strategy", "PlanDeviation"}  # a plan's means are probes or a strategy (S3-TestPlan), probes here; a deviation only where a criterion is left unplanned (sheet 10-16)
RECORD = RUN["record"]  # the bundle (sheet 10-31)
JUDGMENTS_ALLOWED = (("passed", "sufficient", "appropriate"), ("failed", "sufficient", "appropriate"), ("cantTell", "sufficient", "appropriate"),
                     ("cantTell", "insufficient", "appropriate"), ("inapplicable", "sufficient", "inappropriate"))  # the five combinations S6 allows (sheet 10-12); a determination says cantTell where an attestation says inapplicable
START = datetime(2026, 9, 1, 9, 0, tzinfo=timezone.utc)


@dataclass(frozen=True)
class Params:
    requirements: int = 1
    criteria_per_requirement: int = 3
    planned: int = 2          # criteria the plan exercises; the rest stay uncovered
    sessions: int = 1
    turns: int | None = None   # turns per session; None applies every probe once
    populations: int = 2      # the first is interviewed, the others represented
    judgments: tuple = (("failed", "sufficient", "appropriate"), ("passed", "sufficient", "appropriate"))   # (outcome, sufficiency, appropriateness), cycled over the covered criteria (sheet 10-12)


PARAM_NAMES = {"requirements": "requirements", "criteria": "criteria_per_requirement", "planned": "planned", "sessions": "sessions", "populations": "populations"}


def params_of(**given: int) -> Params:
    """A Params from the command line's names (criteria is criteria_per_requirement); unspecified ones keep their defaults."""
    return Params(**{PARAM_NAMES[k]: v for k, v in given.items()})


def params_dict(p: Params) -> dict:
    """The parameters under the command line's names, in the order printed."""
    return {k: getattr(p, f) for k, f in PARAM_NAMES.items()}


CAP_CRITERIA = 100   # requirements times criteria
CAP_SESSIONS = 20
CAP_WORK = 100       # requirements times criteria times sessions: every criterion is probed in every session, and the checks are quadratic in that work (100 runs in about a minute)
CAP_POPULATIONS = 20
CAP_NOTE = (f"capped: requirements times criteria at most {CAP_CRITERIA}, sessions at most {CAP_SESSIONS}, requirements times criteria times sessions at most {CAP_WORK}, "
            f"populations at most {CAP_POPULATIONS} (every criterion is probed in every session and the checks are quadratic in that work; over a cap, exit 1 with the reason and no run)")


def validate(p: Params) -> str | None:
    """The reason a Params cannot be run, or None: every count a positive
    integer, the planned criteria at most the criteria that exist, and the
    caps held (requirements times criteria, sessions, populations)."""
    for k, f in PARAM_NAMES.items():
        v = getattr(p, f)
        if not isinstance(v, int) or isinstance(v, bool) or v < 1:
            return f"{k} must be a positive integer (got {v!r})"
    total = p.requirements * p.criteria_per_requirement
    if total > CAP_CRITERIA:
        return f"requirements times criteria must be at most {CAP_CRITERIA} ({p.requirements} x {p.criteria_per_requirement} = {total}): the checks are quadratic in the criteria"
    if p.sessions > CAP_SESSIONS:
        return f"sessions must be at most {CAP_SESSIONS} (got {p.sessions}): the checks are quadratic in the sessions"
    if total * p.sessions > CAP_WORK:
        return f"requirements times criteria times sessions must be at most {CAP_WORK} ({p.requirements} x {p.criteria_per_requirement} x {p.sessions} = {total * p.sessions}): every criterion is probed in every session and the checks are quadratic in that work"
    if p.populations > CAP_POPULATIONS:
        return f"populations must be at most {CAP_POPULATIONS} (got {p.populations})"
    if p.planned > total:
        return f"planned must be at most requirements times criteria ({p.requirements} x {p.criteria_per_requirement} = {total}; got planned {p.planned})"
    return None


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
        member(self.g, n)
        return n


def member(g: Graph, n):
    """Every item and agent is a member of the record, the bundle, and is tagged synthetic (sheets 10-31, 10-43)."""
    g.add((n, OGC.inRecord, RECORD)); g.add((n, OGC.synthetic, Literal(True)))


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
    g.add((RECORD, RDF.type, PROV.Entity)); g.add((RECORD, RDF.type, PROV.Bundle)); g.add((RECORD, RDFS.label, Literal("the executed evaluation")))
    g.add((RECORD, EPO.independenceLevel, EPO.person)); g.add((RECORD, OGC.synthetic, Literal(True)))  # the bundle, at independence level person (sheets 10-15, 10-31, 10-43)
    def agent(tag, label, *types, **props):
        n = RUN[tag]
        for t in (PROV.Agent, *types):
            g.add((n, RDF.type, t))
        g.add((n, RDFS.label, Literal(label)))
        for k, v in props.items():
            g.add((n, EPO[k] if k not in ("actedOnBehalfOf",) else PROV[k], v))
        member(g, n)
        return n
    a = r.agents
    a["SponsorOrganization"] = agent("sponsor", "sponsor organization", PROV.Organization, role=EPO.sponsorRole, providesTestItem=Literal(False))
    a["AccountableOrganization"] = agent("accountable", "test item provider", PROV.Organization, role=EPO.accountableOrganizationRole, providesTestItem=Literal(True))
    a["TestingOrganization"] = agent("testing-org", "testing organization", PROV.Organization, role=EPO.testingOrganizationRole)
    a["SponsorSignatory"] = agent("signatory", "sponsor signatory", PROV.Person, role=EPO.sponsorSignatoryRole, actedOnBehalfOf=a["SponsorOrganization"])  # sheet 10-06
    a["AccountExecutive"] = agent("executive", "authorized representative", PROV.Person, role=EPO.accountExecutiveRole, actedOnBehalfOf=a["TestingOrganization"])
    a["DomainExpert"] = agent("expert", "domain expert", PROV.Person, role=EPO.domainExpertRole, actedOnBehalfOf=a["TestingOrganization"])
    a["EvaluationOperator"] = agent("operator", "evaluation operator", PROV.Person, role=EPO.evaluationOperatorRole, actedOnBehalfOf=a["TestingOrganization"])
    a["TestItem"] = agent("test-item", "test item", PROV.SoftwareAgent, EARL.TestSubject, version=Literal("1"), actedOnBehalfOf=a["AccountableOrganization"])
    a["TestDriver"] = agent("test-driver", "test driver", PROV.SoftwareAgent, version=Literal("1"), actedOnBehalfOf=a["TestingOrganization"])
    a["ConformanceChecker"] = agent("checker", "conformance checker", PROV.SoftwareAgent, version=Literal("1"), actedOnBehalfOf=a["TestingOrganization"])
    a["ReportAssembler"] = agent("assembler", "report assembler", PROV.SoftwareAgent, version=Literal("1"), actedOnBehalfOf=a["TestingOrganization"])
    a["Representative"] = a["DomainExpert"]  # a domain expert may be a representative; the operator represents the interviewed population
    a["AffectedPopulation"] = []
    for i in range(params.populations):
        p = agent(f"population-{i + 1}", f"affected population {i + 1}", EPO.Population)
        if i > 0:
            g.add((p, EPO.representedBy, a["DomainExpert"]))  # who speaks for a represented population (sheet 10-13)
        else:
            g.add((p, EPO.representedBy, a["EvaluationOperator"])); g.add((p, EPO.responsibleParty, a["EvaluationOperator"]))  # who speaks for and who engaged the interviewed population (S0-Population, sheets 08, 10-13)
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
    g.add((m, RDFS.label, Literal("the sponsor's purpose and its obligations towards the affected populations"))); by(r, m, "Mission")
    n = r.new("Need", "need", i, 1)
    g.add((n, EPO.underMission, m)); g.add((n, RDFS.label, Literal("the sponsor's stated need"))); by(r, n, "Need")
    return {"Mission", "Need"}


def t_propose(r, i, p):
    n = r.new("Proposal", "proposal", i)
    r.g.add((n, EPO.respondsTo, r.items["Need"][0])); r.g.add((n, RDFS.label, Literal("the provider's proposal"))); by(r, n, "Proposal")
    return {"Proposal"}


def t_agree(r, i, p):
    g = r.g
    n = r.new("ServiceAgreement", "agreement", i)
    g.add((n, EPO.signedBy, r.agents["SponsorSignatory"])); g.add((n, EPO.signedBy, r.agents["AccountExecutive"]))  # two persons sign, each for their organization (sheet 10-06)
    g.add((n, EPO.accepts, r.items["Proposal"][0])); g.add((n, RDFS.label, Literal("the service agreement; accepts the proposal")))  # sheet 10-05
    sow = r.new("StatementOfWork", "statement-of-work", i)  # dated with the agreement it is under (sheet 10-05)
    g.add((sow, EPO.underAgreement, n)); g.add((sow, RDFS.label, Literal("the scope of work: the first population interviewed, the others represented"))); by(r, sow, "StatementOfWork")
    for k, pop in enumerate(r.agents["AffectedPopulation"]):
        d = RUN[f"engagement-{k + 1}"]
        g.add((d, RDF.type, EPO.EngagementDecision)); g.add((d, EPO.population, pop)); member(g, d)
        g.add((d, EPO.engagement, EPO.interview if k == 0 else EPO.representation)); g.add((sow, EPO.decides, d))
    ind = r.new("IndependenceDeclaration", "independence-declaration", i, 1)  # sheet 10-07
    g.add((ind, EPO.independentOf, r.agents["AccountableOrganization"])); g.add((ind, RDFS.label, Literal("the testing organization declares itself independent of the test item provider"))); by(r, ind, "IndependenceDeclaration")
    ui = r.new("UserInterestDeclaration", "user-interest-declaration", i, 1)
    g.add((ui, EPO.hasUserInterest, Literal(True))); g.add((ui, RDFS.label, Literal("the sponsor declares its user interest in the test item"))); by(r, ui, "UserInterestDeclaration")
    return {"ServiceAgreement", "StatementOfWork", "IndependenceDeclaration", "UserInterestDeclaration"}


def t_access(r, i, p):
    n = r.new("TestItemAccess", "access", i)
    g = r.g
    g.add((n, EPO.grantsAccessTo, r.agents["TestItem"])); g.add((n, EPO.underAgreement, r.items["ServiceAgreement"][0])); by(r, n, "TestItemAccess")
    g.add((n, EPO.versionIdentity, Literal("test item, version 1"))); g.add((n, EPO.accessFrom, r.at(i))); g.add((n, EPO.accessUntil, r.at(i + 30)))  # sheet 10-04
    g.add((n, EPO.underInstrument, Literal("the provider's own instrument with the sponsor, outside this agreement"))); g.add((n, EPO.environment, Literal("the provider's test environment")))
    return {"TestItemAccess"}


def t_scope(r, i, p):
    g = r.g
    for k, pop in enumerate(r.agents["AffectedPopulation"]):
        rep = r.new("StakeholderRepresentation", "representation", i, 2 * k + 1)
        g.add((rep, EPO.represents, pop)); g.add((rep, RDFS.label, Literal(f"population {k + 1}, spoken for")))
        if k == 0:  # the interviewed population: its interview feeds the representation (series wiring, R-49)
            s = r.new("StakeholderInput", "input", i, 2 * k)
            g.add((s, PROV.wasAttributedTo, pop)); g.add((s, RDFS.label, Literal("interview notes")))
            g.add((rep, PROV.used, s)); g.add((rep, PROV.wasAttributedTo, r.agents["EvaluationOperator"]))
        else:
            g.add((rep, PROV.wasAttributedTo, r.agents["DomainExpert"]))
    d = r.new("DsoRelease", "dso", i, 2 * len(r.agents["AffectedPopulation"]) + 1)
    g.add((d, EPO.version, Literal("r1"))); g.add((d, EPO.approvedBy, r.agents["DomainExpert"])); by(r, d, "DsoRelease")
    return {"StakeholderInput", "StakeholderRepresentation", "DsoRelease"}


def t_declare(r, i, p):
    g = r.g
    rs = r.new("RequirementSet", "requirements", i)
    g.add((rs, EPO.environment, Literal("the declared operational environment"))); g.add((rs, EPO.systemUnderTest, r.agents["TestItem"]))
    g.add((rs, EPO.underAgreement, r.items["ServiceAgreement"][0])); by(r, rs, "RequirementSet")  # the operator's alone (sheet 10-15)
    for q in range(p.requirements):
        req = r.new("Requirement", "requirement", i, 0, timed="")
        g.add((req, EPO.partOf, rs)); g.add((req, EPO.text, Literal(f"requirement {q + 1}")))
        for c in range(p.criteria_per_requirement):
            a = r.new("AcceptanceCriterion", "criterion", i)  # dated, with its weight's rationale (sheet 10-10); no threshold
            g.add((a, PROV.wasDerivedFrom, req)); g.add((a, EPO.text, Literal(f"criterion {q + 1}.{c + 1}")))
            g.add((a, EPO.expectedResult, Literal(f"expected result {q + 1}.{c + 1}"))); g.add((a, EPO.weight, Literal(1))); g.add((a, EPO.weightRationale, Literal("every criterion weighs the same in this run")))
    ass = r.new("AppropriatenessAssessment", "assessment", i, 1, timed="endedAtTime")
    g.add((ass, EARL.subject, rs)); g.add((ass, EARL.mode, EARL.manual)); g.add((ass, EARL.assertedBy, r.agents["DomainExpert"]))
    g.add((ass, PROV.used, r.items["StakeholderInput"][0])); g.add((ass, EPO.appropriateness, EPO.appropriate))
    result(g, ass, "passed")
    ap = r.new("RequirementSetApproval", "requirement-set-approval", i, 2)  # the sponsor's signatory approves, after the set and before any session (sheet 10-01)
    g.add((ap, EPO.approvesRequirementSet, rs)); g.add((ap, RDFS.label, Literal("the sponsor's signatory approves the requirement set"))); by(r, ap, "RequirementSetApproval")
    return {"RequirementSet", "AcceptanceCriterion", "AppropriatenessAssessment", "RequirementSetApproval"}


def t_plan(r, i, p):
    g = r.g
    dso, rs = r.items["DsoRelease"][0], r.items["RequirementSet"][0]
    der = r.new("ProbeDerivation", "derivation", i, 0, timed="endedAtTime")
    g.add((der, PROV.used, dso)); g.add((der, PROV.used, rs)); g.add((der, PROV.wasAssociatedWith, r.agents["TestDriver"]))
    plan = r.new("TestPlan", "plan", i, 1)
    g.add((plan, PROV.wasDerivedFrom, rs)); g.add((plan, PROV.wasDerivedFrom, dso)); g.add((plan, PROV.wasGeneratedBy, der)); by(r, plan, "TestPlan")
    covered = r.items["AcceptanceCriterion"][:p.planned]
    for a in r.items["AcceptanceCriterion"][p.planned:]:  # every criterion left unplanned has its deviation, the operator's, with a reason (sheet 10-16)
        dev = r.new("PlanDeviation", "plan-deviation", i, 2)
        g.add((dev, EPO.deviatesFrom, plan)); g.add((dev, EPO.concerns, a)); g.add((dev, EPO.reason, Literal("left unplanned in this run"))); by(r, dev, "PlanDeviation")
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
    g.add((ap, PROV.wasAssociatedWith, r.agents["DomainExpert"])); result(g, ap, "passed")
    return {"TestPlan", "Probe", "PlanApproval", "PlanDeviation"}


def t_execute(r, i, p):
    g = r.g
    plan = r.items["TestPlan"][0]
    probes = r.items["Probe"]
    for s in range(p.sessions):
        ses = r.new("Session", "session", i, s, timed="startedAtTime")
        g.add((ses, PROV.wasAssociatedWith, r.agents["TestItem"])); g.add((ses, PROV.wasAssociatedWith, r.agents["EvaluationOperator"]))
        g.add((ses, PROV.endedAtTime, r.at(i, s + 1)))
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
    determiners = r.supplier["Determination"]  # DomainExpert, EvaluationOperator: either may determine (R-21)
    for k, a in enumerate(covered):
        evs = [e for e in r.items["Evidence"] if (e, EPO.bearsOn, a) in g]
        outcome, sufficiency, appropriateness = p.judgments[k % len(p.judgments)]
        determined = outcome if outcome in ("passed", "failed", "cantTell") else "cantTell"  # a determination never says inapplicable
        who = r.agents[determiners[k % len(determiners)]]
        dets = []
        for j, person in enumerate([who] if who is r.agents["DomainExpert"] else [who, r.agents["DomainExpert"]]):
            # the operator ran the session the evidence came from, so the operator's determination is paired with the expert's (independence at the person level, sheet 10-15)
            det = r.new("Determination", "determination", i, 2 * k + j, timed="endedAtTime")
            g.add((det, EARL.test, a)); g.add((det, EARL.subject, r.agents["TestItem"])); g.add((det, EARL.mode, EARL.manual)); g.add((det, EARL.assertedBy, person))
            g.add((det, PROV.wasAssociatedWith, person))
            for e in evs:
                g.add((det, PROV.used, e))
            result(g, det, determined)
            dets.append(det)
        att = r.new("Attestation", "attestation", i, 2 * k + 2, timed="endedAtTime")
        g.add((att, EARL.test, a)); g.add((att, EARL.subject, r.agents["TestItem"])); g.add((att, EARL.mode, EARL.manual)); g.add((att, EARL.assertedBy, r.agents["DomainExpert"]))
        g.add((att, PROV.wasAssociatedWith, r.agents["DomainExpert"])); g.add((att, EPO.appropriateness, EPO[appropriateness])); g.add((att, EPO.sufficiency, EPO[sufficiency]))
        for det in dets:  # every determination on the criterion (no cherry-picking, sheet 10-14)
            g.add((att, PROV.used, det))
        result(g, att, outcome)
    return {"Determination", "Attestation"}


def t_report(r, i, p):
    """The report step opened (sheet 10-41): the checker's verdict on the record first, then the coverage computation that used it,
    the final report resting on it, the domain expert's approval, and the recommendation the approval owns (sheet 10-11)."""
    g = r.g
    from .graph import digests
    dg = digests(views_root())  # what the checker and the assembler ran, by sha256 (sheet 10-18)
    ok, fired = conformance(g, *_checker_graphs())  # the verdict is the checker's own finding on the record so far, never a constant (sheet 10-19)
    ver = r.new("ConformanceVerdict", "verdict", i, 0, timed="endedAtTime")
    g.add((ver, EARL.subject, RECORD)); g.add((ver, EARL.mode, EARL.automatic)); g.add((ver, EARL.assertedBy, r.agents["ConformanceChecker"]))
    g.add((ver, PROV.wasAssociatedWith, r.agents["ConformanceChecker"])); g.add((ver, PROV.used, RECORD))
    for k, v in dg.items():
        g.add((ver, EPO[k], Literal(v)))
    result(g, ver, "passed" if ok else "failed", info="the record conforms to the EPO shapes" if ok else "the record fails " + ", ".join(fired))
    comp = r.new("CoverageComputation", "coverage", i, 1, timed="endedAtTime")
    g.add((comp, PROV.used, r.items["RequirementSet"][0])); g.add((comp, PROV.used, ver)); g.add((comp, PROV.wasAssociatedWith, r.agents["ReportAssembler"])); g.add((comp, EARL.mode, EARL.automatic))
    for k, v in dg.items():
        g.add((comp, EPO[k], Literal(v)))
    for att in r.items["Attestation"]:
        g.add((comp, PROV.used, att))
    rep = r.new("Report", "report", i, 1)
    g.add((rep, PROV.wasGeneratedBy, comp)); g.add((rep, PROV.used, ver)); g.add((rep, EPO.draft, Literal(False)))  # final: it rests on the verdict
    row = next(iter(g.query((views_root() / "queries" / "coverage.rq").read_text())))
    for k in ("coverage", "passRate", "failRate", "cantTellRate"):
        g.add((rep, EPO[k], Literal(round(float(getattr(row, k)), 6))))
    ap = r.new("ReportApproval", "report-approval", i, 2, timed="endedAtTime")
    g.add((ap, EPO.approvesReport, rep)); g.add((ap, EARL.subject, rep)); g.add((ap, EARL.mode, EARL.manual)); g.add((ap, EARL.assertedBy, r.agents["DomainExpert"]))
    g.add((ap, PROV.wasAssociatedWith, r.agents["DomainExpert"])); g.add((ap, PROV.used, rep)); g.add((ap, PROV.used, ver)); result(g, ap, "passed")
    rec = r.new("Recommendation", "recommendation", i, 3)
    g.add((rec, EPO.text, Literal("the recommendation"))); by(r, rec, "Recommendation")
    g.add((rec, PROV.wasDerivedFrom, ap))  # the approval owns the recommendation (sheet 10-11)
    for att in r.items["Attestation"]:
        g.add((rec, PROV.wasDerivedFrom, att))
        for det in g.objects(att, PROV.used):
            for e in g.objects(det, PROV.used):
                g.add((rec, PROV.wasDerivedFrom, e))
    g.add((rec, PROV.wasDerivedFrom, r.items["TestPlan"][0])); g.add((rec, PROV.wasDerivedFrom, r.items["DsoRelease"][0])); g.add((rec, PROV.wasDerivedFrom, rep))
    return {"ConformanceVerdict", "Report", "ReportApproval", "Recommendation", "PlanDeviation"}


def t_deliver(r, i, p):
    d = r.new("Delivery", "delivery", i)
    g = r.g
    g.add((d, PROV.wasDerivedFrom, r.items["Report"][0])); g.add((d, PROV.wasDerivedFrom, r.items["Recommendation"][0])); g.add((d, PROV.wasDerivedFrom, r.items["ReportApproval"][0]))
    g.add((d, EPO.deliveredTo, r.agents["SponsorOrganization"])); g.add((d, EPO.underAgreement, r.items["ServiceAgreement"][0])); by(r, d, "Delivery")
    return {"Delivery"}


def t_accept(r, i, p):
    a = r.new("Acceptance", "acceptance", i)
    r.g.add((a, EPO.accepts, r.items["Delivery"][0])); by(r, a, "Acceptance")  # the signatory's act on receipt (sheets 10-03, 10-06)
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
    for k, v in (("epo", EPO), ("ogc", OGC), ("prov", PROV), ("earl", EARL), ("ex", RUN), ("rdfs", RDFS), ("xsd", XSD)):
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


def m_skip_report_approval(g):
    """The report is delivered without a domain expert's approval of its contents: correctly constructed, unsigned."""
    for a in list(g.subjects(RDF.type, EPO.ReportApproval)):
        g.remove((a, None, None)); g.remove((None, None, a))


def m_pad_pass_rate(g):
    """The report's stored rates are padded to a full pass while the attestations stand: the rates are recomputed by S7 (SCI-08, sheet 10-19)."""
    for rep in list(g.subjects(RDF.type, EPO.Report)):
        for k in (EPO.passRate, EPO.failRate, EPO.cantTellRate):
            g.remove((rep, k, None))
        g.add((rep, EPO.passRate, Literal(1.0))); g.add((rep, EPO.failRate, Literal(0.0))); g.add((rep, EPO.cantTellRate, Literal(0.0)))


def m_one_person_team(g):
    """The domain expert also holds the evaluation operator's role: one person judges what the same person tested (S0-Roles, sheet 10-13)."""
    ex = next(g.subjects(EPO.role, EPO.domainExpertRole))
    g.add((ex, EPO.role, EPO.evaluationOperatorRole))


def m_cherry_pick(g):
    """Every attestation that aggregates two determinations drops the later one without naming it as excluded (S6-Attestation, sheet 10-14)."""
    for a in g.subjects(RDF.type, EPO.Attestation):
        dets = sorted(g.objects(a, PROV.used), key=str)
        if len(dets) > 1:
            g.remove((a, PROV.used, dets[-1]))


def m_engagement_mismatch(g):
    """The statement of work is made to decide an interview for a population the record only speaks for: a representation-only decision is flipped to interview, or, with a single population, its interview is struck from the record while the decision stands (series wiring, R-49)."""
    reps = [d for d in g.subjects(RDF.type, EPO.EngagementDecision) if (d, EPO.engagement, EPO.representation) in g]
    if reps:
        g.remove((reps[0], EPO.engagement, None)); g.add((reps[0], EPO.engagement, EPO.interview))
        return
    for s in list(g.subjects(RDF.type, EPO.StakeholderInput)):
        g.remove((s, None, None)); g.remove((None, None, s))


MUTATIONS = {
    "skip-assessment": ("skip the appropriateness assessment (a step's output missing)", m_skip_assessment),
    "skip-approval": ("skip the plan approval", m_skip_approval),
    "skip-access": ("skip the access grant (a contracting step missing)", m_skip_access),
    "unwire-evidence": ("cut the wire binding evidence to its plan", m_unwire_evidence),
    "executive-attests": ("the authorized representative attests instead of the domain expert", m_executive_attests),
    "attest-without-determination": ("attestations aggregate no determination", m_attest_without_determination),
    "requirements-before-agreement": ("the requirement set dated before the agreement", m_requirements_before_agreement),
    "engagement-mismatch": ("the statement of work decides an interview for a population the record only speaks for", m_engagement_mismatch),
    "skip-report-approval": ("the report delivered without a domain expert's approval of its contents", m_skip_report_approval),
    "pad-pass-rate": ("the report's pass rate padded to one while every attestation stands", m_pad_pass_rate),
    "one-person-team": ("the domain expert also holds the evaluation operator's role", m_one_person_team),  # sheet 10-13
    "cherry-pick": ("an attestation drops one of its determinations without saying why", m_cherry_pick),  # sheet 10-14
}


# --- the checks ---------------------------------------------------------------

_CHECKER: tuple[Graph, Graph, Graph] | None = None


def _checker_graphs() -> tuple[Graph, Graph, Graph]:
    """The shapes, the ontology and the model graph the run's own conformance checker reads, loaded once (the step is derived through the model, sheet 10-33)."""
    global _CHECKER
    if _CHECKER is None:
        root = views_root()
        _CHECKER = (Graph().parse(root / "shapes" / "epo.shapes.ttl"), Graph().parse(root / "vocabulary" / "epo.ttl"), Graph().parse(root / "model" / "og-caie.model.ttl"))
    return _CHECKER


def _data(record: Graph, *others: Graph) -> Graph:
    """One default graph: the record with the vocabulary and the model graph (the shapes' and the queries' precondition, sheet 10-31)."""
    data = Graph()
    for g in (record, *others):
        for t in g:
            data.add(t)
    return data


def conformance(record: Graph, shapes: Graph, epo: Graph, model: Graph | None = None) -> tuple[bool, list[str]]:
    from pyshacl import validate
    data = _data(record, epo, model if model is not None else _checker_graphs()[2])
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
    row = next(iter(_data(record, epo).query((views_root() / "queries" / "coverage.rq").read_text())))
    return {k: round(float(getattr(row, k)), 4) for k in ("coverage", "passRate", "failRate", "cantTellRate")}


def traceback_rows(record: Graph, epo: Graph, model: Graph) -> int:
    return len(list(_data(record, epo, model).query((views_root() / "queries" / "traceback.rq").read_text())))


def check(record: Graph, model: Graph, shapes: Graph, epo: Graph) -> dict:
    ok, fired = conformance(record, shapes, epo, model)
    return {"conforms": ok, "fired": fired, "missing": completeness(record, model), "coverage": coverage(record, epo), "traceback": traceback_rows(record, epo, model)}


VARIANTS = {
    "planned 2 of 3": Params(),
    "planned 3 of 3": Params(planned=3),
    "two sessions, two requirements": Params(requirements=2, criteria_per_requirement=2, planned=4, sessions=2),
    "the five judgments": Params(criteria_per_requirement=5, planned=5, judgments=JUDGMENTS_ALLOWED),  # sheet 10-12: every combination S6 allows, one criterion each
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
