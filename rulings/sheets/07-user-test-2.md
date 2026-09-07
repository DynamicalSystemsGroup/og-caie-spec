# Rulings sheet 07 (2026-09-06): simulated user test, round 2

After the rulings of sheet 06 landed (R-47: restructured chapters, formal
rulings register, record reader, executor parameters, ticked quotes, the
public session cited), the human reader read main at 3693d30 and the
citation auditor read the tree before the three merges; the machine user
and reproducibility reviewers run against the tree after the fixes below.

| Persona | Round 2 | Round 1 | In one line |
|---|---|---|---|
| Human reader | 4 4 4 3 3 4 4 | 3 3 3 2 3 4 4 | the outline, the parts and the command blocks work; the conclusion outran Appendix C's open concern; figures still small |
| Citation auditor | 4 3 4 4 3 3 | 4 3 4 3 4 3 | steps now faithful (4); statuses and consistency dropped on fragment markers placed on the wrong terms, a dead coinage shape, and stale notes, all fixed in code |

Fixed in code without a ruling (79cf10d): fragment markers on the citations
that carry the fragment; the coined-term shape now fires and the four
coined terms render "coined by the authors"; C4's test-environment quote in
full; SEVOCAB delivery on C5 and ISO/IEC 17000 7.3 attestation on step 5;
the bridge's quotes tagged *authors* and the tag defined; the source register
counts step citations and Popper; digests and licence notes current; the
private names and the joining sentences out of the register's notes; the
command blocks fold long lines and say how to see the rest; figure captions
below the figures; the nesting view's titles short; the walkthrough's
derivation and coverage cells filled; the conclusion claims what the
executor shows and points at C-30; the measles coverage explained by its
weights; plain words for evidence and determination; SEBoK, ARIA and SysML
expanded at first use; the guarantees notebook prints its tables; Appendix
D's CI table joins multi-line values.

The rows below need Z.

| Item | Finding (who) | Options | Ruling |
|---|---|---|---|
| 07-01 | C-30 (H) still says nothing shows that every run must conform, while the executor chapter shows generated runs and mutations; the conclusion now says so and points at C-30 (reader) | (a) narrow C-30 to what remains: Z's block-and-wire validation on sheet 05, and rule that the executor's demonstration is the computational half, so the open item is the human half (Recommended); (b) keep C-30 open as written; (c) close C-30 | [ ] |
| 07-02 | The bridge's second-layer row carries the slogan "Context Matters!" where every other row carries a definition (reader; persists from 06-02) | (a) write one sentence in the authors' voice for that row's definition, kept in the session digest as the authors' own words, with the slogan as the quote (Recommended); (b) leave | [ ] |
| 07-03 | Two near-identical hover cards, record and evaluation record; the outcome card listed five values against the three the record uses (reader) | (a) merge: evaluation record keeps the headword, record becomes its alternative label (Recommended); outcome fixed in code; (b) leave both | [ ] |
| 07-04 | The nesting view's chains stack vertically because mermaid ignores a subgraph's direction when edges cross subgraphs; the black box sits far from the chain it opens (reader) | (a) draw it as two figures: the outer chain with fulfil black-boxed, then the inner chain with its three boundary wires drawn to labelled ports, both left-to-right (Recommended); (b) leave | [ ] |
| 07-05 | The four-column bridge table is three screens tall at column width (reader) | (a) move the quotations out of the element column into a paragraph under the table (Recommended); (b) leave | [ ] |
| 07-06 | C4 access still cites a testing-organization process as canonical, where the step is the accountable organization granting access; the auditor would put ISO/IEC 17000 4.10 access there, the researcher on C2 (auditor) | (a) keep 29119-2 as canonical and cite 4.10 on both C2 and C4 as seeAlso (Recommended); (b) 4.10 canonical on C4 | [ ] |
| 07-07 | The SEVOCAB absence check behind the NIST and reserve canonicals is recorded for five words only (auditor) | (a) record the check for session, dialogue, guardrail, repeatability, reproducibility, measurement uncertainty, ontology, trajectory, appropriateness, sufficiency in the SEVOCAB digest, with the date (Recommended); (b) leave | [ ] |
| 07-08 | "The accompanying paper" is named on the vocabulary page and in one definition, but no paper is linked (reader) | (a) name it as forthcoming with the venue, no link until it is public (Recommended); (b) remove the mentions | [ ] |
| 07-09 | Still pending from sheet 05 and earlier: block-and-wire validation (C-30, 49 rows), C-25, C-26, C-43, C-45 | your call | [ ] |
