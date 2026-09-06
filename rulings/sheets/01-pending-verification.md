# Rulings sheet 01 (2026-09-06): pending quote verifications and one open concern

Z: tick each row after checking the quote against the screenshot (or the OBP page for ISO/IEC 17000). 
When ticked, the citation's `ogc:quoteStatus` becomes `human` with `ogc:verifiedBy rul:Z ; ogc:verifiedOn <date>`.

| # | Term | Source | Locator | Screenshot / page | Quote | Verified |
|---|---|---|---|---|---|---|
| 1 | stakeholder | iso-9000-2026 | 3.1.4 | iso-9000-2026-obp-02.png | person or organization that can affect, be affected by, or perceive itself to be affected by a decision or activity | [x] 2026-09-06 |
| 2 | verification | iso-9000-2026 | 3.11.12 | iso-9000-2026-obp-32.png | confirmation, through the provision of objective evidence, that specified requirements have been fulfilled | [x] 2026-09-06 |
| 3 | test | iso-9000-2026 | 3.11.13 | iso-9000-2026-obp-32.png | determination according to requirements for a specific intended use or application | [x] 2026-09-06 |
| 4 | validation | iso-9000-2026 | 3.11.14 | iso-9000-2026-obp-32.png | confirmation, through the provision of objective evidence, that the requirements for a specific intended use or application have been fulfilled | [x] 2026-09-06 |
| 5 | appropriateness | iso-9000-2026 | 3.11.2 review | iso-9000-2026-obp-30.png | determination of the suitability, adequacy or effectiveness of an object to achieve established objectives | [x] 2026-09-06 |
| 6 | technical expert | iso-9000-2026 | 3.12.9 | iso-9000-2026-obp-34.png | person who provides specific knowledge or expertise to the audit team | [x] 2026-09-06 |
| 7 | requirement | iso-9000-2026 | 3.5.1 | iso-9000-2026-obp-11.png | need or expectation that is stated, generally implied or obligatory | [x] 2026-09-06 |
| 8 | operational envelope | iso-9000-2026 | 3.5.1 requirement | iso-9000-2026-obp-11.png | need or expectation that is stated, generally implied or obligatory | [x] 2026-09-06 |
| 9 | requirements traceability | iso-9000-2026 | 3.5.11 traceability | iso-9000-2026-obp-13.png | ability to trace the history, application or location of an object | [x] 2026-09-06 |
| 10 | conformity | iso-9000-2026 | 3.5.9 | iso-9000-2026-obp-13.png | fulfilment of a requirement | [x] 2026-09-06 |
| 11 | performance | iso-9000-2026 | 3.7.3 | iso-9000-2026-obp-17.png | measurable result | [x] 2026-09-06 |
| 12 | record | iso-9000-2026 | 3.8.12 | iso-9000-2026-obp-23.png | document stating results achieved or providing evidence of activities performed | [x] 2026-09-06 |
| 13 | evaluation record | iso-9000-2026 | 3.8.12 record | iso-9000-2026-obp-23.png | document stating results achieved or providing evidence of activities performed | [x] 2026-09-06 |
| 14 | objective evidence | iso-9000-2026 | 3.8.6 | iso-9000-2026-obp-21.png | data supporting the existence or verity of something | [ ] |
| 15 | attestation | iso-iec-17000-2020 | 7.3 | OBP | issue of a statement, based on a decision, that fulfilment of specified requirements has been demonstrated | [ ] |

## Open concern

**C-10** system under test: SEVOCAB's only SUT entry is "parts of the CBSS to be tested" (ISO/IEC 14756:1999). 
Options: (a) keep SUT as prefLabel with that quote (current); (b) make *test item* ("work product to be tested", ISO/IEC/IEEE 29119-2:2021) canonical with SUT as altLabel; (c) make *system-of-interest* canonical. Recommendation: (b).
