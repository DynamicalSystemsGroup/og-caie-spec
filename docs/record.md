# The record

One evaluation record, `track/measles-run.ttl`, in plain Turtle: PROV-O for
who did what and when, EARL for assertions and their outcomes, and the
Evaluation Process Ontology's handle classes (`vocabulary/epo.ttl`) for what
the five steps produce. It is the paper's worked example: a public-health
chatbot during a measles outbreak, one requirement, three acceptance criteria,
one probe run by red teaming, one response, two attestations by two named
domain experts, a report, and a recommendation. The traceback query below is
requirements traceability made executable.

Two things are checked over it. **Conformity** to the EPO shapes
(`shapes/epo.shapes.ttl`, S1 to S8) is machine verification: the process was
followed, the data is shaped, the required fields are filled. **Recomputation**
of coverage and performance by SPARQL (`queries/coverage.rq`) is what makes
the reported numbers falsifiable: anyone holding the record gets the same
numbers, and a padded number would not survive. What no shape checks is
whether the experts were right. That is theirs, and it is recorded with their
names.

The chain the shapes close is the one that makes a requirement a useful
concept: the requirement, as a hypothesis that may be falsified; its
acceptance criteria, each stating the expected result a test could observe;
the test plan, whose objectives are those criteria and whose means are the
probes; the run of a probe against the system, producing the evidence; and
the attestation, a named person's judgment that the actual result did or did
not correspond to the expected one, bound to that evidence and to the probe
under the plan that produced it. An attestation off the plan, one that
interprets evidence no probe for its criterion produced, fails the chain rule.

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

The three counterexamples are small graphs, each built to violate one shape:
a verdict with no evidence behind it (the closure rule, S6), a requirement set
declared after testing started (S2), and a recommendation that rests on no
attestation and names no DSO release (S8). Each fails on exactly that shape.
