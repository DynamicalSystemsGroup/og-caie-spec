```{mermaid}
flowchart LR
  accountable["accountable : test item provider"]
  affected{{"affected : affected population"}}
  sponsor["sponsor : sponsor"]
  sponsor_signatory(["signatory : sponsor signatory"])
  testingOrg_authorizedRepresentative(["authorizedRepresentative : authorized representative"])
  testingOrg_recorder[["recorder : recorder"]]
  testingOrg_team_operator(["operator : evaluation operator"])
  testingOrg_team_representative(["representative : population representative"])
  accountable -- "TestItemAccess" --> testingOrg_recorder
  accountable -- "TestItemAccess" --> testingOrg_team_operator
  affected -- "StakeholderInput" --> testingOrg_recorder
  affected -- "StakeholderInput" --> testingOrg_team_representative
  sponsor -- "Mission, Need, StatementOfWork" --> testingOrg_authorizedRepresentative
  sponsor -- "Mission, Need, StatementOfWork" --> testingOrg_recorder
  sponsor_signatory -- "ServiceAgreement, Acceptance" --> testingOrg_authorizedRepresentative
  sponsor_signatory -- "Acceptance" --> testingOrg_recorder
  testingOrg_authorizedRepresentative -- "Proposal, Delivery" --> sponsor
  testingOrg_authorizedRepresentative -- "Proposal, ServiceAgreement, Delivery" --> testingOrg_recorder
  sponsor -. "obligation" .-> affected
  classDef person fill:#1b5e20,stroke:#a5d6a7,stroke-width:2px,color:#ffffff;
  classDef machine fill:#880e4f,stroke:#f48fb1,stroke-width:2px,color:#ffffff;
  classDef party fill:#f9a825,stroke:#e65100,stroke-width:2px,stroke-dasharray: 6 3,color:#000000;
  classDef organization fill:#37474f,stroke:#cfd8dc,stroke-width:2px,color:#ffffff;
  linkStyle default stroke:#90a4ae,stroke-width:1.5px;
  class sponsor_signatory,testingOrg_authorizedRepresentative,testingOrg_team_operator,testingOrg_team_representative person;
  class testingOrg_recorder machine;
  class affected party;
  class accountable,sponsor organization;
```

**View `contracting`: the contracting slice.** In focus: the parties to the contract and the two parts of the testing organization they touch, the items pinned at the contract braided into one bundle per pair of parts, and the sponsor's obligation to the affected populations, a relation that carries no item. Left out: the evaluation team, the machines and the test item; the evaluation items; the seam names and the ports; the recorder's wires to the machines. Legend: rounded green, a person; double-boxed pink, a machine; dashed amber, an affected population; a plain box, an organization; a solid arrow bundles the items that flow from one part to another; a dotted arrow is a relation that carries no item.
