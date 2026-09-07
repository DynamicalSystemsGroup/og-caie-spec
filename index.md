# OG-CAIE as an executable specification

```{figure} assets/hi-dsg-collaboration.png
:width: 420px
:alt: Humane Intelligence and Dynamical Systems Group

A collaboration between Humane Intelligence and Dynamical Systems Group.
```

Contextual AI Evaluation (CAIE) is the {term}`evaluation` of a deployed AI
system against the needs of one domain, judged by people who know that
domain. OG-CAIE is CAIE performed with the method this site sets out: an
{term}`Evaluation Process Ontology` (EPO), the same six steps for every
domain, performed inside a contracting lifecycle drawn from the engineering
standards, and a {term}`Domain-Specific Ontology` (DSO), the vocabulary of
one domain supplied or approved by its experts. The method is stated here
in a form a machine can check and a person can read, and it is walked
through on one synthetic case, a county public-health chatbot asked about
measles during an outbreak.

This site is a collaboration between Dynamical Systems Group and Humane
Intelligence, co-authored by Michael Zargham and Julie Hollek.

## Why this counts as science

Karl Popper's account of empirical science is short. A hypothesis is a
claim that could be shown false. It is tested under auxiliary assumptions,
the background held fixed while the test runs. Together they yield a
prediction: what should be observed if both are true. Evidence is an
accepted result of observation. A claim is scientific to the extent that it
excludes at least one possible outcome; and context matters, because a
failed prediction does not by itself say which assumption failed.

An evaluation of an AI system counts as science on the same terms. It must
write down, before any test, what would count as failure and under what
assumptions; it must collect what the system actually did; it must record
who ruled on that evidence, and whether the assumptions still held; and it
must leave a record from which anyone can recompute what was covered and
what was not. That is the whole standard. Everything on this site exists to
meet it.

## The bridge to the engineering standards for evaluation

None of this needs new words. Each element of that account already has a
settled name in the standards that govern testing, conformity assessment and
quality: ISO 9000 for {term}`requirement`, {term}`objective evidence` and
{term}`determination`; ISO/IEC 17000 for {term}`attestation`; the IEEE
Software and Systems Engineering Vocabulary for {term}`acceptance criteria`,
{term}`expected results`, {term}`test plan`, {term}`test coverage` and the
test case a {term}`probe` refines; NIST's evaluation reports for
{term}`session`. Using those names rather than coining our own lets someone
else check the record against the same definitions. At
SciPy 2026 the authors led a birds-of-a-feather session, Building
Scientific Approaches to Generative AI, and put Popper's elements to the
room in the words the table's first column keeps. The table is the bridge:
each row takes one of those elements to the standard terms it lands on, to
the place it occupies in an evaluation record, and to the check that makes
it more than a promise.

```{include} generated/popper.md
```

The next chapter gives those terms their canonical definitions, verbatim
and cited. The chapters after it use them to state the specification, first
the contracting of an evaluation and then the evaluation itself, and to
show its properties. The conclusion returns to Popper's terms and says what
has been encoded.

```{include} generated/version.md
```

## Sources cited

```{include} generated/cited-index.md
```
