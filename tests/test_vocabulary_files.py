"""The vocabulary files are ontologies with one home per declaration (round
four, KG 4 and 10): every file under vocabulary/ carries exactly one
owl:Ontology header with owl:versionInfo (the git tag is the version), the
EPO imports PROV-O and EARL and the register imports EARL beside PROV-O and
SKOS, and no IRI is declared a class or a property in two files (the shape
files included: shapes/rulings.shapes.ttl once redeclared the two ruling
texts). Every epo: class carries a short label, under sixty characters,
with its sentence in rdfs:comment; every epo:, ogm: and ogc: property
carries a label (KG 7)."""
from rdflib import OWL, RDF, RDFS, Graph, Literal, URIRef

from conftest import ROOT, load

VOCABULARY = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "vocabulary").glob("*.ttl"))
DECLARING = VOCABULARY + sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "shapes").glob("*.ttl"))
DECLARATION_TYPES = [OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty, OWL.AnnotationProperty, RDFS.Class, RDF.Property]
VERSION = "0.3.0 in preparation; the git tag is the version"
NAMESPACES = {"epo": "https://w3id.org/og-caie/epo#", "ogm": "https://w3id.org/og-caie/model#", "ogc": "https://w3id.org/og-caie/"}
LABEL_MAX = 60


def test_every_vocabulary_file_has_one_ontology_header_with_the_version():
    assert len(VOCABULARY) == 6, VOCABULARY  # the glossary, the EPO, the register, the model's derived ends, the crosswalk, the derived step
    for f in VOCABULARY:
        g = load(f)
        headers = list(g.subjects(RDF.type, OWL.Ontology))
        assert len(headers) == 1, (f, headers)
        assert str(g.value(headers[0], OWL.versionInfo)) == VERSION, f
    epo = load("vocabulary/epo.ttl")
    imports = set(epo.objects(next(epo.subjects(RDF.type, OWL.Ontology)), OWL.imports))
    assert {URIRef("http://www.w3.org/ns/prov-o#"), URIRef("http://www.w3.org/ns/earl#")} <= imports
    reg = load("vocabulary/register.ttl")
    imports = set(reg.objects(next(reg.subjects(RDF.type, OWL.Ontology)), OWL.imports))
    assert {URIRef("http://www.w3.org/ns/prov-o#"), URIRef("http://www.w3.org/ns/earl#"), URIRef("http://www.w3.org/2004/02/skos/core")} <= imports


def test_no_iri_is_declared_in_two_files():
    homes: dict = {}
    for f in DECLARING:
        g = Graph().parse(ROOT / f)
        for t in DECLARATION_TYPES:
            for s in g.subjects(RDF.type, t):
                if isinstance(s, URIRef):
                    homes.setdefault(str(s), set()).add(f)
    twice = {iri: sorted(fs) for iri, fs in homes.items() if len(fs) > 1}
    assert twice == {}, twice
    register = {iri for iri, fs in homes.items() if fs == {"vocabulary/register.ttl"}}
    for local in ("pinnedAt", "term", "inRecord", "synthetic", "rulingText", "verbatim"):
        assert NAMESPACES["ogc"] + local in register, local


def test_every_epo_class_has_a_short_label_and_a_comment():
    g = load("vocabulary/epo.ttl")
    for c in g.subjects(RDF.type, OWL.Class):
        if not str(c).startswith(NAMESPACES["epo"]):
            continue
        labels = list(g.objects(c, RDFS.label))
        assert len(labels) == 1, (c, labels)
        assert 0 < len(str(labels[0])) < LABEL_MAX, (c, str(labels[0]))
        comments = list(g.objects(c, RDFS.comment))
        assert len(comments) == 1 and str(comments[0]).strip(), c


def test_every_property_has_a_label():
    g = load(*VOCABULARY)
    missing = []
    for t in (OWL.ObjectProperty, OWL.DatatypeProperty):
        for p in g.subjects(RDF.type, t):
            if any(str(p).startswith(ns) for ns in NAMESPACES.values()) and not isinstance(g.value(p, RDFS.label), Literal):
                missing.append(str(p))
    assert missing == [], sorted(missing)
