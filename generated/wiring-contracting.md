**View `contracting`: the contracting slice.** In focus: the parties to the contract and the two parts of the testing organization they touch, the items pinned at the contract braided into one bundle per pair of parts, and the sponsor's obligation to the affected populations, a relation that carries no item. Left out: the evaluation team, the machines and the test item; the evaluation items; the seam names and the ports; the recorder's fan-out of the record.

```{mermaid}
flowchart LR
  accountable["accountable : AccountableOrganization"]
  affected{{"affected : AffectedPopulation"}}
  sponsor["sponsor : SponsorOrganization"]
  testingOrg_accountExecutive(["accountExecutive : AccountExecutive"])
  testingOrg_recorder[["recorder : Recorder"]]
  accountable -- "TestItemAccess" --> testingOrg_recorder
  affected -- "StakeholderInput" --> testingOrg_recorder
  sponsor -- "Mission, Need, ServiceAgreement, StatementOfWork, Acceptance" --> testingOrg_accountExecutive
  sponsor -- "Mission, Need, StatementOfWork, Acceptance" --> testingOrg_recorder
  testingOrg_accountExecutive -- "Proposal, Delivery" --> sponsor
  testingOrg_accountExecutive -- "Proposal, ServiceAgreement, Delivery" --> testingOrg_recorder
  sponsor -. "obligation" .-> affected
  classDef person fill:#e8f5e9,stroke:#2e7d32;
  classDef machine fill:#fce4ec,stroke:#ad1457;
  classDef party fill:#fff8e1,stroke:#f9a825,stroke-dasharray: 4 4;
  class testingOrg_accountExecutive person;
  class testingOrg_recorder machine;
  class affected party;
```
