**The executed runs.**

| Run | Shapes S0 to S9 | Item kinds missing | Coverage (pass / fail / cannot tell) | Traceback rows |
|---|---|---|---|---|
| planned 2 of 3 | conforms | none | 0.6667 (0.50 / 0.50 / 0.00) | 2 |
| planned 3 of 3 | conforms | none | 1.0000 (0.33 / 0.67 / 0.00) | 3 |
| two sessions, two requirements | conforms | none | 1.0000 (0.50 / 0.50 / 0.00) | 8 |

**The mutations of the first run.**

| Mutation | Shapes S0 to S9 | Item kinds missing | Coverage (pass / fail / cannot tell) | Traceback rows | Caught by |
|---|---|---|---|---|---|
| skip-assessment: skip the appropriateness assessment (a step's output missing) | fails S2-RequirementSet | AppropriatenessAssessment | 0.6667 (0.50 / 0.50 / 0.00) | 2 | shapes S2-RequirementSet; completeness (AppropriatenessAssessment missing) |
| skip-approval: skip the plan approval | conforms | PlanApproval | 0.6667 (0.50 / 0.50 / 0.00) | 2 | completeness (PlanApproval missing) |
| skip-access: skip the access grant (a contracting step missing) | conforms | TestItemAccess | 0.6667 (0.50 / 0.50 / 0.00) | 0 | completeness (TestItemAccess missing); traceback (no row) |
| unwire-evidence: cut the wire binding evidence to its plan | fails S5-Evidence, S6-Attestation | none | 0.6667 (0.50 / 0.50 / 0.00) | 0 | shapes S5-Evidence, S6-Attestation; traceback (no row) |
| executive-attests: the account executive attests instead of the domain expert | fails S6-Attestation | none | 0.6667 (0.50 / 0.50 / 0.00) | 2 | shapes S6-Attestation |
| attest-without-determination: attestations aggregate no determination | fails S6-Attestation, S8-Recommendation | none | 0.6667 (0.50 / 0.50 / 0.00) | 0 | shapes S6-Attestation, S8-Recommendation; traceback (no row) |
| requirements-before-agreement: the requirement set dated before the agreement | fails S0-Layers, S0-Parties | none | 0.6667 (0.50 / 0.50 / 0.00) | 2 | shapes S0-Layers, S0-Parties |
| engagement-mismatch: the statement of work decides representation for a population the record only interviewed | fails S0-Population | none | 0.6667 (0.50 / 0.50 / 0.00) | 2 | shapes S0-Population |
| skip-report-approval: the report delivered without a domain expert's approval of its contents | fails S8-Delivery | ReportApproval | 0.6667 (0.50 / 0.50 / 0.00) | 2 | shapes S8-Delivery; completeness (ReportApproval missing) |
