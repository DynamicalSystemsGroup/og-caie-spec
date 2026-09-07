# Rulings sheet 05: the blocks and the wires (concern C-30)

Generated from `model/og-caie.model.ttl` by `scripts/render.py`; do not edit the rows by hand, tick them. One row per kind of part (its inputs and outputs) and one per wire (output port on a part to input port on a part). Ticks come from rulings/validated.ttl (Z's walkthrough, R-48 sheet 07-09), so regeneration keeps them; add a concern for anything wrong.

## Blocks

| # | Part kind | Inputs | Outputs | Validated |
|---|---|---|---|---|
| B1 | AccountExecutive | acceptanceIn, agreementIn, missionIn, needIn, recordIn, statementOfWorkIn | agreementOut, deliveryOut, proposalOut | [ ] |
| B2 | AccountableOrganization | (none) | accessOut | [ ] |
| B3 | AffectedPopulation | (none) | inputOut | [ ] |
| B4 | ConformanceChecker | recordIn | (none) | [ ] |
| B5 | CoverageCalculator | recordIn | reportOut | [ ] |
| B6 | DomainExpert | recordIn | assessmentOut, attestationOut, determinationOut, dsoOut, planApprovalOut | [ ] |
| B7 | EvaluationOperator | probesIn, recordIn | determinationOut, evidenceOut, planOut, probesToItem, recommendationOut, requirementsOut | [ ] |
| B8 | ProbeDeriver | recordIn | probesOut | [ ] |
| B9 | Recorder | acceptanceIn, accessIn, agreementIn, assessmentIn, attestationIn, deliveryIn, dsoIn, evidenceIn, expertDeterminationIn, inputIn, missionIn, needIn, operatorDeterminationIn, planApprovalIn, planIn, probeIn, proposalIn, recommendationIn, reportIn, requirementsIn, responseIn, statementOfWorkIn | recordOut | [ ] |
| B10 | SponsorOrganization | deliveryIn, proposalIn | acceptanceOut, agreementOut, missionOut, needOut, statementOfWorkOut | [x] 2026-09-06 |
| B11 | TestItem | probesIn | responseOut | [ ] |

## Wires

| # | Wire | From | To | Carries | Validated |
|---|---|---|---|---|---|
| W1 | acceptanceSeam | SponsorOrganization.acceptanceOut | Recorder.acceptanceIn | AcceptanceWrite | [x] 2026-09-06 |
| W2 | acceptanceToExecutiveSeam | SponsorOrganization.acceptanceOut | AccountExecutive.acceptanceIn | AcceptanceWrite | [x] 2026-09-06 |
| W3 | accessSeam | AccountableOrganization.accessOut | Recorder.accessIn | AccessWrite | [ ] |
| W4 | agreementSeam | SponsorOrganization.agreementOut | AccountExecutive.agreementIn | AgreementWrite | [x] 2026-09-06 |
| W5 | assessmentSeam | DomainExpert.assessmentOut | Recorder.assessmentIn | AssessmentWrite | [ ] |
| W6 | attestationSeam | DomainExpert.attestationOut | Recorder.attestationIn | AttestationWrite | [ ] |
| W7 | countersignSeam | AccountExecutive.agreementOut | Recorder.agreementIn | AgreementWrite | [ ] |
| W8 | deliveryRecordSeam | AccountExecutive.deliveryOut | Recorder.deliveryIn | DeliveryWrite | [ ] |
| W9 | deliverySeam | AccountExecutive.deliveryOut | SponsorOrganization.deliveryIn | DeliveryWrite | [x] 2026-09-06 |
| W10 | derivedProbeSeam | ProbeDeriver.probesOut | EvaluationOperator.probesIn | ProbeWrite | [ ] |
| W11 | dsoSeam | DomainExpert.dsoOut | Recorder.dsoIn | DsoWrite | [ ] |
| W12 | evidenceSeam | EvaluationOperator.evidenceOut | Recorder.evidenceIn | EvidenceWrite | [ ] |
| W13 | expertDeterminationSeam | DomainExpert.determinationOut | Recorder.expertDeterminationIn | DeterminationWrite | [ ] |
| W14 | missionSeam | SponsorOrganization.missionOut | Recorder.missionIn | MissionWrite | [x] 2026-09-06 |
| W15 | missionToExecutiveSeam | SponsorOrganization.missionOut | AccountExecutive.missionIn | MissionWrite | [x] 2026-09-06 |
| W16 | needSeam | SponsorOrganization.needOut | Recorder.needIn | NeedWrite | [x] 2026-09-06 |
| W17 | needToExecutiveSeam | SponsorOrganization.needOut | AccountExecutive.needIn | NeedWrite | [x] 2026-09-06 |
| W18 | operatorDeterminationSeam | EvaluationOperator.determinationOut | Recorder.operatorDeterminationIn | DeterminationWrite | [ ] |
| W19 | planApprovalSeam | DomainExpert.planApprovalOut | Recorder.planApprovalIn | PlanApprovalWrite | [ ] |
| W20 | planSeam | EvaluationOperator.planOut | Recorder.planIn | PlanWrite | [ ] |
| W21 | probeRecordSeam | ProbeDeriver.probesOut | Recorder.probeIn | ProbeWrite | [ ] |
| W22 | probeRunSeam | EvaluationOperator.probesToItem | TestItem.probesIn | ProbeWrite | [ ] |
| W23 | proposalSeam | AccountExecutive.proposalOut | Recorder.proposalIn | ProposalWrite | [ ] |
| W24 | proposalToSponsorSeam | AccountExecutive.proposalOut | SponsorOrganization.proposalIn | ProposalWrite | [x] 2026-09-06 |
| W25 | recommendationSeam | EvaluationOperator.recommendationOut | Recorder.recommendationIn | RecommendationWrite | [ ] |
| W26 | recordToCalculatorSeam | Recorder.recordOut | CoverageCalculator.recordIn | RecordWrite | [ ] |
| W27 | recordToCheckerSeam | Recorder.recordOut | ConformanceChecker.recordIn | RecordWrite | [ ] |
| W28 | recordToDeriverSeam | Recorder.recordOut | ProbeDeriver.recordIn | RecordWrite | [ ] |
| W29 | recordToExecutiveSeam | Recorder.recordOut | AccountExecutive.recordIn | RecordWrite | [ ] |
| W30 | recordToExpertSeam | Recorder.recordOut | DomainExpert.recordIn | RecordWrite | [ ] |
| W31 | recordToOperatorSeam | Recorder.recordOut | EvaluationOperator.recordIn | RecordWrite | [ ] |
| W32 | reportSeam | CoverageCalculator.reportOut | Recorder.reportIn | ReportWrite | [ ] |
| W33 | requirementSeam | EvaluationOperator.requirementsOut | Recorder.requirementsIn | RequirementSetWrite | [ ] |
| W34 | responseSeam | TestItem.responseOut | Recorder.responseIn | ResponseWrite | [ ] |
| W35 | stakeholderInputSeam | AffectedPopulation.inputOut | Recorder.inputIn | StakeholderInputWrite | [ ] |
| W36 | statementOfWorkSeam | SponsorOrganization.statementOfWorkOut | Recorder.statementOfWorkIn | StatementOfWorkWrite | [x] 2026-09-06 |
| W37 | statementOfWorkToExecutiveSeam | SponsorOrganization.statementOfWorkOut | AccountExecutive.statementOfWorkIn | StatementOfWorkWrite | [x] 2026-09-06 |

## Relations

Connections that carry no item: a relation between two parties, drawn dotted in the views (R-38).

| # | Relation | Kind | Between | Validated |
|---|---|---|---|---|
| X1 | obligation | Obligation | sponsor : SponsorOrganization towards affected : AffectedPopulation | [ ] |
