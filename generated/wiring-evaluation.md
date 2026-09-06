```{mermaid}
flowchart LR
  accountable_testItem[["testItem : TestItem"]]
  testingOrg_accountExecutive(["accountExecutive : AccountExecutive"])
  testingOrg_conformanceChecker[["conformanceChecker : ConformanceChecker"]]
  testingOrg_coverageCalculator[["coverageCalculator : CoverageCalculator"]]
  testingOrg_probeDeriver[["probeDeriver : ProbeDeriver"]]
  testingOrg_recorder[["recorder : Recorder"]]
  testingOrg_team_domainExpert(["domainExpert : DomainExpert"])
  testingOrg_team_operator(["operator : EvaluationOperator"])
  testingOrg_team_domainExpert -- "assessmentSeam" --> testingOrg_recorder
  testingOrg_team_domainExpert -- "attestationSeam" --> testingOrg_recorder
  testingOrg_probeDeriver -- "derivedProbeSeam" --> testingOrg_team_operator
  testingOrg_team_domainExpert -- "dsoSeam" --> testingOrg_recorder
  testingOrg_team_operator -- "evidenceSeam" --> testingOrg_recorder
  testingOrg_team_domainExpert -- "expertDeterminationSeam" --> testingOrg_recorder
  testingOrg_team_operator -- "operatorDeterminationSeam" --> testingOrg_recorder
  testingOrg_team_domainExpert -- "planApprovalSeam" --> testingOrg_recorder
  testingOrg_team_operator -- "planSeam" --> testingOrg_recorder
  testingOrg_probeDeriver -- "probeRecordSeam" --> testingOrg_recorder
  testingOrg_team_operator -- "probeRunSeam" --> accountable_testItem
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
  classDef person fill:#e8f5e9,stroke:#2e7d32;
  classDef machine fill:#fce4ec,stroke:#ad1457;
  classDef party fill:#fff8e1,stroke:#f9a825,stroke-dasharray: 4 4;
  class testingOrg_accountExecutive,testingOrg_team_domainExpert,testingOrg_team_operator person;
  class accountable_testItem,testingOrg_conformanceChecker,testingOrg_coverageCalculator,testingOrg_probeDeriver,testingOrg_recorder machine;
```
