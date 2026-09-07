# Rulings sheet 05: the blocks and the wires (concern C-30)

Generated from `model/og-caie.model.ttl` by `scripts/render.py`; do not edit the rows by hand, tick them. One row per kind of part (its inputs and outputs) and one per wire (output port on a part to input port on a part). Ticks come from rulings/validated.ttl (Z's walkthrough, R-48 sheet 07-09), so regeneration keeps them; add a concern for anything wrong.

## Blocks

| # | Part kind | Inputs | Outputs | Validated |
|---|---|---|---|---|
| B1 | AccountExecutive | acceptanceIn, agreementIn, missionIn, needIn, statementOfWorkIn | agreementOut, deliveryOut, independenceDeclarationOut, proposalOut | [x] 2026-09-06 |
| B2 | AccountableOrganization | (none) | accessOut | [x] 2026-09-06 |
| B3 | AffectedPopulation | (none) | inputOut | [x] 2026-09-07 |
| B4 | ConformanceChecker | recordIn | verdictOut | [x] 2026-09-06 |
| B5 | DomainExpert | (none) | assessmentOut, attestationOut, determinationOut, dsoOut, planApprovalOut, reportApprovalOut | [x] 2026-09-06 |
| B6 | EvaluationOperator | accessIn, probesIn | determinationOut, evidenceOut, planDeviationOut, planOut, probesToItem, recommendationOut, requirementsOut | [x] 2026-09-06 |
| B7 | Recorder | acceptanceIn, accessIn, agreementIn, assessmentIn, attestationIn, deliveryIn, dsoIn, evidenceIn, expertDeterminationIn, independenceDeclarationIn, inputIn, missionIn, needIn, operatorDeterminationIn, planApprovalIn, planDeviationIn, planIn, probeIn, proposalIn, recommendationIn, reportApprovalIn, reportIn, representationIn, requirementSetApprovalIn, requirementsIn, responseIn, statementOfWorkIn, userInterestDeclarationIn, verdictIn | recordOut | [x] 2026-09-06 |
| B8 | ReportAssembler | recordIn, verdictIn | reportOut | [ ] |
| B9 | Representative | inputIn | representationOut | [x] 2026-09-07 |
| B10 | SponsorOrganization | deliveryIn, proposalIn | missionOut, needOut, statementOfWorkOut | [x] 2026-09-06 |
| B11 | SponsorSignatory | (none) | acceptanceOut, agreementOut, requirementSetApprovalOut, userInterestDeclarationOut | [x] 2026-09-07 |
| B12 | TestDriver | recordIn | probesOut | [x] 2026-09-07 |
| B13 | TestItem | probesIn | responseOut | [x] 2026-09-07 |

## Wires

| # | Wire | From | To | Carries | Validated |
|---|---|---|---|---|---|
| W1 | acceptanceSeam | SponsorSignatory.acceptanceOut | Recorder.acceptanceIn | AcceptanceWrite | [x] 2026-09-06 |
| W2 | acceptanceToExecutiveSeam | SponsorSignatory.acceptanceOut | AccountExecutive.acceptanceIn | AcceptanceWrite | [x] 2026-09-06 |
| W3 | accessSeam | AccountableOrganization.accessOut | Recorder.accessIn | AccessWrite | [x] 2026-09-06 |
| W4 | accessToOperatorSeam | AccountableOrganization.accessOut | EvaluationOperator.accessIn | AccessWrite | [x] 2026-09-06 |
| W5 | agreementSeam | SponsorSignatory.agreementOut | AccountExecutive.agreementIn | AgreementWrite | [x] 2026-09-06 |
| W6 | assessmentSeam | DomainExpert.assessmentOut | Recorder.assessmentIn | AssessmentWrite | [x] 2026-09-06 |
| W7 | attestationSeam | DomainExpert.attestationOut | Recorder.attestationIn | AttestationWrite | [x] 2026-09-06 |
| W8 | countersignSeam | AccountExecutive.agreementOut | Recorder.agreementIn | AgreementWrite | [x] 2026-09-06 |
| W9 | deliveryRecordSeam | AccountExecutive.deliveryOut | Recorder.deliveryIn | DeliveryWrite | [x] 2026-09-06 |
| W10 | deliverySeam | AccountExecutive.deliveryOut | SponsorOrganization.deliveryIn | DeliveryWrite | [x] 2026-09-06 |
| W11 | derivedProbeSeam | TestDriver.probesOut | EvaluationOperator.probesIn | ProbeWrite | [x] 2026-09-06 |
| W12 | dsoSeam | DomainExpert.dsoOut | Recorder.dsoIn | DsoWrite | [x] 2026-09-06 |
| W13 | evidenceSeam | EvaluationOperator.evidenceOut | Recorder.evidenceIn | EvidenceWrite | [x] 2026-09-06 |
| W14 | expertDeterminationSeam | DomainExpert.determinationOut | Recorder.expertDeterminationIn | DeterminationWrite | [x] 2026-09-06 |
| W15 | independenceDeclarationSeam | AccountExecutive.independenceDeclarationOut | Recorder.independenceDeclarationIn | IndependenceDeclarationWrite | [ ] |
| W16 | missionSeam | SponsorOrganization.missionOut | Recorder.missionIn | MissionWrite | [x] 2026-09-06 |
| W17 | missionToExecutiveSeam | SponsorOrganization.missionOut | AccountExecutive.missionIn | MissionWrite | [x] 2026-09-06 |
| W18 | needSeam | SponsorOrganization.needOut | Recorder.needIn | NeedWrite | [x] 2026-09-06 |
| W19 | needToExecutiveSeam | SponsorOrganization.needOut | AccountExecutive.needIn | NeedWrite | [x] 2026-09-06 |
| W20 | operatorDeterminationSeam | EvaluationOperator.determinationOut | Recorder.operatorDeterminationIn | DeterminationWrite | [x] 2026-09-06 |
| W21 | planApprovalSeam | DomainExpert.planApprovalOut | Recorder.planApprovalIn | PlanApprovalWrite | [x] 2026-09-06 |
| W22 | planDeviationSeam | EvaluationOperator.planDeviationOut | Recorder.planDeviationIn | PlanDeviationWrite | [ ] |
| W23 | planSeam | EvaluationOperator.planOut | Recorder.planIn | PlanWrite | [x] 2026-09-06 |
| W24 | probeRecordSeam | TestDriver.probesOut | Recorder.probeIn | ProbeWrite | [x] 2026-09-07 |
| W25 | probeRunSeam | EvaluationOperator.probesToItem | TestItem.probesIn | ProbeWrite | [x] 2026-09-06 |
| W26 | proposalSeam | AccountExecutive.proposalOut | Recorder.proposalIn | ProposalWrite | [x] 2026-09-06 |
| W27 | proposalToSponsorSeam | AccountExecutive.proposalOut | SponsorOrganization.proposalIn | ProposalWrite | [x] 2026-09-06 |
| W28 | recommendationSeam | EvaluationOperator.recommendationOut | Recorder.recommendationIn | RecommendationWrite | [x] 2026-09-06 |
| W29 | recordToAssemblerSeam | Recorder.recordOut | ReportAssembler.recordIn | RecordWrite | [x] 2026-09-06 |
| W30 | recordToCheckerSeam | Recorder.recordOut | ConformanceChecker.recordIn | RecordWrite | [x] 2026-09-06 |
| W31 | recordToDriverSeam | Recorder.recordOut | TestDriver.recordIn | RecordWrite | [x] 2026-09-06 |
| W32 | reportApprovalSeam | DomainExpert.reportApprovalOut | Recorder.reportApprovalIn | ReportApprovalWrite | [x] 2026-09-07 |
| W33 | reportSeam | ReportAssembler.reportOut | Recorder.reportIn | ReportWrite | [x] 2026-09-06 |
| W34 | representationSeam | Representative.representationOut | Recorder.representationIn | RepresentationWrite | [x] 2026-09-07 |
| W35 | requirementSeam | EvaluationOperator.requirementsOut | Recorder.requirementsIn | RequirementSetWrite | [x] 2026-09-06 |
| W36 | requirementSetApprovalSeam | SponsorSignatory.requirementSetApprovalOut | Recorder.requirementSetApprovalIn | RequirementSetApprovalWrite | [ ] |
| W37 | responseSeam | TestItem.responseOut | Recorder.responseIn | ResponseWrite | [x] 2026-09-07 |
| W38 | stakeholderInputSeam | AffectedPopulation.inputOut | Recorder.inputIn | StakeholderInputWrite | [x] 2026-09-07 |
| W39 | stakeholderInputToRepresentativeSeam | AffectedPopulation.inputOut | Representative.inputIn | StakeholderInputWrite | [x] 2026-09-07 |
| W40 | statementOfWorkSeam | SponsorOrganization.statementOfWorkOut | Recorder.statementOfWorkIn | StatementOfWorkWrite | [x] 2026-09-06 |
| W41 | statementOfWorkToExecutiveSeam | SponsorOrganization.statementOfWorkOut | AccountExecutive.statementOfWorkIn | StatementOfWorkWrite | [x] 2026-09-06 |
| W42 | userInterestDeclarationSeam | SponsorSignatory.userInterestDeclarationOut | Recorder.userInterestDeclarationIn | UserInterestDeclarationWrite | [x] 2026-09-07 |
| W43 | verdictSeam | ConformanceChecker.verdictOut | Recorder.verdictIn | ConformanceVerdictWrite | [x] 2026-09-07 |
| W44 | verdictToAssemblerSeam | ConformanceChecker.verdictOut | ReportAssembler.verdictIn | ConformanceVerdictWrite | [ ] |

## Relations

Connections that carry no item: a relation between two parties, drawn dotted in the views (R-38).

| # | Relation | Kind | Between | Validated |
|---|---|---|---|---|
| X1 | obligation | Obligation | sponsor : SponsorOrganization towards affected : AffectedPopulation | [x] 2026-09-06 |
