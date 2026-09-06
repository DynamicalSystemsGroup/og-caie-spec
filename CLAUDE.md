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
- **conformity** = fulfilment of a requirement by the system (ISO 9000:2026
  3.5.9, attested by a person). **conformance** = the record correctly
  constructed to the EPO shapes (machine-checked; ruling R-16 reclaims the
  word ISO deprecates, on purpose). Never call the SHACL check "validation".
- Attestation = outcome + **appropriateness** (of the declared context) +
  **sufficiency** (of the evidence). Never "adequacy" (ruling R-08).
- **Evidence is the domain, determination the codomain** (R-18, R-20):
  evidence is collected material bearing on one criterion's expected result;
  a determination rules on it with an EARL outcome (passed, failed, cantTell;
  never a Boolean); an attestation aggregates determinations. Evidence exists
  at probe, session or suite level.
- A probe is applied at one **turn** of a **session**; a session's ordered
  pairs are its **trajectory**; a test plan's means are probes or a **test
  strategy** (state feedback policy) (R-13).
- Headword **test item**; prose may say system under test (R-19).
- Two kinds of **technical expert** on the evaluation team: domain expert and
  AI evaluation expert (R-10).
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
- Licence: CC BY-SA 4.0 for the whole work, no Apache split; the licence does
  not extend to source materials (Z, 2026-09-05). Framing: an open standards
  activity under development with a computational implementation pathway.

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

- The work is co-authored by Michael Zargham and Julie Hollek (GitHub jkru).
  Every commit carries the trailer
  `Co-authored-by: Julie Hollek <8205326+jkru@users.noreply.github.com>`.
- No Claude `Co-Authored-By` trailer unless Z explicitly delegates a
  substantive decision to Claude, and then only on that commit.
- Commit on green; push redeploys GitHub Pages.

## Toolchain

- OpenSysML v0.4.3 pinned by digest (`toolchain/`). `-validate -strict`
  accepts `action def` with bare `first A then B;` successions, but
  `-satisfy` then fails on a `perform action` with "action has multiple
  initial nodes"; write successions as `succession first A then B;` (or the
  `then action` chaining form), which both validate and satisfy.
  `interface` usages must be declared before `part` usages in an assembly;
  `-satisfy` on a package with no verification def exits 2; check the exit
  code of the sysml process itself, never of a pipeline after it.
