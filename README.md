# og-caie-spec

**Ontology-Grounded Contextual AI Evaluation (OG-CAIE) as an executable
specification.** Site: <https://dynamicalsystemsgroup.github.io/og-caie-spec/>

The process Humane Intelligence and Dynamical Systems Group use to evaluate a
deployed AI system against the needs of a specific domain, written down as:

- a **glossary** whose every term cites one canonical definition (ISO 9000:2026,
  SEVOCAB, NIST AI 700-2, W3C), with exactly four coined terms;
- a **SysML v2 model** (OpenSysML v0.4.3) of the contracting lifecycle with
  the Evaluation Process Ontology nested inside it, and of the human and
  machine assemblage that runs it: structure only, rendered to RDF as the
  canonical graph; thirteen essentials, each tagged machine-verified or
  human-validated, live beside it in `model/trace.ttl`;
- one **evaluation record** (PROV-O + EARL), the measles evaluation of the
  chatbot example, a bundle checked by SHACL shapes, with counterexamples
  that must fail, each the record with one change;
- a **rulings register** holding every interpretive choice verbatim.

## Status (2026-09-07)

- **Glossary: ratified.** 66 terms, 4 coined (DSO, EPO, CAIE, OG-CAIE),
  settled through 51 rulings (R-01 to R-51) recorded verbatim in
  `rulings/adjudications.ttl`. 91 quotes are machine-located in
  content-hashed snapshots or, where the source is held locally, in its
  committed digest, 56 verified by Z against the ISO screenshots or
  the browsing platforms; none pending. Concerns C-25, C-30, C-43 and C-45 are open.
- **Both cycles are bound to the canon (R-31, R-32).** Each step cites the
  process step it matches: SEBoK's account of the ISO/IEC/IEEE 15288
  acquisition, stakeholder needs and system requirements processes; the
  ISO/IEC/IEEE 29119-2 test strategy and planning, execution and completion
  processes via SEVOCAB; ISO/IEC 17000's review, decision and attestation.
  The contracting lifecycle (need, propose, agree, access, deliver, accept)
  cites its canon step by step: SEBoK's business or mission analysis and
  account of proposals, ISO/IEC/IEEE 15288's agreement processes for the
  agreement itself,
  ISO 9000's contract, the 29119-2 test environment and completion report
  and SEVOCAB's acceptance (sheet 10-22); every item kind says which layer pins it. The
  sponsor's mission and obligations towards the affected populations open
  the record (R-37, R-38).
- **Site: a presentation layer over the model (R-34), seven pages and
  six appendices.** The
  front page runs from why this counts as science to the bridge into the
  engineering standards; the vocabulary page shows exactly the terms the
  site uses, with hover definitions; four chapters (Stakeholders and
  contracting, Context and evaluation, A nested lifecycle, Records and
  reporting) each pair the
  specification with the measles walkthrough in five headed parts and close
  with the separation principle; the conclusion reads the crosswalk
  backwards. Figures are views from a registry (`ogc/views.py`), each
  captioned with what it brings into focus and leaves out (R-38).
  Appendix A is the sample report for the synthetic case (`report/`,
  R-51), a d3 dashboard rendered from the record that answers the
  sponsor's question and nothing else; Appendix B opens the same model as a knowledge graph explorer
  (`explorer/`, R-39), rendered from the RDF with the `ogc` command on
  every node and an in-browser SPARQL box; Appendix C's notebooks run the
  checks each chapter claims (`notebooks/`); Appendix D is the rulings, the
  judgments the model is grounded in (R-41); Appendix E reviews the
  toolchain, rendered from the lock file, the pinned digests, the gate and
  the workflow, with the reviewer recipe (R-43); Appendix F is the works
  cited, rendered from the source register as BibTeX, with each chapter
  closing on the sources it cites (R-48).
- **Model: revised (R-21 to R-38), draft.** SysML holds structure only; the
  pruned RDF rendering `model/og-caie.model.ttl` is the canonical structure
  (R-22), checked by wiring shapes M1 to M5 over kinds of parts and ports:
  four parties, three actor categories within the testing organization, the
  six-step EPO nested as the fulfil step of the contracting lifecycle (one
  model, R-33), both process DAGs, 76 ports and 44 seams, every input wired
  once and every output somewhere, the sponsor's signatory as the person who
  signs, approves and accepts for it (R-50), and the sponsor's obligation to
  the affected populations as a relation. Four model counterexamples fail their
  shape. The essentials SCI-01 to SCI-13 live in `model/trace.ttl`.
- **The end-state demonstration (C-30) is built; one block awaits its rebuild.**
  `ogc/executor.py` walks the process as the model states it and emits a
  record; the run conforms to S0 to S9, is complete against the model, has
  a recomputable coverage and traces fully, and twelve mutations are each
  caught by a named check (`ogc execute`, chapter Records and reporting).
  One finding is open as concern C-43: a record without a plan approval
  conforms to the shapes and is caught only by completeness. Z validated
  every block and wire on rulings sheet 05 but the report assembler (B8),
  rebuilt so that the conformance check on the record precedes the final
  report (sheet 10-41), and the sponsor signatory's block and wires, new
  with R-50; C-30 closes with their ticks.
- **Record and shapes: current (R-50, sheet 10).** The measles evaluation
  (`track/measles-evaluation.ttl`) is a bundle every item is a member of,
  tagged synthetic; it names the parties and the sponsor's signatory, the
  two declarations, the agreement that accepts the proposal, the access
  with its period and instrument, the sponsor's approval of the requirement
  set, three requirements in the county's words with five criteria, four
  sessions of three turns, a paired determination, a cannot-tell resolved by
  a follow-up session and the attestation that supersedes it, a draft report
  with its gap flagged, the verdict on the record before the final report
  with the digests of what it ran, a recommendation that states its fitness
  (R-51), and the acceptance; the step is derived through the model, never
  asserted; shapes S0 to S9 and thirty-nine counterexamples in RDF, each the
  record with one change, follow the rulings; the traceback query reaches
  the parties.
- **Pending outside the repo.** The w3id redirect
  (perma-id/w3id.org#6652) is open; IRIs resolve nowhere until it merges. The
  paper draft and the term contract will be aligned to this glossary once the
  glossary is closed.

## Ask the graph

`uv run -q ogc <command>` navigates the vocabulary graph deterministically:
`ogc schema`, `ogc find`, `ogc term`, `ogc define`, `ogc quote`, `ogc
verify` (terms, sources and steps), `ogc list`, `ogc source`, `ogc sources`, `ogc ruling`, `ogc
rulings`, `ogc concern`, `ogc concerns`, `ogc sci`, `ogc steps`, `ogc epo` (an EPO class or role: its label, superclasses, the layer it is pinned at, the term it names, the disjointness axioms and the shapes that mention it), `ogc shapes`, `ogc shape` (a node shape's target and constraints), `ogc crosswalk`
(`--popper` for the seven Popper rows), `ogc views`, `ogc view` (a model view as mermaid with its perspective), `ogc execute` (the process executed from the model, with its checks and a `VERDICT` line; `--planned`, `--sessions`, `--requirements`, `--criteria` and `--populations` set the executor's parameters, capped at 100 criteria, 20 sessions and 100 criterion-sessions of work because the checks are quadratic), `ogc record` (the measles evaluation item by derived step, with who and when and the synthetic tag; `ogc record <name>` for one item), `ogc check-word`, `ogc sparql`
(read-only, sorted, one merged graph; `--model` adds the model graph, `--record` the record, and a query that names the record or the model graph without its flag is refused), `ogc doctor`. Every output starts with `# ogc <command> <args>
@ <sha>` (for `sparql`, the query as typed with its sha256, re-runnable); `--json` returns the result as one object carrying the same
invocation and sha under `_ogc`, and every error as one object with `_ogc`, `error`, `hint` and `candidates`; ids may be typed as the tool prints them (a local name, a CURIE such as `term:probe` or `rul:R-16`, or a full IRI); exit 0 found, 1 not found, ambiguous, a
bad filter value, refused or a failed verdict, 2 usage. The skill `.claude/skills/ogc-glossary/SKILL.md`
teaches an LLM to use it instead of grepping the Turtle. It follows the
navigation tool the authors built for their earlier glossaries (ruling
R-29).

## Authors and citation

A collaboration between **Dynamical Systems Group** and **Humane Intelligence**,
co-authored by Michael Zargham (DSG) and Julie Hollek (HI). Cite it as such;
`CITATION.cff` carries the machine-readable form (GitHub shows it under
"Cite this repository").

## Run the gate

```bash
uv sync && bash checks/run-checks.sh
```

The only verdict is the `CHECKS: PASS|FAIL` line; details in `checks/out/`.

## IRIs

Ontology and record IRIs are authored under `https://w3id.org/og-caie/`.
Until the w3id redirect is merged they resolve nowhere and are used purely
as identifiers; the site above is the fallback.

## Licence

CC BY-SA 4.0 for the whole work. The licence does not extend to the quoted
source materials, which remain their publishers' property. This is an open
standards activity under development with a computational implementation
pathway. See `LICENSE.md`.
