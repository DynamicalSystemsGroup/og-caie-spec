# Rulings sheet 06 (2026-09-06): simulated user test, round 1

Four fresh, sandboxed persona agents read the tree at 2f2149f (with the
nesting view and the private-reference clean-up of 7f5c770 and 179f0f0 in
some of their worktrees), read-only, and reported. Ratings, 1 to 5:

| Persona | Ratings | In one line |
|---|---|---|
| Human reader (engineering or policy, not an ontologist) | understood the method 3; outline told me what each page holds 3; five blocks taught and showed 3; diagrams legible 2; conclusion earned 3; narrative/appendix split 4; can verify without trusting 4 | the rhythm and the hover definitions work; the walkthroughs are dates and names without content; figures and jargon are the weak points |
| Machine user (an assistant using only `ogc` and the skill) | discoverability 4; completeness 4; robustness 4; determinism and citability 3; JSON fidelity 4 | one crash in about 230 probes (SPARQL GRAPH); ten of twelve questions answered by one command; help strings and id forms uneven |
| Reproducibility reviewer (fresh clone, Appendix D only) | recipe worked 5; prints matched 4; verified by hand 5; appendices as bridge 3; nothing from the authors' machine 4 | `CHECKS: PASS` twice, byte-identical regeneration, hand checks matched the site; network, git and the interpreter were unstated |
| Citation auditor (standards-literate) | traceable 4; statuses honest 3; precedence 4; steps faithful 3; consistency 4; licence and attribution 3 | every citation names a registered source with a locator; 13 pending; some quotes are fragments without ellipsis; four step matches are a stretch |

Fixed in code without a ruling (commits 016f293 and after): the quote
statuses stated from the graph with the three tags defined; open concerns
rendered on Appendix C; the walkthrough tables show what each judgment said
and the measles criteria with their outcomes and the recomputed coverage;
figure legends; the more block points at the appendices with the commands in
a dropdown; the seventh step named; roles introduced at first mention; the
IEEE statement on every rendered SEVOCAB quote; stale digest and licence
notes; README numbers; the recipe's explorer copy; the notebook verdict
printed; the interpreter pinned; prerequisites and network stated; the
`ogc` hardening list (crash, determinism, `--model` in the header, filter
validation, id forms, help strings, JSON header, a shape reader), merged
from branch `ogc-hardening`.

The rows below need Z. Tick the recommended option or write another.

| Item | Finding (who) | Options | Ruling |
|---|---|---|---|
| 06-01 | The front page's first paragraph is one 80-word sentence stacking four acronyms, and the measles case is first met on page 3 (reader) | (a) three sentences and one clause naming the measles case before the science section (Recommended); (b) leave | [ ] |
| 06-02 | The bridge table's second-layer row quotes "Context Matters!" as the definition of the central idea; the deck is introduced only under the table (reader) | (a) introduce the deck in the sentence before the table and give the row a one-line definition from the deck's notes, keeping the exclamation as the quote (Recommended); (b) leave | [ ] |
| 06-03 | The five blocks render as identical blue notes and, being admonitions not headings, leave the Contents panel empty on every chapter (reader) | (a) a small site stylesheet giving the five classes distinct icons and colours, blocks stay admonitions (Recommended); (b) make each block a level-2 heading; (c) leave | [ ] |
| 06-04 | Appendix C's verbatim rulings are chat messages to an assistant, with typos; the form undermines the content for a reader asked to accept them as auxiliary assumptions (reader) | (a) keep verbatim, add a "ruling in short" column rendered from the concern's label and the change note, and say in the intro that the text is the adjudicator's message as sent (Recommended); (b) leave verbatim only; (c) edit the texts (against the rulings rule) | [x] 2026-09-06, R-47 (C-53): rework the texts to a formal register, intents preserved; the message as sent kept in the graph as `ogc:verbatim`, both required |
| 06-05 | Words met undefined: shape, seam, port, wire, part, action def, flow, essentials/SCI, the gate, first and second party, machine/human/pending tags, Apollo-SV (reader) | (a) one sentence at first use per chapter for shape, seam/port/wire, essentials, the gate, and `{term}` roles for first, second and third party where they already exist; the tags are now defined on the vocabulary page (Recommended); (b) a short "how to read this site" box on the vocabulary page listing them; (c) leave | [ ] |
| 06-06 | `outcome` cites W3C EARL as canonical with a narrative definition, against the rule that W3C binds only (auditor) | (a) canonical to SEVOCAB `test result, p. 438`, EARL in the binding (Recommended); (b) canonical to ISO 9000:2026 `result`; (c) leave with a scope note explaining the exception | [ ] |
| 06-07 | `repeatability` and `reproducibility` cite the reserve JCGM VIM as canonical while NIST TN 1297, rank 3, is only a seeAlso (auditor) | (a) set TN 1297 to reserve, since the VIM is the definition it cites (Recommended); (b) make TN 1297 canonical | [ ] |
| 06-08 | Six quotes are fragments presented without an omission mark: deployment sensitivity, probe (SEVOCAB test case), authoritative reference (Hogan), exploratory testing, NIST application, ISO/IEC 17000 7.3 Note 1 (auditor) | (a) mark omission in the locator ("fragment: ...") and keep the quote text as the located string, so the machine check still holds (Recommended); (b) extend each quote to the full sentence and relocate; (c) leave | [ ] |
| 06-09 | Four step matches are a stretch: C2 propose cites SEBoK's definition of a supplier; C4 access cites SEVOCAB test environment (a thing) while ISO/IEC 17000 4.10 access sits on C2; C6 accept's seeAlso 9.6 is recognition of results between bodies; step 2's canonical describes system design (auditor) | (a) move 17000 4.10 access from C2 to C4 as C4's seeAlso, keep the rest and say in each step's scope note why the nearest canon is a thing rather than a process (Recommended); (b) hunt new canon for all four; (c) leave | [ ] |
| 06-10 | The four coined terms cite two internal Google Docs with no digest, so a reader cannot trace them (auditor) | (a) commit an excerpt digest of each document, the paragraphs that define the terms (Recommended); (b) cite the BoF deck instead where it defines them; (c) leave | [ ] |
| 06-11 | `popper-1959` is registered and cited by nothing; the crosswalk cites only the deck (auditor) | (a) add Popper 1959 as a seeAlso on each crosswalk row (Recommended); (b) leave, with a note in the digest | [ ] |
| 06-12 | `ogc` does not read the record, so record items in the explorer point at their class (machine user; concern C-44) | (a) `ogc sparql --record` and a `record` command listing the measles items by step (Recommended); (b) leave | [ ] |
| 06-13 | The executor has no run in which every criterion is planned, so the tool cannot show coverage 1.0 on demand (machine user) | (a) `ogc execute --planned N` and `--sessions N` exposing the executor's parameters (Recommended); (b) leave (the variants table has it) | [ ] |
| 06-14 | Thirteen quotes are pending Z's tick on sheet 04 (mission, monitoring, eleven ISO/IEC 17000 clauses); step 5's only canonical citation is among them (auditor) | tick sheet 04 | [ ] |
| 06-15 | `pytest` in the recipe versus the gate: the reviewer would have liked expected durations and a statement that a zip download cannot run the gate (reproducibility) | done in code (Appendix D says git, two to three minutes) | [x] |

Findings from the same round that needed no ruling were fixed in code and
are listed above; the machine user's twenty findings are fixed with one test each
(`tests/test_ogc.py`, `test_finding_NN_*`).
