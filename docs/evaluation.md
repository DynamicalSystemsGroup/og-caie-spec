# Context and evaluation

Between access and delivery, the contract's `fulfil` step is the whole
evaluation. This chapter opens that black box: the six steps of the
{term}`Evaluation Process Ontology`, the same for every domain, performed
with the {term}`Domain-Specific Ontology` of one domain, and the second
layer of assumptions the evaluation pins for itself. The measles case runs
alongside.

## What the standards say

The steps are the test processes of ISO/IEC/IEEE 29119-2 as SEVOCAB
defines them, the stakeholder and requirement processes of SEBoK, and the
functions of ISO/IEC 17000, none coined here. A {term}`requirement` is ISO
9000's; {term}`acceptance criteria`, {term}`expected results`,
{term}`test plan` and {term}`test coverage` are SEVOCAB's;
{term}`objective evidence` and {term}`determination` are ISO 9000's;
{term}`attestation` is ISO/IEC 17000's; {term}`session` is NIST's, and
{term}`probe` refines SEVOCAB's test case.

```{include} ../generated/steps-evaluation.md
```

Three observations from ISO/IEC 17000 shape the fifth step. Its *decision*
(7.2) is the glossary's determination (ruling R-50), which an attestation
aggregates. Its *review* (7.1) uses the word this specification retired,
which is why we say {term}`appropriateness`. And the measles case is a
{term}`third-party conformity assessment activity`: Humane Intelligence is
independent of the vendor with no user interest; the county, which
commissions and accepts it, is the
{term}`second party <second-party conformity assessment activity>`. The
fifth step as the command line prints it, each quote with its tag,
[defined on the vocabulary page](glossary.md#quote-tags):

```{literalinclude} ../generated/cli/steps-determine-and-attest.md
```

## The specification

The evaluation slice of the wiring, in the parts, ports and wires the
previous chapter defined. Two actor categories do the work: the
{term}`domain expert <technical expert>`, with the team's population
representatives, speaks for the affected populations, supplies or approves
the DSO release, assesses the appropriateness of the requirement set,
approves the plan, and attests;
the {term}`evaluation operator` declares the requirements, writes the
plan, applies the probes to the {term}`test item`, collects the evidence,
records any departure from the plan with its reason, and writes the
recommendation. Either may determine on evidence. The operator is
responsible for the human roles in the test plan and the test driver for
the machine work; the plan says which is which, and a human must deem it
appropriate. The sponsor's signatory approves the requirement set before
any session. At the end the checker's verdict on the record comes first
and the assembler reads both; a draft report may carry flagged gaps, a
final report rests on a passed verdict, and only a final report is
approved and delivered.

```{include} ../generated/wiring-evaluation.md
```

What the evaluation pins is the second layer of assumptions: the
{term}`operational environment` and the {term}`operational envelope`, the
requirement set declaring this test item in this environment, and the DSO
release, all declared and approved before any session runs. Every
attestation then judges {term}`appropriateness` and {term}`sufficiency`.
Appropriateness covers the assumptions and the test planning: no amount of
evidence helps if the plan, the strategy and their assumptions are not
appropriate for what they aim to determine. Sufficiency relates the
evidence to the claim that a requirement is met or not: insufficient
evidence implies cannot tell; sufficient evidence can give pass or fail,
and one failing response can suffice to show a criterion unmet in that
instance. The chain the shapes close: the requirement, a claim a test can
show unmet; its acceptance criteria, each with the expected result a test
could observe; the test plan, whose objectives are those criteria and
whose means are probes or a {term}`test strategy`; the turn at which a
probe is applied, producing the response; the
{term}`evidence <objective evidence>` collected from it, bearing on that
expected result under that plan; the determination, ruling on the evidence
with an {term}`outcome` as EARL, the W3C Evaluation and Report Language,
records one, passed, failed or cannot tell, never a Boolean; and the
attestation, a named person's judgment over every determination for the
criterion, or naming what it left out and why. Evidence exists at probe,
session or suite level, and a session's ordered turns are its
{term}`trajectory`, the observable realization of a state the record never
sees.

The test item is a {term}`non-deterministic system`, and a session with it
is stateful: what it says at a later turn depends on the whole
{term}`dialogue` before. So the record holds sessions, and a plan's means
are probes, each a {term}`scenario` tied to the criteria it exercises, or
a strategy that chooses the next probe from the trajectory so far. Weights
make the testing {term}`risk-based testing <risk-based testing>`: a
criterion's weight is its deployment sensitivity, stated with its reason.
Thresholds and replication are out of scope for this version: the
criteria table counts the observations each judgment rests on; replicate
sessions under {term}`repeatability` conditions, a pass rate with its
{term}`measurement uncertainty`, {term}`reproducibility` across operators,
and evidence rolled up over a {term}`test suite` are the next version's.
Coverage and {term}`performance` are reported together and never merged.
The recommendation is owned by the domain expert's approval of the report
it derives from: "not fit to deploy" is the expert's, written by the
operator. Two mechanical checks make this {term}`verification` rather than
trust: conformance of the record to the shapes, the machine-checked rules
written in SHACL, the W3C Shapes Constraint Language, and
{term}`requirements traceability` by query from any recommendation back to
everything it rests on. The essentials this chapter states:

```{include} ../generated/sci-evaluation.md
```

The essential on attestations as the tool prints it:

```{literalinclude} ../generated/cli/sci-06.md
```

## The walkthrough

Annie, the domain expert, approved the DSO release on 1 August, once both
populations had been spoken for: Apollo-SV, the Apollo Structured
Vocabulary of infectious-disease epidemiology, plus the facts of the 2019
measles outbreak in Clark County, Washington. Theo, the evaluation operator,
declared the requirement set on 2 August, one requirement with three
criteria, each weighted with its reason; Annie assessed it as appropriate
that morning and Dana Okafor approved it for the county before noon. Theo
wrote the plan on 3 August, exercising two criteria with one
public-transit probe, and recorded why the third was left out; the test
driver derived the probe, pySHACL (the SHACL engine) checked it, Annie
approved the plan. On 10 August Theo ran one session of one turn against
chatbot v1, by {term}`red teaming`, and collected two evidence items. On
11 August Annie determined on the first; Theo, who had run the session,
determined on the second and Annie determined on it too, so that no ruling
stands alone with the person who collected its evidence; Annie attested
both criteria failed, on sufficient evidence in an appropriate context. On
12 August pySHACL judged the record conformant, the assembler recomputed
coverage, Annie approved the final report, and Theo wrote the
recommendation the approval owns: not fit to deploy during the outbreak,
and strengthen the {term}`guardrail` on unknown vaccination status. Every
row below names its person and its day; the case is synthetic and none of
its judgments was made by the people the names recognise.

```{include} ../generated/record-evaluation.md
```

The three criteria, what each expected, how much each judgment rests on,
and what Annie attested:

```{include} ../generated/criteria.md
```

## Checked

Shapes S1 to S8 run over the record, from the DSO release approved before
any probe, through the requirement set approved by the sponsor's signatory,
the plan with every departure recorded, the sessions against the one test
item the envelope binds, and the attestations closed over every
determination under the judgment rules, to the verdict on the record
before the final report and the recommendation traced. M2 to M5 run over
the model graph: every wire local, every item kind reaching the recorder,
the steps forming a DAG (a directed acyclic graph, no loop) that produces
every item kind, the roles in their slots. Twenty-three record
counterexamples must fail, each the measles evaluation with one change
named in its header, among them a determination dropped without a reason,
a failed verdict on insufficient evidence and a final report without a
verdict; and two model counterexamples, a port no seam reaches and a
domain expert who applies probes.

:::{admonition} Verdict
:class: checked
The record conforms, and the twenty-five counterexamples fail where they must.
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
