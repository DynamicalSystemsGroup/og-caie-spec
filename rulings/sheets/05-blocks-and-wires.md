# Rulings sheet 05: the blocks and the wires (concern C-30)

Generated from `model/og-caie.model.ttl` by `scripts/render.py`; do not edit the rows by hand, tick them. One row per kind of part (its inputs and outputs) and one per wire (output port on a part to input port on a part). Ticks come from rulings/validated.ttl (Z's walkthrough, R-48 sheet 07-09), so regeneration keeps them; add a concern for anything wrong.

## Blocks

| # | Part kind | Inputs | Outputs | Validated |
|---|---|---|---|---|
| B1 | AccountExecutive | acceptanceIn, agreementIn, missionIn, needIn, recordIn, statementOfWorkIn | agreementOut, deliveryOut, proposalOut | [x] 2026-09-06 |
| B2 | AccountableOrganization | (none) | accessOut | [x] 2026-09-06 |
| B3 | AffectedPopulation | (none) | inputOut | [ ] |
| B4 | ConformanceChecker | recordIn | (none) | [x] 2026-09-06 |
| B5 | CoverageCalculator | recordIn | reportOut | [x] 2026-09-06 |
| B6 | DomainExpert | recordIn | assessmentOut, attestationOut, determinationOut, dsoOut, planApprovalOut | [x] 2026-09-06 |
| B7 | EvaluationOperator | accessIn, probesIn, recordIn | determinationOut, evidenceOut, planOut, probesToItem, recommendationOut, requirementsOut | [x] 2026-09-06 |
| B8 | ProbeDeriver | recordIn | probesOut | [ ] |
| B9 | Recorder | acceptanceIn, accessIn, agreementIn, assessmentIn, attestationIn, deliveryIn, dsoIn, evidenceIn, expertDeterminationIn, inputIn, missionIn, needIn, operatorDeterminationIn, planApprovalIn, planIn, probeIn, proposalIn, recommendationIn, reportIn, requirementsIn, responseIn, statementOfWorkIn | recordOut | [ ] |
| B10 | SponsorOrganization | deliveryIn, proposalIn | acceptanceOut, agreementOut, missionOut, needOut, statementOfWorkOut | [x] 2026-09-06 |
| B11 | TestItem | probesIn | responseOut | [ ] |

## Wires

| # | Wire | From | To | Carries | Validated |
|---|---|---|---|---|---|
| W1 | acceptanceSeam | SponsorOrganization.acceptanceOut | Recorder.acceptanceIn | AcceptanceWrite | [x] 2026-09-06 |
| W2 | acceptanceToExecutiveSeam | SponsorOrganization.acceptanceOut | AccountExecutive.acceptanceIn | AcceptanceWrite | [x] 2026-09-06 |
| W3 | accessSeam | AccountableOrganization.accessOut | Recorder.accessIn | AccessWrite | [x] 2026-09-06 |
| W4 | accessToOperatorSeam | AccountableOrganization.accessOut | EvaluationOperator.accessIn | AccessWrite | [x] 2026-09-06 |
| W5 | agreementSeam | SponsorOrganization.agreementOut | AccountExecutive.agreementIn | AgreementWrite | [x] 2026-09-06 |
| W6 | assessmentSeam | DomainExpert.assessmentOut | Recorder.assessmentIn | AssessmentWrite | [x] 2026-09-06 |
| W7 | attestationSeam | DomainExpert.attestationOut | Recorder.attestationIn | AttestationWrite | [x] 2026-09-06 |
| W8 | countersignSeam | AccountExecutive.agreementOut | Recorder.agreementIn | AgreementWrite | [x] 2026-09-06 |
| W9 | deliveryRecordSeam | AccountExecutive.deliveryOut | Recorder.deliveryIn | DeliveryWrite | [x] 2026-09-06 |
| W10 | deliverySeam | AccountExecutive.deliveryOut | SponsorOrganization.deliveryIn | DeliveryWrite | [x] 2026-09-06 |
| W11 | derivedProbeSeam | ProbeDeriver.probesOut | EvaluationOperator.probesIn | ProbeWrite | [x] 2026-09-06 |
| W12 | dsoSeam | DomainExpert.dsoOut | Recorder.dsoIn | DsoWrite | [x] 2026-09-06 |
| W13 | evidenceSeam | EvaluationOperator.evidenceOut | Recorder.evidenceIn | EvidenceWrite | [x] 2026-09-06 |
| W14 | expertDeterminationSeam | DomainExpert.determinationOut | Recorder.expertDeterminationIn | DeterminationWrite | [x] 2026-09-06 |
| W15 | missionSeam | SponsorOrganization.missionOut | Recorder.missionIn | MissionWrite | [x] 2026-09-06 |
| W16 | missionToExecutiveSeam | SponsorOrganization.missionOut | AccountExecutive.missionIn | MissionWrite | [x] 2026-09-06 |
| W17 | needSeam | SponsorOrganization.needOut | Recorder.needIn | NeedWrite | [x] 2026-09-06 |
| W18 | needToExecutiveSeam | SponsorOrganization.needOut | AccountExecutive.needIn | NeedWrite | [x] 2026-09-06 |
| W19 | operatorDeterminationSeam | EvaluationOperator.determinationOut | Recorder.operatorDeterminationIn | DeterminationWrite | [x] 2026-09-06 |
| W20 | planApprovalSeam | DomainExpert.planApprovalOut | Recorder.planApprovalIn | PlanApprovalWrite | [x] 2026-09-06 |
| W21 | planSeam | EvaluationOperator.planOut | Recorder.planIn | PlanWrite | [x] 2026-09-06 |
| W22 | probeRecordSeam | ProbeDeriver.probesOut | Recorder.probeIn | ProbeWrite | [ ] |
| W23 | probeRunSeam | EvaluationOperator.probesToItem | TestItem.probesIn | ProbeWrite | [x] 2026-09-06 |
| W24 | proposalSeam | AccountExecutive.proposalOut | Recorder.proposalIn | ProposalWrite | [x] 2026-09-06 |
| W25 | proposalToSponsorSeam | AccountExecutive.proposalOut | SponsorOrganization.proposalIn | ProposalWrite | [x] 2026-09-06 |
| W26 | recommendationSeam | EvaluationOperator.recommendationOut | Recorder.recommendationIn | RecommendationWrite | [x] 2026-09-06 |
| W27 | recordToCalculatorSeam | Recorder.recordOut | CoverageCalculator.recordIn | RecordWrite | [x] 2026-09-06 |
| W28 | recordToCheckerSeam | Recorder.recordOut | ConformanceChecker.recordIn | RecordWrite | [x] 2026-09-06 |
| W29 | recordToDeriverSeam | Recorder.recordOut | ProbeDeriver.recordIn | RecordWrite | [ ] |
| W30 | recordToExecutiveSeam | Recorder.recordOut | AccountExecutive.recordIn | RecordWrite | [x] 2026-09-06 |
| W31 | recordToExpertSeam | Recorder.recordOut | DomainExpert.recordIn | RecordWrite | [x] 2026-09-06 |
| W32 | recordToOperatorSeam | Recorder.recordOut | EvaluationOperator.recordIn | RecordWrite | [x] 2026-09-06 |
| W33 | reportSeam | CoverageCalculator.reportOut | Recorder.reportIn | ReportWrite | [x] 2026-09-06 |
| W34 | requirementSeam | EvaluationOperator.requirementsOut | Recorder.requirementsIn | RequirementSetWrite | [x] 2026-09-06 |
| W35 | responseSeam | TestItem.responseOut | Recorder.responseIn | ResponseWrite | [ ] |
| W36 | stakeholderInputSeam | AffectedPopulation.inputOut | Recorder.inputIn | StakeholderInputWrite | [ ] |
| W37 | statementOfWorkSeam | SponsorOrganization.statementOfWorkOut | Recorder.statementOfWorkIn | StatementOfWorkWrite | [x] 2026-09-06 |
| W38 | statementOfWorkToExecutiveSeam | SponsorOrganization.statementOfWorkOut | AccountExecutive.statementOfWorkIn | StatementOfWorkWrite | [x] 2026-09-06 |

## Relations

Connections that carry no item: a relation between two parties, drawn dotted in the views (R-38).

| # | Relation | Kind | Between | Validated |
|---|---|---|---|---|
| X1 | obligation | Obligation | sponsor : SponsorOrganization towards affected : AffectedPopulation | [x] 2026-09-06 |
