| ID | Statement | Checked by |
|---|---|---|
| SCI-01 | The Domain-Specific Ontology release is versioned and approved by a named domain expert before any probe is derived from it. | S1-DsoRelease |
| SCI-02 | The service agreement, the operational environment, the test item and the requirement set are declared, in that order, before any session runs, and every session runs within the period access was granted for: this system in this environment under this contract. | S0-Access, S0-Parties, S2-RequirementSet, S4-Session |
| SCI-03 | Every requirement has at least one acceptance criterion derived from it; every criterion states its expected result and carries a positive weight. | S2-AcceptanceCriterion, S2-Requirement |
| SCI-04 | A test plan states its objectives and its means; every probe belongs to a plan, derives from the DSO release and passes a consistency check before any session. | S3-PlanApproval, S3-PlanDeviation, S3-Probe, S3-Strategy, S3-TestPlan |
| SCI-05 | Every response comes from a numbered turn of a session against a versioned test item; every evidence item bears on one criterion's expected result under the plan. | S4-Session, S4-TestSuite, S4-Turn, S5-Evidence, S5-Response |
| SCI-06 | Determinations rule on evidence with an EARL outcome; attestations aggregate a criterion's determinations, name their assertor, and judge appropriateness and sufficiency; the closure and chain rules hold. | S6-Attestation, S6-Determination |
