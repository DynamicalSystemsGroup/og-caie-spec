# The assemblage

The model is one file, `model/og-caie.sysml`, in SysML v2 (OpenSysML v0.4.3,
pinned by digest). It is read here in the order a reader needs it: the three
layers, then the assemblage of people and software that runs an evaluation,
then the nine requirements that make the result science, then the receipts
that show the model executes.

Status, stated plainly: this model was built before rulings R-12 to R-20
settled the glossary, and it has been patched to keep pace rather than
redesigned. Its part definitions and port definitions do not yet, taken
together, give the Evaluation Process Ontology structure that guarantees
traceability and coverage as the end state, given a Domain-Specific Ontology
and a requirement set expressed in EPO and DSO concepts. That redesign is the
next piece of work; the record and its shapes are ahead of the model.

Scope is Concept Definition and System Requirements Definition, in the sense
of ISO/IEC/IEEE 15288:2023 and SEBoK v2.14: the parts are named only so far as
the requirements need interfaces to be stated against. No architecture is
allocated; the software and cloud realization is a separate concern.

```{include} ../generated/layers.md
```

The Evaluation Process Ontology is an `action def` with five actions in fixed
succession. The Domain-Specific Ontology enters as its parameter. The
assemblage performs it.

```{include} ../generated/wiring.md
```

Every fact passes through the recorder. Humans supply the DSO release, the
requirement set, the attestations and the recommendation; determinations on
evidence may be made by either; machines derive probes, check conformance,
record, and compute coverage. The system under test is a black box inside the
record and outside the boundary of responsibility.

## Parties

Three organizations are parties to every evaluation, and the record names
them (rulings R-21 and R-23). The sponsor organization is the customer: it
receives the evaluation as a service, agrees the requirement set, and gets the
report. The testing organization is the provider: its account executive signs
the contract, its evaluation team does the work, and its machines keep the
record. The accountable organization provides the test item and grants access
to it. Any two may coincide, and the record says whether they do. In the
vocabulary of ISO/IEC 17000 the accountable organization is the first party, a
sponsor with a user interest is a second party, and a testing organization
independent of the provider with no user interest is a third party; the
record states independence as a fact rather than assuming it.

Affected stakeholders are populations, not single entities. A population may
be interviewed, in which case its input is an item in the record, or its
interests may be represented by the domain expert, in which case the record
says who represents it. The evaluation team holds two abstract actor
categories in distinct slots: the domain expert selects the DSO, assesses the
appropriateness of the requirements, may approve the test plan, and attests;
the evaluation operator declares the requirements with the sponsor, writes the
plan, administers the probes, collects the evidence, and drafts the report.
The account executive does neither.

The current model predates these rulings; the revision that wires the
parties, the seven-step process and the three actor categories is in
progress.

```{include} ../generated/sci.md
```

Each requirement is a `requirement def` with a subject of type
`OgCaieEvaluation` and constraints over the run's values. Verification
happens twice: here in SysML over the typed run configuration (`-satisfy`),
and again in RDF over the evaluation record (SHACL shapes S1 to S8 on the
record page). A requirement tagged *human* is still checked by machine for
its form; only the value of the judgment is the person's.

```{include} ../generated/trace.md
```

```{include} ../generated/receipts.md
```

The counterexample pads the record: the third criterion is marked covered
with no attestation behind it, and coverage is reported as 1. SCI-07 rejects
it, and the gate expects that rejection.
