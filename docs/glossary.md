# Glossary

Terms are used, not owned. Each term cites exactly one canonical definition,
chosen from the highest-ranked source that defines it:

1. **ISO 9000:2026**, *Quality management: fundamentals and vocabulary*, the default for every quality and process term;
2. **SEVOCAB**, the IEEE Computer Society's Software and Systems Engineering Vocabulary, for the systems-engineering and testing terms ISO 9000 lacks;
3. **NIST AI 700-2**, the ARIA pilot evaluation report, for the AI-evaluation terms;
4. **W3C** specifications (PROV-O, EARL, SHACL, SKOS) for the technical binding only, never for a narrative definition.

A few single-purpose sources sit in reserve: ISO/IEC 17000 for *attestation*
and *object of conformity assessment*;
Hawkins, Kelly, Knight and Graydon 2011 for *appropriateness* and *sufficiency*;
Gruber 1993 and Hogan et al. 2021 for *ontology* and *knowledge graph*; IEC
60050-351, the control-technology vocabulary, for *trajectory* and the feedback
reading of a *test strategy*; and the VIM (JCGM 200:2012), restated by NIST TN
1297, for *repeatability*, *reproducibility* and *measurement uncertainty*.

Three classes of term. **Adopted** terms are used exactly as the source
defines them. **Refined** terms carry a typed anchor to a standard term and
keep the source's word as an alternative label. **Coined** terms are the
three this project owns: Domain-Specific Ontology, Evaluation Process
Ontology, and OG-CAIE.

One word is used against the grain of its source, and the glossary says so:
*conformance*, deprecated by ISO 9000 as a synonym of *conformity*, is reclaimed
for the machine-checked, correctly constructed record (ruling R-16).

The narrative definition is plain language with no citations and may be
lifted into the paper. The quote is verbatim from the source. Status says how
the quote was checked: *machine* (located in the content-hashed snapshot by
the test suite) or *human* (verified by a named person on a date). A third
status, *pending*, marks a quote transcribed from a browsing platform and
awaiting verification; at this writing no quote is pending.

```{include} ../generated/glossary.md
```

## Sources

The register is `sources/sources.ttl`. Committed snapshots live under
`sources/archive/`; held-locally sources are referenced by content hash only.
This work's CC BY-SA licence does not extend to the sources.

```{include} ../generated/sources.md
```
