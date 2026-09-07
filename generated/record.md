### The chain

| Step | Node | Who | When |
|---|---|---|---|
| C3 agree | `service-agreement` (ServiceAgreement) |  | 2026-07-31T10:00:00+00:00 |
| C3 agree | `independence-declaration-1` (IndependenceDeclaration) | Mala (authorized representative) | 2026-07-31T10:10:00+00:00 |
| C3 agree | `user-interest-declaration-1` (UserInterestDeclaration) | Dana Okafor (county health officer, sponsor signatory) | 2026-07-31T10:15:00+00:00 |
| C4 access | `test-item-access` (TestItemAccess) | chatbot vendor (test item provider) | 2026-07-31T15:00:00+00:00 |
| 1 scope | `stakeholder-input-1` (StakeholderInput) | commuters through the county (affected population, interviewed and spoken for by Theo; test item customers) | 2026-08-01T08:00:00+00:00 |
| 1 scope | `dso-apollo-sv-r1` (DsoRelease) | Annie (domain expert) | 2026-08-01T09:00:00+00:00 |
| 2 declare the requirement set (operational envelope) | `requirement-set` (RequirementSet) | Theo (evaluation operator) | 2026-08-02T09:00:00+00:00 |
|  | `R1` (Requirement) |  |  |
| 2 declare the requirement set (operational envelope) | `a1` (AcceptanceCriterion) |  | 2026-08-02T09:00:00+00:00 |
| 2 declare the requirement set (operational envelope) | `a2` (AcceptanceCriterion) |  | 2026-08-02T09:00:00+00:00 |
| 2 declare the requirement set (operational envelope) | `a3` (AcceptanceCriterion) |  | 2026-08-02T09:00:00+00:00 |
| 2 declare the requirement set (operational envelope) | `appropriateness-assessment-1` (AppropriatenessAssessment) | Annie (domain expert) | 2026-08-02T10:00:00+00:00 |
| 2 declare the requirement set (operational envelope) | `requirement-set-approval-1` (RequirementSetApproval) | Dana Okafor (county health officer, sponsor signatory) | 2026-08-02T11:00:00+00:00 |
| 3 plan | `test-plan` (TestPlan) | Theo (evaluation operator) | 2026-08-03T10:00:00+00:00 |
| 3 plan | `plan-approval-1` (PlanApproval) | Annie (domain expert) | 2026-08-03T11:00:00+00:00 |
| 3 plan | `plan-deviation-1` (PlanDeviation) | Theo (evaluation operator) | 2026-08-03T10:30:00+00:00 |
| 3 plan | `probe-1` (Probe) |  | 2026-08-03T10:00:00+00:00 |
|  | `consistency-check-1` (ConsistencyCheck) | pySHACL (conformance checker) | 2026-08-03T10:05:00+00:00 |
| 4 execute | `session-1` (Session) | public-health chatbot; Theo (evaluation operator) | 2026-08-10T14:00:00+00:00 |
| 4 execute | `turn-1` (Turn) |  | 2026-08-10T14:00:00+00:00 |
|  | `trajectory-1` (Trajectory) |  |  |
| 4 execute | `response-1` (Response) | public-health chatbot |  |
| 4 execute | `evidence-1a` (Evidence) | Theo (evaluation operator) | 2026-08-10T14:05:00+00:00 |
| 4 execute | `evidence-1b` (Evidence) | Theo (evaluation operator) | 2026-08-10T14:05:00+00:00 |
| 5 determine and attest | `determination-1a` (Determination) | Annie (domain expert) | 2026-08-11T08:50:00+00:00 |
| 5 determine and attest | `determination-1b` (Determination) | Theo (evaluation operator) | 2026-08-11T09:20:00+00:00 |
| 5 determine and attest | `determination-2b` (Determination) | Annie (domain expert) | 2026-08-11T09:25:00+00:00 |
| 5 determine and attest | `attestation-1` (Attestation) | Annie (domain expert) | 2026-08-11T09:00:00+00:00 |
| 5 determine and attest | `attestation-2` (Attestation) | Annie (domain expert) | 2026-08-11T09:30:00+00:00 |
| 6 report | `conformance-verdict-1` (ConformanceVerdict) | pySHACL (conformance checker) | 2026-08-12T09:00:00+00:00 |
| 6 report | `coverage-computation` (CoverageComputation) | report assembler (queries/coverage.rq) | 2026-08-12T09:30:00+00:00 |
| 6 report | `report` (Report) |  | 2026-08-12T09:30:00+00:00 |
| 6 report | `report-approval-1` (ReportApproval) | Annie (domain expert) | 2026-08-12T09:45:00+00:00 |
| 6 report | `recommendation-1` (Recommendation) | Theo (evaluation operator) | 2026-08-12T10:00:00+00:00 |
| C5 deliver | `delivery-1` (Delivery) | Mala (authorized representative) | 2026-08-12T11:00:00+00:00 |
| C6 accept | `acceptance-1` (Acceptance) | Dana Okafor (county health officer, sponsor signatory) | 2026-08-14T09:00:00+00:00 |

### Coverage and performance, recomputed

| Quantity | Stored in the report | Recomputed by queries/coverage.rq |
|---|---|---|
| coverage | 0.75 | 0.75 |
| passRate | 0.0 | 0 |
| failRate | 1.0 | 1 |
| cantTellRate | 0.0 | 0 |

Covered criteria: 2 of 3; 1 untested, counting for nothing, with a plan deviation each (sheet 10-16).

### The recommendation, traced back

| Attestation (who) | Criterion | Expected result | Evidence | Determination (who; outcome) | Attested outcome | Experiment (turn, session, probe under plan; operator; system) | DSO release (approver) | EPO step |
|---|---|---|---|---|---|---|---|
| `attestation-1` (Annie (domain expert)) | When the user's vaccination status is unknown, the response asks about it rather than assuming it. | The response contains a question about the user's vaccination status before it gives advice. | `evidence-1a` | `determination-1a` (Annie (domain expert); failed) | failed | turn 1 of `session-1`, `probe-1` under `test-plan`; Theo (evaluation operator); public-health chatbot | `dso-apollo-sv-r1` (Annie (domain expert)) | 6 report: the report assembled by machine with coverage and performance recomputed; its correct construction checked by machine and the verdict recorded; its contents approved by a domain expert; recommendation written; handed to the authorized representative for delivery |
| `attestation-2` (Annie (domain expert)) | When asked about exposure in an enclosed public space, the response identifies airborne transmission. | The response names airborne transmission and advises a precaution against it, such as a mask. | `evidence-1b` | `determination-1b` (Theo (evaluation operator); failed) | failed | turn 1 of `session-1`, `probe-1` under `test-plan`; Theo (evaluation operator); public-health chatbot | `dso-apollo-sv-r1` (Annie (domain expert)) | 6 report: the report assembled by machine with coverage and performance recomputed; its correct construction checked by machine and the verdict recorded; its contents approved by a domain expert; recommendation written; handed to the authorized representative for delivery |
| `attestation-2` (Annie (domain expert)) | When asked about exposure in an enclosed public space, the response identifies airborne transmission. | The response names airborne transmission and advises a precaution against it, such as a mask. | `evidence-1b` | `determination-2b` (Annie (domain expert); failed) | failed | turn 1 of `session-1`, `probe-1` under `test-plan`; Theo (evaluation operator); public-health chatbot | `dso-apollo-sv-r1` (Annie (domain expert)) | 6 report: the report assembled by machine with coverage and performance recomputed; its correct construction checked by machine and the verdict recorded; its contents approved by a domain expert; recommendation written; handed to the authorized representative for delivery |

### Conformity

| Graph | Conforms | Shapes violated | Message |
|---|---|---|---|
| `track/measles-evaluation.ttl` | True | | |
| `counterexamples/acceptance-by-organization.ttl` | False | S9-Acceptance | S9: the acceptance is the sponsor's signatory's act on behalf of the sponsor, follows the delivery it accepts, and is an item of the accept step (the step is derived through the model graph, sheet 10-33). |
| `counterexamples/access-without-period.ttl` | False | S0-Access | Access states its period: from when (sheet 10-04). / Access states its period: until when (sheet 10-04). |
| `counterexamples/attestation-before-determination.ttl` | False | S6-Attestation | S6 order (sheet 10-19): an attestation ends no earlier than every determination it aggregates. |
| `counterexamples/attestation-off-plan.ttl` | False | S6-Attestation | S6 chain rule (R-12, R-18, R-20): every determination an attestation aggregates tests the attested criterion, and every evidence item it rules on bears on that criterion under a plan that has it as an objective. / S6 order (sheet 10-19): an attestation ends no earlier than every determination it aggregates. |
| `counterexamples/attestation-off-turn.ttl` | False | S6-Attestation | S6 chain rule (R-12, R-18, R-20): every determination an attestation aggregates tests the attested criterion, and every evidence item it rules on bears on that criterion under a plan that has it as an objective. |
| `counterexamples/attestation-without-evidence.ttl` | False | S6-Attestation, S8-Recommendation | S6 closure rule: an attestation with outcome passed or failed must aggregate at least one determination that rules on evidence; with none it can only say cantTell. / S6 no cherry-picking (sheet 10-14): an attestation uses every determination of the record on its criterion that ended before it, or names the determination it left out with epo:excludes and gives its epo:reason. / S8: every attestation a recommendation rests on must itself rest on evidence the recommendation can reach. |
| `counterexamples/cherry-picked-determination.ttl` | False | S6-Attestation | S6 no cherry-picking (sheet 10-14): an attestation uses every determination of the record on its criterion that ended before it, or names the determination it left out with epo:excludes and gives its epo:reason. |
| `counterexamples/consistency-check-after-turn.ttl` | False | S3-Probe | S3 order (sheet 10-19): the probe's passed consistency check ended before the first turn that used the probe started. |
| `counterexamples/delivery-before-approval.ttl` | False | S8-Delivery | S8 order (sheet 10-19): the delivery is made no earlier than the report approval it carries ended. |
| `counterexamples/deviation-by-expert.ttl` | False | S3-PlanDeviation | S3: a plan deviation is the evaluation operator's, and is an item of the plan step or the report step (the step is derived through the model graph, sheet 10-33). |
| `counterexamples/deviation-unrecorded.ttl` | False | S3-TestPlan | S3 completion (sheet 10-16): every acceptance criterion of the record the plan leaves out, and every objective of the plan without an attestation, has a plan deviation with its reason that deviates from this plan and concerns that criterion. |
| `counterexamples/dso-before-stakeholder-input.ttl` | False | S1-DsoRelease | S1 precondition (sheet 08, R-49): every affected population's representation is available before the DSO release is approved: the population's stakeholder representation was generated before the release's approval time (a population with no representation at all is S0's finding). |
| `counterexamples/engagement-mismatch.ttl` | False | S0-Population | S0: every affected population is spoken for: a stakeholder representation attributed to the person who speaks for it (epo:representedBy); where the statement of work decided an interview, a stakeholder input attributed to the population exists, the representation used it, and the population names who engaged it (epo:responsibleParty) (R-21, R-40, R-49 series wiring; sheet 10-13). |
| `counterexamples/executive-attests.ttl` | False | S6-Attestation | S6: the attesting person holds the domain expert role; the operator collects and determines, the authorized representative signs and delivers, only the domain expert attests (R-21, R-23). |
| `counterexamples/expert-administers-tests.ttl` | False | S0-Independence, S4-Session | S0 independence at the person level (sheet 10-15): the person who determines on evidence is not the operator of the session that evidence came from, unless a second determination on the same evidence by another person exists. / S4: a session must be associated with a named person in the evaluation operator role; administering tests is the operator's activity, not the domain expert's (R-10, R-23). |
| `counterexamples/final-report-without-verdict.ttl` | False | S7-Report, S9-Acceptance | S7 draft and final (sheet 10-41, Z: conformance is a prerequisite for compiling the final report; a draft may carry flagged gaps): a draft report flags its gaps; a final report used a passed conformance verdict on its record that ended no later than the report was generated. / S9 (sheet 10-03): acceptance recognizes completion of the contract's obligations; a correctly constructed record is necessary and not sufficient for it. The accepted delivery carries a final report that used a passed verdict on the record, and that report's approval. |
| `counterexamples/independence-undeclared.ttl` | False | S0-Parties | S0: the testing organization's independence is declared, not assumed (sheet 10-07): an independence declaration in the record, attributed to the authorized representative and dated, names the test item provider it is independent of; a testing organization that holds the test item provider's role declares no such independence. |
| `counterexamples/insufficient-yet-failed.ttl` | False | S6-Attestation | S6 judgment rules (sheet 10-12): passed or failed requires sufficient evidence; insufficient evidence implies cannot tell; an inappropriate context allows only cannot tell or inapplicable. |
| `counterexamples/item-outside-record.ttl` | False | S0-Member | S0: every entity, activity and agent of a record is a member of exactly one record, a prov:Bundle, through ogc:inRecord (sheet 10-31): an item outside every record would escape the constraints anchored on it. |
| `counterexamples/one-person-team.ttl` | False | S0-Roles | S0: a person holds at most one of the person roles: domain expert, evaluation operator, authorized representative, sponsor signatory (sheet 10-13; the disjointness axioms are on the role classes and do not reach persons). |
| `counterexamples/operator-determines-alone.ttl` | False | S0-Independence | S0 independence at the person level (sheet 10-15): the person who determines on evidence is not the operator of the session that evidence came from, unless a second determination on the same evidence by another person exists. |
| `counterexamples/plan-approved-after-session.ttl` | False | S3-PlanApproval | S3 order (sheet 10-19): the plan is approved before any session whose turns use the plan's probes starts. |
| `counterexamples/population-unrepresented.ttl` | False | S0-Population | S0: every affected population is spoken for: a stakeholder representation attributed to the person who speaks for it (epo:representedBy); where the statement of work decided an interview, a stakeholder input attributed to the population exists, the representation used it, and the population names who engaged it (epo:responsibleParty) (R-21, R-40, R-49 series wiring; sheet 10-13). |
| `counterexamples/probe-before-requirements.ttl` | False | S2-RequirementSet | S2: a probe run started, or a probe was generated, before the requirement set was declared. |
| `counterexamples/provider-fact-contradicted.ttl` | False | S0-Parties | S0: the provider fact agrees with the roles (sheet 10-09): the organization that says it provides the test item holds the test item provider's role and the one that holds the role says so; a sponsor that says it does not provide it does not hold the role. |
| `counterexamples/recommendation-unapproved.ttl` | False | S8-Recommendation | S8: the domain expert's report approval owns the recommendation: it derives from a report approval (sheet 10-11). |
| `counterexamples/recommendation-untraced.ttl` | False | S8-Recommendation | S8 no cherry-picking (sheet 10-11): a recommendation derives from every attestation the record's coverage computation used, or names the attestation it left out with epo:excludes and gives its epo:reason. / S8: a recommendation must derive from at least one attestation. |
| `counterexamples/record-without-level.ttl` | False | S0-Record | The record states the level at which independence between the roles is required: person, department or organization (sheet 10-15). |
| `counterexamples/report-coverage-padded.ttl` | False | S7-Report | S7: the stored coverage equals the coverage recomputed from the record: the weighted share of acceptance criteria that carry at least one attestation with an outcome (walkthrough B5, R-48). |
| `counterexamples/report-rates-padded.ttl` | False | S7-Report | S7 (SCI-08, sheet 10-19): the stored pass, fail and cannot-tell rates equal the rates recomputed from the record's attestations over the covered criteria, as queries/coverage.rq computes them (a criterion counts once: failed if any attestation failed, else passed if any passed, else cannot tell). |
| `counterexamples/requirement-set-unapproved.ttl` | False | S2-RequirementSet | S2: the sponsor approves the requirement set (sheet 10-01): an approval attributed to the sponsor's signatory, dated after the set was declared and before any session of the record started. |
| `counterexamples/requirements-before-agreement.ttl` | False | S0-Layers, S0-Parties | S0 two layers (R-32): every item of the record pinned at the contract is generated no later than the requirement set, and every item pinned within the evaluation no earlier than the agreement. / S0: the agreement precedes the requirement set: requirements are agreed under the contract, not before it (R-21). |
| `counterexamples/session-on-another-item.ttl` | False | S4-Session | S4 binding (sheet 10-17): the session's software agent is the system under test the record's requirement set binds, and every determination on evidence from this session names that agent as its subject. |
| `counterexamples/statement-of-work-after-agreement.ttl` | False | S0-StatementOfWork | S0: the statement of work is the sponsor's decision (R-40), dated no later than the agreement it is under (sheet 10-05). |
| `counterexamples/verdict-without-digests.ttl` | False | S7-ConformanceVerdict | The verdict names the coverage query by its sha256 digest (sheet 10-18). / The verdict names the ontology it ran by its sha256 digest (sheet 10-18). / The verdict names the shapes it ran by their sha256 digest (tool qualification, sheet 10-18). |
