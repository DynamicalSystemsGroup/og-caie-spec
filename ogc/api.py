"""The library: every question the OG-CAIE vocabulary answers, as a function
returning plain, sorted data. The CLI renders these."""
from __future__ import annotations

import hashlib
import re
import unicodedata
from collections import Counter
from pathlib import Path

from rdflib import RDF, RDFS, BNode, Graph, URIRef

from .graph import EARL, EPO, OGC, PROV, RUL, RUN, SH, SKOS, SRC, TERM, PREFIXES

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
    rulings = []
    for r in sorted(g.objects(s, PROV.wasDerivedFrom), key=str):
        rulings.append(dict(id=local(r), label=one(g, r, RDFS.label)))
    concerns = sorted((dict(id=local(c), status=one(g, c, OGC.status), label=one(g, c, RDFS.label)) for c in g.subjects(OGC.concernsTerm, s)), key=lambda d: d["id"])
    sci = sorted(local(t) for t in g.subjects(OGC.usesTerm, s))
    xw = sorted(one(g, x, RDFS.label) for x in g.subjects(OGC.mapsTo, s))
    canon = g.value(s, OGC.canonical)
    return dict(iri=str(s), local=local(s), pref=one(g, s, SKOS.prefLabel), definition=norm(one(g, s, SKOS.definition)),
                alts=many(g, s, SKOS.altLabel), **{"class": one(g, s, OGC["class"])}, anchor_relation=one(g, s, OGC.anchorRelation),
                canonical=citation_record(g, canon) if canon is not None else {}, see_also=sorted((citation_record(g, c) for c in g.objects(s, OGC.seeAlso)), key=lambda d: (d["source"], d["locator"])),
                scope_note=norm(one(g, s, OGC.scopeNote)), binding=one(g, s, OGC.binding), rulings=rulings, concerns=concerns, sci=sci, crosswalk=xw)


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
    """Exact, then prefix, then substring over prefLabel and altLabel, then over quote text."""
    key = norm(text).lower()
    hits = {}

    def put(t, rank, kpri, via):
        cur = hits.get(t)
        if cur is None or (rank, kpri) < (cur["rank"], cur["kpri"]):
            hits[t] = dict(rank=rank, kpri=kpri, match=["exact", "prefix", "substring"][rank], via=via, pref=one(g, t, SKOS.prefLabel),
                           local=local(t), **{"class": one(g, t, OGC["class"])}, source=local(g.value(g.value(t, OGC.canonical), OGC.cites)) if g.value(t, OGC.canonical) is not None else "")

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
        rows.append({"term": t["pref"], "local": t["local"], "class": t["class"], "source": t["canonical"].get("source", ""),
                     "locator": t["canonical"].get("locator", ""), "status": t["canonical"].get("status", "")})
    return sorted(rows, key=lambda r: r["term"].lower())


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
        for holder, c in [("canonical", g.value(t, OGC.canonical)), *[("seeAlso", x) for x in g.objects(t, OGC.seeAlso)]]:
            if c is not None and g.value(c, OGC.cites) == s:
                cits.append(dict(term=one(g, t, SKOS.prefLabel), holder=holder, locator=one(g, c, OGC.locator), quote=one(g, c, OGC.quote), status=cite_status(g, c)))
    for x in g.subjects(OGC.cites, s):
        if (x, RDF.type, OGC.Crosswalk) in g:
            cits.append(dict(term=f"crosswalk: {one(g, x, RDFS.label)}", holder="crosswalk", locator=one(g, x, OGC.locator), quote=one(g, x, OGC.quote), status=cite_status(g, x)))
    return dict(slug=slug, label=one(g, s, RDFS.label), rank=one(g, s, OGC.rank), kind=one(g, s, OGC.kind), posture=one(g, s, OGC.posture),
                url=one(g, s, OGC.url), digest=one(g, s, OGC.digest), status=one(g, s, OGC.status), retrieval=one(g, s, OGC.retrievalNote),
                licence=one(g, s, OGC.licenceNote), permission=one(g, s, OGC.permissionStatement), snapshots=snaps,
                citations=sorted(cits, key=lambda d: (d["term"].lower(), d["holder"], d["locator"])))


def sources_table(g: Graph, rank=None, posture=None, uncited=False) -> list[dict]:
    counts = Counter()
    for t in concepts(g):
        for c in [g.value(t, OGC.canonical), *g.objects(t, OGC.seeAlso)]:
            if c is not None:
                counts[g.value(c, OGC.cites)] += 1
    for x in g.subjects(RDF.type, OGC.Crosswalk):
        counts[g.value(x, OGC.cites)] += 1
    rows = []
    for s in sorted(g.subjects(RDF.type, OGC.Source), key=str):
        r, p = one(g, s, OGC.rank), one(g, s, OGC.posture)
        if rank and r != rank:
            continue
        if posture and p != posture:
            continue
        if uncited and counts[s] > 0:
            continue
        rows.append(dict(slug=local(s), rank=r, posture=p, kind=one(g, s, OGC.kind), citations=counts[s],
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
    return dict(id=rid, order=int(one(g, r, OGC.order) or 0), text=one(g, r, OGC.rulingText), change=one(g, r, OGC.changeNote),
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
            for field, val in (("text", one(g, r, OGC.rulingText)), ("change", one(g, r, OGC.changeNote))):
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
    """The seven EPO steps with the canon step each matches (R-31)."""
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
    for holder, c in [("canonical", g.value(st, OGC.canonical)), *[("seeAlso", x) for x in sorted(g.objects(st, OGC.seeAlso), key=lambda x: (str(g.value(x, OGC.cites)), str(g.value(x, OGC.locator))))]]:
        if c is not None:
            out.append(dict(holder=holder, **{k: v for k, v in citation_record(g, c).items() if k != "node"}))
    return out


def crosswalk(g: Graph, klass=None, source=None) -> list[dict]:
    """One row per term: its class, anchor relation, canonical source and locator, and binding."""
    rows = []
    for t in all_terms(g).values():
        if klass and t["class"] != klass:
            continue
        if source and t["canonical"].get("source", "").lower() != norm(source).lower():
            continue
        rows.append({"term": t["pref"], "class": t["class"], "relation": t["anchor_relation"], "source": t["canonical"].get("source", ""),
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
             sense=first_sentence(t["definition"]), canonical=f"{c.get('source', '')} {c.get('locator', '')}" + (f" [{c['status']}]" if c.get("status") else ""),
             also=[dict(term=one(g, h[1], SKOS.prefLabel), local=local(h[1]), label=h[3], matched_as=h[2]) for h in hits[1:]],
             quote_hits=[], concerns=concerns)
    d["advice"] = (f"an alternate label; the headword is '{t['pref']}': write " if kind == "alt" else "registered: write ") + "{term}`" + (f"{l} <{t['pref']}>" if kind == "alt" else t["pref"]) + "` in prose"
    if d["also"]:
        d["advice"] += "; the word also lands on " + ", ".join(f"{a['term']} (alt '{a['label']}')" for a in d["also"]) + ": say which sense"
    if any(x["status"] == "open" for x in concerns):
        d["advice"] += "; an open concern mentions the word"
    return d


# ---------------------------------------------------------------- verify, schema

def verify_citations(g: Graph, root: Path, terms: list, only_src=None) -> list[dict]:
    from .verify import locate
    rows = []
    for t in terms:
        for holder, c in [("canonical", g.value(t, OGC.canonical)), *[("seeAlso", x) for x in g.objects(t, OGC.seeAlso)]]:
            if c is None:
                continue
            src = g.value(c, OGC.cites)
            if only_src is not None and src != only_src:
                continue
            state, where = locate(g, root, c)
            rows.append(dict(holder=one(g, t, SKOS.prefLabel) or one(g, t, RDFS.label).split(":")[0], citation=holder, source=local(src), posture=one(g, src, OGC.posture),
                             locator=one(g, c, OGC.locator), status=cite_status(g, c), state=state, where=where))
    return sorted(rows, key=lambda d: (d["holder"].lower(), d["citation"], d["source"], d["locator"]))


def verify_term(g: Graph, root: Path, s) -> list[dict]:
    return verify_citations(g, root, [s])


def verify_source(g: Graph, root: Path, slug: str) -> list[dict] | None:
    src = resolve_source(g, slug)
    if src is None:
        return None
    return verify_citations(g, root, concepts(g), only_src=src)


def verify_all(g: Graph, root: Path) -> list[dict]:
    return verify_citations(g, root, concepts(g) + sorted(set(g.subjects(RDF.type, EPO.EpoStep)) | set(g.subjects(RDF.type, EPO.ContractingStep)) | {EPO.ContractingStep}, key=str))


def schema(g: Graph) -> dict:
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
                            concerns=sum(1 for _ in g.subjects(RDF.type, OGC.Concern)), shapes=sum(1 for _ in g.subjects(RDF.type, SH.NodeShape)),
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

SHAPE_FILES = ["shapes/epo.shapes.ttl", "shapes/model.shapes.ttl", "shapes/rulings.shapes.ttl", "shapes/glossary.shapes.ttl"]
_PATH_OPS = {SH.inversePath: "^{}", SH.zeroOrMorePath: "{}*", SH.oneOrMorePath: "{}+", SH.zeroOrOnePath: "{}?"}


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
    constraints (path, min, max, class, in, hasValue, datatype, message) and
    each SPARQL constraint's message."""
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
    sparql = sorted(one(g, x, SH.message) for x in g.objects(hit, SH.sparql))
    return dict(id=local(hit), iri=str(hit), file=where[hit], target=_shape_targets(g, hit), message=one(g, hit, SH.message),
                closed=one(g, hit, SH.closed), properties=props, sparql=sparql)


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
    """Every named subject of the record (the `run:` namespace), sorted; the graph must have been loaded with the record."""
    return sorted({s for s in g.subjects() if isinstance(s, URIRef) and str(s).startswith(str(RUN))}, key=str)


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


def _who(g: Graph, n) -> list[str]:
    return sorted({_label(g, o) or local(o) for p in WHO for o in g.objects(n, p)})


def _when(g: Graph, n) -> str:
    for p in WHEN:
        v = g.value(n, p)
        if v is not None:
            return str(v)[:10]
    return ""


def record_rows(g: Graph) -> list[dict]:
    """One row per item of the record: the stepped items in step order (group
    `step`), then the items without a step (`no-step`), then the parties and
    machines (`party`). The record entity itself is left out."""
    heads = step_heads(g)
    stepped, unstepped, parties = [], [], []
    for n in record_subjects(g):
        if set(g.objects(n, RDF.type)) == {PROV.Entity}:
            continue  # run:record, the record's own entity, is not an item of it
        row = dict(item=local(n), iri=str(n), **{"class": ", ".join(_classes(g, n))}, label=one(g, n, RDFS.label) or one(g, n, EPO.text), who=_who(g, n), when=_when(g, n))
        st = g.value(n, EPO.step)
        if (n, RDF.type, PROV.Agent) in g:
            parties.append(dict(group="party", step="", order=0, **row))
        elif st is not None and str(st) in heads:
            order, head = heads[str(st)]
            stepped.append(dict(group="step", step=head, order=order, **row))
        else:
            unstepped.append(dict(group="no-step", step="", order=0, **row))
    stepped.sort(key=lambda r: (r["order"], r["when"], r["item"]))
    unstepped.sort(key=lambda r: (r["class"], r["item"]))
    parties.sort(key=lambda r: r["item"])
    return stepped + unstepped + parties


def resolve_record_item(g: Graph, name: str):
    """(iri, candidates): the record subject whose local name is `name`, case-insensitive; else None and the local names containing it."""
    key = norm(name).lower()
    subjects = record_subjects(g)
    hit = next((s for s in subjects if local(s).lower() == key), None)
    if hit is not None:
        return hit, []
    return None, [local(s) for s in subjects if key and key in local(s).lower()][:8]


def record_item(g: Graph, n) -> dict:
    """Everything the record says about one item: every triple with it as
    subject (a blank node's own triples inline, as `[ p o ; ... ]`), each
    object's label where it has one, and the triples that point at it."""
    def render(o):
        if isinstance(o, BNode):
            inner = sorted((qname(g, p), render(x)) for p, x in g.predicate_objects(o))
            return "[ " + " ; ".join(f"{p} {x}" for p, x in inner) + " ]"
        return qname(g, o)
    out = [dict(predicate=qname(g, p), object=render(o), label=_label(g, o)) for p, o in g.predicate_objects(n)]
    out.sort(key=lambda t: (t["predicate"] != "rdf:type", t["predicate"], t["object"]))
    inn = [dict(subject=qname(g, s), predicate=qname(g, p), label=_label(g, s)) for s, p in g.subject_predicates(n) if isinstance(s, URIRef)]
    inn.sort(key=lambda t: (t["predicate"], t["subject"]))
    heads = step_heads(g)
    st = g.value(n, EPO.step)
    return dict(item=local(n), iri=str(n), label=one(g, n, RDFS.label) or one(g, n, EPO.text), **{"class": ", ".join(_classes(g, n))},
                step=heads[str(st)][1] if st is not None and str(st) in heads else "", who=_who(g, n), when=_when(g, n), out=out, **{"in": inn})
