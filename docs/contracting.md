# Stakeholders and contracting

An evaluation is work done under a contract. Before any test runs, a
{term}`customer` has stated a need, a {term}`provider` has answered it, the
two have signed, and the organization accountable for the {term}`test item`
has opened it up. After the last attestation, the provider delivers and the
customer accepts. This chapter is that outer cycle: who the parties are,
what the standards call each step, what the contract pins, and how the
measles case walked through it.

:::{admonition} What the standards say
:class: standards

Three organizations are parties. The sponsor is ISO 9000's customer, the
testing organization its provider, and the organization that provides the
test item is ISO/IEC 17000's first party; a sponsor with a user interest is
a second party, and a testing organization working on its behalf performs a
second-party activity even when independent of the provider. Affected
stakeholders are populations, interviewed or represented. The six steps are
the standards' own, none coined here:

```{include} ../generated/steps-contracting.md
```

The outer cycle has a seventh step between access and delivery, `fulfil`,
which is the whole evaluation performed by the testing organization; the
table lists the six the contract performs itself, and the chapter on the
nested lifecycle draws the seventh.
:::

:::{admonition} The specification
:class: specification

Four parties, three actor categories within the testing organization, and
the wires between them. The sponsor holds an obligation towards the
affected populations, states its mission and then its need, and receives
the proposal; the account executive answers, countersigns and, at the end,
delivers; the accountable organization grants access; every item reaches
the recorder. Input wires are unique, output wires fan out, and each wire
carries one item kind. One item sits on the boundary between the contract
and its fulfilment: the {term}`statement of work`, the sponsor's scope-of-work
decision that says, for each affected population, whether it is interviewed,
with its stakeholder needs documented as input, or represented by the domain
expert. Decided with the agreement, it is what the scope step consumes, and
the record must realize it either way. The figure is one view of the model: wires between
the same two parts are braided into one bundle labelled by what flows, in
the order it is produced, and the obligation is dotted because it is a
relation, not a flow. The caption says what the view brings into focus and
what it leaves out. In the model this cycle is the outer action def, and
its `fulfil` step is the whole evaluation as a black box.

```{include} ../generated/wiring-contracting.md
```

What the contract pins is the first layer of assumptions: the
counterparties, the test item, the frame of the requirements and the
method. The evaluation takes them as given and cannot change them. The
essentials this chapter states:

```{include} ../generated/sci-contracting.md
```
:::

:::{admonition} The walkthrough
:class: walkthrough

The county public-health office exists to protect the health of residents
and of the people passing through the county, and must inform the public
accurately during an outbreak; that mission is the first item in the
record. It needed to know whether its chatbot could give measles advice to
the public. Humane Intelligence proposed an OG-CAIE
evaluation; Mala, its account executive, signed for it on 31 July with the
county; the chatbot's
vendor opened API access to version 1 the same day. Two populations were
affected: commuters, who were interviewed, and county residents, whom
Annie, the domain expert, represents. That split was the county's decision in its statement of work,
made with the agreement: representation is the common case, and interviews
are reserved for underrepresented stakeholders or underdocumented needs
because of the effort they cost; the commuters' needs were underdocumented,
the residents' were not. The example splits the two on purpose, to show that
both options are valid and traceable. After the evaluation, Mala delivered
the report and the
recommendation on 12 August and the county accepted on 14 August. The case
is synthetic: the names are borrowed from real colleagues whose roles they
recognise, and no signature or attestation here was made by them.

```{include} ../generated/record-contracting.md
```

Two further steps are observed in practice and are deliberately not part of
the contracting lifecycle. The county tells the chatbot's vendor that it
must implement changes that produce a demonstrable change in behaviour,
per Humane Intelligence's findings; the vendor implements them; and the
county may then require new testing to certify that the flagged issues were
addressed. For a safety-critical deployment one would expect the evaluation
to be paired with a release in exactly this way. Both parties are already in
the record, the sponsor and the accountable organization, so nothing new is
needed to say it; the standards call the repeat {term}`monitoring`, the
status of the system determined again at a later stage. It is what makes
this more than an academic exercise: an evaluation record that traces every finding to its
evidence is what a sponsor hands a vendor, and what a second evaluation is
measured against.
:::

:::{admonition} Checked
:class: checked

Shapes S0-Parties, S0-Access, S0-Population, S0-StatementOfWork, S0-Need,
S0-Proposal, S0-Layers and S9-Acceptance run over the record; M1-Parties, M1-Obligation and
M5-Cardinality run over the model graph. The record conforms. Two counterexamples fail where
they must: a requirement set declared before the agreement was signed fails
the layer rule, and an affected population neither interviewed nor
represented fails S0-Population, and so does a population the statement of
work said would be interviewed but the record only represents. A model with a sponsor and populations but
no obligation between them fails M1-Obligation.
Computational proof: [run the checks](../notebooks/checked-contracting.ipynb).
:::

:::{admonition} There is more in the model
:class: more

```{include} ../generated/more-contracting.md
```
:::
