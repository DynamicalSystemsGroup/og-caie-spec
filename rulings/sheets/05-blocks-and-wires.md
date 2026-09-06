# Rulings sheet 05: the blocks and the wires (concern C-30)

Generated from `model/og-caie.model.ttl` by `scripts/render.py`; do not edit the rows by hand, tick them. One row per kind of part (its inputs and outputs) and one per wire (output port on a part to input port on a part). Z: tick a row when the block or the wire is validated; add a concern for anything wrong.

## Blocks

| # | Part kind | Inputs | Outputs | Validated |
|---|---|---|---|---|
| B1 | AccountExecutive | acceptanceIn, agreementIn, needIn, recordIn | agreementOut, deliveryOut, proposalOut | [ ] |
| B2 | AccountableOrganization | (none) | accessOut | [ ] |
| B3 | AffectedPopulation | (none) | inputOut | [ ] |
| B4 | ConformanceChecker | recordIn | (none) | [ ] |
| B5 | CoverageCalculator | recordIn | reportOut | [ ] |
| B6 | DomainExpert | recordIn | assessmentOut, attestationOut, determinationOut, dsoOut, planApprovalOut | [ ] |
| B7 | EvaluationOperator | probesIn, recordIn | determinationOut, evidenceOut, planOut, probesToItem, recommendationOut, requirementsOut | [ ] |
| B8 | ProbeDeriver | recordIn | probesOut | [ ] |
| B9 | Recorder | acceptanceIn, accessIn, agreementIn, assessmentIn, attestationIn, deliveryIn, dsoIn, evidenceIn, expertDeterminationIn, inputIn, needIn, operatorDeterminationIn, planApprovalIn, planIn, probeIn, proposalIn, recommendationIn, reportIn, requirementsIn, responseIn | recordOut | [ ] |
| B10 | SponsorOrganization | deliveryIn, proposalIn | acceptanceOut, agreementOut, needOut | [ ] |
| B11 | TestItem | probesIn | responseOut | [ ] |

## Wires

| # | Wire | From | To | Carries | Validated |
|---|---|---|---|---|---|
| W1 | acceptanceSeam | SponsorOrganization.acceptanceOut | Recorder.acceptanceIn | AcceptanceWrite | [ ] |
| W2 | acceptanceToExecutiveSeam | SponsorOrganization.acceptanceOut | AccountExecutive.acceptanceIn | AcceptanceWrite | [ ] |
| W3 | accessSeam | AccountableOrganization.accessOut | Recorder.accessIn | AccessWrite | [ ] |
| W4 | agreementSeam | SponsorOrganization.agreementOut | AccountExecutive.agreementIn | AgreementWrite | [ ] |
| W5 | assessmentSeam | DomainExpert.assessmentOut | Recorder.assessmentIn | AssessmentWrite | [ ] |
| W6 | attestationSeam | DomainExpert.attestationOut | Recorder.attestationIn | AttestationWrite | [ ] |
| W7 | countersignSeam | AccountExecutive.agreementOut | Recorder.agreementIn | AgreementWrite | [ ] |
| W8 | deliveryRecordSeam | AccountExecutive.deliveryOut | Recorder.deliveryIn | DeliveryWrite | [ ] |
| W9 | deliverySeam | AccountExecutive.deliveryOut | SponsorOrganization.deliveryIn | DeliveryWrite | [ ] |
| W10 | derivedProbeSeam | ProbeDeriver.probesOut | EvaluationOperator.probesIn | ProbeWrite | [ ] |
| W11 | dsoSeam | DomainExpert.dsoOut | Recorder.dsoIn | DsoWrite | [ ] |
| W12 | evidenceSeam | EvaluationOperator.evidenceOut | Recorder.evidenceIn | EvidenceWrite | [ ] |
| W13 | expertDeterminationSeam | DomainExpert.determinationOut | Recorder.expertDeterminationIn | DeterminationWrite | [ ] |
| W14 | needSeam | SponsorOrganization.needOut | Recorder.needIn | NeedWrite | [ ] |
| W15 | needToExecutiveSeam | SponsorOrganization.needOut | AccountExecutive.needIn | NeedWrite | [ ] |
| W16 | operatorDeterminationSeam | EvaluationOperator.determinationOut | Recorder.operatorDeterminationIn | DeterminationWrite | [ ] |
| W17 | planApprovalSeam | DomainExpert.planApprovalOut | Recorder.planApprovalIn | PlanApprovalWrite | [ ] |
| W18 | planSeam | EvaluationOperator.planOut | Recorder.planIn | PlanWrite | [ ] |
| W19 | probeRecordSeam | ProbeDeriver.probesOut | Recorder.probeIn | ProbeWrite | [ ] |
| W20 | probeRunSeam | EvaluationOperator.probesToItem | TestItem.probesIn | ProbeWrite | [ ] |
| W21 | proposalSeam | AccountExecutive.proposalOut | Recorder.proposalIn | ProposalWrite | [ ] |
| W22 | proposalToSponsorSeam | AccountExecutive.proposalOut | SponsorOrganization.proposalIn | ProposalWrite | [ ] |
| W23 | recommendationSeam | EvaluationOperator.recommendationOut | Recorder.recommendationIn | RecommendationWrite | [ ] |
| W24 | recordToCalculatorSeam | Recorder.recordOut | CoverageCalculator.recordIn | RecordWrite | [ ] |
| W25 | recordToCheckerSeam | Recorder.recordOut | ConformanceChecker.recordIn | RecordWrite | [ ] |
| W26 | recordToDeriverSeam | Recorder.recordOut | ProbeDeriver.recordIn | RecordWrite | [ ] |
| W27 | recordToExecutiveSeam | Recorder.recordOut | AccountExecutive.recordIn | RecordWrite | [ ] |
| W28 | recordToExpertSeam | Recorder.recordOut | DomainExpert.recordIn | RecordWrite | [ ] |
| W29 | recordToOperatorSeam | Recorder.recordOut | EvaluationOperator.recordIn | RecordWrite | [ ] |
| W30 | reportSeam | CoverageCalculator.reportOut | Recorder.reportIn | ReportWrite | [ ] |
| W31 | requirementSeam | EvaluationOperator.requirementsOut | Recorder.requirementsIn | RequirementSetWrite | [ ] |
| W32 | responseSeam | TestItem.responseOut | Recorder.responseIn | ResponseWrite | [ ] |
| W33 | stakeholderInputSeam | AffectedPopulation.inputOut | Recorder.inputIn | StakeholderInputWrite | [ ] |
