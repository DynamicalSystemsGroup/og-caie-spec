```{mermaid}
flowchart LR
  accountable["accountable : AccountableOrganization"]
  affected{{"affected : AffectedPopulation"}}
  sponsor["sponsor : SponsorOrganization"]
  testingOrg_accountExecutive(["accountExecutive : AccountExecutive"])
  testingOrg_recorder[["recorder : Recorder"]]
  sponsor -- "acceptanceSeam" --> testingOrg_recorder
  sponsor -- "acceptanceToExecutiveSeam" --> testingOrg_accountExecutive
  accountable -- "accessSeam" --> testingOrg_recorder
  sponsor -- "agreementSeam" --> testingOrg_accountExecutive
  testingOrg_accountExecutive -- "countersignSeam" --> testingOrg_recorder
  testingOrg_accountExecutive -- "deliveryRecordSeam" --> testingOrg_recorder
  testingOrg_accountExecutive -- "deliverySeam" --> sponsor
  sponsor -- "missionSeam" --> testingOrg_recorder
  sponsor -- "missionToExecutiveSeam" --> testingOrg_accountExecutive
  sponsor -- "needSeam" --> testingOrg_recorder
  sponsor -- "needToExecutiveSeam" --> testingOrg_accountExecutive
  testingOrg_accountExecutive -- "proposalSeam" --> testingOrg_recorder
  testingOrg_accountExecutive -- "proposalToSponsorSeam" --> sponsor
  affected -- "stakeholderInputSeam" --> testingOrg_recorder
  classDef person fill:#e8f5e9,stroke:#2e7d32;
  classDef machine fill:#fce4ec,stroke:#ad1457;
  classDef party fill:#fff8e1,stroke:#f9a825,stroke-dasharray: 4 4;
  class testingOrg_accountExecutive person;
  class testingOrg_recorder machine;
  class affected party;
```
