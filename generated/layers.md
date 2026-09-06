## The layers

**View `layers`: the layers.** In focus: the two cycles as chains of steps, the DSO as the expert-supplied parameter, and how execution and interpretation rest on the record. Left out: every part, port, seam and item kind; the steps' inputs and outputs; who performs which step.

```{mermaid}
flowchart TB
  subgraph PARTIES["Contracting lifecycle: the parties (AccountableOrganization, SponsorOrganization, TestingOrganization; affected populations) pin the first layer of assumptions"]
    direction LR
    c0[need] --> c1[propose] --> c2[agree] --> c3[access] --> c4[fulfil] --> c5[deliver] --> c6[acceptDelivery]
  end
  subgraph EPO["Evaluation Process Ontology: the standard operating procedure, fixed across domains"]
    direction LR
    s0[scope] --> s1[declareRequirements] --> s2[plan] --> s3[execute] --> s4[determineAndAttest] --> s5[report]
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
