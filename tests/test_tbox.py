"""The terminological box after the audit (rulings sheet 08, on Z's
instruction under R-48): every concept is connected to another by a SKOS
relation, every broader has its narrower and there is no cycle, every term
maps to the standard's own concept by the relation its class and anchor
dictate, every EPO class names its glossary term or says why it cannot,
disjoint classes share no instance in the record, the party model holds on
the measles record (two providers, two customers, the sponsor acting on
behalf of the populations), every affected population has an engagement,
a responsible party and, when represented, its representative, and the DSO
release's approval is preconditioned on every population's input. Counts
are pinned so drift in either direction fails."""
from pyshacl import validate
from rdflib import OWL, RDF, RDFS, SKOS, Namespace

from conftest import EPO, OGC, load

PROV = Namespace("http://www.w3.org/ns/prov#")
SH = Namespace("http://www.w3.org/ns/shacl#")
EV = Namespace("https://w3id.org/og-caie/evaluation/measles#")  # the measles evaluation (sheet 10-42)
TERM = Namespace("https://w3id.org/og-caie/terms#")
OGC_TERM = OGC["term"]  # OGC.term would be rdflib's Namespace.term method

CONCEPTS = 66            # 62 before the audit, plus the four party specializations
BROADER = 20             # each with its narrower stated on the other term
RELATED = 180  # sheet 10: three pairs made symmetric            # stated on one or both sides in the Turtle; read in both directions
CLAUSES = 57  # sheet 10-45 and 10-26: SEVOCAB ontology, repeatability, reproducibility, dialog; NIST tester             # the standards' own concepts (src: nodes) the canonical citations name
MAPPINGS = {"exactMatch": 43, "broadMatch": 17, "closeMatch": 2, "relatedMatch": 0}  # adopted, specializes, corresponds, synonym; sheet 10-23, 24, 25, 30: attestation, determination, technical expert and mission refined
EPO_CLASSES = 64  # R-51 (sheet 10-48): epo:FitnessValue; sheet 10: epo:Step, the range of epo:step over both cycles; R-50: RequirementSetApproval, IndependenceDeclaration, UserInterestDeclaration, PlanDeviation, SponsorSignatoryRole, IndependenceLevel         # 40 before the audit, plus the twelve role classes and epo:Affectedness, plus the report step opened (R-49: ConformanceVerdict, ReportApproval)
DISJOINT = 8             # party/actor, the three actor categories pairwise, the two cycles, evidence/determination, probe/response, the two judgment values
RELATION_BY_ANCHOR = {("adopted", ""): SKOS.exactMatch, ("refined", "specializes"): SKOS.broadMatch,
                      ("refined", "corresponds"): SKOS.closeMatch, ("refined", "synonym"): SKOS.relatedMatch}


def glossary():
    return load("vocabulary/og-caie.ttl", "sources/sources.ttl")


def epo():
    return load("vocabulary/epo.ttl", "vocabulary/og-caie.ttl")


def record():
    return load("vocabulary/epo.ttl", "model/og-caie.model.ttl", "track/measles-evaluation.ttl")  # the model graph too: the step is derived through it (sheet 10-33)


def concepts(g):
    return sorted(g.subjects(RDF.type, SKOS.Concept), key=str)


def test_counts_pinned():
    g = glossary()
    assert len(concepts(g)) == CONCEPTS
    assert sum(1 for _ in g.subject_objects(SKOS.broader)) == BROADER
    assert sum(1 for _ in g.subject_objects(SKOS.related)) == RELATED
    assert sum(1 for _ in g.subjects(RDF.type, OGC.SourceConcept)) == CLAUSES
    for name, n in MAPPINGS.items():
        assert sum(1 for _ in g.subject_objects(SKOS[name])) == n, name
    e = load("vocabulary/epo.ttl")
    assert sum(1 for c in e.subjects(RDF.type, OWL.Class) if str(c).startswith(str(EPO))) == EPO_CLASSES
    assert sum(1 for _ in e.subject_objects(OWL.disjointWith)) == DISJOINT


def test_no_concept_is_disconnected():
    g = glossary()
    cs = set(concepts(g))
    connected = set()
    for p in (SKOS.broader, SKOS.narrower, SKOS.related):
        for s, o in g.subject_objects(p):
            assert s in cs and o in cs, (p, s, o)
            connected |= {s, o}
    assert cs <= connected, sorted(str(c) for c in cs - connected)


def test_every_broader_has_its_inverse_and_no_cycle():
    g = glossary()
    for s, o in g.subject_objects(SKOS.broader):
        assert (o, SKOS.narrower, s) in g, (s, o)
    for s, o in g.subject_objects(SKOS.narrower):
        assert (o, SKOS.broader, s) in g, (s, o)
    for c in concepts(g):
        assert c not in set(g.transitive_objects(c, SKOS.broader)) - {c}, f"broader cycle through {c}"
        assert c not in {x for x in g.transitive_objects(c, SKOS.broader) if x != c and (x, SKOS.broader, c) in g}


def test_every_term_maps_to_the_standards_concept_by_its_anchor():
    """Adopted terms map exactly, specializations broadly, correspondences
    closely, synonyms as related; the target is a src: node that names its
    source and its locator; a coined term maps to nothing."""
    g = glossary()
    for c in concepts(g):
        klass = str(g.value(c, OGC["class"]))
        rel = RELATION_BY_ANCHOR.get((klass, str(g.value(c, OGC.anchorRelation) or "")))
        found = {p for p in RELATION_BY_ANCHOR.values() if any(True for _ in g.objects(c, p))}
        if klass == "coined":
            assert not found, c
            continue
        assert found == {rel}, (c, found, rel)
        for target in g.objects(c, rel):
            assert (target, RDF.type, OGC.SourceConcept) in g, target
            assert (g.value(target, OGC.cites), RDF.type, OGC.Source) in g, target
            assert g.value(target, OGC.locator) is not None and g.value(target, RDFS.label) is not None, target
            # the clause is the one the canonical citation names (same source)
            assert g.value(target, OGC.cites) == g.value(g.value(c, OGC.canonical), OGC.cites), c


def test_every_epo_class_names_its_term_or_says_why_not():
    g = epo()
    terms = set(concepts(g))
    for c in g.subjects(RDF.type, OWL.Class):
        if not str(c).startswith(str(EPO)):
            continue
        named = set(g.objects(c, OGC_TERM))
        if named:
            assert named <= terms, (c, named - terms)
        else:
            comment = str(g.value(c, RDFS.comment) or "")
            assert "no term" in comment.lower(), f"{c} neither names a term nor says why not"  # the sentence comes first, the reason after it (round four, KG 7)


def test_role_classes_form_a_tree_under_role_and_the_individuals_keep_their_iris():
    g = load("vocabulary/epo.ttl")
    roles = {c for c in g.subjects(RDF.type, OWL.Class) if EPO.Role in g.transitive_objects(c, RDFS.subClassOf)}
    assert {EPO.PartyRole, EPO.ActorRole, EPO.ProviderRole, EPO.CustomerRole, EPO.EvaluationServiceProviderRole, EPO.TestItemProviderRole,
            EPO.EvaluationCustomerRole, EPO.TestItemCustomerRole, EPO.TechnicalExpertRole, EPO.DomainExpertRole, EPO.EvaluationOperatorRole,
            EPO.AuthorizedRepresentativeRole} <= roles
    assert set(g.subjects(RDFS.subClassOf, EPO.ProviderRole)) == {EPO.EvaluationServiceProviderRole, EPO.TestItemProviderRole}
    assert set(g.subjects(RDFS.subClassOf, EPO.CustomerRole)) == {EPO.EvaluationCustomerRole, EPO.TestItemCustomerRole}
    assert (EPO.EvaluationCustomerRole, OWL.disjointWith, EPO.TestItemCustomerRole) not in g, "the sponsor may also be the test item customer"
    assert (EPO.EvaluationServiceProviderRole, OWL.disjointWith, EPO.TestItemProviderRole) not in g, "disjoint only when independent: a record fact"
    individuals = {EPO.sponsorRole: EPO.EvaluationCustomerRole, EPO.testingOrganizationRole: EPO.EvaluationServiceProviderRole,
                   EPO.accountableOrganizationRole: EPO.TestItemProviderRole, EPO.authorizedRepresentativeRole: EPO.AuthorizedRepresentativeRole,
                   EPO.domainExpertRole: EPO.DomainExpertRole, EPO.evaluationOperatorRole: EPO.EvaluationOperatorRole, EPO.testItemCustomerRole: EPO.TestItemCustomerRole}
    for ind, cls in individuals.items():
        assert (ind, RDF.type, cls) in g, ind
    assert (EPO.representedBy, RDFS.subPropertyOf, EPO.responsibleParty) in g
    assert (EPO.actsOnBehalfOf, RDFS.subPropertyOf, PROV.actedOnBehalfOf) not in g, "sheet 10-34: a plain property; PROV's direction of responsibility runs the other way"
    assert (EPO.SponsorSignatoryRole, RDFS.subClassOf, EPO.Role) in g and (EPO.sponsorSignatoryRole, RDF.type, EPO.SponsorSignatoryRole) in g  # sheet 10-06


def test_glossary_mirrors_the_party_model():
    g = glossary()
    assert set(g.objects(TERM.provider, SKOS.narrower)) == {TERM["evaluation-service-provider"], TERM["test-item-provider"]}
    assert set(g.objects(TERM.customer, SKOS.narrower)) == {TERM["evaluation-customer"], TERM["test-item-customer"]}
    assert (TERM["evaluation-record"], SKOS.broader, TERM.record) in g and (TERM.record, SKOS.narrower, TERM["evaluation-record"]) in g
    assert str(g.value(TERM["authorized-representative"], SKOS.prefLabel)) == "authorized representative"
    assert "account executive" in {str(a) for a in g.objects(TERM["authorized-representative"], SKOS.altLabel)}
    assert str(g.value(TERM["test-item-provider"], SKOS.prefLabel)) == "test item provider"
    assert "accountable organization" in {str(a) for a in g.objects(TERM["test-item-provider"], SKOS.altLabel)}
    canon = g.value(TERM["authorized-representative"], OGC.canonical)
    assert str(g.value(canon, OGC.cites)).endswith("#sevocab") and "authorized representative of the acquirer" == str(g.value(canon, OGC.quote))
    assert str(g.value(TERM["authorized-representative"], OGC.anchorRelation)) == "corresponds"


def _types_with_roles(g, n):
    types = set(g.objects(n, RDF.type))
    for r in g.objects(n, EPO.role):
        types |= set(g.objects(r, RDF.type))
    closure = set()
    for t in types:
        closure |= set(g.transitive_objects(t, RDFS.subClassOf))
    return closure


def test_disjoint_classes_share_no_instance_in_the_record():
    g = record()
    pairs = list(g.subject_objects(OWL.disjointWith))
    assert len(pairs) == DISJOINT
    for n in {s for s in g.subjects() if str(s).startswith(str(EV))}:
        types = _types_with_roles(g, n)
        for a, b in pairs:
            assert not (a in types and b in types), (n, a, b)


def test_party_axioms_hold_on_the_measles_record():
    g = record()
    sponsor = EV["county-public-health-office"]
    testing = EV["humane-intelligence"]
    vendor = EV["chatbot-vendor"]
    assert EPO.EvaluationCustomerRole in _types_with_roles(g, sponsor) and EPO.CustomerRole in _types_with_roles(g, sponsor)
    assert EPO.TestItemCustomerRole in _types_with_roles(g, sponsor), "the sponsor deploys the chatbot: it is also the test item customer"
    assert EPO.EvaluationServiceProviderRole in _types_with_roles(g, testing) and EPO.ProviderRole in _types_with_roles(g, testing)
    assert EPO.TestItemProviderRole in _types_with_roles(g, vendor) and EPO.ProviderRole in _types_with_roles(g, vendor)
    assert set(g.objects(sponsor, EPO.actsOnBehalfOf)) == set(g.subjects(RDF.type, EPO.Population)) == set(g.objects(EV["mission-1"], EPO.regards))
    # independent: declared, not assumed (sheet 10-07): the testing organization's authorized representative declares it independent of the test item provider, a different organization
    decl = next(g.subjects(RDF.type, EPO.IndependenceDeclaration))
    assert g.value(decl, EPO.independentOf) == vendor and testing != vendor
    assert (g.value(decl, PROV.wasAttributedTo), PROV.actedOnBehalfOf, testing) in g
    assert (testing, EPO.role, EPO.accountableOrganizationRole) not in g
    # the provider fact (sheet 10-09): the vendor provides the test item, the sponsor says it does not
    assert str(g.value(vendor, EPO.providesTestItem)) == "true" and str(g.value(sponsor, EPO.providesTestItem)) == "false"
    assert (sponsor, EPO.role, EPO.accountableOrganizationRole) not in g
    # the sponsor's user interest is declared by its signatory (sheet 10-06, 10-07)
    ui = next(g.subjects(RDF.type, EPO.UserInterestDeclaration))
    signatory = g.value(ui, PROV.wasAttributedTo)
    assert str(g.value(ui, EPO.hasUserInterest)) == "true" and (signatory, EPO.role, EPO.sponsorSignatoryRole) in g and (signatory, PROV.actedOnBehalfOf, sponsor) in g


def test_every_population_has_an_engagement_a_responsible_party_and_its_representative():
    g = record()
    for p in g.subjects(RDF.type, EPO.Population):
        decisions = [d for d in g.subjects(EPO.population, p) if (d, RDF.type, EPO.EngagementDecision) in g]
        assert len(decisions) == 1, p
        engagement = g.value(decisions[0], EPO.engagement)
        assert engagement in (EPO.interview, EPO.representation), p
        responsible = set(g.objects(p, EPO.responsibleParty)) | set(g.objects(p, EPO.representedBy))
        assert responsible, p
        for a in responsible:
            assert (a, RDF.type, PROV.Person) in g or (a, RDF.type, PROV.Organization) in g, (p, a)
        rep = g.value(p, EPO.representedBy)  # sheet 10-13: who speaks is any team member, not necessarily a domain expert
        assert rep is not None and (rep, RDF.type, PROV.Person) in g and any((rep, PROV.actedOnBehalfOf, t) in g for t in g.subjects(EPO.role, EPO.testingOrganizationRole)), p
        if engagement == EPO.interview:
            assert any((i, PROV.wasAttributedTo, p) in g for i in g.subjects(RDF.type, EPO.StakeholderInput)), p
            assert g.value(p, EPO.responsibleParty) is not None, p  # who engaged it
        assert set(g.objects(p, EPO.affectedAs)) <= {EPO.asCustomer, EPO.indirectly} and set(g.objects(p, EPO.affectedAs)), p


def test_dso_precondition_holds_on_the_record_and_its_counterexample_fails():
    shapes = load("shapes/epo.shapes.ttl")
    ok, _, report = validate(record(), shacl_graph=shapes, advanced=True)
    assert ok, report
    ok, results, _ = validate(load("vocabulary/epo.ttl", "model/og-caie.model.ttl", "counterexamples/dso-before-stakeholder-input.ttl"), shacl_graph=shapes, advanced=True)
    assert not ok
    fired = {str(s).rsplit("/", 1)[-1] for s in results.objects(None, SH.sourceShape)}
    assert fired == {"S1-DsoRelease"}, fired
    messages = " ".join(str(m) for m in results.objects(None, SH.resultMessage))
    assert "before the DSO release is approved" in messages
