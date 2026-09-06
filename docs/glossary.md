# Glossary

The front page ends at the bridge from a plain account of science to the
engineering standards for evaluation. This chapter gives the terms on the
far side of that bridge their definitions: rigorous, cited verbatim, and not
exhaustive. It lists exactly the terms this site uses. The full register of
59 terms is generated from the same graph for the paper.

## The map of the site

- **Glossary**, this chapter: the terms, their canonical definitions, and
  the sources they rest on.
- **Assemblage**: the human and machine parts of an evaluation wired along
  typed ports, the seven-step process, and the wiring rules. It is being
  divided into two chapters, the contracting of an evaluation and the
  evaluation itself.
- **Record**: the measles evaluation record, its conformance to the process
  shapes, coverage recomputed by query, and the recommendation traced back.
- **Rulings**: every interpretive choice, in the adjudicator's words.
- **Conclusion**: what the specification encodes, in the front page's terms.

## Vocabulary discipline

Terms are used, not owned. Each term cites exactly one canonical definition,
chosen from the highest-ranked source that defines it: ISO 9000:2026,
*Quality management: fundamentals and vocabulary*, for every quality and
process term; SEVOCAB, the IEEE Computer Society's Software and Systems
Engineering Vocabulary, for the systems-engineering and testing terms ISO
9000 lacks; NIST AI 700-2, the ARIA pilot evaluation report, for the
AI-evaluation terms; and W3C specifications (PROV-O, EARL, SHACL, SKOS) for
the technical binding only, never for a narrative definition. A few
single-purpose sources sit in reserve, named in the sources table below.

Exactly four terms are coined, with their shorthands:
{term}`Contextual AI Evaluation` (CAIE), {term}`OG-CAIE`,
{term}`Evaluation Process Ontology` (EPO) and
{term}`Domain-Specific Ontology` (DSO). Everything else is grounded in
cited standards and literature. *Adopted* terms are used exactly as the
source defines them; *refined* terms carry a typed anchor to a standard
term and keep the source's word as an alternative label. One word is used
against the grain of its source, and says so: {term}`conformance`,
deprecated by ISO 9000 as a synonym of {term}`conformity`, is reclaimed for
the machine-checked, correctly constructed {term}`evaluation record`.

Every quote is verified, by machine against a content-hashed snapshot or by
a named person against the source on a date; no quote is pending.

## How to navigate

Hover any highlighted term on any page to see its definition. The entries
below are exactly those terms: the narrative definition, then the canonical
source with its locator and verbatim quote, then the alternative labels and
the ruling the term rests on. Terms the site's prose does not yet reach,
such as test case, knowledge graph and authoritative reference, stay in the
full register until a chapter needs them.

The vocabulary graph answers directly from the command line: `uv run -q ogc
term probe` gives one entry with its citations, rulings and the essentials
it is stated in; `ogc define`, `ogc quote` and `ogc verify` give the
definition, the verbatim quotes and where each quote was found; `ogc find`
searches labels and quotes; `ogc check-word` says whether a word is a
headword, an alternative label or retired, and what to write; `ogc sci`,
`ogc rulings`, `ogc concerns` and `ogc sources` read the rest of the
record, and `ogc crosswalk` prints the anchor table or, with a flag, the
bridge rows of the front page; `ogc sparql` takes a read-only query. Every
answer starts with the command and the commit it was read at, so it can be
cited. The tool is a port of the Mission Twin glossary's `mtg` (ruling
R-29).

```{include} ../generated/key-terms.md
```

## Sources

The register is `sources/sources.ttl`. Committed snapshots live under
`sources/archive/`; held-locally sources are referenced by content hash only.
This work's CC BY-SA licence does not extend to the sources.

```{include} ../generated/sources.md
```
