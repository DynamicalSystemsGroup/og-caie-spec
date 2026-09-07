## The assemblage

Organizations are boxes containing their parts; people are rounded (green), machines are double-boxed (red), affected populations are dashed (amber); each solid edge bundles the seams from one part to another, labelled by the item kinds that flow; the dotted edge is a relation that carries no item.

```{mermaid}
flowchart LR
  subgraph accountable["accountable : test item provider"]
    accountable_testItem[["testItem : test item"]]
  end
  affected{{"affected : affected population"}}
  subgraph sponsor["sponsor : sponsor"]
    sponsor_signatory(["signatory : sponsor signatory"])
  end
  subgraph testingOrg["testingOrg : testing organization"]
    testingOrg_accountExecutive(["accountExecutive : authorized representative"])
    testingOrg_conformanceChecker[["conformanceChecker : conformance checker"]]
    testingOrg_recorder[["recorder : recorder"]]
    testingOrg_reportAssembler[["reportAssembler : report assembler"]]
    subgraph testingOrg_team["team : evaluation team"]
      testingOrg_team_domainExpert(["domainExpert : domain expert"])
      testingOrg_team_operator(["operator : evaluation operator"])
      testingOrg_team_representative(["representative : population representative"])
    end
    testingOrg_testDriver[["testDriver : test driver"]]
  end
  accountable -- "TestItemAccess" --> testingOrg_recorder
  accountable -- "TestItemAccess" --> testingOrg_team_operator
  accountable_testItem -- "Response" --> testingOrg_recorder
  affected -- "StakeholderInput" --> testingOrg_recorder
  affected -- "StakeholderInput" --> testingOrg_team_representative
  sponsor -- "Mission, Need, StatementOfWork" --> testingOrg_accountExecutive
  sponsor -- "Mission, Need, StatementOfWork" --> testingOrg_recorder
  sponsor_signatory -- "ServiceAgreement, Acceptance" --> testingOrg_accountExecutive
  sponsor_signatory -- "UserInterestDeclaration, RequirementSetApproval, Acceptance" --> testingOrg_recorder
  testingOrg_accountExecutive -- "Proposal, Delivery" --> sponsor
  testingOrg_accountExecutive -- "Proposal, ServiceAgreement, IndependenceDeclaration, Delivery" --> testingOrg_recorder
  testingOrg_conformanceChecker -- "ConformanceVerdict" --> testingOrg_recorder
  testingOrg_conformanceChecker -- "ConformanceVerdict" --> testingOrg_reportAssembler
  testingOrg_recorder -- "EvaluationRecord" --> testingOrg_conformanceChecker
  testingOrg_recorder -- "EvaluationRecord" --> testingOrg_reportAssembler
  testingOrg_recorder -- "EvaluationRecord" --> testingOrg_testDriver
  testingOrg_reportAssembler -- "Report" --> testingOrg_recorder
  testingOrg_team_domainExpert -- "DsoRelease, AppropriatenessAssessment, PlanApproval, Attestation, Determination, ReportApproval" --> testingOrg_recorder
  testingOrg_team_operator -- "Probe" --> accountable_testItem
  testingOrg_team_operator -- "RequirementSet, PlanDeviation, TestPlan, Evidence, Determination, Recommendation" --> testingOrg_recorder
  testingOrg_team_representative -- "StakeholderRepresentation" --> testingOrg_recorder
  testingOrg_testDriver -- "Probe" --> testingOrg_recorder
  testingOrg_testDriver -- "Probe" --> testingOrg_team_operator
  sponsor -. "obligation" .-> affected
  classDef person fill:#1b5e20,stroke:#a5d6a7,stroke-width:2px,color:#ffffff;
  classDef machine fill:#880e4f,stroke:#f48fb1,stroke-width:2px,color:#ffffff;
  classDef party fill:#f9a825,stroke:#e65100,stroke-width:2px,stroke-dasharray: 6 3,color:#000000;
  classDef organization fill:#37474f,stroke:#cfd8dc,stroke-width:2px,color:#ffffff;
  linkStyle default stroke:#90a4ae,stroke-width:1.5px;
  class sponsor_signatory,testingOrg_accountExecutive,testingOrg_team_domainExpert,testingOrg_team_operator,testingOrg_team_representative person;
  class accountable_testItem,testingOrg_conformanceChecker,testingOrg_recorder,testingOrg_reportAssembler,testingOrg_testDriver machine;
  class affected party;
```

**View `assemblage`: the assemblage.** In focus: every party and every part of the testing organization, nested in the organization that holds it, with one bundled edge per pair of parts labelled by the item kinds that flow between them, and the sponsor's obligation to the affected populations dotted. Left out: the seam names and the ports (the wiring table has them, one row per port), and the order in which the items flow. Legend: rounded green, a person; double-boxed pink, a machine; dashed amber, an affected population; a plain box, an organization; a solid arrow bundles the items that flow from one part to another; a dotted arrow is a relation that carries no item.
