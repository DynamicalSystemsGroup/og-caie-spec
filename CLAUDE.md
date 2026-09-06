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
- Coinage is exactly four, with shorthands (R-29): Domain-Specific Ontology
  (DSO), Evaluation Process Ontology (EPO), Contextual AI Evaluation (CAIE),
  OG-CAIE (CAIE performed with the EPO and DSO method). A fifth needs a
  ruling first.
- Two cycles, twelve steps, each citing the canon step it matches (R-31,
  R-32; the contracting lifecycle pins the first layer of assumptions, the
  evaluation the second; ogc:pinnedAt on every item class):
  SEBoK/15288 processes, 29119-2 test processes via SEVOCAB, ISO/IEC
  17000 functions); a new step needs a matching citation, never a coinage.
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
- Three actor categories, all roles within the testing organization (R-10,
  R-23): **domain expert** (DSO, appropriateness, plan approval, attestation),
  **evaluation operator** (requirements, plan, probes, evidence,
  recommendation; never attests) and one **account executive** (signs the
  contract, delivers the report; never judges). Parties (R-21): sponsor
  organization (customer), testing organization (provider), accountable
  organization (first party), affected populations [0..*].
- The worked example names Mala, Annie and Theo: synthetic case, real
  people's roles recognised, no attestation made by them (R-23).
- Prose: no em-dashes; short sentences; every glossary term used in docs
  must be in the glossary. Reference key terms with `{term}` roles; the
  glossary page renders exactly the referenced terms (hover definitions);
  the full table is generated for the paper only (R-29).
- The arc (R-29, R-30): the front page and the conclusion are the
  bookends, why and what, grounded in Popper ("CAIE would be science if it
  covers these things"; "OG-CAIE demonstrably covers these things"). The
  inner chapters are what and how, achieved through the engineering
  standards, in theory by the executable spec and in practice by the worked
  example. The restriction is on using Popper's senses inside, not on the
  ordinary words (a test bans only the name and falsifiability's forms; the
  sense rule is read). Chapters are scoped one at a time, working forward.

## Presentation over representation (R-34)

- The site is a view; the repository is the model. Nothing on a page may
  say what the graphs cannot answer by query; numbers and tables come from
  `generated/` fragments, never typed by hand.
- Chapter pages (contracting, evaluation, model, guarantees) follow five
  titled admonition blocks in order: What the standards say; The
  specification; The walkthrough; Checked; There is more in the model.
  Specification and walkthrough always appear as a pair; the walkthrough is
  the measles record for exactly the rule the specification states.
- Calibrated for a human reader: one rule, one table, one concrete row a
  reader can hold in mind; everything larger lives behind "there is more
  in the model" and is reached by `ogc` or the files. 400 to 1,400 words of
  prose per chapter page, tested.
- Every SCI carries `ogc:page` (contracting, evaluation, guarantees) and is
  rendered on that page only.

## Ask the graph, never grep it

- `uv run -q ogc <command>` (schema, find, term, define, quote, verify,
  list, source, sources, ruling, rulings, concern, concerns, sci, crosswalk,
  check-word, sparql, doctor) is the reader of the vocabulary, sources,
  rulings and essentials; the skill `.claude/skills/ogc-glossary/SKILL.md`
  says how. Never answer a vocabulary question from memory or by grepping
  the Turtle. `ogc doctor` runs in the gate; a label that resolves to two
  terms fails it (alternative labels that repeat a headword carry the sense
  in parentheses).

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
- TDD: tests before substrate. Lambda discipline (Z, 2026-09-06): targeted
  tests inline, then commit on the fast feed; the full gate runs in the
  background as the slow bar; push only after it prints `CHECKS: PASS`;
  CI watched to conclusion.

## Git

- The work is co-authored by Michael Zargham and Julie Hollek (GitHub jkru).
  Every commit carries the trailer
  `Co-authored-by: Julie Hollek <8205326+jkru@users.noreply.github.com>`.
- No Claude `Co-Authored-By` trailer unless Z explicitly delegates a
  substantive decision to Claude, and then only on that commit.
- Commit on green; push redeploys GitHub Pages.

## Model (R-22)

- SysML is structure only: part defs, port defs, interface defs, the
  two action defs (contracting lifecycle, evaluation), the assembly, and a
  run that binds names. No
  requirement defs, no `-satisfy`, no value constraints (v0.4.3 cannot
  quantify over collections anyway).
- The canonical structure is the pruned RDF rendering
  `model/og-caie.model.ttl` (`scripts/prune_model.py`: term map
  `model/sysml_term_map.csv`, manifest, `TRIPLE_BUDGET` with a rationale,
  pattern from ADCS-lifecycle-demo). Committed; the gate regenerates it
  byte-identically. Wiring rules are SHACL M-shapes over that graph;
  value and provenance rules are S-shapes over the record. The essentials
  SCI-01..12 live in `model/trace.ttl`.
- Actors perform activities; activities have precise inputs and outputs
  (R-24). One port def per item kind, one item kind per activity output;
  never reuse another actor's output port for a different activity
  (delivery is not recommending). DeterminationWrite is the one supplier
  port two roles carry, because either expert may determine (R-21).
- Input wires are unique, output wires may be shared because what flows
  is information whose use is nondestructive (R-25): one output port per
  item kind per actor, fanned out to its readers.
- One nested model (R-33): the contracting lifecycle is the outer action
  def; its `fulfil` step is `action fulfil : EvaluationProcess`, a black
  box whose inputs (agreement, access) and outputs (report, recommendation)
  are bound by `flow` from and to the contracting steps; the evaluation
  process is the drill-down and conforms by typing (shape M4-Nesting).
  The assembly performs one action, the contracting lifecycle. Deeper
  refinement follows the same pattern: type a step by an action def, bind
  its parameters, never restate its interface.
- Wiring rules are defined over kinds of parts and kinds of ports and are
  checked locally (R-26): at the part (inputs present, outputs go
  somewhere) and at the wire (output port on a part to input port on a
  part). The EPO is a process DAG; loops only by ruling.
- Adding a `sysml:` term to the graph means adding a row to the term map
  with a rationale; a bigger graph means bumping the budget with one.

## Next (C-30, open)

- Z validates the model block by block and wire by wire; then a
  computational demonstration that the EPO guarantees a complete record
  with full traceability and coverage (every run conforms to S0..S8).

## Toolchain

- OpenSysML v0.4.3 pinned by digest (`toolchain/`). `-validate -strict`;
  `accept` is a keyword (a step is `acceptDelivery`); a `flow` end must use
  dot notation on both sides, so an action def's own parameter is bound to a
  step's with `bind step.param = param;`. `-convert ttl` writes Turtle to
  stdout, deterministically, using the OMG
  `sysml:` vocabulary plus `sysx:` for tool-specific facts (interface ends
  as `sysx:relatedFeature` feature-chain expressions). SHACL-SPARQL
  constraints may not contain VALUES; use BIND unions. Write successions
  as `succession first A then B;`; `interface` usages must be declared
  before `part` usages in an assembly; check the exit code of the sysml
  process itself, never of a pipeline after it.
