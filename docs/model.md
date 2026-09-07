# A nested lifecycle

The two cycles are one model. The contracting lifecycle is the outer
process; its `fulfil` step is typed by the evaluation process, a black box
from outside and the whole of the previous chapter from inside. This chapter
shows why the nesting is the standards' own, how the model states it, and
how the measles record splits along it.

## What the standards say

ISO/IEC/IEEE 15288 keeps its process groups coordinate; nothing nests.
What nests here is the work: the acquirer's agreement
opens and closes it, and the supplier performs the ISO/IEC/IEEE 29119-2
test processes under it. So an evaluation is what a {term}`provider` does between the
test item provider's grant of access and its own delivery to the {term}`customer`, and the six steps of
the inner cycle sit between C4 and C5 of the outer one. `ogc steps` prints
both cycles with the canon step each matches; the previous two chapters
quote them.

## The specification

One view, read from the model graph, shows the nesting and nothing else:
the outer chain with `fulfil` as a black box, the inner chain it opens
into, and the only wires that cross the boundary. The contract hands in the
agreement, the statement of work and the access; the evaluation hands back
the report, its approval and the recommendation. Everything inside each chain is left
out on purpose; the two chapters before this one draw it.

```{include} ../generated/nesting.md
```

The same view as the tool prints it, perspective first, figure beneath:

```{literalinclude} ../generated/cli/view-nesting.md
```

In SysML v2, the systems modelling language the model is written in, the
outer cycle is an `action def`, a process as steps in fixed succession, of
seven steps, and the inner cycle another of six. The step `fulfil` is declared `action fulfil : EvaluationProcess`;
its inputs, the agreement and the access, are bound by `flow`, SysML's
binding of one step's output to another's input, from the agree and access
steps, and its outputs, the report, its approval and the recommendation, flow
to the deliver step. The inner process is the drill-down, the black box opened one
level down, and conforms to the layer above by typing: shape M4-Nesting, one
of the machine-checked rules over the model graph, checks that every input
of the evaluation process is fed by a contracting step and every output
feeds one. The assembly performs one action, the contracting lifecycle.
The report step is opened the same way one level down: the checker's
verdict on the record first, then the assembly of the report that rests on
it, two nested actions bound to the step's parameters.

The record and the report rest on both lifecycles at once: the mission,
the agreement and the access come from the contracting lifecycle; the
requirement set, the plan, the evidence and the attestations from the
evaluation. The traceback from a recommendation reaches both sides in one
query, and the report leaves the inner cycle to become the delivery's
content in the outer. A record that held only the evaluation could say what was found,
not under what contract or for whom; one that held only the contract could
say what was agreed, not what was shown. Shape S0-Layers on the record and
shape M4-Nesting on the model guarantee that both are present.

SysML holds structure only: the source file is the authoring view, and its
rendering as RDF by the pinned OpenSysML converter is the canonical
structure every shape and figure reads, pruned to the terms in the term
map (`model/sysml_term_map.csv`, each term with a rationale) and committed
with a manifest and a triple budget (the cap on the graph's size, raised
only with a reason).

## The walkthrough

The measles record splits along the same seam. What the contract pinned was
recorded between 28 July and 31 July and again between 12 and 14 August:
the mission, the need, the proposal, the agreement, the access, the
delivery and the acceptance. What the evaluation pinned was recorded
between 1 and 12 August, inside that window, by Annie, Theo and the
machines. The table counts what each layer contributed to the one record
the report and the traceback read.

```{include} ../generated/layers-walkthrough.md
```

The shape that holds the layers apart, as the tool prints it:

```{literalinclude} ../generated/cli/shape-s0-layers.md
```

## Checked

The authoring view validates strictly under the pinned converter; the
canonical graph regenerates byte for byte within its budget; M4-Steps,
M4-Nesting, M4-ProcessDag and M4-EveryItemProduced hold over it, the third
checking that the steps form a DAG (a directed acyclic graph, no loop);
S0-Layers holds
over the record, and the counterexample of a requirement set declared
before the agreement must fail it.

```{include} ../generated/receipts.md
```

:::{admonition} Verdict
:class: checked
The authoring view validates, the canonical graph regenerates and conforms,
the record conforms, and the counterexample fails where it must.
Computational proof: [run the checks](../notebooks/checked-model.ipynb).
:::

## There is more in the model

:::{admonition} Ask the graph
:class: more

```{include} ../generated/more-model.md
```
:::

## Sources cited

```{include} ../generated/cited-model.md
```
