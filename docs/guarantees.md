# Records and reporting

The claim of this specification is an end state: an evaluation that
follows the wiring leaves a {term}`record` from which {term}`test coverage`
is recomputed by anyone who holds it, and from which every recommendation
is traced back to the evidence, the experiments, the judgments and the
people. The previous chapters state the rules. This one executes them: a
program walks the process as the model states it, emits a record, and the checks run over that record and over broken copies of it.

## What the standards say

ISO 9000 says what a record is for: to formalize
{term}`requirements traceability` and to provide evidence of
{term}`verification`. SEVOCAB's test coverage is the degree to which
specified items have been exercised by tests, and its test completion
report summarises what was covered. The record here is one in that sense,
and the two queries that read it, coverage and traceback, are those
purposes made executable. The word {term}`conformance` is reclaimed on
purpose for the machine check of the record against the shapes, the rules
written in SHACL (the W3C Shapes Constraint Language), keeping
{term}`conformity` for the fulfilment of a requirement by the test item.

## The specification

The essentials this chapter states, each with the shapes that check it:

```{include} ../generated/sci-guarantees.md
```

The executor reads the canonical model graph and nothing else for the
structure: the contracting steps in succession order, the `fulfil` step
opened into the evaluation steps, the item kinds each step produces and
consumes, and, from the wiring, which part supplies each item kind. It then
emits a record by walking the steps, one template per step saying what a
conformant item of each kind carries, written against the shapes. It
refuses to run if a template's outputs disagree with the model's step
signature, or if a step consumes an item no earlier step produced, so executor and model cannot drift apart. Over the emitted record four
checks run: conformance to the shapes S0 to S9; completeness, every item
kind the process produces being present; coverage, recomputed by the
coverage query; and the traceback, one row per attestation from the
recommendation back through the evidence, the session, the probe, the plan,
the DSO release, the agreement, the parties and the delivery. The guarantee is the
conjunction: a run that follows the wiring conforms, is complete, has a
recomputable coverage and traces fully, and each way of departing from the
wiring is caught by a named check.

## The walkthrough

The measles record of the previous chapters is one run, written by hand;
its report, as the sponsor receives it, is the sample report in
[Appendix A](appendix-report.md).
The executor's runs are generated from the same model with named parties,
one requirement, three criteria, a plan that exercises two of them, and one
session that applies every probe once. Coverage comes out at two thirds by
weight because one criterion was left unplanned, as in the measles case
(three quarters); the traceback returns one row per attestation. The variants change
the parameters; the mutations each break one thing in the first run and
the last column names the check that catches it.

```{include} ../generated/executor.md
```

The first run as the command line executes it, ending in the verdict line
the gate reads:

```{literalinclude} ../generated/cli/execute.md
```

## Checked

The tests execute the runs, pin the coverage and the traceback row counts,
assert that the first run conforms and is complete, that each of the nine
mutations is caught by a named check, that two executions produce
identical graphs, and that a model with a step's output removed makes the
executor refuse. Two findings are stated rather than hidden: skipping
the plan approval or the access grant leaves a record the shapes accept,
because the S-shapes judge the items that exist and none yet requires
those items to exist; both are caught by completeness against the model,
and the missing access also empties the traceback. Whether the shapes
should require them is concern C-43, open for a ruling. The second, as the
command line shows it: the shapes accept, completeness and the traceback
refuse, the verdict fails.

```{literalinclude} ../generated/cli/execute-mutate-skip-access.md
```

:::{admonition} Verdict
:class: checked
The first run conforms, is complete, recomputes its coverage and traces
fully; every mutation is caught by a named check.
Computational proof: [run the checks](../notebooks/checked-guarantees.ipynb).
:::

## There is more in the model

:::{admonition} Ask the graph
:class: more

```{include} ../generated/more-guarantees.md
```
:::

## Sources cited

```{include} ../generated/cited-guarantees.md
```
