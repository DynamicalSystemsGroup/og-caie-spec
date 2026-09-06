## The assemblage

Organizations are boxes containing their parts; people are rounded (green), machines are double-boxed (red), affected populations are dashed (amber); each solid edge bundles the seams from one part to another, labelled by the item kinds that flow; the dotted edge is a relation that carries no item.

**View `assemblage`: the assemblage.** In focus: every party and every part of the testing organization, nested in the organization that holds it, with one bundled edge per pair of parts labelled by the item kinds that flow between them, and the sponsor's obligation to the affected populations dotted. Left out: the seam names and the ports (the wiring table has them, one row per port), and the order in which the items flow.

```{mermaid}
flowchart LR
  subgraph accountable["accountable : AccountableOrganization"]
    accountable_testItem[["testItem : TestItem"]]
  end
  affected{{"affected : AffectedPopulation"}}
  sponsor["sponsor : SponsorOrganization"]
  subgraph testingOrg["testingOrg : TestingOrganization"]
    testingOrg_accountExecutive(["accountExecutive : AccountExecutive"])
    testingOrg_conformanceChecker[["conformanceChecker : ConformanceChecker"]]
    testingOrg_coverageCalculator[["coverageCalculator : CoverageCalculator"]]
    testingOrg_probeDeriver[["probeDeriver : ProbeDeriver"]]
    testingOrg_recorder[["recorder : Recorder"]]
    subgraph testingOrg_team["team : EvaluationTeam"]
      testingOrg_team_domainExpert(["domainExpert : DomainExpert"])
      testingOrg_team_operator(["operator : EvaluationOperator"])
    end
  end
  accountable -- "TestItemAccess" --> testingOrg_recorder
  accountable_testItem -- "Response" --> testingOrg_recorder
  affected -- "StakeholderInput" --> testingOrg_recorder
  sponsor -- "Mission, Need, ServiceAgreement, StatementOfWork, Acceptance" --> testingOrg_accountExecutive
  sponsor -- "Mission, Need, StatementOfWork, Acceptance" --> testingOrg_recorder
  testingOrg_accountExecutive -- "Proposal, Delivery" --> sponsor
  testingOrg_accountExecutive -- "Proposal, ServiceAgreement, Delivery" --> testingOrg_recorder
  testingOrg_coverageCalculator -- "Report" --> testingOrg_recorder
  testingOrg_probeDeriver -- "Probe" --> testingOrg_recorder
  testingOrg_probeDeriver -- "Probe" --> testingOrg_team_operator
  testingOrg_recorder -- "EvaluationRecord" --> testingOrg_accountExecutive
  testingOrg_recorder -- "EvaluationRecord" --> testingOrg_conformanceChecker
  testingOrg_recorder -- "EvaluationRecord" --> testingOrg_coverageCalculator
  testingOrg_recorder -- "EvaluationRecord" --> testingOrg_probeDeriver
  testingOrg_recorder -- "EvaluationRecord" --> testingOrg_team_domainExpert
  testingOrg_recorder -- "EvaluationRecord" --> testingOrg_team_operator
  testingOrg_team_domainExpert -- "DsoRelease, AppropriatenessAssessment, PlanApproval, Attestation, Determination" --> testingOrg_recorder
  testingOrg_team_operator -- "Probe" --> accountable_testItem
  testingOrg_team_operator -- "RequirementSet, TestPlan, Evidence, Determination, Recommendation" --> testingOrg_recorder
  sponsor -. "obligation" .-> affected
  classDef person fill:#e8f5e9,stroke:#2e7d32;
  classDef machine fill:#fce4ec,stroke:#ad1457;
  classDef party fill:#fff8e1,stroke:#f9a825,stroke-dasharray: 4 4;
  class testingOrg_accountExecutive,testingOrg_team_domainExpert,testingOrg_team_operator person;
  class accountable_testItem,testingOrg_conformanceChecker,testingOrg_coverageCalculator,testingOrg_probeDeriver,testingOrg_recorder machine;
  class affected party;
```
