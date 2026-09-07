# Records and reporting

The claim of this specification is an end state: an evaluation that
follows the wiring leaves a {term}`record` from which {term}`test coverage`
is recomputed by anyone who holds it, and from which every recommendation
is traced back to the evidence, the experiments, the judgments and the
people. This chapter executes the rules the previous ones state: a program
walks the process as the model states it, emits a record, and the checks
run over that record and over broken copies of it.

## What the standards say

ISO 9000 says what a record is for: to formalize
{term}`requirements traceability` and to provide evidence of
{term}`verification`. SEVOCAB's test coverage is the degree to which
specified items have been exercised by tests, and its test completion
report summarises what was covered. The record here is one record in that
sense, and the two queries that read it, coverage and traceback, are those
two purposes made executable. The word {term}`conformance` is reclaimed for
the machine check of the record against the shapes, the rules written in
SHACL (the W3C Shapes Constraint Language), keeping {term}`conformity` for
the fulfilment of a requirement by the test item.

## The specification

The essentials this chapter states, each with the shapes that check it:

```{include} ../generated/sci-guarantees.md
```

The executor reads the canonical model graph and nothing else for the
structure: the steps in succession order, the `fulfil` step opened into
the evaluation steps, the item kinds each step produces and consumes, and,
from the wiring, which part supplies each. It emits a record by walking
the steps, one template per step saying what a conformant item of each
kind carries, written against the shapes, and refuses to run if a
template's outputs disagree with the model's step signature. Over the emitted record four checks run: conformance to the shapes S0 to S9; completeness, every item
kind the process produces being present; coverage, recomputed by the
coverage query; and the traceback from every recommendation back to the
evidence, the experiment, the judgments and their people, the DSO release,
the agreement, the parties with their declarations, and the delivery. The
guarantee is the
conjunction: a run that follows the wiring conforms, is complete, has a
recomputable coverage and traces fully, and each way of departing from the
wiring is caught by a named check.

## The walkthrough

The measles evaluation of the previous chapters is one record, written by
hand: three requirements, five criteria, four sessions, a draft that
flagged one cannot-tell, a final report after the follow-up resolved it,
one criterion unmet and a recommendation fit with conditions. Its report
is the sample report in [Appendix A](appendix-report.md). The executor's records are generated from the same model with named parties,
one requirement, three criteria, a plan that exercises two of them with
the third's deviation recorded, and one session that applies every probe
once. Coverage comes out at two thirds by weight because one criterion was
left unplanned, where the measles case, every criterion attested, reaches
one; the operator's determination is paired with the domain expert's, so
the traceback returns three rows. The variants change the parameters, one
cycling through every judgment the shapes allow; each mutation breaks one
thing, and the last column names the check that catches it.

```{include} ../generated/executor.md
```

The first run as the command line executes it:

```{literalinclude} ../generated/cli/execute.md
```

## Checked

The tests execute the runs, pin the coverage and the traceback row counts,
assert that the first run conforms and is complete, that each of the twelve
mutations is caught by at least one check, that two executions produce
identical graphs, and that a model with a step's output removed makes the
executor refuse to run. One finding is stated rather than hidden: skipping
the plan approval leaves a record the shapes accept, because no shape yet
requires that item to exist; completeness against the model catches it,
and whether a shape should is concern C-43, open for a ruling. Skipping
the access grant was such a finding until the envelope was bound to the
test item an access grant names; now a shape, completeness and the
traceback all refuse it:

```{literalinclude} ../generated/cli/execute-mutate-skip-access.md
```

:::{admonition} Verdict
:class: checked
The first run conforms, is complete, recomputes its coverage and traces
fully; every mutation is caught by a named check. Each mutation is applied
to the finished run, whose verdict it keeps; the checks rerun.
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
