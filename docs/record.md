# The record

One evaluation record, `track/measles-run.ttl`, in plain Turtle: PROV-O for
who did what and when, EARL for assertions and their outcomes, and the
Evaluation Process Ontology's handle classes (`vocabulary/epo.ttl`) for what
the seven steps produce. It is a record in the ISO 9000:2026 sense, a
document stating results achieved or providing evidence of activities
performed, and the standard's own note on the term (3.8.12, Note 1) says what
records are for: to formalize traceability and to provide evidence of
verification. That is the whole job of this file. It is the paper's worked example: a public-health
chatbot during a measles outbreak. Four parties: a county public-health
office as sponsor, the chatbot's vendor as the accountable organization,
Humane Intelligence as the testing organization, and two affected
populations, one interviewed and one represented. One service agreement,
one requirement, three acceptance criteria, one test plan, one session of one
turn run by red teaming, one probe, one response, two evidence items bearing
on two criteria, two determinations, two attestations, a report, a
recommendation and a delivery. The traceback query below is
requirements traceability made executable.

The case is synthetic (ruling R-23). Mala, the account executive who signs
the agreement and delivers the report; Annie, the domain expert who approves
the DSO release, assesses the requirement set, approves the plan and attests;
and Theo, the evaluation operator who declares the requirements, writes the
plan, runs the session, collects the evidence and writes the recommendation,
are named after real people at Humane Intelligence so that their roles are
recognised. No attestation, determination or signature in this record was
made by them; the record says so in its own header.

Two things are checked over it. **Conformance** to the EPO shapes
(`shapes/epo.shapes.ttl`, S0 to S8) is machine verification: the record is
correctly constructed, so the process was followed, the data is shaped, the
required fields are filled. The word is reclaimed on purpose (ruling R-16):
ISO 9000 deprecates it as a synonym of *conformity*, which this specification
keeps for fulfilment of a requirement by the system; and SHACL's own word for
the check, validation, is by this specification's split verification. **Recomputation**
of coverage and performance by SPARQL (`queries/coverage.rq`) is what makes
the reported numbers falsifiable: anyone holding the record gets the same
numbers, and a padded number would not survive. What no shape checks is
whether the experts were right. That is theirs, and it is recorded with their
names.

Evidence has three levels (rulings R-18 and R-20). An evidence item is what
is collected as the basis for a ruling: one response at a turn, a whole
session's trajectory, or several rolled up over a test suite of sessions such
as a robustness battery. It bears on one acceptance criterion's expected result
and is bound to the test plan it was collected under. Evidence is the domain.
The determination made on it, the paper's judgment, is the codomain: the ruling
that the expected result was met, was not met, or cannot be told, an EARL
outcome rather than a Boolean, made by machine or by a named person. The
attestation then aggregates a criterion's determinations. The response itself
stays in the record as what the system said.

The chain the shapes close is the one that makes a requirement a useful
concept: the requirement, as a hypothesis that may be falsified; its
acceptance criteria, each stating the expected result a test could observe;
the test plan, whose objectives are those criteria and whose means are the
probes or a strategy that chooses them; the turn of a session at which a probe
is applied to the system, producing the response; the evidence
collected from it bearing on the expected result; the determination that rules
on that evidence; and the attestation, a named person's judgment aggregating
the determinations for the criterion, bound through them to the evidence and
the plan. An attestation off the plan, one that aggregates a determination
made for a different criterion, fails the chain rule.

The system under test is a non-deterministic system, and a session with it
is stateful: what it says at a later turn depends on the whole dialogue
before. So the record does not hold a bare run. It holds a session, pairing
one tester with one system, whose turns each apply one probe and yield one
response, and whose ordered pairs form the trajectory, the observable
realization standing in for a state the record never sees. A test plan's
means may be a list of probes or a test strategy, a state feedback policy
that chooses the next probe from the trajectory so far. The measles example
has one turn; the two-turn counterexample below, driven by a strategy, shows
the chain rule refusing an attestation that reads turn two's criterion off
turn one's response. Replicate sessions under repeatability conditions are
what turn a criterion's probes into a pass rate with a measurement
uncertainty; reproducibility across operators and teams is what makes two
evaluations of the same requirement set comparable.

```{include} ../generated/record.md
```

Three observations from ISO/IEC 17000:2020, the conformity-assessment
vocabulary that gives us *attestation*, are worth keeping in view. Its
*decision* (7.2), "conclusion, based on the results of review, that fulfilment
of specified requirements has or has not been demonstrated", is exactly the
outcome inside an attestation. Its *review* (7.1) is a consideration of
"suitability, adequacy and effectiveness", which is why this specification does
not use the word adequacy for the context judgment and says appropriateness
instead. And its note on 7.3 observes that first-party attestation is a
declaration and third-party attestation a certification, "but there is no
corresponding term applicable to second-party attestation": a testing
organization attesting on a sponsor's behalf about a vendor's system performs
a second-party activity even when it is independent of the vendor (4.4, Note
2), which is the measles case, and the audit offered at the end of the front
page is the third-party case.

The counterexamples are small graphs, each built to violate one shape: an
attestation with no determination behind its verdict (the closure rule, S6),
an attestation aggregating a determination made for a different criterion
(the chain rule, S6), the same fault across two turns of a strategy-driven
session (S6), a requirement set declared after testing started (S2), and a
recommendation that rests on no attestation and names no DSO release (S8), a
requirement set declared before the agreement was signed (S0), an affected
population neither interviewed nor represented (S0), a session run by the
domain expert instead of the operator (S4), and an attestation by the account
executive (S6). Each fails on exactly that shape. Three more, in SysML,
break the wiring and fail their M-shape on the assemblage page.
