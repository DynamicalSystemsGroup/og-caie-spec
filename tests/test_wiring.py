"""The assemblage is fully wired, read from the canonical model graph:
every seam resolves to two existing ports of matching conjugated types,
every port of every part is an end of exactly one seam, every item kind
reaches the recorder, and the three actor categories share no supplier
port definition (R-10, R-23)."""
from collections import Counter

from rdflib import RDF

from conftest import load
from test_model_graph import OGM, SYS

SEAMS = 35
PORTS = 59


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


def test_inputs_unique_outputs_shared():
    """R-25: every input port is the end of exactly one seam; every output
    port of at least one, and may feed several consumers because what flows
    is information, whose use is nondestructive."""
    g = graph()
    ports = [p for p in g.subjects(RDF.type, SYS.PortUsage) if g.value(p, SYS.isEnd) is None]
    assert len(ports) == PORTS
    used = Counter(g.objects(None, OGM.resolvesTo))
    shared = []
    for p in ports:
        label = f"{name(g, g.value(p, SYS.owner))}.{name(g, p)}"
        if g.value(p, SYS.isConjugated):
            assert used[p] == 1, f"input {label} wired {used[p]} times"
        else:
            assert used[p] >= 1, f"output {label} unwired"
            if used[p] > 1:
                shared.append((label, used[p]))
    assert sum(used.values()) == 2 * SEAMS
    assert sorted(shared) == [("AccountExecutive.deliveryOut", 2), ("AccountExecutive.proposalOut", 2), ("ProbeDeriver.probesOut", 2),
                              ("Recorder.recordOut", 6), ("SponsorOrganization.acceptanceOut", 2), ("SponsorOrganization.missionOut", 2), ("SponsorOrganization.needOut", 2)]


def test_every_item_kind_reaches_the_recorder():
    g = graph()
    recorder = next(d for d in g.subjects(RDF.type, SYS.PartDefinition) if name(g, d) == "Recorder")
    received = {g.value(p, SYS.type) for p in g.subjects(SYS.owner, recorder) if g.value(p, SYS.isConjugated)}
    kinds = {d for d in g.subjects(RDF.type, SYS.PortDefinition) if name(g, d) != "RecordWrite"}
    assert kinds <= received, sorted(name(g, k) for k in kinds - received)


def test_actor_categories_share_no_supplier_port_definition():
    """Actors perform activities; activities have precise outputs (R-24).
    The one activity two actor categories may both perform is determining
    on evidence (R-21: the domain expert may interpret evidence), so
    DeterminationWrite is the only supplier port definition two roles carry.
    Delivery is its own activity with its own output, not a reuse of the
    operator's recommendation port."""
    g = graph()
    roles = {"DomainExpert", "EvaluationOperator", "AccountExecutive"}
    shared_by_design = {d for d in g.subjects(RDF.type, SYS.PortDefinition) if name(g, d) == "DeterminationWrite"}
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
