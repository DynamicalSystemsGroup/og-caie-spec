## The essentials

13 requirements: 11 verified by machine alone; 2 checked by machine for form, with the judgment itself made by a named person. They live in `model/trace.ttl`; SysML holds structure only (ruling R-22).

| ID | Name | Checked by | Statement |
|---|---|---|---|
| SCI-01 | DsoApprovedBeforeProbes | machine | The Domain-Specific Ontology release is versioned and approved by a named domain expert before any probe is derived from it. |
| SCI-02 | EnvelopeDeclaredBeforeSessions | machine | The service agreement, the operational environment, the test item and the requirement set are declared, in that order, before any session runs: this system in this environment under this contract. |
| SCI-03 | CriteriaWellFormed | machine | Every requirement has at least one acceptance criterion derived from it; every criterion states its expected result and carries a positive weight. |
| SCI-04 | PlanBeforeRuns | machine | A test plan states its objectives and its means; every probe belongs to a plan, derives from the DSO release and passes a consistency check before any session. |
| SCI-05 | EvidenceFromNamedRuns | machine | Every response comes from a numbered turn of a session against a versioned test item; every evidence item bears on one criterion's expected result under the plan. |
| SCI-06 | AttestationsWellFormed | machine for form; human for the judgment | Determinations rule on evidence with an EARL outcome; attestations aggregate a criterion's determinations, name their assertor, and judge appropriateness and sufficiency; the closure and chain rules hold. |
| SCI-07 | CoverageRecomputable | machine | Coverage is recomputable from a conformant record: a criterion counts as covered only with an attestation behind it. |
| SCI-08 | CoverageAndPerformanceKeptApart | machine | Coverage and performance are reported together and never merged. |
| SCI-09 | RecommendationTraceable | machine for the trace; human for the recommendation | Every recommendation traces to the attestations it rests on, their evidence, the DSO release and the EPO step. |
| SCI-10 | PartiesNamedAndAgreed | machine | The sponsor, the testing organization and the accountable organization are named; the sponsor's mission and obligations towards the affected populations are recorded before the need, and its statement of work decides, per population, interview or representation; the agreement is signed by the sponsor and the account executive; every affected population is interviewed or represented by a named domain expert. |
| SCI-11 | EndStateGuaranteed | machine | The wiring guarantees the end state, checked locally over kinds of parts and ports: every wire runs from an output port on a part to an input port on a part carrying one item kind; at every part every input is present once and every output goes somewhere; every item kind reaches the recorder; the seven steps form a process DAG that produces every item kind; a conformant record then yields traceability in both directions and coverage, and answers why. |
| SCI-12 | RolesDistinct | machine | The domain expert who approves the DSO, assesses appropriateness and attests is not the evaluation operator who administers tests and collects evidence, and neither is the account executive who signs the agreement; one account executive, one or more of each expert. |
| SCI-13 | TwoLayersOfAssumptions | machine | What the contract pins (the counterparties, the test item, the requirements' frame, the method) is recorded and closed before what the evaluation pins (the environment, the requirement set, the DSO release, the plan) is declared; the evaluation documents the first layer and cannot change it. |
