# Stakeholders and contracting

An evaluation is work done under a contract. Before any test runs, a
{term}`customer` has stated a need, a {term}`provider` has answered it, the
two have signed, and the {term}`test item`'s provider
has opened it up. After the last attestation, the provider delivers and the
customer accepts. This chapter is that outer cycle: the parties, the steps,
what the contract pins, and the measles case.

## What the standards say

Three organizations are parties. The sponsor is ISO 9000's customer, the
testing organization its provider, and the organization that provides the
test item is accountable for it as its provider, ISO/IEC 17000's
{term}`first party <first-party conformity assessment activity>`. The
sponsor's obligation to the affected populations is its own and the
contract does not transfer it. A sponsor with a user interest in the test
item performs a {term}`second-party <second-party conformity assessment activity>`
activity when it commissions and accepts the evaluation; the independent
testing organization performs a third-party activity whoever commissions
it. Affected stakeholders are
populations, spoken for, sometimes interviewed, who sign nothing. The
six steps are the standards' own; each quote carries its tag,
[defined on the vocabulary page](glossary.md#quote-tags):

```{include} ../generated/steps-contracting.md
```

A seventh step, `fulfil`, the whole evaluation, sits between access and
delivery; the nested lifecycle chapter draws it.

## The specification

The model states the cycle as parts, ports and wires: a part is a party or
a role inside the testing organization, a port the typed point where an
item leaves or enters a part, and a wire (a seam, in the model) joins an
output port to an input port and carries one item kind. The sponsor holds
an obligation towards the affected populations, states its mission and
then its need, and receives the proposal. Where the sponsor signs, a
named person signs for it: its signatory signs the agreement, declares the
user interest, approves the requirement set and accepts the delivery. The
authorized representative answers, countersigns, declares the testing
organization's independence and, at the end, delivers. The agreement
accepts the proposal; the statement of work, the access and the delivery
are performed under it. The test item provider grants access for a stated
version and period in a named environment; its duty to give that access
comes from an instrument outside this agreement, and the record names it.
Every item reaches the recorder, the machine that keeps the record; input
wires are unique, output wires fan out. One item sits on the boundary
between the contract and its fulfilment: the {term}`statement of work`,
the sponsor's decision that says, for each affected population, whether
it is interviewed before it is spoken for. A team member speaks for every
population; the interview, when decided, feeds that representation, and
the record must realize the decision. In
the model this cycle is the outer `action def`, SysML's definition of a
process as steps in succession, and its `fulfil` step is the whole
evaluation as a black box.

```{include} ../generated/wiring-contracting.md
```

What the contract pins is the first layer of assumptions: the
counterparties, the test item, the frame of the requirements and the
method. The evaluation takes them as given and cannot change them. The
record states the level at which independence between roles is required;
the measles evaluation is at the person level: nobody determines alone on
evidence from a session they ran, and nobody assesses a requirement set
they wrote. The {term}`report` is the record's delivered export; the record itself
is not delivered but is independently auditable, access to it a special
case, publication not assumed.
Acceptance is the sponsor's act on receipt of the deliverables,
recognizing completion of the contract's obligations; a correctly
constructed record is necessary and not sufficient for it, and it is not
the {term}`acceptance criteria` the evaluation tests. The
essentials are the statements the specification must keep, SCI-01 to
SCI-13, each naming the shapes that check it, a shape being one
machine-checked rule written in SHACL, the W3C Shapes Constraint Language.
The essentials this chapter states:

```{include} ../generated/sci-contracting.md
```

The first of them as `ogc`, the reader of the repository's graphs, prints
it:

```{literalinclude} ../generated/cli/sci-10.md
```

## The walkthrough

The county public-health office exists to protect the health of residents
and of the people passing through the county, and must inform the public
accurately during an outbreak; that mission opens the record. It needed to
know whether its chatbot could give measles advice to the public. Humane
Intelligence proposed an OG-CAIE evaluation; Mala, its
authorized representative, signed for it on 31 July and declared it
independent of the vendor; Dana Okafor, the county's health officer,
signed for the county and declared its user interest in the chatbot; the
vendor opened API access to version 1 the same day, for August, under its
deployment contract with the county. Two populations were affected:
commuters, interviewed and then spoken for by Theo, and county residents,
spoken for by Annie, the domain expert, without an interview, as the
county's statement of work decided. After the
evaluation, Mala delivered the final report, its approval and the
{term}`recommendation`, fit to deploy once the vaccination question is asked before
any advice, on 12 August, and Dana Okafor accepted for the county on 14
August. The case is synthetic: the names are borrowed from real colleagues
whose roles they recognise, the health officer is invented, and no
signature or attestation here was made by them.

```{include} ../generated/record-contracting.md
```

The statement of work as the tool reads it, with its canonical quote and
the ruling that made it an item of its own:

```{literalinclude} ../generated/cli/term-statement-of-work.md
```

Two further steps are observed in practice and are not part of the
contracting lifecycle: the county tells the vendor to change the chatbot,
and may then require new testing. The standards call
the repeat {term}`monitoring`, the status of the system determined again
at a later stage; a new version of the test item opens a new record linked
to the old one, and a record that traces every finding to its evidence is
what a second evaluation is measured against.

## Checked

Shapes S0-Record, S0-Member, S0-Parties, S0-Roles, S0-Independence,
S0-Access, S0-Population, S0-StatementOfWork, S0-Mission, S0-Need,
S0-Proposal, S0-Layers, S8-Delivery and S9-Acceptance run over the record; M1-Parties, M1-Obligation
and M5-Cardinality run over the model graph. Seven counterexamples, six
records and a model broken on purpose, must fail: among them a requirement
set declared before the agreement, a population nobody speaks for, a
person holding two roles, an independence nobody declared, an acceptance
by the organization instead of its signatory, and a model with no
obligation between the sponsor and the populations. Five rows await their ticks on
rulings sheet 05 (C-30).

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
