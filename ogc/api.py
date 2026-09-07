"""The library: every question the OG-CAIE vocabulary answers, as a function
returning plain, sorted data. The CLI renders these."""
from __future__ import annotations

import difflib
import hashlib
import json
import re
import textwrap
import unicodedata
from collections import Counter
from pathlib import Path

from rdflib import RDF, RDFS, BNode, Graph, URIRef

from .graph import EPO, EARL, EPO, EV, OGC, PROV, RUL, SH, SHAPE_FILES, SKOS, SRC, TERM, PREFIXES

COINED = "(coined)"  # the source column of a coined term: it cites no source, it was coined (ruling R-29)

RETIRED = {"adequacy": "ruling R-08: say appropriateness (of the context) or sufficiency (of the evidence)",
           "adequate": "ruling R-08: say appropriate or sufficient",
           "inadequate": "ruling R-08: say inappropriate or insufficient",
           "validation": "reserved: by this specification's split, machine checks over the record are verification (conformance); validation is the named person's judgment (R-16)"}


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", s or "")).strip()


def one(g: Graph, s, p) -> str:
    return str(next(iter(g.objects(s, p)), ""))


def many(g: Graph, s, p) -> list[str]:
    return sorted(str(o) for o in g.objects(s, p))


def local(iri) -> str:
    s = str(iri)
    return s.split("#")[-1] if "#" in s else s.rstrip("/").split("/")[-1]


_CURIE = re.compile(r"([A-Za-z_][\w.-]*):(\S+)")


def _split_id(text: str) -> tuple[str | None, str]:
    """(prefix, local): the known prefix an id is under and the local name
    behind it. A CURIE's prefix is taken in any case and lowercased (round
    three, M2: the help promises case-insensitive ids); a full IRI in a known
    namespace, with or without angle brackets, gives that namespace's prefix.
    Any other text (a label, even one with a colon inside it) gives (None,
    the text normalised)."""
    s = norm(text)
    if s.startswith("<") and s.endswith(">"):
        s = s[1:-1].strip()
    m = _CURIE.fullmatch(s)
    if m and m.group(1).lower() in PREFIXES:
        return m.group(1).lower(), m.group(2)
    for k, ns in sorted(PREFIXES.items(), key=lambda kv: -len(str(kv[1]))):
        ns = str(ns)
        if s.startswith(ns) and len(s) > len(ns):
            return k, s[len(ns):]
    return None, s


def bare(text: str) -> str:
    """The local name behind the id forms the tool itself prints: a CURIE in a
    known prefix (`term:probe`, `rul:R-16`, `ev:mission-1`, `ogc:S0-Layers`;
    the prefix in any case) or a full IRI in a known namespace, with or
    without angle brackets. Any other text (a label, even one with a colon
    inside it) comes back normalised and otherwise untouched."""
    return _split_id(text)[1]


def prefix_of(text: str) -> str | None:
    """The known prefix a CURIE or IRI is under (lowercased), None for a label or a bare local name (round three, M4)."""
    return _split_id(text)[0]


def _tokens(s: str) -> set[str]:
    return {t for t in re.split(r"[^a-z0-9]+", s.lower()) if len(t) >= 3}


def near(key: str, names: list[str], limit: int = 8) -> list[str]:
    """Up to `limit` near misses for a name that did not resolve: substring
    hits first, then names sharing a token of three letters or more, then
    names within edit distance (difflib ratio 0.6 or better); never the whole
    list, and nothing when nothing is near."""
    k = norm(key).lower()
    if not k:
        return []
    kt = _tokens(k)
    scored = []
    for n in names:
        l = n.lower()
        ratio = difflib.SequenceMatcher(None, k, l).ratio()
        if k in l:
            rank = 0
        elif kt & _tokens(l):
            rank = 1
        elif ratio >= 0.6:
            rank = 2
        else:
            continue
        scored.append((rank, -ratio, n))
    return [n for _, _, n in sorted(scored)[:limit]]


def first_sentence(s: str) -> str:
    m = re.match(r"(.+?\.)(\s|$)", norm(s))
    return m.group(1) if m else norm(s)


def concepts(g: Graph):
    return sorted(set(g.subjects(RDF.type, SKOS.Concept)), key=str)


# ---------------------------------------------------------------- terms

def citation_record(g: Graph, c) -> dict:
    src = g.value(c, OGC.cites)
    return dict(source=local(src), source_label=one(g, src, RDFS.label), rank=one(g, src, OGC.rank), posture=one(g, src, OGC.posture),
                locator=one(g, c, OGC.locator), quote=one(g, c, OGC.quote), status=cite_status(g, c),
                pdf_page=one(g, c, OGC.pdfPage), file=one(g, c, OGC.file), verified_by=local(g.value(c, OGC.verifiedBy)) if g.value(c, OGC.verifiedBy) else "",
                verified_on=one(g, c, OGC.verifiedOn), node=c)


def cite_status(g: Graph, c) -> str:
    """One status vocabulary for every rendering: the quote's status (machine,
    human, pending) or `cite-only` when the citation carries no quote."""
    return one(g, c, OGC.quoteStatus) or ("cite-only" if not one(g, c, OGC.quote) else "unstated")


def term_record(g: Graph, s) -> dict:
    rulings = [dict(id=local(r), label=ruling_label(g, r)) for r in sorted(g.objects(s, PROV.wasDerivedFrom), key=str)]
    concerns = sorted((dict(id=local(c), status=one(g, c, OGC.status), label=one(g, c, RDFS.label)) for c in g.subjects(OGC.concernsTerm, s)), key=lambda d: d["id"])
    sci = sorted(local(t) for t in g.subjects(OGC.usesTerm, s))
    xw = sorted(one(g, x, RDFS.label) for x in g.subjects(OGC.mapsTo, s))
    canon = g.value(s, OGC.canonical)
    return dict(iri=str(s), local=local(s), pref=one(g, s, SKOS.prefLabel), definition=norm(one(g, s, SKOS.definition)),
                alts=many(g, s, SKOS.altLabel), **{"class": one(g, s, OGC["class"])}, anchor_relation=one(g, s, OGC.anchorRelation),
                canonical=citation_record(g, canon) if canon is not None else {}, coined_by=one(g, s, OGC.coinedBy), see_also=sorted((citation_record(g, c) for c in g.objects(s, OGC.seeAlso)), key=lambda d: (d["source"], d["locator"])),
                scope_note=norm(one(g, s, OGC.scopeNote)), binding=one(g, s, OGC.binding), rulings=rulings, concerns=concerns, sci=sci, crosswalk=xw,
                **relations(g, s))


def ruling_label(g: Graph, r) -> str:
    """What a ruling is about, for a reference to it: the labels of the
    concerns it resolves, joined as the rulings log joins them; failing those,
    the first words of its formal text (round three, M3: a bare `R-49` told
    the reader nothing)."""
    labels = sorted(l for l in (one(g, c, RDFS.label) for c in g.objects(r, OGC.resolves)) if l)
    if labels:
        return " / ".join(labels)
    words = norm(one(g, r, OGC.rulingText)).split()
    return " ".join(words[:8]) + (" ..." if len(words) > 8 else "")


MATCHES = (SKOS.exactMatch, SKOS.closeMatch, SKOS.broadMatch, SKOS.relatedMatch)


def relations(g: Graph, s) -> dict:
    """The SKOS relations of a term (tbox audit, sheet 08): broader, narrower
    and related terms within the glossary (related read in both directions),
    the mappings to the standards' own concepts (a src: clause node with its
    locator), and the EPO classes that name the term (ogc:term)."""
    def terms(objs):
        return sorted((dict(term=one(g, t, SKOS.prefLabel), local=local(t)) for t in objs if (t, RDF.type, SKOS.Concept) in g), key=lambda d: d["term"].lower())
    related = set(g.objects(s, SKOS.related)) | set(g.subjects(SKOS.related, s))
    matches = []
    for p in MATCHES:
        for c in g.objects(s, p):
            src = g.value(c, OGC.cites)
            matches.append(dict(relation=local(p), concept=one(g, c, RDFS.label) or local(c), local=local(c), source=local(src) if src is not None else "", locator=one(g, c, OGC.locator)))
    matches.sort(key=lambda d: (d["relation"], d["concept"]))
    classes = sorted(f"epo:{local(c)}" for c in g.subjects(OGC["term"], s))  # OGC.term would be rdflib's Namespace.term method
    return dict(broader=terms(g.objects(s, SKOS.broader)), narrower=terms(g.objects(s, SKOS.narrower)), related=terms(related), matches=matches, classes=classes)


def all_terms(g: Graph) -> dict[str, dict]:
    return {str(s): term_record(g, s) for s in concepts(g)}


def _labels(g: Graph, s) -> list[tuple[str, str]]:
    return [("local", local(s)), ("pref", one(g, s, SKOS.prefLabel))] + [("alt", a) for a in many(g, s, SKOS.altLabel)]


def resolve_term(g: Graph, text: str):
    """(iri, candidates, meta): one exact match on local name, prefLabel or altLabel, case-insensitive."""
    key = norm(text).lower()
    exact = {}
    for s in concepts(g):
        for kind, l in _labels(g, s):
            if norm(l).lower() == key:
                exact.setdefault(s, (kind, l))
                break
    if len(exact) == 1:
        s, (kind, l) = next(iter(exact.items()))
        return s, [], dict(via=f"{kind}:{l}" if kind == "alt" else "")
    return None, sorted((one(g, s, SKOS.prefLabel), local(s)) for s in exact), dict(via="")


def find(g: Graph, text: str, quotes: bool = True) -> list[dict]:
    """Exact, then prefix, then substring over prefLabel and altLabel, then
    over quote text, then over the EPO's class and role labels (round three,
    M5; a hit there says `via epo:<Name>` and is read by `ogc epo`). Nothing
    else is indexed: not the rulings, the concerns, the sources or the record."""
    key = norm(text).lower()
    hits = {}

    def put(t, rank, kpri, via, **row):
        cur = hits.get(t)
        if cur is None or (rank, kpri) < (cur["rank"], cur["kpri"]):
            hits[t] = dict(rank=rank, kpri=kpri, match=["exact", "prefix", "substring"][rank], via=via, **(row or dict(
                pref=one(g, t, SKOS.prefLabel), local=local(t), **{"class": one(g, t, OGC["class"])},
                source=local(g.value(g.value(t, OGC.canonical), OGC.cites)) if g.value(t, OGC.canonical) is not None else "")))

    def rank_of(l):
        return 0 if l == key else 1 if l.startswith(key) else 2 if key in l else None

    for t in concepts(g):
        for kind, l in _labels(g, t):
            if kind == "local":
                continue
            r = rank_of(norm(l).lower())
            if r is not None:
                put(t, r, 0 if kind == "pref" else 1, f"{kind}:{l}")
        if quotes:
            for c in [g.value(t, OGC.canonical), *g.objects(t, OGC.seeAlso)]:
                if c is None:
                    continue
                q = norm(one(g, c, OGC.quote)).lower()
                if q and key in q:
                    put(t, 2, 2, f"quote:{local(g.value(c, OGC.cites))}")
    for c, kind in epo_nodes(g):  # the EPO's labels: exact and prefix on the head before the colon, substring over the whole label
        label = norm(one(g, c, RDFS.label))
        head = label.split(":", 1)[0].strip().lower()
        r = rank_of(head)
        if r is None and key in label.lower():
            r = 2
        if r is not None:
            put(c, r, 3, f"epo:{local(c)}", pref=head, local=f"epo:{local(c)}", **{"class": f"epo {kind}"}, source="")
    out = sorted(hits.values(), key=lambda d: (d["rank"], d["kpri"], d["pref"].lower()))
    for d in out:
        d.pop("kpri", None)
    return out


def candidates(g: Graph, text: str, limit: int = 8) -> list[str]:
    return [f"{d['pref']} ({d['local']}) via {d['via']}" for d in find(g, text)[:limit]]


def list_terms(g: Graph, klass=None, source=None) -> list[dict]:
    rows = []
    for t in all_terms(g).values():
        if klass and t["class"] != klass:
            continue
        if source and t["canonical"].get("source", "").lower() != norm(source).lower():
            continue
        rows.append({"term": t["pref"], "local": t["local"], "class": t["class"], "source": _source_col(t),
                     "locator": t["canonical"].get("locator", ""), "status": t["canonical"].get("status", "")})
    return sorted(rows, key=lambda r: r["term"].lower())


def _source_col(t: dict) -> str:
    """The source column of a term row: the canonical source's slug, or `(coined)` for a coined term."""
    return COINED if t["class"] == "coined" and not t["canonical"] else t["canonical"].get("source", "")


# ---------------------------------------------------------------- sources

def source_slugs(g: Graph) -> list[str]:
    return sorted(local(s) for s in g.subjects(RDF.type, OGC.Source))


def resolve_source(g: Graph, slug: str):
    """The source IRI for a slug, stripped and case-insensitive; None if unregistered."""
    key = norm(slug).lower()
    for s in g.subjects(RDF.type, OGC.Source):
        if local(s).lower() == key:
            return s
    return None


def source_record(g: Graph, slug: str) -> dict | None:
    s = resolve_source(g, slug)
    if s is None:
        return None
    slug = local(s)
    snaps = sorted((dict(file=one(g, sn, OGC.file), hash=one(g, sn, OGC.contentHash)) for sn in g.objects(s, OGC.snapshot)), key=lambda d: d["file"])
    cits = []
    for t in concepts(g):
        for kind, c in [("canonical", g.value(t, OGC.canonical)), *[("seeAlso", x) for x in g.objects(t, OGC.seeAlso)]]:
            if c is not None and g.value(c, OGC.cites) == s:
                cits.append(dict(term=one(g, t, SKOS.prefLabel), citation=kind, locator=one(g, c, OGC.locator), quote=one(g, c, OGC.quote), status=cite_status(g, c)))
    for x in g.subjects(OGC.cites, s):
        if (x, RDF.type, OGC.Crosswalk) in g:
            cits.append(dict(term=f"crosswalk: {one(g, x, RDFS.label)}", citation="crosswalk", locator=one(g, x, OGC.locator), quote=one(g, x, OGC.quote), status=cite_status(g, x)))
    return dict(slug=slug, label=one(g, s, RDFS.label), rank=one(g, s, OGC.rank), kind=one(g, s, OGC.kind), posture=one(g, s, OGC.posture),
                url=one(g, s, OGC.url), bibkey=one(g, s, OGC.bibkey), digest=one(g, s, OGC.digest), status=one(g, s, OGC.status), retrieval=one(g, s, OGC.retrievalNote),
                licence=one(g, s, OGC.licenceNote), permission=one(g, s, OGC.permissionStatement), snapshots=snaps,
                citations=sorted(cits, key=lambda d: (d["term"].lower(), d["citation"], d["locator"])))


def sources_table(g: Graph, rank=None, posture=None, uncited=False) -> list[dict]:
    counts = Counter()
    holders = set(concepts(g)) | set(g.subjects(RDF.type, EPO.EpoStep)) | set(g.subjects(RDF.type, EPO.ContractingStep)) | {EPO.ContractingStep}
    for t in holders:
        for c in [g.value(t, OGC.canonical), *g.objects(t, OGC.seeAlso)]:
            if c is not None:
                counts[g.value(c, OGC.cites)] += 1
    for x in g.subjects(RDF.type, OGC.Crosswalk):
        counts[g.value(x, OGC.cites)] += 1
        for a in g.objects(x, OGC.also):
            counts[a] += 1
    rows = []
    for s in sorted(g.subjects(RDF.type, OGC.Source), key=str):
        r, p = one(g, s, OGC.rank), one(g, s, OGC.posture)
        if rank and r != rank:
            continue
        if posture and p != posture:
            continue
        if uncited and counts[s] > 0:
            continue
        rows.append(dict(slug=local(s), rank=r, posture=p, kind=one(g, s, OGC.kind), bibkey=one(g, s, OGC.bibkey), citations=counts[s],
                         snapshots=sum(1 for _ in g.objects(s, OGC.snapshot)), label=one(g, s, RDFS.label)))
    return rows


# ---------------------------------------------------------------- judgment record

ID_FORM = r"^(?:(r|c|sci)-?)?0*(\d+)$"


def norm_id(text: str, kind: str) -> str | None:
    """One normaliser for the three id kinds (rulings R, concerns C, essentials
    SCI): `^(r|c|sci)-?0*(\\d+)$`, case-insensitive, the kind prefix optional
    when the command implies it. R16, r-016, 16 all give R-16; a prefix of
    another kind gives None."""
    m = re.fullmatch(ID_FORM, norm(text), re.I)
    if not m or (m.group(1) and m.group(1).upper() != kind):
        return None
    return f"{kind}-{int(m.group(2)):02d}"


def ruling_record(g: Graph, rid: str) -> dict | None:
    rid = norm_id(rid, "R")
    if rid is None:
        return None
    r = RUL[rid]
    if (r, RDF.type, OGC.Ruling) not in g:
        return None
    return dict(id=rid, order=int(one(g, r, OGC.order) or 0), text=one(g, r, OGC.rulingText), verbatim=one(g, r, OGC.verbatim), change=one(g, r, OGC.changeNote),
                date=one(g, r, PROV.generatedAtTime), attributed=one(g, g.value(r, PROV.wasAttributedTo), RDFS.label),
                resolves=sorted(local(c) for c in g.objects(r, OGC.resolves)),
                resolves_labels=sorted(one(g, c, RDFS.label) for c in g.objects(r, OGC.resolves)),
                derived_terms=sorted(one(g, t, SKOS.prefLabel) for t in g.subjects(PROV.wasDerivedFrom, r) if (t, RDF.type, SKOS.Concept) in g))


def rulings_table(g: Graph, term_iri=None, grep=None) -> list[dict]:
    rows = []
    needle = norm(grep or "").lower()
    pat = re.compile(re.escape(needle), re.I) if needle else None
    for r in g.subjects(RDF.type, OGC.Ruling):
        if term_iri is not None and (term_iri, PROV.wasDerivedFrom, r) not in g and not any((c, OGC.concernsTerm, term_iri) in g for c in g.objects(r, OGC.resolves)):
            continue
        matched = snippet = ""
        if pat:
            for field, val in (("text", one(g, r, OGC.rulingText)), ("verbatim", one(g, r, OGC.verbatim)), ("change", one(g, r, OGC.changeNote))):
                m = pat.search(val)
                if m:
                    matched = field
                    a, b = max(0, m.start() - 40), min(len(val), m.end() + 40)
                    snippet = ("…" if a else "") + norm(val[a:b]) + ("…" if b < len(val) else "")
                    break
            if not matched:
                continue
        rows.append(dict(id=local(r), order=int(one(g, r, OGC.order) or 0), date=one(g, r, PROV.generatedAtTime),
                         resolves=sorted(local(c) for c in g.objects(r, OGC.resolves)),
                         concern=" / ".join(sorted(one(g, c, RDFS.label) for c in g.objects(r, OGC.resolves))), matched=matched, snippet=snippet,
                         text=first_sentence(one(g, r, OGC.rulingText))))
    return sorted(rows, key=lambda d: d["order"])


def concern_record(g: Graph, cid: str) -> dict | None:
    cid = norm_id(cid, "C")
    if cid is None:
        return None
    c = RUL[cid]
    if (c, RDF.type, OGC.Concern) not in g:
        return None
    return dict(id=cid, label=one(g, c, RDFS.label), problem=one(g, c, OGC.problem), severity=one(g, c, OGC.severity), status=one(g, c, OGC.status),
                surfaced=one(g, c, OGC.surfacedOn), how=one(g, c, OGC.surfacedHow),
                terms=sorted(one(g, t, SKOS.prefLabel) for t in g.objects(c, OGC.concernsTerm)),
                resolved_by=sorted(local(r) for r in g.subjects(OGC.resolves, c)))


def concerns_table(g: Graph, open_only=False, status=None, severity=None) -> list[dict]:
    rows = []
    for c in g.subjects(RDF.type, OGC.Concern):
        st, sev = one(g, c, OGC.status), one(g, c, OGC.severity)
        if open_only and st != "open":
            continue
        if status and st != status:
            continue
        if severity and sev != severity:
            continue
        rows.append(dict(id=local(c), severity=sev, status=st, terms=sorted(one(g, t, SKOS.prefLabel) for t in g.objects(c, OGC.concernsTerm)),
                         resolved_by=sorted(local(r) for r in g.subjects(OGC.resolves, c)), label=one(g, c, RDFS.label)))
    return sorted(rows, key=lambda d: (int(d["id"].split("-")[1]), d["id"]))


def concerns_mentioning(g: Graph, word: str) -> list[dict]:
    pat = re.compile(r"(?<![\w-])" + re.escape(norm(word)) + r"(?![\w-])", re.I)
    rows = []
    for c in g.subjects(RDF.type, OGC.Concern):
        if pat.search(one(g, c, RDFS.label)) or pat.search(one(g, c, OGC.problem)):
            rows.append(dict(id=local(c), status=one(g, c, OGC.status), label=one(g, c, RDFS.label)))
    return sorted(rows, key=lambda d: (int(d["id"].split("-")[1]), d["id"]))


# ---------------------------------------------------------------- essentials, crosswalks, check-word

def sci_table(g: Graph, sid=None) -> list[dict]:
    rows = []
    want = norm_id(sid, "SCI") if sid else None
    for t in g.subjects(RDF.type, OGC.Trace):
        i = local(t)
        if sid and i.upper() != want:
            continue
        rows.append(dict(id=i, name=one(g, t, RDFS.label).split(" ", 1)[-1], tag=one(g, t, OGC.tag), statement=one(g, t, RDFS.comment),
                         shapes=sorted(local(s) for s in g.objects(t, OGC.checkedBy)),
                         terms=sorted(one(g, x, SKOS.prefLabel) for x in g.objects(t, OGC.usesTerm)),
                         rests_on=sorted(local(x) for x in g.objects(t, OGC.restsOn))))
    return sorted(rows, key=lambda d: d["id"])


def steps_table(g: Graph) -> list[dict]:
    """The twelve steps of the two cycles, C1..C6 then 1..6, with the canon step each matches (R-31, R-32)."""
    rows = []
    for st in list(g.subjects(RDF.type, EPO.ContractingStep)) + list(g.subjects(RDF.type, EPO.EpoStep)):
        label = one(g, st, RDFS.label)
        c = g.value(st, OGC.canonical)
        canon = citation_record(g, c) if c is not None else {}
        head = label.split(" ", 1)[0]
        rows.append(dict(cycle="contracting" if head.startswith("C") else "evaluation", order=(0 if head.startswith("C") else 10) + int(head.lstrip("C")), step=local(st), label=label, source=canon.get("source", ""), locator=canon.get("locator", ""),
                         quote=canon.get("quote", ""), status=canon.get("status", ""),
                         also=[{k: v for k, v in citation_record(g, x).items() if k != "node"} for x in sorted(g.objects(st, OGC.seeAlso), key=lambda x: (str(g.value(x, OGC.cites)), str(g.value(x, OGC.locator))))]))
    return sorted(rows, key=lambda d: d["order"])


def resolve_step(g: Graph, text: str):
    """A step IRI from its local name (`scope`, `acceptDelivery`), the head of
    its label (`1 scope`, `C1 need`) or that head without the number (`need`,
    `accept`); case-insensitive. None when nothing matches."""
    key = norm(text).lower()
    for st in sorted(set(g.subjects(RDF.type, EPO.ContractingStep)) | set(g.subjects(RDF.type, EPO.EpoStep)), key=str):
        head = one(g, st, RDFS.label).split(":", 1)[0]
        names = {local(st), head, head.split(" ", 1)[-1], one(g, st, RDFS.label)}
        if key in {norm(n).lower() for n in names}:
            return st
    return None


def step_citations(g: Graph, st) -> list[dict]:
    """The canonical and seeAlso citations of a step, in the form `ogc quote` prints."""
    out = []
    for kind, c in [("canonical", g.value(st, OGC.canonical)), *[("seeAlso", x) for x in sorted(g.objects(st, OGC.seeAlso), key=lambda x: (str(g.value(x, OGC.cites)), str(g.value(x, OGC.locator))))]]:
        if c is not None:
            out.append(dict(citation=kind, **{k: v for k, v in citation_record(g, c).items() if k != "node"}))
    return out


def crosswalk(g: Graph, klass=None, source=None) -> list[dict]:
    """One row per term: its class, anchor relation, canonical source and locator, and binding."""
    rows = []
    for t in all_terms(g).values():
        if klass and t["class"] != klass:
            continue
        if source and t["canonical"].get("source", "").lower() != norm(source).lower():
            continue
        rows.append({"term": t["pref"], "class": t["class"], "relation": t["anchor_relation"], "source": _source_col(t),
                     "locator": t["canonical"].get("locator", ""), "status": t["canonical"].get("status", ""), "see_also": len(t["see_also"]), "binding": t["binding"]})
    return sorted(rows, key=lambda r: r["term"].lower())


def popper(g: Graph) -> list[dict]:
    rows = []
    for x in g.subjects(RDF.type, OGC.Crosswalk):
        rows.append(dict(order=int(one(g, x, OGC.order)), concept=one(g, x, RDFS.label), quote=one(g, x, OGC.quote),
                         terms=sorted(one(g, t, SKOS.prefLabel) for t in g.objects(x, OGC.mapsTo)),
                         realized_by=sorted(local(r) for r in g.objects(x, OGC.realizedBy)), where=one(g, x, OGC.where), checkable=one(g, x, OGC.checkable)))
    return sorted(rows, key=lambda d: d["order"])


def check_word(g: Graph, word: str) -> dict:
    key = norm(word).lower()
    hits = []
    for s in concepts(g):
        for kind, l in _labels(g, s):
            if kind == "local":
                continue
            if norm(l).lower() == key:
                hits.append((("pref", "alt").index(kind), s, kind, l))
                break
    concerns = concerns_mentioning(g, word) if len(key) >= 2 else []
    retired = RETIRED.get(key, "")
    quote_hits = [dict(term=r["pref"], source=r["via"].split(":", 1)[1]) for r in find(g, word) if r["via"].startswith("quote:")] if len(key) >= 2 else []
    if retired:
        return dict(word=word, registered=False, retired=retired, also=[], quote_hits=quote_hits, concerns=concerns, advice="do not use in prose; " + retired)
    if not hits:
        d = dict(word=word, registered=False, retired="", also=[], quote_hits=quote_hits, concerns=concerns, advice="not a registered label; plain English is free to use")
        if quote_hits:
            d["advice"] = "not a label here, but a cited source uses the word in a quote on " + ", ".join(f"{q['term']}" for q in quote_hits) + ": that term is the glossary's word for it"
        if any(c["status"] == "open" for c in concerns):
            d["advice"] += "; an open concern mentions the word: read it before relying on the word"
        return d
    hits.sort(key=lambda h: (h[0], str(h[1])))
    _, s, kind, l = hits[0]
    t = term_record(g, s)
    c = t["canonical"]
    d = dict(word=word, registered=True, retired="", term=t["pref"], local=t["local"], matched_as=kind, label=l, **{"class": t["class"]},
             sense=first_sentence(t["definition"]), canonical=(f"{c.get('source', '')} {c.get('locator', '')}" + (f" [{c['status']}]" if c.get("status") else "")) if c else None,
             coined_by=t["coined_by"] or None,
             also=[dict(term=one(g, h[1], SKOS.prefLabel), local=local(h[1]), label=h[3], matched_as=h[2]) for h in hits[1:]],
             quote_hits=[], concerns=concerns)
    d["advice"] = (f"an alternate label; the headword is '{t['pref']}': write " if kind == "alt" else "registered: write ") + "{term}`" + (f"{l} <{t['pref']}>" if kind == "alt" else t["pref"]) + "` in prose"
    if d["also"]:
        d["advice"] += "; the word also lands on " + ", ".join(f"{a['term']} (alt '{a['label']}')" for a in d["also"]) + ": say which sense"
    if any(x["status"] == "open" for x in concerns):
        d["advice"] += "; an open concern mentions the word"
    return d


# ---------------------------------------------------------------- verify, schema

AUTHORS = "authors"  # the quote status of the crosswalk rows: the authors' own words (the session's definitions), not a quote from a source


def _locate(g: Graph, root: Path, c) -> tuple[str, str]:
    from .verify import locate
    if cite_status(g, c) == AUTHORS:
        return AUTHORS, "the authors' own words; nothing to locate"
    return locate(g, root, c)


def verify_citations(g: Graph, root: Path, terms: list, only_src=None) -> list[dict]:
    rows = []
    for t in terms:
        for kind, c in [("canonical", g.value(t, OGC.canonical)), *[("seeAlso", x) for x in g.objects(t, OGC.seeAlso)]]:
            if c is None:
                continue
            src = g.value(c, OGC.cites)
            if only_src is not None and src != only_src:
                continue
            state, where = _locate(g, root, c)
            rows.append(dict(holder=one(g, t, SKOS.prefLabel) or one(g, t, RDFS.label).split(":")[0], citation=kind, source=local(src), posture=one(g, src, OGC.posture),
                             locator=one(g, c, OGC.locator), status=cite_status(g, c), state=state, where=where))
    return sorted(rows, key=lambda d: (d["holder"].lower(), d["citation"], d["source"], d["locator"]))


def verify_crosswalk(g: Graph, root: Path) -> list[dict]:
    """The crosswalk rows as citations: each cites the session where the definitions were presented; their quotes are the authors' words (status `authors`)."""
    rows = []
    for x in g.subjects(RDF.type, OGC.Crosswalk):
        src = g.value(x, OGC.cites)
        state, where = _locate(g, root, x)
        rows.append(dict(holder=f"crosswalk: {one(g, x, RDFS.label)}", citation="crosswalk", source=local(src), posture=one(g, src, OGC.posture),
                         locator=one(g, x, OGC.locator), status=cite_status(g, x), state=state, where=where))
    return sorted(rows, key=lambda d: (d["holder"].lower(), d["source"], d["locator"]))


def verify_term(g: Graph, root: Path, s) -> list[dict]:
    return verify_citations(g, root, [s])


def verify_source(g: Graph, root: Path, slug: str) -> list[dict] | None:
    src = resolve_source(g, slug)
    if src is None:
        return None
    return verify_citations(g, root, concepts(g), only_src=src)


def verify_all(g: Graph, root: Path) -> list[dict]:
    """Every citation in the graph: the terms', the steps' and the crosswalk rows'."""
    rows = verify_citations(g, root, concepts(g) + sorted(set(g.subjects(RDF.type, EPO.EpoStep)) | set(g.subjects(RDF.type, EPO.ContractingStep)) | {EPO.ContractingStep}, key=str))
    return rows + verify_crosswalk(g, root)


def schema(g: Graph, root: Path | None = None) -> dict:
    """The map; the shape count reads every shape file (the loaded graph carries two of them), the way `ogc shapes` does."""
    inv = {str(v): k for k, v in PREFIXES.items()}

    def qname(x):
        s = str(x)
        for ns, k in sorted(inv.items(), key=lambda kv: -len(kv[0])):
            if s.startswith(ns):
                return f"{k}:{s[len(ns):]}"
        return s
    classes = Counter(qname(o) for o in g.objects(None, RDF.type))
    props = Counter(qname(p) for p in g.predicates())
    return dict(classes=[dict(cls=c, count=n) for c, n in sorted(classes.items())],
                properties=[dict(prop=p, uses=n) for p, n in sorted(props.items())],
                counts=dict(terms=len(concepts(g)), coined=sum(1 for t in concepts(g) if one(g, t, OGC["class"]) == "coined"),
                            sources=sum(1 for _ in g.subjects(RDF.type, OGC.Source)), rulings=sum(1 for _ in g.subjects(RDF.type, OGC.Ruling)),
                            concerns=sum(1 for _ in g.subjects(RDF.type, OGC.Concern)), shapes=len(shapes_graph(root)[1]) if root is not None else sum(1 for _ in g.subjects(RDF.type, SH.NodeShape)),
                            essentials=sum(1 for _ in g.subjects(RDF.type, OGC.Trace)), crosswalk_rows=sum(1 for _ in g.subjects(RDF.type, OGC.Crosswalk))))


def ambiguous_labels(g: Graph) -> list[dict]:
    """Labels (pref or alt) that resolve to more than one term: a hover or a
    {term} role on such a label cannot be honest."""
    seen = {}
    for s in concepts(g):
        for kind, l in _labels(g, s):
            if kind != "local":
                seen.setdefault(norm(l).lower(), set()).add(s)
    return sorted((dict(label=l, terms=sorted(one(g, t, SKOS.prefLabel) for t in ts)) for l, ts in seen.items() if len(ts) > 1), key=lambda d: d["label"])


# ---------------------------------------------------------------- shapes

_PATH_OPS ={SH.inversePath: "^{}", SH.zeroOrMorePath: "{}*", SH.oneOrMorePath: "{}+", SH.zeroOrOnePath: "{}?"}


def shapes_graph(root: Path) -> tuple[Graph, dict]:
    """The shape files parsed on their own (the loaded graph carries only two of
    them); returns the merged graph and a map shape IRI -> file."""
    g = Graph()
    for k, v in PREFIXES.items():
        g.bind(k, v, replace=True)
    where = {}
    for f in SHAPE_FILES:
        part = Graph().parse(root / f)
        for s in part.subjects(RDF.type, SH.NodeShape):
            where[s] = f
        for t in part:
            g.add(t)
    return g, where


def qname(g: Graph, x) -> str:
    if isinstance(x, URIRef):
        try:
            return g.namespace_manager.normalizeUri(x)
        except Exception:
            return str(x)
    return x.n3(g.namespace_manager) if x is not None else ""


def rdf_list(g: Graph, node) -> list:
    out = []
    while node is not None and node != RDF.nil:
        out.append(g.value(node, RDF.first))
        node = g.value(node, RDF.rest)
    return out


def path_text(g: Graph, node) -> str:
    """A SHACL property path as text: predicate, sequence (a / b), alternative (a | b), inverse (^a), and the closures."""
    if isinstance(node, URIRef):
        return qname(g, node)
    if isinstance(node, BNode):
        if g.value(node, RDF.first) is not None:
            return " / ".join(path_text(g, x) for x in rdf_list(g, node))
        alt = g.value(node, SH.alternativePath)
        if alt is not None:
            return "(" + " | ".join(path_text(g, x) for x in rdf_list(g, alt)) + ")"
        for op, form in _PATH_OPS.items():
            inner = g.value(node, op)
            if inner is not None:
                return form.format(path_text(g, inner))
    return qname(g, node)


def _shape_targets(g: Graph, s) -> list[str]:
    out = [qname(g, c) for c in g.objects(s, SH.targetClass)]
    out += [f"node {qname(g, n)}" for n in g.objects(s, SH.targetNode)]
    out += [f"subjects of {qname(g, p)}" for p in g.objects(s, SH.targetSubjectsOf)]
    out += [f"objects of {qname(g, p)}" for p in g.objects(s, SH.targetObjectsOf)]
    out += ["sparql target" for _ in g.objects(s, SH.target)]
    return sorted(out)


def shapes_table(root: Path) -> list[dict]:
    g, where = shapes_graph(root)
    rows = []
    for s, f in where.items():
        rows.append(dict(id=local(s), target=_shape_targets(g, s), properties=sum(1 for _ in g.objects(s, SH.property)),
                         sparql=sum(1 for _ in g.objects(s, SH.sparql)), file=f))
    return sorted(rows, key=lambda d: (d["file"], d["id"].lower()))


def shape_record(root: Path, sid: str) -> dict | None:
    """One node shape, case-insensitive on its local name: target, property
    constraints (path, min, max, class, in, hasValue, datatype, message),
    each SPARQL constraint's message with its `sh:select` body, and the
    executor's mutations that fire it (`counterexamples`, from
    ogc.executor.MUTATION_SHAPES; round four, M5); the shape's own message
    and closed flag are None when absent."""
    from .executor import MUTATION_SHAPES
    g, where = shapes_graph(root)
    key = norm(sid).lower()
    hit = next((s for s in sorted(where, key=str) if local(s).lower() == key), None)
    if hit is None:
        return None

    def q(node, p):
        v = g.value(node, p)
        return qname(g, v) if v is not None else ""
    props = []
    for p in g.objects(hit, SH.property):
        props.append({"path": path_text(g, g.value(p, SH.path)), "min": one(g, p, SH.minCount), "max": one(g, p, SH.maxCount),
                      "class": q(p, SH["class"]), "in": [qname(g, x) if isinstance(x, URIRef) else str(x) for x in rdf_list(g, g.value(p, SH["in"]))],
                      "hasValue": q(p, SH.hasValue), "datatype": q(p, SH.datatype), "nodeKind": q(p, SH.nodeKind), "message": one(g, p, SH.message)})
    props.sort(key=lambda d: (d["path"], d["message"]))
    sparql = sorted((dict(message=one(g, x, SH.message), select=textwrap.dedent(one(g, x, SH.select)).strip()) for x in g.objects(hit, SH.sparql)), key=lambda d: (d["message"], d["select"]))
    return dict(id=local(hit), iri=str(hit), file=where[hit], target=_shape_targets(g, hit), message=one(g, hit, SH.message) or None,
                closed=one(g, hit, SH.closed) or None, properties=props, sparql=sparql,
                counterexamples=sorted(m for m, fired in MUTATION_SHAPES.items() if local(hit) in fired))


# ---------------------------------------------------------------- the EPO's classes and roles (round three, M5)

OWL = URIRef("http://www.w3.org/2002/07/owl#")


def _is_subclass(g: Graph, c, sup, seen=None) -> bool:
    seen = seen or set()
    if c == sup:
        return True
    for x in g.objects(c, RDFS.subClassOf):
        if x not in seen:
            seen.add(x)
            if _is_subclass(g, x, sup, seen):
                return True
    return False


def epo_nodes(g: Graph) -> list[tuple]:
    """(node, kind) for what `ogc epo` reads: every `owl:Class` in the epo:
    namespace (kind `class`) and every individual typed by a role class
    (kind `role`, the role handles the record's agents fill). The steps are
    left out: `ogc quote`, `ogc verify` and `ogc steps` read them."""
    classes = {c for c in g.subjects(RDF.type, URIRef(str(OWL) + "Class")) if str(c).startswith(str(EPO))}
    out = [(c, "class") for c in classes]
    for c in classes:
        if _is_subclass(g, c, EPO.Role):
            out += [(i, "role") for i in g.subjects(RDF.type, c) if str(i).startswith(str(EPO)) and i not in classes]
    return sorted(set(out), key=lambda x: str(x[0]))


def resolve_epo(g: Graph, name: str):
    """(node, kind, candidates): the EPO class or role whose local name is `name`, case-insensitive; else (None, None, near misses)."""
    key = norm(name).lower()
    nodes = epo_nodes(g)
    exact = next(((n, k) for n, k in nodes if local(n) == norm(name)), None)  # a class and its role individual differ only by case (AuthorizedRepresentativeRole, authorizedRepresentativeRole; sheet 10-49)
    if exact is not None:
        return exact[0], exact[1], []
    hits = [(n, k) for n, k in nodes if local(n).lower() == key]
    if len(hits) == 1:
        return hits[0][0], hits[0][1], []
    if hits:  # ambiguous in lower case: name the exact spellings
        return None, None, [f"epo:{local(n)}" for n, _ in hits]
    return None, None, [f"epo:{c}" for c in near(key, [local(n) for n, _ in nodes])]


def _mentions(text: str, curie: str, iri: str) -> bool:
    return bool(re.search(r"(?<![\w:])" + re.escape(curie) + r"(?![\w-])", text)) or iri in text


def epo_record(g: Graph, root: Path, node, kind: str) -> dict:
    """One EPO class or role: label, comment, superclasses (a role's types),
    subclasses and instances, the layer it is pinned at, the terms it names
    (with their headwords), the disjointness axioms in either direction, and
    the node shapes whose targets, property paths or SPARQL bodies mention it
    (the shapes' text searched for the CURIE and the IRI)."""
    curie, iri = f"epo:{local(node)}", str(node)
    pinned = g.value(node, OGC.pinnedAt)
    sg, where = shapes_graph(root)
    shapes = []
    for s in sorted(where, key=str):
        found = []
        if any(_mentions(t, curie, iri) for t in _shape_targets(sg, s)) or any(_mentions(qname(sg, x), curie, iri) for t in sg.objects(s, SH.target) for x in [t]):
            found.append("target")
        props = []
        for p in sg.objects(s, SH.property):
            props.append(path_text(sg, sg.value(p, SH.path)))
            props += [qname(sg, sg.value(p, k)) for k in (SH["class"], SH.hasValue) if sg.value(p, k) is not None]
            props += [qname(sg, x) for x in rdf_list(sg, sg.value(p, SH["in"])) if isinstance(x, URIRef)]
        if any(_mentions(t, curie, iri) for t in props):
            found.append("property")
        bodies = [one(sg, x, SH.select) for x in sg.objects(s, SH.sparql)] + [one(sg, t, SH.select) for t in sg.objects(s, SH.target)]
        if any(_mentions(b, curie, iri) for b in bodies):
            found.append("sparql")
        if found:
            shapes.append(dict(id=local(s), file=where[s], where=", ".join(found)))
    return dict(id=curie, iri=iri, kind=kind, label=norm(one(g, node, RDFS.label)), comment=norm(one(g, node, RDFS.comment)) or None,
                superclasses=sorted(qname(g, x) for x in g.objects(node, RDFS.subClassOf)) if kind == "class" else [],
                types=sorted(qname(g, x) for x in g.objects(node, RDF.type)) if kind == "role" else [],
                subclasses=sorted(qname(g, x) for x in g.subjects(RDFS.subClassOf, node)),
                instances=sorted(qname(g, x) for x in g.subjects(RDF.type, node) if isinstance(x, URIRef)) if kind == "class" else [],
                pinned_at=dict(id=qname(g, pinned), label=norm(one(g, pinned, RDFS.label))) if pinned is not None else None,
                terms=sorted((dict(local=local(t), headword=one(g, t, SKOS.prefLabel)) for t in g.objects(node, OGC["term"])), key=lambda d: d["local"]),
                disjoint_with=sorted({qname(g, x) for x in g.objects(node, URIRef(str(OWL) + "disjointWith"))} | {qname(g, x) for x in g.subjects(URIRef(str(OWL) + "disjointWith"), node)}),
                shapes=shapes)


# ---------------------------------------------------------------- blank nodes

def bnode_labels(g: Graph, rounds: int = 3) -> dict:
    """Run-independent labels for the blank nodes of a graph: a hash of each
    node's neighbourhood, refined over a few rounds so that a node's label
    also reflects the labels of the blank nodes it touches. Nodes whose
    neighbourhoods stay identical after that are numbered in an arbitrary
    order; everything else is stable across runs for the same graph."""
    nodes = {n for t in g for n in (t[0], t[2]) if isinstance(n, BNode)}
    sig = {b: "" for b in nodes}
    for _ in range(rounds):
        new = {}
        for b in nodes:
            parts = [f">{p}|{sig[o] if isinstance(o, BNode) else o.n3()}" for p, o in g.predicate_objects(b)]
            parts += [f"<{p}|{sig[s] if isinstance(s, BNode) else s.n3()}" for s, p in g.subject_predicates(b)]
            new[b] = hashlib.sha256("\n".join(sorted(parts)).encode()).hexdigest()[:12]
        sig = new
    labels, seen = {}, Counter()
    for b in sorted(nodes, key=lambda b: (sig[b], str(b))):
        seen[sig[b]] += 1
        labels[b] = f"b{sig[b]}" + (f"n{seen[sig[b]]}" if seen[sig[b]] > 1 else "")
    return labels


# ---------------------------------------------------------------- the record (C-44, ruling R-47)

WHO = [PROV.wasAttributedTo, EARL.assertedBy, EPO.approvedBy, EPO.signedBy, PROV.wasAssociatedWith]
WHEN = [PROV.generatedAtTime, PROV.startedAtTime, PROV.endedAtTime]


def record_subjects(g: Graph) -> list:
    """Every named subject of the record (the `ev:` namespace, the measles evaluation), sorted; the graph must have been loaded with the record."""
    return sorted({s for s in g.subjects() if isinstance(s, URIRef) and str(s).startswith(str(EV))}, key=str)


def record_classes(g: Graph) -> set[str]:
    """The local names of the EPO classes whose instances live only in a
    record (Attestation, Evidence, Session, Report and the other item kinds,
    roles' bearers, checks): every `epo:` class with no instance in the
    graph as loaded without the record. A query typing a variable by one of
    them answers nothing until --record loads the record."""
    OWL_CLASS = URIRef("http://www.w3.org/2002/07/owl#Class")
    typed = {c for c in g.objects(None, RDF.type)}
    return {local(c) for c in g.subjects(RDF.type, OWL_CLASS) if str(c).startswith(str(EPO)) and c not in typed}


def record_only(g: Graph, root: Path, cache: bool = True) -> dict[str, list[str]]:
    """The predicates and the classes that occur in the record and nowhere in
    the graph loaded by default, as CURIEs (round four, M1): what a query
    without --record names when its empty answer would be a lie. The set
    difference is computed once per checkout state and cached under
    .cache/, keyed on the files as the graph cache is; `ogc:derivedStep`,
    derived in memory whenever the record is loaded, is always in it."""
    from .graph import RECORD_FILE, SOURCE_FILES, _key
    if not (root / RECORD_FILE).exists():
        return {"predicates": [], "classes": []}
    paths = [root / f for f in SOURCE_FILES] + [root / RECORD_FILE]
    cp = root / ".cache" / f"ogc-record-only-{_key(paths)}.json"
    if cache and cp.exists():
        try:
            return json.loads(cp.read_text())
        except Exception:
            pass
    rec = Graph().parse(root / RECORD_FILE)
    preds = (set(rec.predicates()) - set(g.predicates())) | {OGC.derivedStep}
    classes = set(rec.objects(None, RDF.type)) - set(g.objects(None, RDF.type))
    out = {"predicates": sorted(qname(g, x) for x in preds), "classes": sorted(qname(g, x) for x in classes)}
    if cache:
        try:
            cp.parent.mkdir(exist_ok=True)
            for old in cp.parent.glob("ogc-record-only-*.json"):
                old.unlink()
            cp.write_text(json.dumps(out))
        except Exception:
            pass
    return out


def step_heads(g: Graph) -> dict:
    """Step IRI -> (order, head) as the two cycles order them: C1..C6 (1..6), then 1..6 (11..16), the order `ogc steps` prints."""
    return {str(EPO[r["step"]]): (r["order"], r["label"].split(":", 1)[0]) for r in steps_table(g)}


def _label(g: Graph, x) -> str:
    if not isinstance(x, URIRef):
        return ""
    if (x, RDF.type, EPO.EpoStep) in g or (x, RDF.type, EPO.ContractingStep) in g:
        return one(g, x, RDFS.label).split(":", 1)[0]
    return one(g, x, RDFS.label) or one(g, x, SKOS.prefLabel)


def _classes(g: Graph, n) -> list[str]:
    epo = sorted(local(t) for t in g.objects(n, RDF.type) if str(t).startswith(str(EPO)))
    return epo or sorted(local(t) for t in g.objects(n, RDF.type) if t != PROV.Agent)


def _who(g: Graph, n) -> list[str] | None:
    """Who made, signed, approved or asserted the item; None when the record names nobody."""
    return sorted({_label(g, o) or local(o) for p in WHO for o in g.objects(n, p)}) or None


def _when(g: Graph, n, preds=WHEN) -> str | None:
    """The item's date (generated, started or ended at, in that order); None when the record carries none."""
    for p in preds:
        v = g.value(n, p)
        if v is not None:
            return str(v)[:10]
    return None


def attribution(g: Graph, n) -> dict:
    """`who`, `when` and `via`: the item's own attribution and date, or, when
    it carries none, the agent and the end time of the activity that
    generated it (`prov:wasGeneratedBy`), named in `via` (round three, L9:
    the report is generated by the coverage computation, which the report
    assembler performed and ended at a time). `via` is None when nothing
    was derived."""
    who, when, via = _who(g, n), _when(g, n), None
    if who is None or when is None:
        act = next(iter(sorted(g.objects(n, PROV.wasGeneratedBy), key=str)), None)
        if act is not None:
            d_who = _who(g, act) if who is None else None
            d_when = _when(g, act, [PROV.endedAtTime, PROV.generatedAtTime, PROV.startedAtTime]) if when is None else None
            if d_who or d_when:
                who, when, via = who or d_who, when or d_when, local(act)
    return dict(who=who, when=when, via=via)


def _step(g: Graph, n, heads: dict):
    """(order, head) of the item's derived step (sheet 10-33: `ogc:derivedStep` is added in memory by ogc.graph.infer_steps through the
    model graph); a kind two steps may produce is listed at the earlier; (None, "") when no step derives."""
    found = sorted(heads[str(st)] for st in g.objects(n, OGC.derivedStep) if str(st) in heads)
    return found[0] if found else (None, "")


def record_rows(g: Graph) -> list[dict]:
    """One row per subject of the record: the record's own entity first
    (group `record`, the prov:Bundle; round three, M7; sheet 10-31), then
    the stepped items in step order (`step`), then the items without a step
    (`no-step`), then the parties and machines (`party`). Every row says
    whether it is tagged `synthetic` (sheet 10-43)."""
    heads = step_heads(g)
    entity, stepped, unstepped, parties = [], [], [], []
    for n in record_subjects(g):
        row = dict(item=local(n), iri=str(n), **{"class": ", ".join(_classes(g, n))}, label=one(g, n, RDFS.label) or one(g, n, EPO.text), **attribution(g, n),
                   synthetic=str(g.value(n, OGC.synthetic)).lower() == "true")
        order, head = _step(g, n, heads)
        if (n, RDF.type, PROV.Bundle) in g:
            entity.append(dict(group="record", step="", order=0, **row))  # ev:record, the record's own entity, the bundle
        elif (n, RDF.type, PROV.Agent) in g:
            parties.append(dict(group="party", step="", order=0, **row))
        elif order is not None:
            stepped.append(dict(group="step", step=head, order=order, **row))
        else:
            unstepped.append(dict(group="no-step", step="", order=0, **row))
    stepped.sort(key=lambda r: (r["order"], r["when"] or "", r["item"]))
    unstepped.sort(key=lambda r: (r["class"], r["item"]))
    parties.sort(key=lambda r: r["item"])
    return entity + stepped + unstepped + parties


def resolve_record_item(g: Graph, name: str):
    """(iri, candidates): the record subject whose local name is `name`, case-insensitive; else None and up to eight near misses."""
    key = norm(name).lower()
    subjects = record_subjects(g)
    hit = next((s for s in subjects if local(s).lower() == key), None)
    if hit is not None:
        return hit, []
    return None, near(key, [local(s) for s in subjects])


def record_item(g: Graph, n) -> dict:
    """Everything the record says about one item: every triple with it as
    subject (`triples`; a blank node's own triples inline, as `[ p o ; ... ]`),
    each object's label where it has one (the derived step among them, under
    `ogc:derivedStep`, as a DESCRIBE over the loaded graph shows it; round
    four, H3), and the triples that point at it
    (`referenced_by`); `who` and `when` are None when the record carries none
    and nothing can be derived through `prov:wasGeneratedBy` (then `via` names
    the generating activity)."""
    def render(o):
        if isinstance(o, BNode):
            inner = sorted((qname(g, p), render(x)) for p, x in g.predicate_objects(o))
            return "[ " + " ; ".join(f"{p} {x}" for p, x in inner) + " ]"
        return qname(g, o)
    out = [dict(predicate=qname(g, p), object=render(o), label=_label(g, o)) for p, o in g.predicate_objects(n)]
    out.sort(key=lambda t: (t["predicate"] != "rdf:type", t["predicate"], t["object"]))
    inn = [dict(subject=qname(g, s), predicate=qname(g, p), label=_label(g, s)) for s, p in g.subject_predicates(n) if isinstance(s, URIRef)]
    inn.sort(key=lambda t: (t["predicate"], t["subject"]))
    return dict(item=local(n), iri=str(n), label=one(g, n, RDFS.label) or one(g, n, EPO.text), **{"class": ", ".join(_classes(g, n))},
                step=_step(g, n, step_heads(g))[1], **attribution(g, n), synthetic=str(g.value(n, OGC.synthetic)).lower() == "true", triples=out, referenced_by=inn)
