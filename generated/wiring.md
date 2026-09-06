## The assemblage

Humans are rounded (green), machines are boxed (red); every edge is one interface usage, named as in the model.

```{mermaid}
flowchart LR
  domainExpert(["domainExpert : DomainExpert"])
  evaluator(["evaluator : Evaluator"])
  sponsor(["sponsor : Sponsor"])
  systemUnderTest[["systemUnderTest : SystemUnderTest"]]
  probeDeriver[["probeDeriver : ProbeDeriver"]]
  conformanceChecker[["conformanceChecker : ConformanceChecker"]]
  recorder[["recorder : Recorder"]]
  coverageCalculator[["coverageCalculator : CoverageCalculator"]]
  domainExpert -- "dsoSeam" --> recorder
  evaluator -- "requirementSeam" --> recorder
  probeDeriver -- "derivedProbeSeam" --> evaluator
  evaluator -- "probeRunSeam" --> systemUnderTest
  systemUnderTest -- "responseSeam" --> recorder
  evaluator -- "evaluatorAttestationSeam" --> recorder
  domainExpert -- "expertAttestationSeam" --> recorder
  recorder -- "recordToDeriverSeam" --> probeDeriver
  recorder -- "recordToCheckerSeam" --> conformanceChecker
  recorder -- "recordToCalculatorSeam" --> coverageCalculator
  coverageCalculator -- "reportSeam" --> sponsor
  evaluator -- "recommendationSeam" --> sponsor
  classDef human fill:#e8f5e9,stroke:#2e7d32;
  classDef machine fill:#fce4ec,stroke:#ad1457;
  class domainExpert,evaluator,sponsor human;
  class systemUnderTest,probeDeriver,conformanceChecker,recorder,coverageCalculator machine;
```
