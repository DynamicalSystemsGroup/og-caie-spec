---
name: ogc-glossary
description: >
  Navigating the OG-CAIE vocabulary graph with the `ogc` CLI: what a term
  means, its class and anchor, its canonical citation with the verbatim quote
  and where the quote was found, which ruling settled it, which concern names
  it, which essential (SCI) is stated in it, which shape checks it, whether a
  word may be used in prose and how to mark it up, the Popper crosswalk, the
  sources, the rulings, the concerns, the views of the model, the executed
  process, the worked example's record (the measles evaluation) item by item.
  Triggers: any glossary question, "what does X mean", quotes,
  sources, rulings, concerns, shapes, {term} markup, check a word, the
  measles record, who attested or signed what and when, the model's
  parts and wires, a SPARQL question over any of the repository's graphs.
---

# Ask the graph with `ogc`

The one rule: **run `ogc`; never grep the Turtle, never answer from the
rendered pages or from memory, never invent a definition.** The graph is
the record; the tool is the only honest reader of it. Everything it prints
is deterministic (sorted, no timestamps) and starts with
`# ogc <command> <args> @ <git-sha>`, so a quoted answer is citable. The
header is the canonical form of the invocation, not the keystrokes: `--root`
and the global flags are dropped, `--model` and `--record` come last in that
order wherever they were typed, whitespace is collapsed and newlines are
escaped as `\n`; two invocations that differ only in those print the same
header.

Run it from the repo as `uv run -q ogc ...` (`-q` keeps uv's warnings out
of the transcript); `python -m ogc` is the same tool. From elsewhere, pass
`--root <checkout>` or set `OGC_ROOT`. `--json` gives the api result as
one object with an `_ogc` key (`command`, `args`, `sha`); a list result sits
under `rows`, and `verify --all` adds a `summary`. Flags may go before or
after the subcommand. Exit 0 found, 1 not found or ambiguous or a bad
filter value (candidates and allowed values are listed) or refused or a
failed VERDICT, 2 usage (an empty or blank id, a flag where it does not
apply, filters that exclude each other). Under `--json` every error is one
object too: `_ogc` (with the real command name), `error`, `hint`,
`candidates`; without `--json` a usage error or a refusal goes to stderr
as `ogc: ...` and nothing is printed on stdout.

Ids are case-insensitive and one normaliser serves rulings, concerns and
essentials: `R-16`, `R16`, `r-016` and a bare `16` all name R-16; the same
for `C-24` and `SCI-07`. Every reader also takes the id forms the tool
itself prints: a CURIE (`term:probe`, `rul:R-16`, `rul:C-30`, `tr:SCI-07`,
`src:sevocab`, `ogc:S0-Layers`, `ev:mission-1`, `epo:Report`; the prefix
in any case, `TERM:PROBE` is `term:probe`) or the full IRI, with or without
angle brackets. A CURIE under a prefix the command does not read is a miss
(exit 1) whose hint names the reader that does: `ogc term rul:R-16` says
try `ogc ruling R-16`, `ogc define epo:StakeholderRepresentation` says try
`ogc epo StakeholderRepresentation`, `ogc record term:probe` says try `ogc
term probe`; the shapes live under `ogc:`, so `ogc shape epo:S3-PlanApproval`
is a miss too. Source slugs, view names, mutation names, shape ids and
filter values are case-insensitive too. A miss lists up to eight near
misses (substring, shared word, edit distance), never the whole list; an
argument longer than eighty characters is echoed cut, with three dots, in
the error line (the header keeps it whole).

`--model` and `--record` are accepted only where they change (or name)
what is read: `--model` where the model graph is read (`sparql`, `execute`,
`view`, `views`), `--record` where the record is read (`sparql`, `record`);
anywhere else, `ogc views --record` or `ogc record --model` included, they
are a usage error (exit 2).

## The mental model (twelve lines)

1. Terms are used, not owned: each term cites exactly one canonical
   definition, from the highest-ranked source that defines it (1 ISO
   9000:2026, 2 SEVOCAB, 3 NIST AI 700-2, 4 W3C/OMG for binding only;
   reserve sources for single terms; internal sources for the four coinages).
   `ogc term <term>` reads it.
2. Three classes: adopted (used as the source defines it), refined (a typed
   anchor, specializes / corresponds / synonym, keeping the source's word as
   an altLabel), coined (exactly four: DSO, EPO, CAIE, OG-CAIE).
   `ogc list --class coined`. The anchor is also stated in SKOS (sheet 08):
   each term maps to the standard's own concept, a clause node in `src:`
   with its locator (adopted `skos:exactMatch`, specializes
   `skos:broadMatch`, corresponds `skos:closeMatch`, synonym
   `skos:relatedMatch`), and terms relate within the glossary by
   `skos:broader`, `skos:narrower` and `skos:related` (record is broader
   than evaluation record; provider and customer each have two narrower
   terms, evaluation service provider and test item provider, evaluation
   customer and test item customer); every EPO class names its term by
   `ogc:term`. `ogc term <term>` prints broader, narrower, related, matches
   and the EPO classes naming it; the explorer draws them as links.
3. Every canonical citation of an adopted or refined term carries a
   verbatim quote with a status: machine (located in a content-hashed
   snapshot by the tests), human (verified by a named person on a date,
   usually against an ISO screenshot), pending (transcribed; awaiting one),
   cite-only (a citation that carries no quote), authors (the seven
   crosswalk rows: the authors' own definitions as presented at the
   session, so there is nothing to locate). One vocabulary, used
   everywhere: `ogc quote`, `ogc verify`, `ogc steps`, `ogc define --json`.
   In JSON the kind of a citation is always `citation` (canonical, seeAlso,
   crosswalk) and `holder` is the term, step or crosswalk row that carries
   it. A coined term has no citation: `ogc term` and `ogc define` print
   `coined by:` and the tables show `(coined)` in the source column.
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
8. The Popper crosswalk maps seven Popperian elements to standard terms and
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
12. The record of the worked example, the measles evaluation
    (`track/measles-evaluation.ttl`, sheet 10-42), is read by `ogc record`
    (R-47), in four sections: `## the record` (the record's own entity,
    `ev:record`, a `prov:Bundle` every item and agent is a member of, which
    carries the synthetic-case note), then `## items by step` (C1..C6 then
    1..6, each with who made, signed, approved or asserted it and when),
    then `## items without a step` (the requirement, the engagement
    decisions, the trajectory, the consistency check), then `## parties and
    machines`. The step is derived, never asserted (sheet 10-33): no record
    file carries `epo:step`; the tool derives it through the model graph
    (the item's class is realized by an item kind, `ogm:realizes`, produced
    by a step) and loads the model graph with the record for that. Every
    row carries a `synthetic` flag (`tag` column `synthetic` in the text
    listing, the count in the `## the record` header; sheet 10-43): the
    measles evaluation is synthetic throughout. When an item carries no
    attribution or date of its own, who and when are derived through
    `prov:wasGeneratedBy` to the generating activity's agent and end time,
    and the listing says so: `report assembler (queries/coverage.rq) (via
    coverage-computation)`. `ogc record <local-name>` prints everything the
    record says about one item, its derived step in the heading. `--record`
    adds the record to `sparql` (the `ev:` prefix).

## What is loaded

By default: the vocabulary, the EPO steps, the crosswalk, the sources, the
rulings and concerns, the essentials, and the EPO and model shapes, merged
into one graph (named graphs are not exposed; GRAPH, FROM and FROM NAMED are
refused). `--model` adds the canonical model graph, the OMG `sysml:`
rendering of the structure (part, port, interface and action definitions,
the assembly and its wiring), not EPO instances; `view`, `views` and
`execute` load it on their own. `--record` adds the worked example's record
(`track/measles-evaluation.ttl`, the `ev:` namespace) together with the
model graph, through which each item's step is derived (sheet 10-33);
`record` loads both on its own. The record is read by `ogc record` and
`--record` (ruling R-47, which closes concern C-44). Both flags are part of
the printed and hashed args, so a `sparql` answer says which graphs it was
asked over.

The files behind the tool are `vocabulary/og-caie.ttl`, `vocabulary/epo.ttl`,
`vocabulary/crosswalk.ttl`, `sources/sources.ttl`,
`rulings/adjudications.ttl`, `model/trace.ttl`, the four shape files under
`shapes/`, `model/og-caie.model.ttl` and `track/measles-evaluation.ttl`.
Never open these; they are what ogc reads. `ogc doctor` parses every one
of them; `ogc shapes` and `ogc schema` count the shapes over all four
shape files.

## Start here

- `ogc schema`: the counts, the classes and properties in use, the prefixes.
- `ogc find <text>`: what matches, exact then prefix then substring. It
  indexes term labels and quotes and EPO class labels (the classes' and
  roles' `rdfs:label` in `vocabulary/epo.ttl`) and nothing else: not the
  rulings, the concerns, the sources or the record (`ogc rulings --grep`,
  `ogc concerns`, `ogc sources` and `ogc record` search those). A quote hit
  says `via quote:<source>`; an EPO hit says `via epo:<Name>`, its class
  column reads `epo class` or `epo role`, and it is read with `ogc epo`,
  not `ogc term`. `--no-quotes` restricts it to labels (and appears in the
  printed args).
- `ogc epo <class-or-role>`: one EPO class or role by local name, CURIE or
  IRI (`ogc epo StakeholderRepresentation`, `ogc epo
  AuthorizedRepresentativeRole`, `ogc epo accountExecutiveRole`): its
  label (in the EPO the class's `rdfs:label` is its definition), its
  superclasses (a role's types), subclasses and instances, the layer it is
  pinned at (`ogc:pinnedAt`, contract or evaluation), the term it names
  (`ogc:term`) with that term's headword, the disjointness axioms, and the
  node shapes whose targets, property paths or SPARQL bodies mention it. A
  step (`scope`, `need`) is not read here: `ogc quote`, `ogc verify` and
  `ogc steps` read the steps.

## Recipes

| Question | Command |
|---|---|
| What does this word mean here? | `ogc define <term>` (says `resolved via alt:...` when you typed an alternative label; `--json` carries the quote `status`) |
| The whole entry: class, anchor, citations with quotes and status, scope note, binding, rulings, concerns, essentials, crosswalk | `ogc term <term>` |
| The canon behind a term, or behind a step, verbatim | `ogc quote <term>`; `ogc quote scope`, `ogc quote "C1 need"`, `ogc quote need` |
| Is each quote really where its citation says? | `ogc verify <term>`, `ogc verify <source-slug>`, `ogc verify <step>`, `ogc verify --all` (every citation: the terms', the steps' and the crosswalk rows'; summary line; in JSON a `summary`); the first column is `holder` (a term, a step or a crosswalk row), the second `citation` (canonical, seeAlso or crosswalk) |
| Which quotes are pending, or in any one status or state? | `ogc verify --all --status pending` (the quote's tag: machine, human, pending, cite-only, authors); `ogc verify --all --state digest` (where it was located: verified, digest, human, pending, cite-only, authors, NOT FOUND); an empty answer prints `(none)` with exit 0 |
| May I use this word in prose, and how do I mark it up? | `ogc check-word <word> [<word> ...]` (several words at once; quote multi-word ones; registered / alternative / retired; the `{term}` role to write; other terms the word lands on; concerns that mention it; empty words are refused) |
| Every term a source supports, with the quotes | `ogc source <slug>`; the register: `ogc sources --rank 1`, `--posture heldLocally`, `--uncited` (not with `--rank 1`, `2` or `3`: a precedence-ranked source is cited by the terms defined from it, so the two exclude each other, exit 2) |
| The terms by class or by source | `ogc list --class refined`, `ogc list --source sevocab` (an unregistered slug exits 1 with the candidates) |
| Why is it defined this way? | `ogc rulings --term <term>`; a substring over ruling texts, messages as sent and change notes: `ogc rulings --grep conformance`; one ruling, the decision and then the message as sent: `ogc ruling R-16` (`--json` carries `text` and `verbatim`) |
| What was in doubt, and what is still open | `ogc concerns --open`, `ogc concerns --status ruled`, `ogc concerns --severity H`; `ogc concern C-25` (`--open` is `--status open`; with another `--status` the two exclude each other, exit 2) |
| What must a scientific record contain? | `ogc sci`; one essential: `ogc sci SCI-07` |
| Which canon step does each of the twelve steps match? | `ogc steps` |
| What is this EPO class or role, what does it name, what checks it? | `ogc epo StakeholderRepresentation`, `ogc epo EngagementDecision`, `ogc epo ReportApproval`, `ogc epo ConformanceVerdict`, `ogc epo AuthorizedRepresentativeRole` (label, superclasses, pinned at, term and headword, disjoint with, shapes mentioning it; `--json` is one object with `id`, `kind`, `label`, `comment`, `superclasses`, `types`, `subclasses`, `instances`, `pinned_at`, `terms`, `disjoint_with`, `shapes`) |
| What does a shape check, and over what? | `ogc shapes` (every node shape with its target and file, over all four shape files); `ogc shape S3-PlanApproval`, `ogc shape m1-parties`, `ogc shape RulingShape` (target, property constraints, each SPARQL constraint's message and its `sh:select` body, indented; in JSON `sparql` is a list of `message` and `select`, and `message` and `closed` are null when the shape has none) |
| The views of the model: what each brings into focus and leaves out | `ogc views` |
| One view as mermaid, with its perspective (nesting, assemblage, contracting, evaluation) | `ogc view contracting` |
| Execute the process from the model and run the checks over the emitted record; break one or more things | `ogc execute` (ends in `VERDICT: PASS` or `FAIL`, exit 1 on FAIL), `ogc execute --mutate skip-access`, `--mutate` repeated applies them in order, `ogc execute --turtle` |
| Execute with other parameters: how many requirements, criteria per requirement, planned criteria, sessions, populations | `ogc execute --planned 3` (coverage 1.0), `ogc execute --requirements 2 --criteria 2 --planned 4 --sessions 2`; the `parameters:` line and the `params` key say what ran; positive integers, `planned` at most requirements times criteria; capped, because every criterion is probed in every session and the checks are quadratic in that work: requirements times criteria at most 100, sessions at most 20, requirements times criteria times sessions at most 100 (about a minute), populations at most 20; over a cap, exit 1 with the reason and no run. The `VERDICT` line repeats the header's args in its parenthesis |
| What is in the measles record, step by step: who made, signed, approved or asserted each item, and when; which content is synthetic | `ogc record` (`## the record`, then `## items by step` C1..C6 then 1..6, the step derived through the model graph, then `## items without a step`, then `## parties and machines`; who and when derived through the generating activity say `(via <activity>)`; the `tag` column says `synthetic`) |
| Everything the record says about one item, with the objects' labels and what points at it | `ogc record mission-1`, `ogc record attestation-1`, `ogc record annie`, `ogc record record` (local names, case-insensitive; a miss lists candidates) |
| A query over the record | `ogc sparql 'DESCRIBE ev:mission-1' --record`, `ogc --record sparql 'SELECT ?a WHERE { ?a a epo:Attestation }'`; without `--record` a query that names `ev:` or types a variable by a record class (Attestation, Evidence, Session, Report, Determination, Turn and the other item kinds) is refused, exit 1, with the hint on stderr: the record is not loaded by default, so the empty answer would be a lie |
| The model's own vocabulary | `ogc --model sparql 'SELECT ?n WHERE { ?p a sysml:PartDefinition ; sysml:declaredName ?n }'`: without `--model` a query that names `sysml:`, `sysx:`, `elmt:` or `ogm:` (or types a variable by a model class) is refused, exit 1, with the hint on stderr, as the record refusal does; the model graph speaks the OMG `sysml:` vocabulary, names are `sysml:declaredName` (model nodes have no `rdfs:label`), containment is `sysml:owner`, typing is `sysml:specializes` and `sysml:definition`, the nodes are `elmt:` IRIs (`urn:sysmlv2:element:`), tool-specific facts are `sysx:`; `ogc schema --json` does not list them, `ogc --model sparql 'SELECT DISTINCT ?c WHERE { ?x a ?c FILTER(STRSTARTS(STR(?c), "https://www.omg.org/spec/SysML#")) }'` does |
| The anchor table, one row per term | `ogc crosswalk`, `ogc crosswalk --class refined`, `ogc crosswalk --source iso-9000-2026` |
| Popper to the standards and back | `ogc crosswalk --popper` (the seven rows; `--class` and `--source` exclude it, exit 2) |
| Anything else | `ogc sparql '<SELECT ...>'` or `ogc sparql @query.rq` (prefixes injected; read-only; `--model` adds the model graph, `--record` the record; both appear in the printed and hashed args) |
| Is the graph healthy? | `ogc doctor` (VERDICT line; runs in the gate) |

The twelve mutations of `execute`, as `ogc execute --help` lists them:
`skip-assessment`, `skip-approval`, `skip-access`, `unwire-evidence`,
`executive-attests`, `attest-without-determination`,
`requirements-before-agreement`, `engagement-mismatch`,
`skip-report-approval`, `pad-pass-rate`, `one-person-team` (sheet 10-13),
`cherry-pick` (sheet 10-14); the help says what each breaks.
Naming one twice is a usage error (`mutation named twice`, exit 2).

## The `--json` keys

- `execute`: `mutations`, `params`, `conforms`, `fired`, `missing`,
  `coverage` (with `coverage`, `passRate`, `failRate`, `cantTellRate`),
  `traceback`, `ok`, `verdict`; with `--turtle`: `mutations`, `params`,
  `turtle`.
- `define`: `term`, `definition`, `class`, `canonical`, `coined_by`,
  `status`, `resolved`.
- `record`: the listing is `rows`, each with `group` (record, step,
  no-step, party), `step`, `order`, `item`, `iri`, `class`, `label`, `who`,
  `when`, `via`, `synthetic` (`who` and `when` are null when the record
  carries none and nothing can be derived; `via` names the generating
  activity they were derived through, else null; `synthetic` is true where
  the graph tags the item, sheet 10-43); one item is `item`, `iri`,
  `label`, `class`, `step`, `who`, `when`, `via`, `synthetic`, `triples`,
  `referenced_by` (`triples` are
  `predicate`, `object`, `label`; `referenced_by` are `subject`,
  `predicate`, `label`).
- `view`: `name`, `title`, `focus`, `leaves_out`, `mermaid`.
- `term`: the whole entry; its `rulings` are `id` and `label`, the label
  being the resolved concerns' labels or the first words of the ruling.

## What the tool does not read

- The rulings sheets under `rulings/sheets/` are provenance the tool does
  not read: a shape message or a scope note citing "sheet 10-19" points at
  a file, and the tool cannot follow it; open the sheet.
- The works cited per chapter are not in the graph yet (rulings sheet
  10-40, for the authors); `ogc sources` is the source register, not a
  bibliography.

## SPARQL notes

- Term IRIs live in `term:` (`https://w3id.org/og-caie/terms#`), so
  `ogc sparql 'DESCRIBE term:probe'` prints one term's triples; sources
  are `src:`, rulings and concerns `rul:`, steps `epo:`, essentials `tr:`,
  crosswalk rows `xw:`, the model `ogm:` with the OMG `sysml:` vocabulary,
  the record's items `ev:` (`https://w3id.org/og-caie/evaluation/measles#`,
  present only under `--record`; the executor's own emitted record uses
  `ex:` for `evaluation/executed#` and is never loaded). `ogc schema`
  prints the whole prefix list.
- The citation header is re-runnable: `# ogc sparql <query> #sha256:<12
  hex> @ <sha>` carries the query as typed, with newlines escaped as `\n`
  and comments intact (unescape `\n` to run it again), and the sha256 of
  the query text; for `@file` it carries the path as typed and the sha256
  of the file's content. `@` with a directory, or a bare `@`, is a usage
  error. Comments are stripped before the record and model checks, so an
  `ev:` or a `sysml:` inside a comment does not trigger a refusal.
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
