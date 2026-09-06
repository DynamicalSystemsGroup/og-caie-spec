# OG-CAIE as an executable specification

```{figure} assets/hi-dsg-collaboration.png
:width: 420px
:alt: Humane Intelligence and Dynamical Systems Group

A collaboration between Humane Intelligence and Dynamical Systems Group.
```

Ontology-Grounded Contextual AI Evaluation (OG-CAIE) is the process Humane
Intelligence and Dynamical Systems Group use to evaluate a deployed AI system
against the needs of a specific domain. This site is the specification of
that process in a form a machine can check and a person can read. It is a
collaboration between Dynamical Systems Group and Humane Intelligence,
co-authored by Michael Zargham and Julie Hollek.

It is deliberately small. It asks one question: what is *essential* for an
evaluation of this kind to count as science? The answer is a short list of
requirements, each of which is either verified by machine over the evaluation
record or validated by a named human whose judgment is recorded with the
evidence it rests on.

## Why this counts as science

At the SciPy 2026 birds-of-a-feather session the authors set out, after
Popper, what an empirical claim needs: a hypothesis that could be falsified,
the auxiliary assumptions held fixed while testing it, a prediction that
says what should be observed, and evidence, an accepted result of
observation. Context matters, because a failed prediction does not by itself
say which assumption failed.

OG-CAIE puts each of these where a machine can find it. The acceptance
criteria are the hypotheses, each specific enough to be wrong, each stating
the expected result a test could observe. The operational environment, the
requirement set and the Domain-Specific Ontology release are the auxiliary
assumptions, declared before any session is run and recorded with who
approved them. A probe is the prediction's test case, applied at one turn of
a session. The system's response is collected as evidence bearing on a
criterion's expected result. A determination rules on that evidence: met, not
met, or cannot tell. An attestation is a named person's judgment aggregating
the determinations for a criterion, who also says whether the declared
context was appropriate and the evidence sufficient. Coverage is falsifiable:
if a criterion has no attested outcome behind it, the reported number was
overstated by exactly that criterion's weight, and anyone holding the record
can show it.

So the evaluation is itself verified and validated before it says anything
about the system. Verification of the evaluation is mechanical: conformance of
the record to the process shapes and coverage recomputed from the record. Validation of
the evaluation is human: the technical experts on the evaluation team, the
domain experts and the AI evaluation experts, attest that the declared
context was appropriate and the evidence sufficient. Requirements
traceability, in the systems-engineering sense, is the thread that lets a
reader walk from a recommendation back through attestation, determination,
evidence, turn, session, probe and test plan to the requirement it answers.

## What is here

- **Glossary.** Every term with its one canonical citation, verbatim quote and
  checked status; three coined terms, everything else adopted or refined.
- **Assemblage.** The three layers, the human and machine parts wired along
  typed ports, the twelve requirements tagged machine or human, and the receipts
  showing every requirement holds and the counterexample fails. The model was
  built before most of the rulings and is next in line for a deep revision.
- **Record.** The measles evaluation record, its conformance to the EPO shapes,
  coverage and performance recomputed by query, the recommendation traced back
  to evidence, experiments, determinations, attestations, DSO release and EPO
  step, and five counterexamples that fail where they must.
- **Rulings.** Every interpretive choice, with the adjudicator's words verbatim.

## Scope

Concept Definition and System Requirements Definition, in the sense of
ISO/IEC/IEEE 15288:2023 and SEBoK v2.14: mission analysis, stakeholder needs,
system requirements, and the interfaces those requirements are stated
against. No architecture is modeled here; the software and cloud realization
is a separate concern.

## Vocabulary discipline

Terms are used, not owned. Each term cites one canonical source, chosen in
this order: ISO 9000:2026, SEVOCAB, NIST AI 700-2, then W3C and OMG
specifications for the technical binding only. Exactly three terms are coined:
Domain-Specific Ontology, Evaluation Process Ontology, and OG-CAIE itself.
One word is reclaimed against its source and says so: *conformance*,
deprecated by ISO 9000 as a synonym of *conformity*, names the machine-checked,
correctly constructed record, a special case of conformity. Every quote in the
glossary is verified, by machine against a hashed snapshot or by a named
person against the source.

## Where this goes

Two offers close this specification. Use OG-CAIE: the process, the
vocabulary and the record format are open, and the measles example shows the
whole chain on one page. Or have your own AI evaluation practice audited
against it: every requirement here is checkable, so an existing practice can
be walked through the twelve essentials and shown where its record would and
would not conform.
