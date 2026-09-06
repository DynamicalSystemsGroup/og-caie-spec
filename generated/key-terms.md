```{glossary}
acceptance criteria
: A specific, checkable condition a response must meet for a requirement to count as satisfied. The unit that coverage is measured over: each criterion either traces to an attested outcome or it does not. Source: IEEE Computer Society, acceptance criteria, p. 4: "criteria that a system or component is required to satisfy to be accepted by a user, customer, or other authorized entity" (machine). Also: acceptance criterion.

appropriateness
: The expert judgment that the declared context (operational environment, requirement set and Domain-Specific Ontology) was the right frame for the judgment being made. Not whether the system passed, and not whether there was enough evidence. Source: Hawkins, Section 3.2 Asserted context, p. 7: "it is being asserted that the context is appropriate for the argument elements to which it applies" (machine). Ruling R-08.

attestation
: The recorded judgment of a named person that links one acceptance criterion to the evidence reviewed and records an outcome, together with the judgments of appropriateness of the declared context and sufficiency of the evidence. Source: ISO/IEC 17000:2020(en) Conformity assessment — Vocabulary and general principles, 7.3: "issue of a statement, based on a decision, that fulfilment of specified requirements has been demonstrated" (human). Also: annotation.

conformance
: The record is correctly constructed: it satisfies every rule the Evaluation Process Ontology's shapes state about how an evaluation must be recorded. A mechanical yes or no, produced by machine. If the record conforms, the process was followed, its data is shaped, its required fields are filled, and coverage can be computed. A special case of conformity: fulfilment of the record-keeping requirements. Source: ISO 9000:2026(en) Quality management — Fundamentals and vocabulary, 3.5.9 conformity, Note 1: "The term "conformance" is synonymous but deprecated." (human). Also: correct construction, correctness by construction. Ruling R-16.

conformity
: Fulfilment of a requirement, in the ISO sense: the system under test conforms to an acceptance criterion when its response fulfils it, as a named person attests. For the machine-checked shape of the record itself, see conformance. Source: ISO 9000:2026(en) Quality management — Fundamentals and vocabulary, 3.5.9: "fulfilment of a requirement" (human). Ruling R-16.

Contextual AI Evaluation
: The evaluation of a deployed AI system against the needs of a specific domain and deployment context, judged by people who know that domain. The class of evaluation this specification is for; OG-CAIE is the way it is performed here. Source: Ontology-Grounded Contextual AI Evaluation, Introduction and Background. Also: CAIE. Ruling R-29.

determination
: The ruling, made on one or more evidence items, that a criterion's expected result was met, was not met, or cannot be told. It is the codomain of evidence, recorded with an EARL outcome of passed, failed or cannot tell, made by machine or by a named person, and it is what an attestation aggregates for a criterion. The paper calls it a judgment. Source: ISO 9000:2026(en) Quality management — Fundamentals and vocabulary, 3.11.1: "activity to find out one or more characteristics and their characteristic values" (human). Also: judgment. Ruling R-20.

Domain-Specific Ontology
: The vocabulary and relations of the problem domain, imported from an existing ontology or supplied by domain experts, that equip one evaluation with the concepts it needs. A domain expert supplies or approves the release used. It changes when the domain changes. Source: Humane Intelligence, Section 1C, DSO (Domain-Specific Ontology). Also: DSO. Ruling R-09.

evaluation
: Systematically determining how far something meets its specified criteria. An OG-CAIE evaluation determines, for a declared requirement set, which criteria the system under test met, and reports coverage and performance separately. Source: IEEE Computer Society, evaluation, p. 155: "systematic determination of the extent to which an entity meets its specified criteria" (machine). Also: AI evaluation.

Evaluation Process Ontology
: The reusable, domain-independent description of how a rigorous evaluation is run: the standard operating procedure whose seven steps, when followed, make a coverage claim checkable. It assumes a Domain-Specific Ontology is in place and does not change across domains. Source: Humane Intelligence, Section 1C, EPO (Evaluation Process Ontology). Also: EPO. Ruling R-09.

evaluation record
: The record of one evaluation, bound by the Evaluation Process Ontology: the DSO release, the requirement set, the test plan, the probes, the sessions and their trajectories, the evidence, the attestations, the report and the recommendations, with who did what and when. The EPO determines what must be present for requirements traceability in both directions and for coverage, and makes all three checkable by machine; a conformant record therefore provides both traceability directions and coverage. Source: ISO 9000:2026(en) Quality management — Fundamentals and vocabulary, 3.8.12 record: "document stating results achieved or providing evidence of activities performed" (human). Also: record, test log. Ruling R-17.

expected results
: What the system under test should observably do if it meets an acceptance criterion under the probe's conditions. Stated on the criterion before testing, so the criterion is defined in terms of evidence a test can collect, and the attestation is a judgment that the actual result did or did not correspond. Source: IEEE Computer Society, expected results, p. 160: "observable predicted behavior of the test item under specified conditions based on its specification or another source" (machine). Also: expected result. Ruling R-12.

objective evidence
: Data that supports the existence or truth of something. Here, what is collected as the basis for a determination: a response at one turn, a session's trajectory, or several of them rolled up over a test suite, as in a robustness battery. Each evidence item bears on one acceptance criterion's expected result and is bound to the test plan it was collected under. Evidence is the domain; the determination made on it, passed, failed or cannot tell, is the codomain. On its own evidence verifies nothing; a determination rules on it and an attestation judges it. Source: ISO 9000:2026(en) Quality management — Fundamentals and vocabulary, 3.8.6: "data supporting the existence or verity of something" (human). Also: evidence. Ruling R-18, R-20.

OG-CAIE
: Contextual AI Evaluation performed with the method this specification sets out: the Evaluation Process Ontology, the same seven steps for every domain, applied with a Domain-Specific Ontology supplied or approved by the domain's experts, leaving a record anyone can check for conformance, traceability and coverage. Source: Ontology-Grounded Contextual AI Evaluation, Introduction and Background. Also: Ontology-Grounded Contextual AI Evaluation. Ruling R-09, R-29.

operational envelope
: The requirements this system under test must meet in this operational environment, with their acceptance criteria and weights, declared before any probe is run. It refines the idea of a requirement by adding specificity: the same system in a different environment, or a different system in the same environment, gets a different envelope. That is what makes the evaluation contextual, and what separates it from a benchmark; the nearest practice is that of safety-critical systems. Coverage is measured over the envelope and only over it. Source: ISO 9000:2026(en) Quality management — Fundamentals and vocabulary, 3.5.1 requirement: "need or expectation that is stated, generally implied or obligatory" (human). Also: requirement set. Ruling R-03, R-14.

operational environment
: The conditions and assumptions about the deployment setting under which acceptable behavior is defined: who uses the system, for what, and what is out of scope. Source: IEEE Computer Society, operational environment, p. 282: "physical context, setting, and circumstances used to support the in-service operation of a system" (machine). Also: operating environment. Ruling R-02.

outcome
: The result recorded for a judgment: passed, failed, cannot tell, inapplicable, or untested. Not binary on purpose. Source: W3C, Section 2.7 OutcomeValue Class: "a value or expression that describes a resulting condition from carrying out the test" (machine).

probe
: A scenario tied to the acceptance criteria it exercises, derived from the Domain-Specific Ontology and checked for consistency before use, applied at one turn of a session. Its run yields one prompt and response pair; the response is the evidence. A test plan may list its probes or choose them by a test strategy as the trajectory unfolds. Source: IEEE Computer Society, test case, p. 432: "set of test inputs, execution conditions, and expected results developed for a particular objective" (machine). Also: prompt, task, test case.

requirement
: Something the system must do, or a condition it must meet, to be fit for its purpose. Broad requirements are decomposed into acceptance criteria that can be checked one at a time. Source: ISO 9000:2026(en) Quality management — Fundamentals and vocabulary, 3.5.1: "need or expectation that is stated, generally implied or obligatory" (human).

requirements traceability
: The documented path linking what was required to how it was tested and what was found, so a coverage claim can be checked by anyone holding the record. Source: IEEE Computer Society, requirements traceability, p. 352: "identification and documentation of the derivation path (upward) and allocation/ flow-down path (downward) of requirements in the requirements set" (machine). Ruling R-15.

session
: One pairing of one tester with one system under test, in which a sequence of turns is run. Sessions are stateful: what the system says at a later turn depends on everything said before, so evidence belongs to its session, not only to its probe. Source: NIST AI 700-2, Appendix A, Session, p. 17: "A single unit of ARIA testing, consisting of a pairing of one tester and one application." (machine). Ruling R-13.

sufficiency
: The expert judgment that the evidence gathered is enough to support the claim being made. A quantity judgment, distinct from appropriateness. A judgment with no evidence cannot record a pass or a fail. Source: Hawkins, Section 3.3 Asserted solution, p. 10: "it is being asserted that the evidence put forward is sufficient to support the claim" (machine). Ruling R-08.

test coverage
: How much of the declared acceptance criteria the evaluation actually reached, as a share weighted by deployment sensitivity. It says how much was evaluated, not how well the system did. Source: IEEE Computer Society, test coverage, p. 433: "degree, expressed as a percentage, to which specified test coverage items have been exercised by a test case or test cases" (machine). Also: coverage. Ruling R-01.

test plan
: The statement, made before any test runs, of what the evaluation will test and how: which acceptance criteria are its objectives, which probes are its means, and what each probe is expected to show. Derived from the requirement set and the Domain-Specific Ontology in step three; every attestation is bound to the plan that produced its evidence. Source: IEEE Computer Society, test plan, p. 437: "detailed description of test objectives to be achieved and the means and schedule for achieving them, organized to coordinate testing activities for some test item or set of test items" (machine). Ruling R-12.

trajectory
: The recorded sequence of prompt and response pairs of a session, in order. The system's internal state is never observed; the trajectory is the observable realization, and plays the role a time series of measurements plays in system identification. A small change early in a trajectory can change everything after it. Source: IEC 60050-351:2013 International Electrotechnical Vocabulary, 351-41-10 trajectory: "representation of the solution x(t) of the state equation as connecting line of the ends of the vector x(t) in state space with time as parameter" (human). Also: history, realization. Ruling R-13.

```
