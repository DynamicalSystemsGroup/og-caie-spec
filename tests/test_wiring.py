"""The assemblage is fully wired, read from the canonical model graph:
every seam resolves to two existing ports of matching conjugated types,
every port of every part is an end of exactly one seam, every item kind
reaches the recorder, and the three actor categories share no supplier
port definition (R-10, R-23)."""
from collections import Counter

from rdflib import RDF

from conftest import load
from ogc import views
from test_model_graph import OGM, SYS

SEAMS = 44  # R-49 B3: 39; R-50 (sheet 10): the two declarations, the requirement-set approval, the plan deviation, the verdict to the assembler
PORTS = 76  # R-50: the signatory's four (three moved off the sponsor organization), the executive's declaration, the operator's deviation, the assembler's verdict, the recorder's four


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
    assert sorted(shared) == sorted([("AuthorizedRepresentative.deliveryOut", 2), ("AuthorizedRepresentative.proposalOut", 2), ("AccountableOrganization.accessOut", 2), ("AffectedPopulation.inputOut", 2),
                              ("ConformanceChecker.verdictOut", 2),  # sheet 10-41: the recorder and the assembler read the verdict
                              ("Recorder.recordOut", 3), ("SponsorOrganization.missionOut", 2), ("SponsorOrganization.needOut", 2), ("SponsorOrganization.statementOfWorkOut", 2),
                              ("SponsorSignatory.acceptanceOut", 2),  # sheet 10-06: the acceptance is the signatory's
                              ("TestDriver.probesOut", 2)])  # sorted on both sides: the rename of 10-49 reordered the names


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
    roles = {"DomainExpert", "EvaluationOperator", "AuthorizedRepresentative"}
    shared_by_design = {d for d in g.subjects(RDF.type, SYS.PortDefinition) if name(g, d) == "DeterminationWrite"}
    supplied = {}
    for d in g.subjects(RDF.type, SYS.PartDefinition):
        if name(g, d) in roles | {"SponsorSignatory"}:
            supplied[name(g, d)] = {g.value(p, SYS.type) for p in g.subjects(SYS.owner, d)
                                    if (p, RDF.type, SYS.PortUsage) in g and g.value(p, SYS.isConjugated) is None}
    assert set(supplied) == roles | {"SponsorSignatory"}
    for a in roles:
        for b in roles:
            if a < b:
                assert (supplied[a] & supplied[b]) <= shared_by_design, (a, b, supplied[a] & supplied[b])
    # sheet 10-06: the sponsor's signatory, a person on the other side of the contract, shares one supplier port
    # definition with the authorized representative, the agreement both sign, and nothing with the two experts
    agreement = {d for d in g.subjects(RDF.type, SYS.PortDefinition) if name(g, d) == "AgreementWrite"}
    assert supplied["SponsorSignatory"] & supplied["AuthorizedRepresentative"] == agreement
    assert not (supplied["SponsorSignatory"] & (supplied["DomainExpert"] | supplied["EvaluationOperator"]))


def test_parties_and_roles_present():
    g = graph()
    defs = {name(g, d): d for d in g.subjects(RDF.type, SYS.PartDefinition)}
    assembly = defs["OgCaieEvaluation"]
    typed = {name(g, g.value(u, SYS.type)) for u in g.subjects(SYS.owner, assembly) if (u, RDF.type, SYS.PartUsage) in g}
    assert typed == {"SponsorOrganization", "TestingOrganization", "AccountableOrganization", "AffectedPopulation"}
    org = defs["TestingOrganization"]
    held = {name(g, g.value(u, SYS.type)) for u in g.subjects(SYS.owner, org) if (u, RDF.type, SYS.PartUsage) in g}
    assert {"AuthorizedRepresentative", "EvaluationTeam", "Recorder", "TestDriver", "ConformanceChecker", "ReportAssembler"} <= held
    sponsor = defs["SponsorOrganization"]  # sheet 10-06: the sponsor holds its signatory, a person
    assert {name(g, g.value(u, SYS.type)) for u in g.subjects(SYS.owner, sponsor) if (u, RDF.type, SYS.PartUsage) in g} == {"SponsorSignatory"}
    assert name(g, g.value(defs["SponsorSignatory"], SYS.specializes)) == "Person"


def test_obligation_relates_sponsor_to_populations():
    """R-38: the sponsor's obligation towards the affected populations is a
    relation in the assembly, from the sponsor part to the affected part,
    carrying no item; the mission regards one or more populations."""
    g = graph()
    rels = views.relations(g)
    assert [(dname, name(g, a), name(g, b)) for _, dname, (a, b) in rels] == [("Obligation", "sponsor", "affected")]
    mission = next(d for d in g.subjects(RDF.type, SYS.ItemDefinition) if name(g, d) == "Mission")
    regards = next(u for u in g.subjects(SYS.owner, mission) if (u, RDF.type, SYS.PartUsage) in g)
    assert name(g, g.value(regards, SYS.type)) == "AffectedPopulation"


def test_views_have_perspectives_and_cover_every_seam():
    """R-38: every view documents what it brings into focus and what it
    leaves out; the two slice views together draw every seam, and a bundle
    between two parts names every item kind that flows between them."""
    g = graph()
    for v in views.VIEWS.values():
        assert v.focus.endswith(".") and v.leaves_out.endswith("."), v.name
        assert v.render(g).startswith("flowchart")
    drawn = {name(g, s) for sl in ("contracting", "evaluation") for s in views.seams(g, sl)}
    assert drawn == {name(g, s) for s in views.seams(g)}
    contracting = views.wiring(g, "contracting")
    assert 'sponsor -- "Mission, Need, StatementOfWork" --> testingOrg_authorizedRepresentative' in contracting  # sheet 10-06: what the organization sends
    assert 'sponsor_signatory -- "ServiceAgreement, Acceptance" --> testingOrg_authorizedRepresentative' in contracting  # and what its signatory signs
    assert 'sponsor -. "obligation" .-> affected' in contracting
