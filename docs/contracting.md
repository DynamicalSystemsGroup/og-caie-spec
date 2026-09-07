# Stakeholders and contracting

An evaluation is work done under a contract. Before any test runs, a
{term}`customer` has stated a need, a {term}`provider` has answered it, the
two have signed, and the organization accountable for the {term}`test item`
has opened it up. After the last attestation, the provider delivers and the
customer accepts. This chapter is that outer cycle: who the parties are,
what the standards call each step, what the contract pins, and how the
measles case walked through it.

## What the standards say

Three organizations are parties. The sponsor is ISO 9000's customer, the
testing organization its provider, and the organization that provides the
test item is ISO/IEC 17000's
{term}`first party <first-party conformity assessment activity>`, the one
accountable for it as its provider. A sponsor with a user interest in the
test item performs a {term}`second-party <second-party conformity assessment activity>`
activity when it commissions and accepts the evaluation; the independent
testing organization performs a third-party activity whoever commissions it. Affected stakeholders are
populations, spoken for, sometimes interviewed, who sign nothing. The
six steps are the standards' own; each quote carries its tag,
[defined on the vocabulary page](glossary.md#quote-tags):

```{include} ../generated/steps-contracting.md
```

The outer cycle has a seventh step between access and delivery, `fulfil`,
which is the whole evaluation performed by the testing organization; the
table lists the six the contract performs itself, and the chapter on the
nested lifecycle draws the seventh.

## The specification

The model states the cycle as parts, ports and wires: a part is a party or
a role inside the testing organization, a port the typed point where an
item leaves or enters a part, and a wire (a seam, in the model) joins an
output port to an input port and carries one item kind. Four parties,
the fourth the affected populations who sign nothing, three actor
categories within the testing organization, and the wires between them. The sponsor holds an obligation towards the
affected populations, states its mission and then its need, and receives
the proposal; the authorized representative answers, countersigns and, at the end,
delivers; the test item provider grants access; every item reaches
the recorder, the machine that keeps the record. Input wires are unique,
output wires fan out. One item sits on the boundary between the contract
and its fulfilment: the {term}`statement of work`, the sponsor's
scope-of-work decision that says, for each affected population, whether it
is interviewed before it is spoken for. A representative on the team speaks
for every population; the interview, when decided, feeds that representation.
Decided with the agreement, it is what the scope step consumes, and the
record must realize it either way.

The figure is one view of the model: wires between the same two parts are
braided into one bundle labelled by what flows, in the order it is
produced, and the obligation is dotted because it is a relation, not a
flow. The caption says what the view brings into focus and what it leaves
out. In the model this cycle is the outer `action def`, SysML's definition
of a process as steps in succession, and its `fulfil` step is the whole
evaluation as a black box.

```{include} ../generated/wiring-contracting.md
```

What the contract pins is the first layer of assumptions: the
counterparties, the test item, the frame of the requirements and the
method. The evaluation takes them as given and cannot change them. The
essentials are the statements the specification must keep, SCI-01 to
SCI-13, each naming the shapes that check it; a shape is one
machine-checked rule over the record or over the model, written in SHACL,
the W3C Shapes Constraint Language. The essentials this chapter states:

```{include} ../generated/sci-contracting.md
```

The first of them as `ogc`, the reader of the repository's graphs, prints
it, with the shapes that check it and the rulings and sources it rests on:

```{literalinclude} ../generated/cli/sci-10.md
```

## The walkthrough

The county public-health office exists to protect the health of residents
and of the people passing through the county, and must inform the public
accurately during an outbreak; that mission is the first item in the
record. It needed to know whether its chatbot could give measles advice to
the public. Humane Intelligence proposed an OG-CAIE evaluation; Mala, its
authorized representative, signed for it on 31 July with the county; the chatbot's
vendor opened API access to version 1 the same day. Two populations were
affected: commuters, interviewed and then spoken for by Theo from the
interview, and county residents, spoken for by Annie, the domain expert,
without one. The split was the county's decision in its statement of work, made with
the agreement: representation is the common case, and interviews are
reserved for underdocumented needs because of the effort they cost; the
commuters' needs were underdocumented, the residents' were not. After the
evaluation, Mala delivered the report and the recommendation on 12 August
and the county accepted on 14 August. The case is synthetic: the
names are borrowed from real colleagues whose roles they recognise, and no
signature or attestation here was made by them.

```{include} ../generated/record-contracting.md
```

The statement of work as the tool reads it, with its canonical quote and
the ruling that made it an item of its own:

```{literalinclude} ../generated/cli/term-statement-of-work.md
```

Two further steps are observed in practice and are deliberately not part
of the contracting lifecycle: the county tells the vendor to implement
changes that produce a demonstrable change in behaviour, per Humane
Intelligence's findings, and may then require new testing to certify that
the flagged issues were addressed, as a safety-critical deployment would
pair an evaluation with a release. Both parties are already in the record,
so nothing new is needed to say it; the standards call the repeat
{term}`monitoring`, the status of the system determined again at a later
stage. An evaluation record that traces every finding to its evidence is
what a sponsor hands a vendor, and what a second evaluation is measured
against.

## Checked

Shapes S0-Parties, S0-Access, S0-Population, S0-StatementOfWork, S0-Need,
S0-Proposal, S0-Layers and S9-Acceptance run over the record; M1-Parties,
M1-Obligation and M5-Cardinality run over the model graph. Four
counterexamples, three records and a model broken on purpose, must fail: a
requirement set declared before the agreement was signed fails the layer
rule; an affected population nobody speaks for fails
S0-Population, and so does a population the statement of work said would be
interviewed but the record only speaks for; a model with a sponsor and
populations but no obligation between them fails M1-Obligation. Every
block and wire of this slice is validated on rulings sheet 05.

:::{admonition} Verdict
:class: checked
The record conforms, and every counterexample fails where it must.
Computational proof: [run the checks](../notebooks/checked-contracting.ipynb).
:::

## There is more in the model

:::{admonition} Ask the graph
:class: more

```{include} ../generated/more-contracting.md
```
:::

## Sources cited

```{include} ../generated/cited-contracting.md
```
