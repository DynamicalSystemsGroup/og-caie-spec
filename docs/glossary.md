# Glossary

The front page ends at the bridge from a plain account of science to the
engineering standards for evaluation. This chapter gives the terms on the
far side of that bridge their definitions: rigorous, cited verbatim, and not
exhaustive. It lists exactly the terms this site uses. The full register of
59 terms is generated from the same graph for the paper.

## The map of the site

Eight pages, each a view of the model in the repository. The front page
sets the bar for science in plain terms and crosses the bridge into the
standards;
this page gives the terms and the two cycles; **Contracting** is the outer
cycle, from need to acceptance; **The evaluation** is the inner cycle,
scope to report; **The nested model** shows why the two are one model; **What
the record proves** runs the checks; **Rulings** is the judgment record;
the **Conclusion** returns to the front page's terms. Each chapter from Contracting on keeps
one rhythm: what the standards say, the specification, the walkthrough,
what was checked, and there is more in the model. The assemblage and record
pages remain until their chapters are written.

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

## Two cycles, and the canon they match

Work on an evaluation happens in two cycles, and neither is invented. The
outer cycle is the contracting lifecycle, from the sponsor's need to its
acceptance of the delivery: its actors are the parties named above, and its
six steps are the ISO/IEC/IEEE 15288 agreement processes as the SEBoK
describes them, ISO/IEC 17000's access, scheme and acceptance, ISO 9000's
{term}`contract`, and the ISO/IEC/IEEE 29119-2 test environment and
completion report. The inner cycle is the {term}`Evaluation Process
Ontology <Evaluation Process Ontology>`, performed between access and
delivery: its six steps are the 15288 stakeholder-needs and
system-requirements processes, the 29119-2 test strategy and planning, test
execution and test completion processes, and ISO/IEC 17000's own function,
review, decision and attestation (ruling R-31).

The distinction matters for what the record must say. What the contract pins
is the first layer of assumptions: the counterparties, the test item, the
frame of the requirements and the method. The evaluation takes those as
given, documents them, and cannot change them. What the evaluation pins is
the second layer: the operational environment, the requirement set, the DSO
release, the plan. Every item kind in the record declares which layer fixes
it, and a shape checks that the first layer is closed before the second
opens (ruling R-32). In the model the two cycles are one nested model
(ruling R-33): the contracting lifecycle's fulfil step is a black box typed
by the evaluation process, its inputs the agreement and the access the
contract pinned, its outputs the report and the recommendation the delivery
carries; the evaluation process is that box opened, and it conforms to the
interface above it by typing, with a shape checking that every input is fed
and every output used. What this specification adds to the standards is
only the executable form: each step's inputs and outputs typed, each seam
wired, each record checked.

```{include} ../generated/steps.md
```

## Sources

The register is `sources/sources.ttl`. Committed snapshots live under
`sources/archive/`; held-locally sources are referenced by content hash only.
This work's CC BY-SA licence does not extend to the sources.

```{include} ../generated/sources.md
```
