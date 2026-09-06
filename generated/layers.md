## The layers

```{mermaid}
flowchart TB
  subgraph EPO["Evaluation Process Ontology: the standard operating procedure, fixed across domains"]
    direction LR
    s0[scope] --> s1[declareRequirements] --> s2[deriveProbes] --> s3[runAndAttest] --> s4[report]
  end
  subgraph DSO["Domain-Specific Ontology: the expert-supplied parameter, one per domain"]
    direction LR
    de[DomainExpert] -- supplies or approves --> dso[(DsoRelease)]
  end
  subgraph EXEC["Execution: the human and machine assemblage performs EPO with DSO"]
    direction LR
    H["humans: DomainExpert, Evaluator, Sponsor"]
    M["machines: SystemUnderTest, ProbeDeriver, ConformityChecker, Recorder, CoverageCalculator"]
    H --- rec[(evaluation record)]
    M --- rec
  end
  subgraph INTERP["Interpretation: named humans judge; every judgment traces back"]
    direction LR
    att[attestations: outcome, appropriateness, sufficiency] --> recmd[recommendation]
    recmd -. evidence .-> rec
    recmd -. experiments run .-> rec
    recmd -. assessments and who made them .-> att
    recmd -. DSO release and who approved it .-> dso
    recmd -. EPO step .-> EPO
  end
  EPO ==> EXEC
  DSO ==> EXEC
  EXEC ==> INTERP
```
