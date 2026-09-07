# Rulings sheet 11: the drift loop's log

The read layer of the consistency and drift loop (the plan of 2026-09-07,
section 6): after each merge a drift reader, a sandboxed persona on a
detached worktree of the merged tip, reads the range since the last pass
and every page, docstring, help string, shape message and notebook cell it
touches, against the model, the record, the shapes and the rulings. Each
pass is logged here with its range, its findings and what was done; a
finding that needs Z's judgment is put on the current rulings sheet
instead. The mechanical layer is `scripts/drift_check.py`, a gate step.

| Pass | Range | Read on | Findings | Fixed in code | Deferred | Added to the script |
|---|---|---|---|---|---|---|
| 1 | fa5a1a0..b18a1bc (R-50, R-51, the vocabulary slice, register and model vocabularies, the version line, the drift step, the sample report scaffold and the relettered appendices) | 2026-09-07 | 34: one gate-breaking (the four SEVOCAB canonicals absent from the digest, so CI failed on b18a1bc), fourteen wrong statements (the party reading in two chapters, the decision sentence, the pending-tick sentence, the version clause, the fulfil boundary on three pages, the C4 access sentence, C-30 in CLAUDE.md and the README, "never judges", the coinages "citing" the session, the C4 scope note contradicting itself, the drift script's docstring, the version script's fallback), nine stale names, six counts, four polish | the digest rows and the CI rule (ac76516); the rest of the pages, CLAUDE.md, the README, the skill, the glossary shape's message, the C4 and step 5 scope notes, the version line, the digest's rank word, the notebook's count (this commit) | the SysML doc comments, model/trace.ttl SCI-10, the executor's mutation text, the explorer's labels, the traceback comment, the model shape's message and the CLI help strings: files slice A is rewriting; fixed after its merge (drift pass 2) | phrases matched with whitespace collapsed; notebooks, queries and the executor scanned; retired words read from the tool's list; appendix mentions and counts against the table of contents; the mutation count against the executor; every machine quote on a held-locally source located in its digest |
