---
name: ogc-glossary
description: >
  Navigating the OG-CAIE vocabulary graph with the `ogc` CLI: what a term
  means, its class and anchor, its canonical citation with the verbatim quote
  and where the quote was found, which ruling settled it, which concern names
  it, which essential (SCI) is stated in it, whether a word may be used in
  prose and how to mark it up, the Popper crosswalk, the sources, the
  rulings, the concerns. Triggers: any glossary question, "what does X
  mean", quotes, sources, rulings, concerns, {term} markup, check a word,
  og-caie.ttl, sources.ttl, adjudications.ttl, trace.ttl, crosswalk.ttl.
---

# Ask the graph with `ogc`

The one rule: **run `ogc`; never grep the Turtle, never answer from the
rendered pages or from memory, never invent a definition.** The graph is
the record; the tool is the only honest reader of it. Everything it prints
is deterministic (sorted, no timestamps) and starts with
`# ogc <command> <args> @ <git-sha>`, so a quoted answer is citable.

Run it from the repo as `uv run -q ogc ...` (`-q` keeps uv's warnings out
of the transcript); `python -m ogc` is the same tool. `--json` gives the raw
result and may go before or after the subcommand. Exit 0 found, 1 not found
or ambiguous or a bad filter value (candidates and allowed values are
listed), 2 usage. Ids (`R-16`, `C-24`, `SCI-07`) are case-insensitive and
unpadded forms work (`r-5`, `c-7`).

## The mental model (ten lines)

1. Terms are used, not owned: each term cites exactly one canonical
   definition, from the highest-ranked source that defines it (1 ISO
   9000:2026, 2 SEVOCAB, 3 NIST AI 700-2, 4 W3C/OMG for binding only;
   reserve sources for single terms; internal sources for the four coinages).
2. Three classes: adopted (used as the source defines it), refined (a typed
   anchor, specializes / corresponds / synonym, keeping the source's word as
   an altLabel), coined (exactly four: DSO, EPO, CAIE, OG-CAIE).
3. Every canonical citation of an adopted or refined term carries a
   verbatim quote with a status: machine (located in a content-hashed
   snapshot by the tests), human (verified by a named person on a date,
   usually against an ISO screenshot), pending (transcribed; awaiting one).
4. Sources have a posture: committed (snapshot in the repo), heldLocally
   (hash committed, file not), citeOnly (no quote or a human-verified one).
5. seeAlso citations are neighbours, never definitions.
6. Rulings are Z's words verbatim, dated; refined and coined terms derive
   from one. Concerns are the register of what was in doubt; open ones
   have no resolving ruling.
7. The essentials SCI-01..12 (`model/trace.ttl`) name the shapes that check
   them, the terms they are stated in, and what they rest on.
8. The Popper crosswalk (`vocabulary/crosswalk.ttl`) maps six Popperian
   elements to standard terms and to the EPO classes and shapes that
   realize them; Popper's words appear only on the front page and the
   conclusion.
9. Retired words (adequacy and its forms) are barred from prose (R-08);
   conformance is reclaimed on purpose (R-16); the headword is test item
   and prose may say system under test (R-19).
10. A label resolves to exactly one term; an alternative label that repeats
    a headword carries its sense in parentheses. `ogc doctor` fails otherwise.
11. Diagrams are views (`ogc/views.py`, R-38): each reads only the model
    graph, documents its perspective (in focus, left out), braids wires
    between the same two parts into one bundle, and draws relations that
    carry no item dotted. The site's figures come from the same registry.

## Start here

- `ogc schema`: the counts, the classes and properties in use, the prefixes.
- `ogc find <text>`: which terms match, exact then prefix then substring,
  over labels and over quote text (`via quote:<source>`).

## Recipes

| Question | Command |
|---|---|
| What does this word mean here? | `ogc define <term>` (says `resolved via alt:...` when you typed an alternative label) |
| The whole entry: class, anchor, citations with quotes and status, scope note, binding, rulings, concerns, essentials, crosswalk | `ogc term <term>` |
| The canon behind a term, verbatim | `ogc quote <term>` |
| Is each quote really where its citation says? | `ogc verify <term>`, `ogc verify <source-slug>`, `ogc verify --all` |
| May I use this word in prose, and how do I mark it up? | `ogc check-word <word> ...` (registered / alternative / retired; the `{term}` role to write; other terms the word lands on; concerns that mention it) |
| Every term a source supports, with the quotes | `ogc source <slug>`; the register: `ogc sources --rank 1`, `--posture heldLocally`, `--uncited` |
| The terms by class or by source | `ogc list --class refined`, `ogc list --source sevocab` |
| Why is it defined this way? | `ogc rulings --term <term>`; one ruling verbatim: `ogc ruling R-16` |
| What was in doubt, and what is still open | `ogc concerns --open`; `ogc concern C-25` |
| What must a scientific record contain? | `ogc sci`; one essential: `ogc sci SCI-07` |
| Which canon step does each EPO step match? | `ogc steps` |
| The views of the model: what each brings into focus and leaves out | `ogc views` |
| One view as mermaid, with its perspective (layers, assemblage, contracting, evaluation) | `ogc view contracting` |
| Execute the process from the model and run the checks over the emitted record; break one thing | `ogc execute`, `ogc execute --mutate skip-access`, `ogc execute --turtle` |
| The anchor table, one row per term | `ogc crosswalk`, `ogc crosswalk --class refined`, `ogc crosswalk --source iso-9000-2026` |
| Popper to the standards and back | `ogc crosswalk --popper` |
| Anything else | `ogc sparql '<SELECT ...>'` or `ogc sparql @query.rq` (prefixes injected; read-only; `--model` adds the canonical model graph) |
| Is the graph healthy? | `ogc doctor` (VERDICT line; runs in the gate) |

## Writing prose

Reference a key term as `` {term}`probe` `` (the headword) or
`` {term}`system under test <test item>` `` (display text, then the headword
in angle brackets). The glossary page renders exactly the referenced terms
with hover definitions; `ogc check-word` prints the role to write. Never use
a retired word; never coin a fifth term without a ruling.
