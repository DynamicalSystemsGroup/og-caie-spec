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

```{include} ../generated/record.md
```

The three counterexamples are small graphs, each built to violate one shape:
a verdict with no evidence behind it (the closure rule, S6), a requirement set
declared after testing started (S2), and a recommendation that rests on no
attestation and names no DSO release (S8). Each fails on exactly that shape.
