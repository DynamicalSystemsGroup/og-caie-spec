---
name: ogc-glossary
description: >
  Navigating the OG-CAIE vocabulary graph with the `ogc` CLI: what a term
  means, its class and anchor, its canonical citation with the verbatim quote
  and where the quote was found, which ruling settled it, which concern names
  it, which essential (SCI) is stated in it, which shape checks it, whether a
  word may be used in prose and how to mark it up, the Popper crosswalk, the
  sources, the rulings, the concerns, the views of the model, the executed
  process. Triggers: any glossary question, "what does X mean", quotes,
  sources, rulings, concerns, shapes, {term} markup, check a word,
  og-caie.ttl, sources.ttl, adjudications.ttl, trace.ttl, crosswalk.ttl,
  epo.shapes.ttl, model.shapes.ttl, og-caie.model.ttl.
---

# Ask the graph with `ogc`

The one rule: **run `ogc`; never grep the Turtle, never answer from the
rendered pages or from memory, never invent a definition.** The graph is
the record; the tool is the only honest reader of it. Everything it prints
is deterministic (sorted, no timestamps) and starts with
`# ogc <command> <args> @ <git-sha>`, so a quoted answer is citable.

Run it from the repo as `uv run -q ogc ...` (`-q` keeps uv's warnings out
of the transcript); `python -m ogc` is the same tool. From elsewhere, pass
`--root <checkout>` or set `OGC_ROOT`. `--json` gives the api result as
one object with an `_ogc` key (`command`, `args`, `sha`); a list result sits
under `rows`, and `verify --all` adds a `summary`. Flags may go before or
after the subcommand. Exit 0 found, 1 not found or ambiguous or a bad
filter value (candidates and allowed values are listed) or a failed
VERDICT, 2 usage.

Ids are case-insensitive and one normaliser serves rulings, concerns and
essentials: `R-16`, `R16`, `r-016` and a bare `16` all name R-16; the same
for `C-24` and `SCI-07`. Source slugs, view names, mutation names, shape ids
and filter values are case-insensitive too.

## The mental model (eleven lines)

1. Terms are used, not owned: each term cites exactly one canonical
   definition, from the highest-ranked source that defines it (1 ISO
   9000:2026, 2 SEVOCAB, 3 NIST AI 700-2, 4 W3C/OMG for binding only;
   reserve sources for single terms; internal sources for the four coinages).
   `ogc term <term>` reads it.
2. Three classes: adopted (used as the source defines it), refined (a typed
   anchor, specializes / corresponds / synonym, keeping the source's word as
   an altLabel), coined (exactly four: DSO, EPO, CAIE, OG-CAIE).
   `ogc list --class coined`.
3. Every canonical citation of an adopted or refined term carries a
   verbatim quote with a status: machine (located in a content-hashed
   snapshot by the tests), human (verified by a named person on a date,
   usually against an ISO screenshot), pending (transcribed; awaiting one),
   cite-only (a citation that carries no quote). One vocabulary, used
   everywhere: `ogc quote`, `ogc verify`, `ogc steps`, `ogc define --json`.
4. Sources have a posture: committed (snapshot in the repo), heldLocally
   (hash committed, file not), citeOnly (no quote or a human-verified one).
   `ogc sources` is the register, `ogc source <slug>` one entry.
5. seeAlso citations are neighbours, never definitions.
6. Rulings are dated decisions in the register's words (`ogc:rulingText`),
   each keeping Z's message as sent in `ogc:verbatim` (R-47); refined and
   coined terms derive from one. Concerns are the register of what was in doubt; open ones
   have no resolving ruling. `ogc rulings`, `ogc concerns --open`.
7. The essentials SCI-01..13 name the shapes that check them, the terms
   they are stated in, and what they rest on. `ogc sci`.
8. The Popper crosswalk maps six Popperian elements to standard terms and
   to the EPO classes and shapes that realize them; Popper's words appear
   only on the front page and the conclusion. `ogc crosswalk --popper`.
9. Retired words (adequacy and its forms) are barred from prose (R-08);
   conformance is reclaimed on purpose (R-16); the headword is test item
   and prose may say system under test (R-19). `ogc check-word <word>`.
10. A label resolves to exactly one term; an alternative label that repeats
    a headword carries its sense in parentheses. `ogc doctor` fails otherwise.
11. Diagrams are views (R-38): each reads only the model graph, documents
    its perspective (in focus, left out), braids wires between the same two
    parts into one bundle, and draws relations that carry no item dotted.
    The site's figures come from the same registry. `ogc views`, `ogc view
    <name>`; the shapes that check the model and the record: `ogc shapes`.

## What is loaded

By default: the vocabulary, the EPO steps, the crosswalk, the sources, the
rulings and concerns, the essentials, and the EPO and model shapes, merged
into one graph (named graphs are not exposed; GRAPH, FROM and FROM NAMED are
refused). `--model` adds the canonical model graph, the OMG `sysml:`
rendering of the structure (part, port, interface and action definitions,
the assembly and its wiring), not EPO instances; `view`, `views` and
`execute` load it on their own. `ogc` does not load the record
(`track/measles-run.ttl`) yet: reading the record is open concern C-44 and
needs a ruling before a reader is added, so questions about the measles run
go to the notebooks and the pages for now.

## Start here

- `ogc schema`: the counts, the classes and properties in use, the prefixes.
- `ogc find <text>`: which terms match, exact then prefix then substring,
  over labels and over quote text (`via quote:<source>`); `--no-quotes`
  restricts it to labels (and appears in the printed args).

## Recipes

| Question | Command |
|---|---|
| What does this word mean here? | `ogc define <term>` (says `resolved via alt:...` when you typed an alternative label; `--json` carries the quote `status`) |
| The whole entry: class, anchor, citations with quotes and status, scope note, binding, rulings, concerns, essentials, crosswalk | `ogc term <term>` |
| The canon behind a term, or behind a step, verbatim | `ogc quote <term>`; `ogc quote scope`, `ogc quote "C1 need"`, `ogc quote need` |
| Is each quote really where its citation says? | `ogc verify <term>`, `ogc verify <source-slug>`, `ogc verify <step>`, `ogc verify --all` (summary line; in JSON a `summary`); the first column is `holder` (a term or a step), the second `citation` (canonical or seeAlso) |
| May I use this word in prose, and how do I mark it up? | `ogc check-word <word> [<word> ...]` (several words at once; quote multi-word ones; registered / alternative / retired; the `{term}` role to write; other terms the word lands on; concerns that mention it; empty words are refused) |
| Every term a source supports, with the quotes | `ogc source <slug>`; the register: `ogc sources --rank 1`, `--posture heldLocally`, `--uncited` |
| The terms by class or by source | `ogc list --class refined`, `ogc list --source sevocab` (an unregistered slug exits 1 with the candidates) |
| Why is it defined this way? | `ogc rulings --term <term>`; a substring over ruling texts, messages as sent and change notes: `ogc rulings --grep conformance`; one ruling, the decision and then the message as sent: `ogc ruling R-16` (`--json` carries `text` and `verbatim`) |
| What was in doubt, and what is still open | `ogc concerns --open`, `ogc concerns --status ruled`, `ogc concerns --severity H`; `ogc concern C-25` |
| What must a scientific record contain? | `ogc sci`; one essential: `ogc sci SCI-07` |
| Which canon step does each of the twelve steps match? | `ogc steps` |
| What does a shape check, and over what? | `ogc shapes` (every node shape with its target and file); `ogc shape S3-PlanApproval`, `ogc shape m1-parties`, `ogc shape RulingShape` (target, property constraints, each SPARQL constraint's message) |
| The views of the model: what each brings into focus and leaves out | `ogc views` |
| One view as mermaid, with its perspective (nesting, assemblage, contracting, evaluation) | `ogc view contracting` |
| Execute the process from the model and run the checks over the emitted record; break one or more things | `ogc execute` (ends in `VERDICT: PASS` or `FAIL`, exit 1 on FAIL), `ogc execute --mutate skip-access`, `--mutate` repeated applies them in order, `ogc execute --turtle` |
| The anchor table, one row per term | `ogc crosswalk`, `ogc crosswalk --class refined`, `ogc crosswalk --source iso-9000-2026` |
| Popper to the standards and back | `ogc crosswalk --popper` |
| Anything else | `ogc sparql '<SELECT ...>'` or `ogc sparql @query.rq` (prefixes injected; read-only; `--model` adds the model graph and appears in the printed and hashed args) |
| Is the graph healthy? | `ogc doctor` (VERDICT line; runs in the gate) |

The eight mutations of `execute`: `skip-assessment`, `skip-approval`,
`skip-access`, `unwire-evidence`, `executive-attests`,
`attest-without-determination`, `requirements-before-agreement`,
`engagement-mismatch`; `ogc execute --help` says what each breaks.

## SPARQL notes

- Term IRIs live in `term:` (`https://w3id.org/og-caie/terms#`), so
  `ogc sparql 'DESCRIBE term:probe'` prints one term's triples; sources
  are `src:`, rulings and concerns `rul:`, steps `epo:`, essentials `tr:`,
  crosswalk rows `xw:`, the model `ogm:` with the OMG `sysml:` vocabulary.
  `ogc schema` prints the whole prefix list.
- Labels and definitions are language-tagged (`"probe"@en`): match with
  `STR(?l) = "probe"` or `LCASE(STR(?l))`.
- The determinism promise: rows are sorted when the query has no ORDER BY,
  and a LIMIT or OFFSET without ORDER BY is applied after that sort (to
  rows for SELECT, to triples for CONSTRUCT and DESCRIBE); CONSTRUCT and
  DESCRIBE print a fixed prefix set and sorted triples; blank nodes are
  labelled by a hash of their neighbourhood, so a citation's label is the
  same in every run and in every query. Outside the promise: blank nodes
  whose neighbourhoods are identical (they are numbered in arbitrary
  order), and NOW(), RAND(), BNODE(), UUID() and STRUUID().
- Queries longer than 20,000 characters, SERVICE, GRAPH, FROM and update
  forms are refused with exit 2.

## Writing prose

Reference a key term as `` {term}`probe` `` (the headword) or
`` {term}`system under test <test item>` `` (display text, then the headword
in angle brackets). The glossary page renders exactly the referenced terms
with hover definitions; `ogc check-word` prints the role to write. Never use
a retired word; never coin a fifth term without a ruling.
