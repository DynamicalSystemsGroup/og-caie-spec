# og-caie-spec

**Ontology-Grounded Contextual AI Evaluation (OG-CAIE) as an executable
specification.** Site: <https://dynamicalsystemsgroup.github.io/og-caie-spec/>

The process Humane Intelligence and Dynamical Systems Group use to evaluate a
deployed AI system against the needs of a specific domain, written down as:

- a **glossary** whose every term cites one canonical definition (ISO 9000:2026,
  SEVOCAB, NIST AI 700-2, W3C), with exactly three coined terms;
- a **SysML v2 model** (OpenSysML v0.4.3) of the Evaluation Process Ontology
  as a standard operating procedure and of the human and machine assemblage
  that runs it, with twelve requirements each tagged machine-verified or
  human-validated;
- one **evaluation record** (PROV-O + EARL) of the measles chatbot example,
  checked by SHACL shapes, with counterexamples that must fail;
- a **rulings register** holding every interpretive choice verbatim.

## Status (2026-09-06)

- **Glossary: ratified.** 61 terms, 4 coined (DSO, EPO, CAIE, OG-CAIE),
  settled through 39 rulings (R-01 to R-39) recorded verbatim in
  `rulings/adjudications.ttl`. 75 quotes are machine-located in
  content-hashed snapshots, 34 verified by Z against the ISO screenshots or
  the browsing platforms, 13 transcribed and awaiting Z's tick on rulings
  sheet 04. Concerns C-25, C-26, C-30, C-43, C-44 and C-45 are open.
- **Both cycles are bound to the canon (R-31, R-32).** Each step cites the
  process step it matches: SEBoK's account of the ISO/IEC/IEEE 15288
  acquisition, stakeholder needs and system requirements processes; the
  ISO/IEC/IEEE 29119-2 test strategy and planning, execution and completion
  processes via SEVOCAB; ISO/IEC 17000's review, decision and attestation.
  The contracting lifecycle (need, propose, agree, access, deliver, accept)
  cites SEBoK's agreement processes, ISO/IEC 17000's access, scheme and
  acceptance, ISO 9000's contract and the 29119-2 test environment and
  completion report; every item kind says which layer pins it. The
  sponsor's mission and obligations towards the affected populations open
  the record (R-37, R-38).
- **Site: a presentation layer over the model (R-34), eight pages.** The
  front page runs from why this counts as science to the bridge into the
  engineering standards; the vocabulary page shows exactly the terms the
  site uses, with hover definitions; four chapters (Contracting, The
  evaluation, The nested model, What the record proves) each pair the
  specification with the measles walkthrough in five fixed blocks and close
  with the separation principle; the conclusion reads the crosswalk
  backwards. Figures are views from a registry (`ogc/views.py`), each
  captioned with what it brings into focus and leaves out (R-38).
  Supporting notebooks off the main path run the checks each chapter
  claims (`notebooks/`); the appendix opens the same model as a knowledge
  graph explorer (`explorer/`, R-39), rendered from the RDF with the
  `ogc` command on every node and an in-browser SPARQL box.
- **Model: revised (R-21 to R-38), draft.** SysML holds structure only; the
  pruned RDF rendering `model/og-caie.model.ttl` is the canonical structure
  (R-22), checked by wiring shapes M1 to M5 over kinds of parts and ports:
  four parties, three actor categories within the testing organization, the
  six-step EPO nested as the fulfil step of the contracting lifecycle (one
  model, R-33), both process DAGs, 59 ports and 35 seams, every input wired
  once and every output somewhere, and the sponsor's obligation to the
  affected populations as a relation. Four model counterexamples fail their
  shape. The essentials SCI-01 to SCI-13 live in `model/trace.ttl`.
- **The end-state demonstration (C-30) is built; Z's validation is not.**
  `ogc/executor.py` walks the process as the model states it and emits a
  record; the run conforms to S0 to S9, is complete against the model, has
  a recomputable coverage and traces fully, and seven mutations are each
  caught by a named check (`ogc execute`, chapter What the record proves).
  Two findings are open as concern C-43: a record without a plan approval
  or an access grant conforms to the shapes and is caught only by
  completeness or the traceback. Z's block-by-block and wire-by-wire
  validation on rulings sheet 05 remains, in Z's words (2026-09-06): "i
  still need to work through the model step by step and validate all the
  individual blocks and wires."
- **Record and shapes: current.** The measles record names the parties, the
  mission, the agreement, the access, the stakeholder input, the
  appropriateness assessment, the plan approval and the delivery; shapes S0
  to S9 and nine RDF counterexamples follow the rulings; the traceback query
  reaches the parties.
- **Pending outside the repo.** The w3id redirect
  (perma-id/w3id.org#6652) is open; IRIs resolve nowhere until it merges. The
  paper draft and the term contract will be aligned to this glossary once the
  glossary is closed.

## Ask the graph

`uv run -q ogc <command>` navigates the vocabulary graph deterministically:
`ogc schema`, `ogc find`, `ogc term`, `ogc define`, `ogc quote`, `ogc
verify`, `ogc list`, `ogc source`, `ogc sources`, `ogc ruling`, `ogc
rulings`, `ogc concern`, `ogc concerns`, `ogc sci`, `ogc crosswalk`
(`--popper` for the Popper rows), `ogc views`, `ogc view` (a model view as mermaid with its perspective), `ogc execute` (the process executed from the model, with its checks), `ogc check-word`, `ogc sparql`
(read-only), `ogc doctor`. Every output starts with `# ogc <command> <args>
@ <sha>`; `--json` returns the result unchanged; exit 0 found, 1 not found
or ambiguous, 2 usage. The skill `.claude/skills/ogc-glossary/SKILL.md`
teaches an LLM to use it instead of grepping the Turtle. A port of the
Mission Twin glossary's `mtg` (ruling R-29).

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
