# og-caie-spec: working rules

Executable specification of Ontology-Grounded Contextual AI Evaluation
(OG-CAIE). Plan of record: `~/.claude/plans/i-need-to-build-nifty-beaver.md`
(Z approved 2026-09-05). Sibling of `vendor-fraud-review-formal`; method for
sources and rulings borrowed from `mission-twin-glossary`.

## Vocabulary: use terms, don't own them

- One canonical citation per term, chosen by precedence: (1) ISO 9000:2026,
  (2) SEVOCAB, (3) NIST AI 700-2 (NIST AI RMF for TEVV only), (4) W3C / OMG
  for technical binding only, never for a narrative definition. Lower-ranked
  sources may appear only as `ogc:seeAlso`.
- Coinage is exactly three: Domain-Specific Ontology, Evaluation Process
  Ontology, OG-CAIE. A fourth needs a ruling first.
- Refined terms carry a typed anchor (`specializes` / `corresponds` /
  `synonym`) and keep the source's word as `skos:altLabel`.
- Say **conformity** (ISO 9000:2026 3.5.9 deprecates "conformance"); use
  `sh:conforms` only for the SHACL act.
- Attestation = outcome + **appropriateness** (of the declared context) +
  **sufficiency** (of the evidence). Never "adequacy" (ruling R-08).
- Prose: no em-dashes; short sentences; every glossary term used in docs
  must be in the glossary.

## Sources

- `sources/sources.ttl` is the register; every citation names a registered
  source with a locator; adopted and refined terms carry a verbatim quote.
- Redistribution posture per source: `committed` (public domain, W3C
  licence, CC with attribution), `heldLocally` (hash committed, file under
  `sources/local/`, gitignored: SEBoK v2.14, ISO 9000:2026 screenshots,
  SEVOCAB PDF, INCOSE GtWR sheet), `citeOnly` (quote verified by a named
  person on a date). Ruling R-04.
- SEVOCAB quotes carry the IEEE permission statement the PDF requires.

## Rulings

- Concerns and rulings live in `rulings/adjudications.ttl`; a ruling is Z's
  words verbatim, attributed and dated. File a concern the moment it
  surfaces; never buffer.

## Gate

- `bash checks/run-checks.sh` is the only verdict. Report success only from
  its `CHECKS: PASS` line and `checks/out/report.json`. No `|| true`, no
  filtered output, no conditional steps.
- Pre-push hook runs the gate (`git config core.hooksPath checks/hooks`).
- TDD: tests before substrate; targeted tests inline; full gate at slice
  checkpoints.

## Git

- No `Co-Authored-By` trailer unless Z explicitly delegates a substantive
  decision to Claude, and then only on that commit.
- Commit on green; push redeploys GitHub Pages.

## Toolchain

- OpenSysML v0.4.3 pinned by digest (`toolchain/`). v0.4.3 accepts
  `action def` with `first ... then ...` successions and `perform action`;
  `interface` usages must be declared before `part` usages in an assembly;
  `-satisfy` on a package with no verification def exits 2.
