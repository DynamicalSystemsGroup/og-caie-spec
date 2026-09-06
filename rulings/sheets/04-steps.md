# Rulings sheet 04 (2026-09-06): the ISO/IEC 17000 quotes behind the seven steps

Ruling R-31 bound each EPO step to the canon step it matches. The SEBoK and SEVOCAB quotes are machine-located in the held PDFs; the ISO/IEC 17000 quotes below were read on the Online Browsing Platform by Claude and await Z's tick. Tick with `uv run python scripts/tick.py epo:<step> "<locator>" <date> --source iso-iec-17000-2020` (the EPO term itself: `tick.py evaluation-process-ontology ...`).

| # | Holder | Locator | Quote | Verified |
|---|---|---|---|---|
| 1 | evaluation-process-ontology | 4.1 conformity assessment, Note 3 | Conformity assessment is explained in Annex A as a series of functions. Activities contributing to any of these functions can be described as conformity assessment activities. | [ ] |
| 2 | (moved to row 8) | 4.10 access | opportunity for an applicant to obtain a conformity assessment service from a body under a conformity assessment scheme | [ ] |
| 3 | epo:declareRequirements | 5.1 specified requirement | need or expectation that is stated | [ ] |
| 4 | epo:execute | 6.2 testing | determination of one or more characteristics of an object of conformity assessment, according to a procedure | [ ] |
| 5 | epo:determineAndAttest | 7.2 decision | conclusion, based on the results of review, that fulfilment of specified requirements has or has not been demonstrated | [ ] |
| 6 | epo:determineAndAttest | 7.1 review | consideration of the suitability, adequacy and effectiveness of selection and determination activities, and the results of these activities, with regard to fulfilment of specified requirements by an object of conformity assessment | [ ] |
| 7 | (moved to row 10) | 7.3 attestation, Note 1 | is intended to convey the assurance that the specified requirements have been fulfilled | [ ] |
| 8 | epo:propose | 4.10 access | opportunity for an applicant to obtain a conformity assessment service from a body under a conformity assessment scheme | [ ] |
| 9 | epo:agree | 4.9 conformity assessment scheme | set of rules and procedures that describes the objects of conformity assessment, identifies the specified requirements and provides the methodology for performing conformity assessment | [ ] |
| 10 | epo:deliver | 7.3 attestation, Note 1 | is intended to convey the assurance that the specified requirements have been fulfilled | [ ] |
| 11 | epo:acceptDelivery | 9.6 acceptance | use of a conformity assessment result provided by another person or organization | [ ] |

| 12 | epo:ContractingStep (the lifecycle itself) | 8.1 surveillance | systematic iteration of conformity assessment activities as a basis for maintaining the validity of the statement of conformity | [ ] |

Rows 8 to 11 belong to the contracting lifecycle (ruling R-32); row 2's quote moved from the evaluation's agree step to the contracting step propose, and row 7's to deliver.
