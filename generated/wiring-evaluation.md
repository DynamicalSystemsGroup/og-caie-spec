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
  accountable_testItem -- "Response" --> testingOrg_recorder
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
  classDef person fill:#1b5e20,stroke:#a5d6a7,stroke-width:2px,color:#ffffff;
  classDef machine fill:#880e4f,stroke:#f48fb1,stroke-width:2px,color:#ffffff;
  classDef party fill:#f9a825,stroke:#e65100,stroke-width:2px,stroke-dasharray: 6 3,color:#000000;
  classDef organization fill:#37474f,stroke:#cfd8dc,stroke-width:2px,color:#ffffff;
  linkStyle default stroke:#90a4ae,stroke-width:1.5px;
  class testingOrg_accountExecutive,testingOrg_team_domainExpert,testingOrg_team_operator person;
  class accountable_testItem,testingOrg_conformanceChecker,testingOrg_coverageCalculator,testingOrg_probeDeriver,testingOrg_recorder machine;
```

**View `evaluation`: the evaluation slice.** In focus: the team, the machines, the test item and the recorder, with the evaluation items braided into one bundle per pair of parts. Left out: the sponsor, the account executive's contracting wires and the accountable organization's access grant; the seam names and the ports. Legend: rounded green, a person; double-boxed pink, a machine; dashed amber, an affected population; a plain box, an organization; a solid arrow bundles the items that flow from one part to another; a dotted arrow is a relation that carries no item.
