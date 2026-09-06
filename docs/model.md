# A nested lifecycle

The two cycles are one model. The contracting lifecycle is the outer
process; its `fulfil` step is typed by the evaluation process, a black box
from outside and the whole of the previous chapter from inside. This chapter
shows why the nesting is the standards' own, how the model states it, and
how the measles record splits along it.

:::{admonition} What the standards say
:class: standards

SEBoK and ISO/IEC/IEEE 15288 place the technical processes inside the
agreement processes: needs and requirements are expressed in agreements
between acquirers and suppliers, and the supplier's work is performed under
them. The test processes of ISO/IEC/IEEE 29119-2 are technical processes of
that kind. So an evaluation is what a {term}`provider` does between the
{term}`customer`'s access and the provider's delivery, and the six steps of
the inner cycle sit between C4 and C5 of the outer one. `ogc steps` prints
both cycles with the canon step each matches; the previous two chapters
quote them.
:::

:::{admonition} The specification
:class: specification

One view, read from the model graph, shows the nesting and nothing else:
the outer chain with `fulfil` as a black box, the inner chain it opens
into, and the only wires that cross the boundary. The contract hands in the
agreement, the statement of work and the access; the evaluation hands back
the report and the recommendation. Everything inside each chain is left
out on purpose; the two chapters before this one draw it.

```{include} ../generated/nesting.md
```

In SysML the outer cycle is an `action def` of seven steps in fixed
succession and the inner cycle another of six. The step `fulfil` is declared
`action fulfil : EvaluationProcess`; its inputs, the agreement and the
access, are bound by `flow` from the agree and access steps, and its
outputs, the report and the recommendation, flow to the deliver step. The
inner process is the drill-down and conforms to the layer above by typing:
shape M4-Nesting checks that every input of the evaluation process is fed by
a contracting step and every output feeds one. The assembly performs one
action, the contracting lifecycle.

The record and the report rest on both lifecycles at once, and the nesting
is what lets them. Every item that reaches the recorder comes from one of
the two cycles: the mission, the statement of work, the agreement and the
access from the contracting lifecycle; the DSO release, the requirement set,
the plan, the sessions, the evidence, the determinations and the
attestations from the evaluation. Coverage needs the criteria, an
evaluation item, weighted as the contract's frame allows; the traceback from
a recommendation reaches the evidence and the attestations on the inner
side and the agreement, the access, the three organizations and the
delivery on the outer side, in one query; and the report itself leaves the
inner cycle to become the delivery's content in the outer. A record that
held only the evaluation could say what was found, not under what contract
or for whom; one that held only the contract could say what was agreed,
not what was shown. The chapter on records and reporting counts on both
being present, and shape S0-Layers on the record and shape M4-Nesting on
the model are what guarantee it.

SysML holds structure only: the source
file is the authoring view, and its rendering as RDF by the pinned
OpenSysML converter, pruned to a term map and committed with a manifest and
a triple budget, is the canonical structure that every shape and every
figure reads.
:::

:::{admonition} The walkthrough
:class: walkthrough

The measles record splits along the same seam. What the contract pinned was
recorded between 28 July and 31 July and again between 12 and 14 August:
the mission, the need, the proposal, the agreement, the access, the
delivery and the acceptance. What the evaluation pinned was recorded
between 1 and 12 August, inside that window, by Annie, Theo and the
machines. Shape S0-Layers holds the two apart: no item of the second layer
may be dated before the agreement was signed. The table counts what each
layer contributed to the one record the report and the traceback read.

```{include} ../generated/layers-walkthrough.md
```
:::

:::{admonition} Checked
:class: checked

The authoring view validates strictly under the pinned converter; the
canonical graph regenerates byte for byte within its budget; M4-Steps,
M4-Nesting, M4-ProcessDag and M4-EveryItemProduced hold over it; S0-Layers
holds over the record, and the counterexample of a requirement set declared
before the agreement fails it.

```{include} ../generated/receipts.md
```
Computational proof: [run the checks](../notebooks/checked-model.ipynb).
:::

:::{admonition} There is more in the model
:class: more

```{include} ../generated/more-model.md
```
:::
