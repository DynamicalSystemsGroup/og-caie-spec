"""The assemblage is fully wired, read from the canonical model graph:
every seam resolves to two existing ports of matching conjugated types,
every port of every part is an end of exactly one seam, every item kind
reaches the recorder, and the three actor categories share no supplier
port definition (R-10, R-23)."""
from collections import Counter

from rdflib import RDF

from conftest import load
from test_model_graph import OGM, SYS

SEAMS = 27
PORTS = 54


def graph():
    return load("model/og-caie.model.ttl")


def name(g, n):
    return str(g.value(n, SYS.declaredName))


def test_seams_resolve_to_conjugate_pairs():
    g = graph()
    seams = list(g.subjects(RDF.type, SYS.InterfaceUsage))
    assert len(seams) == SEAMS
    for s in seams:
        sp, cp = g.value(s, OGM.supplierPort), g.value(s, OGM.consumerPort)
        assert sp is not None and cp is not None, name(g, s)
        assert g.value(sp, SYS.type) == g.value(cp, SYS.type), name(g, s)
        assert g.value(sp, SYS.isConjugated) is None and bool(g.value(cp, SYS.isConjugated))


def test_every_part_port_connected_exactly_once():
    g = graph()
    ports = [p for p in g.subjects(RDF.type, SYS.PortUsage) if g.value(p, SYS.isEnd) is None]
    assert len(ports) == PORTS
    used = Counter(g.objects(None, OGM.resolvesTo))
    for p in ports:
        assert used[p] == 1, f"{name(g, g.value(p, SYS.owner))}.{name(g, p)} connected {used[p]} times"
    assert sum(used.values()) == 2 * SEAMS


def test_every_item_kind_reaches_the_recorder():
    g = graph()
    recorder = next(d for d in g.subjects(RDF.type, SYS.PartDefinition) if name(g, d) == "Recorder")
    received = {g.value(p, SYS.type) for p in g.subjects(SYS.owner, recorder) if g.value(p, SYS.isConjugated)}
    kinds = {d for d in g.subjects(RDF.type, SYS.PortDefinition) if name(g, d) != "RecordWrite"}
    assert kinds <= received, sorted(name(g, k) for k in kinds - received)


def test_actor_categories_share_no_supplier_port_definition():
    """Two shares are by design: both experts may make determinations (R-21:
    the domain expert may interpret evidence), and the recommendation the
    operator writes is delivered to the sponsor by the account executive
    (R-23). Everything else belongs to one slot."""
    g = graph()
    roles = {"DomainExpert", "EvaluationOperator", "AccountExecutive"}
    shared_by_design = {d for d in g.subjects(RDF.type, SYS.PortDefinition) if name(g, d) in ("DeterminationWrite", "RecommendationWrite")}
    supplied = {}
    for d in g.subjects(RDF.type, SYS.PartDefinition):
        if name(g, d) in roles:
            supplied[name(g, d)] = {g.value(p, SYS.type) for p in g.subjects(SYS.owner, d)
                                    if (p, RDF.type, SYS.PortUsage) in g and g.value(p, SYS.isConjugated) is None}
    assert set(supplied) == roles
    for a in roles:
        for b in roles:
            if a < b:
                assert (supplied[a] & supplied[b]) <= shared_by_design, (a, b, supplied[a] & supplied[b])


def test_parties_and_roles_present():
    g = graph()
    defs = {name(g, d): d for d in g.subjects(RDF.type, SYS.PartDefinition)}
    assembly = defs["OgCaieEvaluation"]
    typed = {name(g, g.value(u, SYS.type)) for u in g.subjects(SYS.owner, assembly) if (u, RDF.type, SYS.PartUsage) in g}
    assert typed == {"SponsorOrganization", "TestingOrganization", "AccountableOrganization", "AffectedPopulation"}
    org = defs["TestingOrganization"]
    held = {name(g, g.value(u, SYS.type)) for u in g.subjects(SYS.owner, org) if (u, RDF.type, SYS.PartUsage) in g}
    assert {"AccountExecutive", "EvaluationTeam", "Recorder", "ProbeDeriver", "ConformanceChecker", "CoverageCalculator"} <= held
