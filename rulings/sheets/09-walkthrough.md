# Rulings sheet 09 (2026-09-06): the block-and-wire walkthrough (C-30, R-48 sheet 07-09)

Z walked the model block by block in popups; ticks are recorded in
`rulings/validated.ttl` and rendered on sheet 05. Z's answers, as given:

| Block | Answer (as given) | Consequence |
|---|---|---|
| B10 SponsorOrganization | Validated | block and its eleven wires ticked |
| B1 AccountExecutive | "i want to change the headword on this record. account executive ~ top management ~ [tbd]. we need a term that is not confusing for this person" then, on the headword options, "authorized representative (Recommended)"; on the block: "i am not sure i would say the executive never judges in prose but in terms of our ontology, no they are not responsible for the determinationin the report, they are the interface for the organization with its contractual counterparties" | ports and wires ticked; headword to become authorized representative (closes C-26 once renamed, after the tbox audit merges); the prose "never judges" becomes "is not responsible for the determination; the organization's interface with its contractual counterparties" |
| B2 AccountableOrganization | "the organization doing the testing does need to get access. otherwise we make no further assumptions of their involvement in the assessment. we don't assume they are bound to the recommendations. we do narrate in prose an example where monitoring is ongoing and they are involved in a process of pre-release review. we keep that extra process in process, do not force it into the wiring." | a second wire, accessToOperatorSeam, carries the access grant to the evaluation operator (the output shared per R-25); no other port added; monitoring stays prose |
| B4 ConformanceChecker, B5 CoverageCalculator | "coverage should also be computable as a shacl constraint" | both blocks and their three wires ticked; S7-Report gains a SPARQL constraint that recomputes coverage from the attested criteria and compares it with the stored value; counterexample report-coverage-padded.ttl |
| B6 DomainExpert | Validated | block and its six wires ticked |
| B7 EvaluationOperator | Validated | block and its nine wires ticked |

