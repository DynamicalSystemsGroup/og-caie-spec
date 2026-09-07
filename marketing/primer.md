# OG-CAIE Primer

*A working draft, not part of the checked spec. Tracked by open concern
[C-58](../rulings/adjudications.ttl) ("should the marketing-whitepaper
primer become its own page on the site"). Also published as a private
page at https://claude.ai/code/artifact/10eb5116-583c-4e51-9ad1-34e6b8b51e5a
for reading; this file is the editable copy — edit here, not there.*

## What this document is

Not the whitepaper, and not draft copy for it. A shared vocabulary and
process outline for Z and Julie, so the marketing whitepaper for a
business, philanthropy, and public-policy audience starts from words that
mean the same thing to both of you, before either of you drafts a
sentence.

The constraint that makes this non-trivial: the whitepaper cannot
contradict or misrepresent the ontology (per `CLAUDE.md`'s "use terms,
don't own them" and "ask the graph, never grep it" rules), but it also
isn't a scientific publication, so precision can be simplified as long as
it isn't falsified. Everything below was checked against the `ogc`
glossary graph, the SHACL shapes, and the counterexample fixtures — see
Verification at the bottom — not paraphrased from a summary.

## What makes this "scientific" — the readout for coauthors

This is for the two of you to be aligned on, not phrasing to lift
directly into the whitepaper (see the guardrail below). The spec's own
front page grounds "why this counts as science" in Popper's falsifiability
criterion; here is that argument compressed to four moves, each mapped to
where it actually lives in OG-CAIE.

| Popper's idea | Plain reframe | Where it lives in OG-CAIE |
|---|---|---|
| Hypothesis: a claim that could be shown false | What would count as failure, decided *before* testing | Acceptance criteria, inside the operational envelope |
| Auxiliary assumptions: the background held fixed while the test runs | The conditions the test is valid under, written down in two layers | Layer 1: the contract / statement of work. Layer 2: the domain vocabulary (DSO) and operational environment |
| Prediction: what the hypothesis says will happen | The actual test question put to the system | A probe, run in a session |
| Evidence: an accepted result of observation | What the system actually did, recorded as-is | Objective evidence / the session's trajectory |
| Falsifiability + context: the claim could have failed and didn't, and we know which assumptions were in play | A named person rules pass / fail / can't-tell, and the record shows how much was actually tested, and under what frame | Attestation's outcome, test coverage, appropriateness + sufficiency judgments |

The one-line version: *an OG-CAIE evaluation counts as science on the same
terms any experiment does, because it writes down before the test what
would count as failure, records what actually happened, has a named
person rule on it, and leaves a record anyone can use to recompute how
much was actually covered.*

**The thesis that connects this table to everything else here:** Popper's
framing supplies the *definition* of what makes something science — the
five rows above. It doesn't, by itself, make anything checkable.
**Ontology-Grounding is the "OG" doing that work**: it is the mechanism
that takes each of those things — hypothesis, assumptions, prediction,
evidence, falsifiability, context — and defines it as a named class in
the model (largely via the DSO and the EPO, term 3 below), enforces how
they must connect to one another, and leaves a record that can be checked
against that structure by machine. Popper says what science needs;
ontology-grounding is what defines, enforces, and makes verifiable exactly
those things in a given evaluation. That is the single sentence
underneath the whole whitepaper, and it's why "the central distinction"
section below (human judgment vs. the machine check) and the DSO/EPO and
"checked record" terms in the shortlist are not three separate points —
they're the same point, said three ways.

**Guardrail for the whitepaper itself:** `CLAUDE.md` reserves the name
"Popper" and falsifiability's technical vocabulary (hypothesis, auxiliary
assumption, excluded outcome, as formal terms) for the spec's own front
page and conclusion chapter, not the inner chapters. This primer is a
different document, so that rule doesn't technically bind it, but the
same instinct applies for a different reason: this audience did not come
for a philosophy-of-science lesson. Use the *plain reframe* column above
in the whitepaper's actual language (stated in advance, assumptions
declared, evidence gathered, named judgment recorded, coverage counted);
skip naming Popper or "falsifiability" in the marketing text itself. This
table is the coauthors' shared answer to "why do we get to call this
science," not a paragraph to transplant.

## The central distinction: two kinds of checking

The method makes **two different claims**, and conflating them would
misrepresent the work.

1. **Human judgment is still required, and the process says exactly where
   it lands.** A named domain expert judges whether the system met each
   requirement (attestation), and judges whether the requirement set and
   evidence were appropriate and sufficient. The method does not replace
   that judgment with an algorithm.
2. **The record of that judgment is machine-checked**, not for whether
   the judgment was *correct*, but for whether the *process* around it
   was followed: was the verdict backed by evidence collected before it,
   was it signed by a named person, and — critically — did the required
   separation of roles actually hold (the person who ran the test session
   is not the same person who judged its evidence, unless a second,
   independent judgment exists). This is verified against the event
   record itself, not merely declared in a policy document.

Confirmed directly in the shapes (`shapes/epo.shapes.ttl`): `S0-Roles`
rejects a person holding two of {domain expert, evaluation operator,
authorized representative, sponsor signatory} at once; `S0-Independence`
rejects a determination whose signer is the same person who ran the
session the evidence came from, unless someone else also signed off — and
each has a named counterexample on file proving the check catches the
violation (`counterexamples/one-person-team.ttl`,
`counterexamples/operator-determines-alone.ttl`,
`counterexamples/expert-administers-tests.ttl`).

*Plain-language framing for the whitepaper:* "The judgment is always a
named person's — the method never lets a machine decide whether an AI
system is fit for use. What the machine checks is the paperwork around
that judgment: that the right kind of person made it, that they didn't
grade their own test, and that the evidence came before the verdict. That
check is run automatically, and it fails loudly, on purpose, when someone
tries to cut the corner."

## Recommended term shortlist (6 firm terms, 1 candidate below)

Ordered by how load-bearing each is for the "why trust this evaluation"
argument. Each entry gives: the plain-language gloss to use in the
whitepaper, the guardrail that keeps it honest, and the canonical
grounding (for Julie/Z's own reference, not necessarily printed in the
marketing copy).

Keep "ontology" rather than translate it away. Unlike a first instinct,
"ontology" is currently in vogue with this exact audience through AI
thought-leadership writing, so it's a hook, not a barrier, as long as DSO
and EPO stay thin — introduced as the two named ingredients, never
unpacked into the twelve-step process or RDF mechanics.

### 1. Contextual AI Evaluation (CAIE) — the category name

- *Plain gloss:* "Evaluating an AI system against the actual needs of the
  place it will be used, judged by people who know that domain" — not a
  generic benchmark score.
- *Guardrail:* Don't imply this is the only category of eval that exists;
  it's a named class of evaluation, and OG-CAIE is one way to do it
  rigorously.
- *Grounding:* coined term (R-47); the spec's own front page opens with a
  line that already reads almost verbatim as marketing copy.

### 2. OG-CAIE — the branded method

- *Plain gloss:* "CAIE done by a specific, checkable playbook: an agreed
  process, a domain vocabulary supplied by experts, and a record anyone
  can audit afterward."
- *Guardrail:* It's a method name, not a certification mark or legal
  standard (yet) — frame as "an open method," not "the standard."
- *Grounding:* coined term (R-47); README's own line — "an open standards
  activity under development, with a computational implementation
  pathway" — is the project's preferred self-description and is safe to
  reuse close to verbatim.
- *Why "OG" specifically matters (see the thesis above):* the
  Ontology-Grounding is what makes the "scientific" claim more than a
  slogan — it's the mechanism that defines, enforces, and machine-checks
  the things a rigorous evaluation needs. Worth landing this connection
  somewhere in the whitepaper, even briefly.

### 3. The two ingredients: DSO and EPO — kept thin, on purpose

- *Plain gloss:* "Two ingredients make an evaluation an OG-CAIE
  evaluation. A **Domain-Specific Ontology (DSO)**: the vocabulary and
  facts of the world the AI operates in, supplied or approved by real
  experts in that domain. An **Evaluation Process Ontology (EPO)**: the
  same reusable, rigorous procedure for running the evaluation itself,
  regardless of domain. Swap the DSO and the same process works for a
  health chatbot, a lending model, or a hiring tool."
- *Guardrail:* Keep it at that. Don't explain ontology engineering, RDF,
  or the twelve-step process breakdown in the marketing text — "ontology"
  is doing rhetorical work here (it signals rigor to a reader who already
  has some exposure to the word from AI thought-leadership writing), not
  technical work; the whitepaper only needs the reader to know there are
  two named, separable ingredients, one about the domain and one about the
  process.
- *Grounding:* both coined terms (R-47); DSO/EPO are literally the two
  things OG-CAIE is CAIE "performed with," per `CLAUDE.md`'s own coinage
  definition — this pairing is the spec's own structure, simplified, not
  an invention for marketing.

### 4. Independent roles, enforced, not just declared

The separation of domain expert (judges), evaluation operator (tests),
and authorized representative (delivers), across sponsor / tester /
vendor organizations.

- *Plain gloss:* "The person who runs the test never judges it alone, and
  the person who signs the contract doesn't touch the verdict. Where
  possible the tester is independent of the vendor, like an outside
  auditor rather than the vendor grading itself. This isn't a promise on
  paper: the record is checked afterward, and an evaluation where someone
  graded their own test is a check failure, not a style issue."
- *Guardrail:* Independence is declared and checked at a stated level
  (person, team, or organization) — don't claim blanket third-party
  independence as a universal property; the record says what level
  applied to a given evaluation, and the check operates at that level.
- *Grounding:* R-21, R-23, R-49; `docs/contracting.md`'s "nobody
  determines alone on evidence from a session they ran, and nobody
  assesses a requirement set they wrote"; enforced in
  `shapes/epo.shapes.ttl` by `S0-Roles` (one person, one role) and
  `S0-Independence` (the signer of a determination isn't the operator of
  the session it came from, unless a second signer also weighed in) —
  each with a named counterexample proving the check catches the
  violation.

### 5. Attestation — the accountable, named judgment

- *Plain gloss:* "A named expert signs off on each requirement, and
  records two things alongside the verdict: was this the right test for
  the situation, and was there enough evidence to be sure. This is a
  person's call, not a score a machine produces."
- *Guardrail:* An attestation records a person's judgment, not an
  algorithm's score; the process makes that judgment traceable and
  revisable (a later attestation can supersede an earlier one as more
  evidence arrives), not infallible. The method proves the judgment was
  made properly, never that it was made correctly — that stays the named
  expert's responsibility.
- *Grounding:* ISO/IEC 17000 §7.3 + EARL; ruling R-08 (appropriateness +
  sufficiency, not "adequacy").

### 6. A record checked by machine, not taken on faith

The plain-language stand-in for "conformance."

- *Plain gloss:* "After the human judgments are in, a machine checks the
  record itself: was every verdict backed by evidence collected first,
  was it signed by a named person, did the separation of roles hold. It's
  not the machine deciding whether the AI passed — it's proof that the
  process around that human decision was actually followed, so no one has
  to take the write-up on faith."
- *Guardrail:* This is the one term where overclaiming is easiest and
  most damaging — do not let a reader come away thinking the machine
  evaluates the AI system. It evaluates the *record of the evaluation*.
  Keep the technical conformity/conformance pair itself out of the
  marketing text (it's the single riskiest pair for a lay reader, since
  ISO itself deprecates the distinction) and use this plain restatement
  instead.
- *Grounding:* `docs/guarantees.md` ("a run that follows the wiring
  conforms, is complete, has a recomputable coverage and traces fully,
  and each way of departing from the wiring is caught by a named check");
  `conclusion.md`'s own caveat, worth carrying into the whitepaper nearly
  verbatim: "nothing in the record says whether the experts were right;
  that is theirs, and it is recorded with their names."

Deliberately left off the firm shortlist: *trajectory* and *test
strategy* (control-theory borrowings, no marketing value once
translated), the formal *probe*/*session* vocabulary (fine as ordinary
English — "test question," "test run" — not worth teaching as named
terms), and the *conformity*/*conformance* pair itself (superseded above
by term 6).

## Candidate terms — decision deferred to whitepaper-writing time

Terms that are real, correct, and important to the underlying method, but
where whether to surface them to this specific audience is a judgment
call for when you see the actual draft, not one to lock in now. Listed
with pros and cons rather than a recommendation.

### "Cannot tell" as a real, honest outcome

EARL's `cantTell`, alongside passed/failed — the record can say a
question genuinely wasn't settled by the evidence, rather than being
forced to guess pass or fail.

- *Pro:* a genuine differentiator. Most "AI evaluation" claims a reader
  has seen are binary (safe/unsafe, passed/failed); a method that admits
  doubt and requires more testing before it will claim a result is a
  strong, distinctive trust signal, and it's grounded in real EARL
  vocabulary, not invented for the pitch.
- *Con:* Z's read, from experience with this kind of audience, is that
  introducing a third verdict state risks reading as hedging or as an
  unresolved gap, especially without the worked example (the measles
  case) on hand to show it working as intended — resolved, not left
  open. Out of context, "sometimes we can't tell" may cost more trust
  than it buys.
- *Where it's grounded if used later:* EARL outcome vocabulary (passed /
  failed / cantTell); the measles worked example's "enclosed space"
  advice criterion is the concrete illustration (flagged cantTell, then
  resolved by one more targeted test session) — likely only lands well
  paired with that story, which is explicitly out of scope for this pass
  (see below).

### System Under Test, Operating Environment, Operational Envelope

Three more candidates, with a shared wrinkle worth stating as a rule
rather than solving case by case: **the marketing label and the
glossary's formal headword are sometimes different words for the same
term, and the whitepaper should use the friendlier one.** That's not a
deviation from the ontology — in two of these three cases the friendlier
word is itself the ontology's own sanctioned alternative label, not an
invention.

- **System Under Test** — headword is *test item* (SEVOCAB, ISO/IEC/IEEE
  29119-2), but ruling R-19 explicitly keeps "system under test" as the
  alternative label for prose, because the only standards-body definition
  of that exact phrase is a narrow 1999 performance-measurement one; "test
  item" is the family headword (alongside test case, test plan, test
  strategy). *Pro:* reads naturally to anyone who has ever "tested a
  system," no translation needed. *Con:* none of substance — this is
  already the sanctioned prose form, not a marketing coinage. **Use this
  one; it isn't a departure.**
- **Operating Environment** — headword is *operational environment*
  (SEVOCAB, IEEE 982-2024), which itself lists "operating environment" as
  an alternative label. *Pro:* immediately intuitive ("the real-world
  setting the AI runs in"), the way "operating conditions" reads in any
  engineering or business report. *Con:* minor risk of a skimming reader
  half-reading it as "operating system" — avoidable with one full
  sentence of context on first use. **Use this one too; also sanctioned,
  not coined.**
- **Operational Envelope** — this one is different in kind: it's a named
  "house label" (rulings R-03, R-14), not an alternative label already
  sitting on an external standard's term — it broadly matches ISO
  9000:2026's "requirement" but adds the specificity that makes an
  evaluation *contextual* rather than a generic benchmark: the same AI
  system tested in a different environment, or a different system in the
  same environment, gets a different envelope, and coverage is measured
  only over that envelope. *Pro:* this may be the single best
  plain-English argument for why CAIE isn't just a benchmark with an
  ontology attached — borrowed imagery from safety-critical engineering
  ("flight envelope") that already reads as rigorous to a
  policy/business audience. *Con:* say plainly that it's the project's
  own naming convention layered onto a standard concept (the same honesty
  framing as DSO/EPO above), not an external body's term. Given how
  directly it reinforces term 1's claim (CAIE vs. a generic benchmark),
  this is worth considering for promotion to the firm list rather than
  leaving as a candidate.

**General rule to carry forward:** when the ontology gives a term both a
formal headword and one or more alternative labels, check with `ogc term
<name>` which alternatives actually exist before choosing the marketing
word — pick the friendliest *sanctioned* label, never a look-alike phrase
that isn't in the graph, and keep a note of which headword each marketing
term traces back to.

## Simplified process description

Skip the twelve formal steps. Two cycles, described in plain language,
mirror what these readers already recognize from procurement and audits.

**Cycle 1 — the agreement** (what a contract already covers): the
commissioning organization states the need and who could be affected; the
two sides agree what "good" looks like and how it'll be checked; the
vendor grants access to the system. At the end, a report and a
recommendation are delivered, and the commissioning organization accepts
it as fulfilling the agreement.

**Cycle 2 — the evaluation itself, nested inside "do the work"** (what an
audit or test campaign already covers): scope the domain and who's
affected; write down the requirements and how they'll be judged, checked
by a domain expert for fit; plan the tests; run them and collect the
evidence; have a named expert judge each requirement against that
evidence and sign off; assemble a report that is itself checked before it
goes out the door.

Two moments in Cycle 2 are worth calling out by name in the whitepaper,
because they're where "the central distinction" above actually happens in
the process, not just in the abstract:

- **Where judgment lands:** the sign-off step, where a named domain
  expert reviews the evidence and attests an outcome for each requirement
  — this is the one human-judgment moment the whole process builds
  toward.
- **Where the check runs:** report assembly, immediately before delivery,
  where the machine checks that every sign-off was properly evidenced,
  properly attributed, and made by someone who didn't run the test it's
  judging — before the report ever reaches the sponsor.

One-sentence framing to carry into the whitepaper: *"Every evaluation is
wrapped in two familiar cycles — the business agreement on one side, the
actual test campaign on the other — so nothing about 'AI evaluation' asks
a reader to learn a new kind of process, only to see it applied
rigorously to AI, with a named person's judgment at its center and a
machine checking the paperwork around it."*

## Not in scope here (flagged for the next pass)

- The Mala/Annie/Theo (measles chatbot) worked example — good raw
  material for a case study, explicitly synthetic, but outlining/writing
  it is separate work.
- Whitepaper structure, narrative arc, and the adoption/pilot call to
  action. The "what makes this scientific" section above is background
  alignment for the two of you, not draft copy for that narrative.

## Verification

Before locking in copy, spot-check every plain-language gloss above
against the canonical definition with the `ogc` CLI so nothing drifts
into misrepresentation:

```sh
uv run -q ogc term "contextual AI evaluation"
uv run -q ogc term "domain-specific ontology"
uv run -q ogc term "evaluation process ontology"
uv run -q ogc term attestation
uv run -q ogc term conformance
uv run -q ogc term "test item"
uv run -q ogc term "operational environment"
uv run -q ogc term "operational envelope"
uv run -q ogc ruling R-21
uv run -q ogc ruling R-08
uv run -q ogc ruling R-19
```

If a gloss and the canonical definition diverge, tighten the gloss rather
than the term — the whitepaper simplifies, it doesn't redefine.
