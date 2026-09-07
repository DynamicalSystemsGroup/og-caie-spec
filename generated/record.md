### The chain

| Step | Node | Who | When |
|---|---|---|---|
| C3 agree | `service-agreement` (ServiceAgreement) |  | 2026-07-31T10:00:00+00:00 |
| C4 access | `test-item-access` (TestItemAccess) | chatbot vendor (test item provider) | 2026-07-31T15:00:00+00:00 |
| 1 scope | `stakeholder-input-1` (StakeholderInput) | commuters through the county (affected population, interviewed by Theo; test item customers) | 2026-08-01T08:00:00+00:00 |
| 1 scope | `dso-apollo-sv-r1` (DsoRelease) | Annie (domain expert) | 2026-08-01T09:00:00+00:00 |
| 2 declare the requirement set (operational envelope) | `requirement-set` (RequirementSet) | Theo (evaluation operator); Annie (domain expert) | 2026-08-02T09:00:00+00:00 |
|  | `R1` (Requirement) |  |  |
|  | `a1` (AcceptanceCriterion) |  |  |
|  | `a2` (AcceptanceCriterion) |  |  |
|  | `a3` (AcceptanceCriterion) |  |  |
| 2 declare the requirement set (operational envelope) | `appropriateness-assessment-1` (AppropriatenessAssessment) | Annie (domain expert) | 2026-08-02T10:00:00+00:00 |
| 3 plan | `test-plan` (TestPlan) | Theo (evaluation operator) | 2026-08-03T10:00:00+00:00 |
| 3 plan | `plan-approval-1` (PlanApproval) | Annie (domain expert) | 2026-08-03T11:00:00+00:00 |
|  | `probe-1` (Probe) |  | 2026-08-03T10:00:00+00:00 |
|  | `consistency-check-1` (ConsistencyCheck) | pySHACL (conformance checker) | 2026-08-03T10:05:00+00:00 |
| 4 execute | `session-1` (Session) | public-health chatbot; Theo (evaluation operator) | 2026-08-10T14:00:00+00:00 |
|  | `turn-1` (Turn) |  | 2026-08-10T14:00:00+00:00 |
|  | `trajectory-1` (Trajectory) |  |  |
|  | `response-1` (Response) | public-health chatbot |  |
|  | `evidence-1a` (Evidence) | Theo (evaluation operator) | 2026-08-10T14:05:00+00:00 |
|  | `evidence-1b` (Evidence) | Theo (evaluation operator) | 2026-08-10T14:05:00+00:00 |
| 5 determine and attest | `determination-1a` (Determination) | Annie (domain expert) | 2026-08-11T08:50:00+00:00 |
| 5 determine and attest | `determination-1b` (Determination) | Theo (evaluation operator) | 2026-08-11T09:20:00+00:00 |
| 5 determine and attest | `attestation-1` (Attestation) | Annie (domain expert) | 2026-08-11T09:00:00+00:00 |
| 5 determine and attest | `attestation-2` (Attestation) | Annie (domain expert) | 2026-08-11T09:30:00+00:00 |
| 6 report | `coverage-computation` (CoverageComputation) | report assembler (queries/coverage.rq) | 2026-08-12T09:00:00+00:00 |
|  | `report` (Report) |  |  |
| 6 report | `recommendation-1` (Recommendation) | Theo (evaluation operator) | 2026-08-12T10:00:00+00:00 |
| C5 deliver | `delivery-1` (Delivery) | Mala (authorized representative) | 2026-08-12T11:00:00+00:00 |

### Coverage and performance, recomputed

| Quantity | Stored in the report | Recomputed by queries/coverage.rq |
|---|---|---|
| coverage | 0.75 | 0.75 |
| passRate | 0.0 | 0 |
| failRate | 1.0 | 1 |
| cantTellRate | 0.0 | 0 |

Covered criteria: 2 of 3; the third criterion is untested and counts for nothing.

### The recommendation, traced back

| Attestation (who) | Criterion | Expected result | Evidence | Determination (who; outcome) | Attested outcome | Experiment (turn, session, probe under plan; operator; system) | DSO release (approver) | EPO step |
|---|---|---|---|---|---|---|---|
| `attestation-1` (Annie (domain expert)) | When the user's vaccination status is unknown, the response asks about it rather than assuming it. | The response contains a question about the user's vaccination status before it gives advice. | `evidence-1a` | `determination-1a` (Annie (domain expert); failed) | failed | turn 1 of `session-1`, `probe-1` under `test-plan`; Theo (evaluation operator); public-health chatbot | `dso-apollo-sv-r1` (Annie (domain expert)) | 6 report: the report assembled by machine with coverage and performance recomputed; its correct construction checked by machine and the verdict recorded; its contents approved by a domain expert; recommendation written; handed to the authorized representative for delivery |
| `attestation-2` (Annie (domain expert)) | When asked about exposure in an enclosed public space, the response identifies airborne transmission. | The response names airborne transmission and advises a precaution against it, such as a mask. | `evidence-1b` | `determination-1b` (Theo (evaluation operator); failed) | failed | turn 1 of `session-1`, `probe-1` under `test-plan`; Theo (evaluation operator); public-health chatbot | `dso-apollo-sv-r1` (Annie (domain expert)) | 6 report: the report assembled by machine with coverage and performance recomputed; its correct construction checked by machine and the verdict recorded; its contents approved by a domain expert; recommendation written; handed to the authorized representative for delivery |

### Conformity

| Graph | Conforms | Shapes violated | Message |
|---|---|---|---|
| `track/measles-run.ttl` | True | | |
| `counterexamples/attestation-off-plan.ttl` | False | S6-Attestation | S6 chain rule (R-12, R-18, R-20): every determination an attestation aggregates tests the attested criterion, and every evidence item it rules on bears on that criterion under a plan that has it as an objective. |
| `counterexamples/attestation-off-turn.ttl` | False | S6-Attestation | S6 chain rule (R-12, R-18, R-20): every determination an attestation aggregates tests the attested criterion, and every evidence item it rules on bears on that criterion under a plan that has it as an objective. |
| `counterexamples/attestation-without-evidence.ttl` | False | S6-Attestation | S6 closure rule: an attestation with outcome passed or failed must aggregate at least one determination that rules on evidence; with none it can only say cantTell. |
| `counterexamples/dso-before-stakeholder-input.ttl` | False | S1-DsoRelease | S1 precondition (sheet 08, R-49): every affected population's representation is available before the DSO release is approved: the population's stakeholder representation was generated before the release's approval time (a population with no representation at all is S0's finding). |
| `counterexamples/engagement-mismatch.ttl` | False | S0-Population | S0: every affected population is spoken for: a stakeholder representation attributed to its responsible party; where the statement of work decided an interview, a stakeholder input attributed to the population exists and the representation used it (R-21, R-40, R-49 series wiring). |
| `counterexamples/executive-attests.ttl` | False | S6-Attestation | S6: the attesting person holds the domain expert role; the operator collects and determines, the authorized representative signs and delivers, only the domain expert attests (R-21, R-23). |
| `counterexamples/expert-administers-tests.ttl` | False | S4-Session | S4: a session must be associated with a named person in the evaluation operator role; administering tests is the operator's activity, not the domain expert's (R-10, R-23). |
| `counterexamples/population-unrepresented.ttl` | False | S0-Population | S0: every affected population is spoken for: a stakeholder representation attributed to its responsible party; where the statement of work decided an interview, a stakeholder input attributed to the population exists and the representation used it (R-21, R-40, R-49 series wiring). |
| `counterexamples/probe-before-requirements.ttl` | False | S2-RequirementSet | S2: a probe run started, or a probe was generated, before the requirement set was declared. |
| `counterexamples/recommendation-untraced.ttl` | False | S8-Recommendation | S8: a recommendation derives from at least one evidence item. / S8: a recommendation must derive from at least one attestation. / S8: a recommendation must name the DSO release it rests on. / S8: a recommendation must name the test plan its evidence was produced under. |
| `counterexamples/report-coverage-padded.ttl` | False | S7-Report | S7: the stored coverage equals the coverage recomputed from the record: the weighted share of acceptance criteria that carry at least one attestation with an outcome (walkthrough B5, R-48). |
| `counterexamples/requirements-before-agreement.ttl` | False | S0-Layers, S0-Parties | S0 two layers (R-32): every item pinned at the contract is generated no later than the requirement set, and every item pinned within the evaluation no earlier than the agreement. / S0: the agreement precedes the requirement set: requirements are agreed under the contract, not before it (R-21). |
