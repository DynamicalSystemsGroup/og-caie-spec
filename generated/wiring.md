## The assemblage

Organizations are boxes containing their parts; people are rounded (green), machines are double-boxed (red), affected populations are dashed (amber); every edge is one seam, named as in the model, from supplier port to conjugate consumer port.

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
  sponsor -- "acceptanceSeam" --> testingOrg_recorder
  sponsor -- "acceptanceToExecutiveSeam" --> testingOrg_accountExecutive
  accountable -- "accessSeam" --> testingOrg_recorder
  sponsor -- "agreementSeam" --> testingOrg_accountExecutive
  testingOrg_team_domainExpert -- "assessmentSeam" --> testingOrg_recorder
  testingOrg_team_domainExpert -- "attestationSeam" --> testingOrg_recorder
  testingOrg_accountExecutive -- "countersignSeam" --> testingOrg_recorder
  testingOrg_accountExecutive -- "deliveryRecordSeam" --> testingOrg_recorder
  testingOrg_accountExecutive -- "deliverySeam" --> sponsor
  testingOrg_probeDeriver -- "derivedProbeSeam" --> testingOrg_team_operator
  testingOrg_team_domainExpert -- "dsoSeam" --> testingOrg_recorder
  testingOrg_team_operator -- "evidenceSeam" --> testingOrg_recorder
  testingOrg_team_domainExpert -- "expertDeterminationSeam" --> testingOrg_recorder
  sponsor -- "needSeam" --> testingOrg_recorder
  sponsor -- "needToExecutiveSeam" --> testingOrg_accountExecutive
  testingOrg_team_operator -- "operatorDeterminationSeam" --> testingOrg_recorder
  testingOrg_team_domainExpert -- "planApprovalSeam" --> testingOrg_recorder
  testingOrg_team_operator -- "planSeam" --> testingOrg_recorder
  testingOrg_probeDeriver -- "probeRecordSeam" --> testingOrg_recorder
  testingOrg_team_operator -- "probeRunSeam" --> accountable_testItem
  testingOrg_accountExecutive -- "proposalSeam" --> testingOrg_recorder
  testingOrg_accountExecutive -- "proposalToSponsorSeam" --> sponsor
  testingOrg_team_operator -- "recommendationSeam" --> testingOrg_recorder
  testingOrg_recorder -- "recordToCalculatorSeam" --> testingOrg_coverageCalculator
  testingOrg_recorder -- "recordToCheckerSeam" --> testingOrg_conformanceChecker
  testingOrg_recorder -- "recordToDeriverSeam" --> testingOrg_probeDeriver
  testingOrg_recorder -- "recordToExecutiveSeam" --> testingOrg_accountExecutive
  testingOrg_recorder -- "recordToExpertSeam" --> testingOrg_team_domainExpert
  testingOrg_recorder -- "recordToOperatorSeam" --> testingOrg_team_operator
  testingOrg_coverageCalculator -- "reportSeam" --> testingOrg_recorder
  testingOrg_team_operator -- "requirementSeam" --> testingOrg_recorder
  accountable_testItem -- "responseSeam" --> testingOrg_recorder
  affected -- "stakeholderInputSeam" --> testingOrg_recorder
  classDef person fill:#e8f5e9,stroke:#2e7d32;
  classDef machine fill:#fce4ec,stroke:#ad1457;
  classDef party fill:#fff8e1,stroke:#f9a825,stroke-dasharray: 4 4;
  class testingOrg_accountExecutive,testingOrg_team_domainExpert,testingOrg_team_operator person;
  class accountable_testItem,testingOrg_conformanceChecker,testingOrg_coverageCalculator,testingOrg_probeDeriver,testingOrg_recorder machine;
  class affected party;
```
