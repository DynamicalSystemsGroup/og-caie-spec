# OG-CAIE Primer

*A working draft, not part of the checked spec. Tracked by open concern
[C-58](../rulings/adjudications.ttl) ("should the marketing-whitepaper
primer become its own page on the site"). Also published as a private
page at https://claude.ai/code/artifact/10eb5116-583c-4e51-9ad1-34e6b8b51e5a
for reading; this file is the editable copy — edit here, not there.*

## What this document is

Not the whitepaper, and not draft copy for it. A shared vocabulary and
process outline so the marketing whitepaper for a business, philanthropy,
and public-policy audience starts from words that mean the same thing to
everyone who touches it.

For the person writing the whitepaper: the terms below mean exactly what
they say here. The whitepaper may simplify them, and should, but it may
not redefine them. Everything else, the voice, the structure, the story,
the examples, is yours.

The constraint that makes this non-trivial: the whitepaper cannot
contradict or misrepresent the ontology (per `CLAUDE.md`'s "use terms,
don't own them" and "ask the graph, never grep it" rules), but it also
isn't a scientific publication, so precision can be simplified as long as
it isn't falsified. Everything below was checked against the `ogc`
glossary graph, the SHACL shapes, and the counterexample fixtures — see
Verification at the bottom — not paraphrased from a summary.

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

## Recommended term shortlist (8 firm terms, 3 candidates below)

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
  standard (yet) — frame as "an open method," not "the standard." Write
  it as OG-CAIE; "ontology CAIE" is not a name.
- *Grounding:* coined term (R-47); README's own line — "an open standards
  activity under development, with a computational implementation
  pathway" — is the project's preferred self-description and is safe to
  reuse close to verbatim.
- *Why "OG" specifically matters (see the thesis at the end):* the
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
- *One more sentence the whitepaper needs:* "Filled in with the facts of
  one situation (this outbreak, this county), the DSO becomes the
  reference the system's answers are judged against; a domain expert
  approves it before any test runs." That is the whole story of the
  knowledge graph; the phrase "knowledge graph" may appear as ordinary
  English or not at all.
- *Guardrail:* Keep it at that. Don't explain ontology engineering, RDF,
  graphs, or the twelve-step process breakdown in the marketing text —
  "ontology" is doing rhetorical work here (it signals rigor to a reader
  who already has some exposure to the word from AI thought-leadership
  writing), not technical work; the whitepaper only needs the reader to
  know there are two named, separable ingredients, one about the domain
  and one about the process. The EPO never changes from one evaluation
  to the next; nobody "defines the EPO" for a chatbot. What is written
  for one evaluation is the envelope (term 4).
- *Grounding:* both coined terms (R-47); DSO/EPO are literally the two
  things OG-CAIE is CAIE "performed with," per `CLAUDE.md`'s own coinage
  definition — this pairing is the spec's own structure, simplified, not
  an invention for marketing.

### 4. Operational envelope — what this evaluation promises to test

- *Plain gloss:* "The list of specific, checkable things the system must
  do in this deployment, each weighted by how much it matters, agreed
  before testing starts." Broad rules (requirements) are broken into
  specific checkable conditions (acceptance criteria); each criterion
  carries a weight set by the consequence of getting it wrong, with the
  reason written down. The same system in a different setting, or a
  different system in the same setting, gets a different envelope.
- *Guardrail:* The envelope is declared, judged appropriate by a domain
  expert, and approved by the sponsor before any test runs, weights
  included; it is never adjusted after results come in. It is the
  project's own naming convention layered onto a standard concept (the
  nearest practice is safety-critical engineering, the "flight
  envelope"), not an external body's term; say so if asked. "Acceptance
  criteria" and "weight" are fine as plain words.
- *Grounding:* rulings R-03 and R-14; `ogc term "operational envelope"`,
  `ogc term "acceptance criteria"`, `ogc term "deployment sensitivity"`
  (the weight, refined from SEVOCAB risk-based testing, R-05).

### 5. Independent roles, enforced, not just declared

The separation of domain expert (judges), evaluation operator (tests),
and authorized representative (delivers), all inside the testing
organization, with the sponsor and the system's builder as the other
parties.

- *Plain gloss:* "The person who runs the test never judges it alone, and
  the person who signs the contract doesn't touch the verdict. Where
  possible the tester is independent of the vendor, like an outside
  auditor rather than the vendor grading itself. This isn't a promise on
  paper: the record is checked afterward, and an evaluation where someone
  graded their own test is a check failure, not a style issue."
- *Two more things the whitepaper should say:* before any test runs, the
  operator writes the envelope, a domain expert judges whether it fits
  the situation, and the sponsor signs it; and the people the system
  will affect (residents, commuters) are named and spoken for by a member
  of the team, interviewed where the agreement calls for it. Their needs
  are where the requirements come from, and a record where a population
  nobody speaks for is a check failure.
- *Guardrail:* Independence is declared and checked at a stated level
  (person, team, or organization) — don't claim blanket third-party
  independence as a universal property; the record says what level
  applied to a given evaluation, and the check operates at that level.
- *Grounding:* R-21, R-23, R-49; `docs/contracting.md`'s "nobody
  determines alone on evidence from a session they ran, and nobody
  assesses a requirement set they wrote"; enforced in
  `shapes/epo.shapes.ttl` by `S0-Roles` (one person, one role),
  `S0-Independence` (the signer of a determination isn't the operator of
  the session it came from, unless a second signer also weighed in) and
  `S0-Population` (every affected population spoken for) — each with a
  named counterexample proving the check catches the violation.

### 6. Attestation — the accountable, named judgment

- *Plain gloss:* "A named expert signs off on each requirement, and
  records two things alongside the verdict: was this the right test for
  the situation (appropriate), and was there enough evidence to be sure
  (sufficient). This is a person's call, not a score a machine
  produces." The verdict is pass, fail, or cannot tell; never a number
  against a threshold.
- *Guardrail:* An attestation records a person's judgment, not an
  algorithm's score; the process makes that judgment traceable and
  revisable (a later attestation can supersede an earlier one as more
  evidence arrives), not infallible. The method proves the judgment was
  made properly, never that it was made correctly — that stays the named
  expert's responsibility. The word is "appropriate," never "adequate"
  (the spec retired that word on purpose, R-08). "Annotation" is an
  accepted plain synonym.
- *Grounding:* ISO/IEC 17000 §7.3 + EARL; ruling R-08 (appropriateness +
  sufficiency, not "adequacy").

### 7. A record checked by machine, not taken on faith

The plain-language stand-in for "conformance."

- *Plain gloss:* "After the human judgments are in, a machine checks the
  record itself: was every verdict backed by evidence collected first,
  was it signed by a named person, did the separation of roles hold. It's
  not the machine deciding whether the AI passed — it's proof that the
  process around that human decision was actually followed, so no one has
  to take the write-up on faith. A report is not final until that check
  passes."
- *Guardrail:* This is the one term where overclaiming is easiest and
  most damaging — do not let a reader come away thinking the machine
  evaluates the AI system. It evaluates the *record of the evaluation*.
  Keep the technical conformity/conformance pair itself out of the
  marketing text (it's the single riskiest pair for a lay reader, since
  ISO itself deprecates the distinction) and use this plain restatement
  instead. Call it "checked by machine"; never "validated" or "verified"
  (see the don't-say list).
- *Grounding:* `docs/guarantees.md` ("a run that follows the wiring
  conforms, is complete, has a recomputable coverage and traces fully,
  and each way of departing from the wiring is caught by a named check");
  `conclusion.md`'s own caveat, worth carrying into the whitepaper nearly
  verbatim: "nothing in the record says whether the experts were right;
  that is theirs, and it is recorded with their names."

### 8. Coverage and performance — the two numbers a report gives

- *Plain gloss:* "**Coverage** is how much of the envelope was actually
  judged: the share of the criteria, weighted by how much each matters,
  that a named expert ruled on. **Performance** is how the system did on
  what was judged: the share that passed, failed, or could not be told.
  The two are always reported side by side and never combined, because
  combining them would hide a system that passed everything it was asked
  while most of the envelope went untested."
- *What makes coverage a strong claim:* it is counted over the record,
  not estimated, so anyone holding the record recomputes the same
  number. A finished evaluation always covers 100% of its envelope (a
  report isn't final until every criterion has been judged), so the
  percentage alone says nothing and the report has to say what it is
  100% *of*. "100% of questions about measles" and "100% of questions
  about all communicable diseases" are different claims and are not
  comparable. That is the exaggerated-claims problem, closed by
  construction.
- *Guardrail:* Coverage under 100% belongs only to a draft, where it
  says what is left to test and where the weights say the next effort
  should go. Two evaluations are comparable only when they share an
  envelope; don't say "statistically comparable," nothing statistical is
  claimed. Don't describe a pass threshold: a criterion with several
  judgments is failed if any judgment failed, and the evaluation's
  verdict is the expert's recommendation (see "How it ends" below).
- *Grounding:* `ogc term "test coverage"` (SEVOCAB 29119-2, R-01: counts
  criteria with an attested outcome), `ogc term performance` (ISO 9000
  3.7.3), essentials SCI-07 (coverage recomputable) and SCI-08 (coverage
  and performance kept apart); `queries/coverage.rq`.

Deliberately left off the firm shortlist: *trajectory* and *test
strategy* (control-theory borrowings, no marketing value once
translated), the formal *probe*/*session* vocabulary (fine as ordinary
English — "test question," "test run" — not worth teaching as named
terms), *knowledge graph* (one sentence under term 3 is the whole
story), *verification*/*validation* (the split is already said in plain
words under terms 6 and 7; the words themselves stay off the page), and
the *conformity*/*conformance* pair itself (superseded above by term 7).

## Don't say / say instead

Six word swaps. Each one, as written in the current draft, contradicts
the spec; each fix is a single word.

| Don't say | Say instead | Why |
|---|---|---|
| "the ontology CAIE methodology" | OG-CAIE | that is the method's name; the other is not a name |
| "adequacy," "adequate" | appropriate, appropriateness | the spec retired "adequacy" (R-08) |
| "validation," "validated," "verified" for the machine check | checked by machine | those words are reserved for other things in the spec (R-16); "verified" is not what experts do either, they approve or attest |
| "conformity" for a machine check | checked against | in the spec, conformity is a person's judgment that the system met a requirement |
| "define the EPO," "this EPO," "the organization defining the EPO" | the envelope | the EPO never changes; what is written per evaluation is the envelope |
| "statistically comparable" | comparable (when they share an envelope) | comparability comes from a shared envelope; nothing statistical is claimed |

Words already in the draft that are fine as they are: system under test,
SUT, operating environment, knowledge graph, source of truth, scenario,
deployment sensitivity, annotation, red teaming, coverage, performance,
guardrail.

## Don't claim yet

The spec defers three things to its next version, and the whitepaper
should not promise them: confidence intervals or uncertainty on pass
rates; a minimum pass rate or any threshold that turns judgments into a
verdict; and a final report that carries criteria nobody reviewed. (That
last one is an open concern for Z; if it is ruled in, a final report may
carry named untested criteria with reasons, and the recommendation may
not say "fit to deploy" over one.)

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
  unresolved gap, especially without a worked example on hand to show it
  working as intended — resolved, not left open. Out of context,
  "sometimes we can't tell" may cost more trust than it buys.
- *If used:* it is a ruling on evidence that did not settle the
  question. It never means "nobody looked"; a criterion nobody reviewed
  has no verdict at all and keeps the report a draft. The story that
  lands it: one criterion could not be told from the first
  conversations, a few targeted follow-ups settled it, and the later
  judgment is recorded as replacing the earlier one.
- *Where it's grounded:* EARL outcome vocabulary (passed / failed /
  cantTell); the spec's measles record has exactly this beat.

### System Under Test, Operating Environment

Two more candidates, with a shared wrinkle worth stating as a rule
rather than solving case by case: **the marketing label and the
glossary's formal headword are sometimes different words for the same
term, and the whitepaper should use the friendlier one.** In both of
these cases the friendlier word is itself the ontology's own sanctioned
alternative label, not an invention.

- **System Under Test** — headword is *test item* (SEVOCAB, ISO/IEC/IEEE
  29119-2), but ruling R-19 explicitly keeps "system under test" (and
  "SUT") as the alternative label for prose, because the only
  standards-body definition of that exact phrase is a narrow 1999
  performance-measurement one; "test item" is the family headword
  (alongside test case, test plan, test strategy). *Pro:* reads naturally
  to anyone who has ever "tested a system," no translation needed.
  *Con:* none of substance — this is already the sanctioned prose form,
  not a marketing coinage. **Use this one; it isn't a departure.** Write
  it unhyphenated.
- **Operating Environment** — headword is *operational environment*
  (SEVOCAB, IEEE 982-2024), which itself lists "operating environment" as
  an alternative label. *Pro:* immediately intuitive ("the real-world
  setting the AI runs in"), the way "operating conditions" reads in any
  engineering or business report. *Con:* minor risk of a skimming reader
  half-reading it as "operating system" — avoidable with one full
  sentence of context on first use. **Use this one too; also sanctioned,
  not coined.**

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
organization that built the system, sometimes the sponsor itself and
sometimes a vendor, opens it up for testing. At the end, a report and a
recommendation are delivered, and the commissioning organization accepts
it as fulfilling the agreement.

**Cycle 2 — the evaluation itself, nested inside "do the work"** (what an
audit or test campaign already covers): scope the domain, name the
people the system will affect and have a team member speak for each, and
have a domain expert approve the domain vocabulary; write down the
envelope (the requirements, their criteria, their weights), judged for
fit by a domain expert and signed by the sponsor; plan the tests, the
test questions generated by machine from the domain facts and the
envelope, checked for consistency, the plan approved by a domain expert;
run them and collect the evidence; have a named expert judge each
criterion against that evidence and sign off; assemble a report that is
itself checked before it goes out the door.

Three moments in Cycle 2 are worth calling out by name in the whitepaper,
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
- **How it ends:** the machine check passes, coverage and performance
  are computed, and the report is either a draft with its gaps flagged or
  a final, approved by a domain expert. The evaluation's verdict is a
  named expert's recommendation: fit to deploy, fit with conditions, or
  not fit, with the conditions or the fix named. "Fit to deploy" is off
  the table if any criterion failed. There is no score threshold; a
  person decides, and says why.

One-sentence framing to carry into the whitepaper: *"Every evaluation is
wrapped in two familiar cycles — the business agreement on one side, the
actual test campaign on the other — so nothing about 'AI evaluation' asks
a reader to learn a new kind of process, only to see it applied
rigorously to AI, with a named person's judgment at its center and a
machine checking the paperwork around it."*

## Not in scope here

- The worked example. The whitepaper's example should be invented on the
  measles-chatbot premise, not retold from the spec's record; the guidance
  for its shape lives in the draft's comments. The spec's own case
  (`docs/evaluation.md`) is there to check a beat against, not to copy.
- Whitepaper structure, narrative arc, and the adoption/pilot call to
  action.

## For the coauthors: what makes this "scientific"

This is for Julie and Z to be aligned on, not phrasing to lift directly
into the whitepaper (see the guardrail below). The spec's own front page
grounds "why this counts as science" in Popper's falsifiability
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
the model (largely via the DSO and the EPO, term 3 above), enforces how
they must connect to one another, and leaves a record that can be checked
against that structure by machine. Popper says what science needs;
ontology-grounding is what defines, enforces, and makes verifiable exactly
those things in a given evaluation. That is the single sentence
underneath the whole whitepaper, and it's why "the central distinction"
section (human judgment vs. the machine check) and the DSO/EPO and
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
skip naming Popper or "falsifiability" in the marketing text itself. "The
first step of the scientific method: say what you are testing" is fine
as a colloquial hook. This table is the coauthors' shared answer to "why
do we get to call this science," not a paragraph to transplant.

## Verification

Before locking in copy, spot-check every plain-language gloss above
against the canonical definition with the `ogc` CLI so nothing drifts
into misrepresentation:

```sh
uv run -q ogc term "contextual AI evaluation"
uv run -q ogc term "domain-specific ontology"
uv run -q ogc term "evaluation process ontology"
uv run -q ogc term "operational envelope"
uv run -q ogc term "acceptance criteria"
uv run -q ogc term "deployment sensitivity"
uv run -q ogc term attestation
uv run -q ogc term conformance
uv run -q ogc term "test coverage"
uv run -q ogc term performance
uv run -q ogc term recommendation
uv run -q ogc term "test item"
uv run -q ogc term "operational environment"
uv run -q ogc check-word adequacy
uv run -q ogc check-word validation
uv run -q ogc ruling R-21
uv run -q ogc ruling R-08
uv run -q ogc ruling R-16
uv run -q ogc ruling R-19
uv run -q ogc concern C-57
```

If a gloss and the canonical definition diverge, tighten the gloss rather
than the term — the whitepaper simplifies, it doesn't redefine.
