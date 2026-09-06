# The assemblage

The model is one file, `model/og-caie.sysml`, in SysML v2 (OpenSysML v0.4.3,
pinned by digest). It is read here in the order a reader needs it: the three
layers, then the assemblage of people and software that runs an evaluation,
then the nine requirements that make the result science, then the receipts
that show the model executes.

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
requirement set, the attestations and the recommendation; machines derive
probes, check conformity, record, and compute coverage. The system under test
is a black box inside the record and outside the boundary of responsibility.

```{include} ../generated/sci.md
```

Each requirement is a `requirement def` with a subject of type
`OgCaieEvaluation` and constraints over the run's values. Verification
happens twice: here in SysML over the typed run configuration (`-satisfy`),
and again in RDF over the evaluation record (SHACL shapes S1 to S8 on the
record page). A requirement tagged *human* is still checked by machine for
its form; only the value of the judgment is the person's.

```{include} ../generated/receipts.md
```

The counterexample pads the record: the third criterion is marked covered
with no attestation behind it, and coverage is reported as 1. SCI-07 rejects
it, and the gate expects that rejection.
