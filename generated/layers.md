## The layers

```{mermaid}
flowchart TB
  subgraph PARTIES["Parties: AccountableOrganization, SponsorOrganization, TestingOrganization; affected populations"]
    direction LR
    agree[service agreement] --> reqs[requirement set]
  end
  subgraph EPO["Evaluation Process Ontology: the standard operating procedure, fixed across domains"]
    direction LR
    s0[agree] --> s1[scope] --> s2[declareRequirements] --> s3[plan] --> s4[execute] --> s5[determineAndAttest] --> s6[report]
  end
  subgraph DSO["Domain-Specific Ontology: the expert-supplied parameter, one per domain"]
    direction LR
    de[DomainExpert] -- supplies or approves --> dso[(DsoRelease)]
  end
  subgraph EXEC["Execution: the human and machine assemblage performs EPO with DSO"]
    direction LR
    H["people: AccountExecutive, DomainExpert, EvaluationOperator, Person"]
    M["machines: ConformanceChecker, CoverageCalculator, Machine, ProbeDeriver, Recorder, TestItem"]
    H --- rec[(evaluation record)]
    M --- rec
  end
  subgraph INTERP["Interpretation: named humans judge; every judgment traces back"]
    direction LR
    det[determinations on evidence: passed, failed, cantTell] --> att[attestations: outcome, appropriateness, sufficiency]
    att --> recmd[recommendation]
    recmd -. evidence collected .-> rec
    recmd -. experiments run: sessions, turns, probes under the test plan .-> rec
    recmd -. assessments and who made them .-> att
    recmd -. DSO release and who approved it .-> dso
    recmd -. EPO step .-> EPO
  end
  PARTIES ==> EPO
  EPO ==> EXEC
  DSO ==> EXEC
  EXEC ==> INTERP
```
