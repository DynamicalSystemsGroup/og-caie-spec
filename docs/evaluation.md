# Context and evaluation

Between access and delivery, the contract's `fulfil` step is the whole
evaluation. This chapter opens that black box: the six steps of the
{term}`Evaluation Process Ontology`, the same for every domain, performed by
the evaluation team and its machines with the {term}`Domain-Specific Ontology`
of one domain, and the second layer of assumptions the evaluation pins for
itself. The measles case runs alongside.

## What the standards say

The steps are the test processes of ISO/IEC/IEEE 29119-2 as SEVOCAB
defines them, the stakeholder and requirement processes of SEBoK, and the
functions of ISO/IEC 17000, none coined here. A {term}`requirement` is ISO
9000's; {term}`acceptance criteria`, {term}`expected results`,
{term}`test plan` and {term}`test coverage` are SEVOCAB's;
{term}`objective evidence` and {term}`determination` are ISO 9000's;
{term}`attestation` is ISO/IEC 17000's; {term}`session` and {term}`probe`
are NIST's.

```{include} ../generated/steps-evaluation.md
```

Three observations from ISO/IEC 17000 shape the fifth step. Its *decision*
(7.2), the conclusion that fulfilment of specified requirements has or has
not been demonstrated, is exactly the outcome inside an attestation. Its
*review* (7.1) names, for the fitness of what was done, a word this
specification retired for the context judgment (the middle word of its
quote in the table above), which is why we say {term}`appropriateness`
instead. And its note on 7.3 observes that there is
no term for second-party attestation: a testing organization attesting on a
sponsor's behalf about a vendor's system performs a
{term}`second-party <second-party conformity assessment activity>` activity
even when it is independent of the vendor, which is the measles case; an
audit of the evaluation by a body with no user interest would be the
{term}`third-party conformity assessment activity`. The command line prints
the fifth step with each match and its quote's tag, machine, human or
pending, [defined on the vocabulary page](glossary.md#quote-tags):

```{literalinclude} ../generated/cli/steps-determine-and-attest.md
```

## The specification

The evaluation slice of the wiring, in the parts, ports and wires the
previous chapter defined. Two actor categories do the work: the
{term}`domain expert <technical expert>` engages the affected populations
as the statement of work decided, interviewing or representing each,
supplies or approves the DSO release, assesses the appropriateness of the
requirement set, approves the plan, and attests; the
{term}`evaluation operator` declares the requirements, writes the plan,
applies the probes to the {term}`test item`, collects the evidence and
writes the recommendation. Either may determine on evidence. Machines drive the tests (the test driver derives the probes),
check conformance, assemble the report and keep the record; every item
reaches the recorder, and the record fans out to whoever reads it. The
{term}`account executive` appears only to receive the report.

```{include} ../generated/wiring-evaluation.md
```

What the evaluation pins is the second layer of assumptions: the
{term}`operational environment` and the {term}`operational envelope`, the
requirement set declaring this test item in this environment, and the DSO
release, all declared and approved before any session runs. Every
attestation then says whether that declared context was appropriate and
whether the evidence was sufficient. The chain the shapes close is what
makes a requirement useful: the requirement, as a claim a test can show
unmet; its acceptance criteria, each stating the expected result a test
could observe; the test plan, whose objectives are those criteria and whose
means are probes or a {term}`test strategy`; the turn of a session at which
a probe is applied to the test item, producing the response; the
{term}`evidence <objective evidence>` collected from it, bearing on that
expected result under that plan; the determination that rules on the
evidence with an {term}`outcome` as EARL, the W3C Evaluation and Report
Language, records one, passed, failed or cannot tell, never a Boolean; and
the attestation, a named person's judgment aggregating the determinations
for the criterion. Evidence is what is ruled on and the determination is the ruling;
evidence exists at probe, session or suite level, and a session's ordered
turns are its {term}`trajectory`, the observable realization of a state the
record never sees.

The test item is a {term}`non-deterministic system`, and a session with it
is stateful: what it says at a later turn depends on the whole
{term}`dialogue` before. So the record holds sessions, not bare runs, and a
plan's means are probes, each a {term}`scenario` tied to the criteria it
exercises, or a strategy that chooses the next probe from the trajectory so
far. Weights make the testing {term}`risk-based testing <risk-based testing>`:
a criterion's weight is its deployment sensitivity, so coverage reflects
consequence. Replicate sessions under {term}`repeatability` conditions turn a
criterion's probes into a pass rate with a {term}`measurement uncertainty`;
{term}`reproducibility` across operators and teams is what makes two
evaluations of the same requirement set comparable; evidence rolled up over
a {term}`test suite` of sessions is evidence at the third level. Coverage
and {term}`performance` are reported together and never merged. Two
mechanical checks make this {term}`verification` rather than trust:
conformance of the record to the shapes, the machine-checked rules written
in SHACL, the W3C Shapes Constraint Language, and
{term}`requirements traceability` by query from any recommendation back to
everything it rests on. The essentials this chapter states, each with the
shapes that check it:

```{include} ../generated/sci-evaluation.md
```

The essential on attestations as the tool prints it:

```{literalinclude} ../generated/cli/sci-06.md
```

## The walkthrough

Annie, the domain expert, approved the DSO release on 1 August, after the
commuters were interviewed and county residents represented: Apollo-SV, the
Apollo Structured Vocabulary of infectious-disease epidemiology, an ontology
published through the OBO Foundry (the Open Biological and Biomedical
Ontologies library), plus the facts of the 2019 measles outbreak in Clark
County, Washington, which the synthetic case is modelled after. Theo, the
evaluation operator, declared the requirement set on 2 August, one
requirement with three acceptance criteria, and Annie assessed it as
appropriate the same morning. Theo wrote the plan on 3 August, exercising two
criteria with one public-transit probe and leaving the third unplanned; the
probe deriver derived it, pySHACL (the SHACL engine) checked it, Annie
approved the plan. On 10 August Theo ran one session of one turn against
chatbot v1, by {term}`red teaming`, and collected two evidence items. On 11
August Annie and Theo each determined on one, and Annie attested both
criteria, judging the declared context appropriate and recording the
{term}`sufficiency` of the evidence for each. On 12 August the coverage
calculator recomputed coverage from the record and Theo wrote the
recommendation: not fit to deploy during the outbreak, and strengthen the
{term}`guardrail` on unknown vaccination status. Every row below names its
person and its day; the case is synthetic and no judgment here was made by
the people whose roles the names recognise.

```{include} ../generated/record-evaluation.md
```

The three criteria, what each expected, and what Annie attested:

```{include} ../generated/criteria.md
```

## Checked

Shapes S1 to S8 run over the record, from the DSO release approved before
any probe to the recommendation traced to attestations, evidence, the DSO
release and the step: every criterion with an expected result and a
weight, the plan approved before any session, every response from a
numbered turn against a versioned test item, every evidence item bearing
on one criterion under the plan, determinations with an EARL outcome,
attestations closed over their determinations by a domain expert, and
coverage recomputed from attestations alone. M2 to M5 run over the model graph: every wire local, every item
kind reaching the recorder, the steps in order forming a DAG (a directed
acyclic graph: each step after the ones that produce what it consumes, and
no loop) that produces every item kind, the three roles in their slots.
Seven record counterexamples must fail: an attestation without a
determination behind it, one aggregating a determination for another
criterion, the same fault across two turns of a strategy-driven session, a
probe derived before the requirements, a recommendation resting on nothing,
a session run by the domain expert, and an attestation by the account
executive. Two model counterexamples must fail theirs: a port no seam
reaches, and a domain expert who applies probes.

:::{admonition} Verdict
:class: checked
The record conforms, and the nine counterexamples fail where they must.
Computational proof: [run the checks](../notebooks/checked-evaluation.ipynb).
:::

## There is more in the model

:::{admonition} Ask the graph
:class: more

```{include} ../generated/more-evaluation.md
```
:::

## Sources cited

```{include} ../generated/cited-evaluation.md
```
