```{glossary}
acceptance criteria
: A specific, checkable condition a response must meet for a requirement to count as satisfied. The unit that coverage is measured over: each criterion either traces to an attested outcome or it does not. Source: IEEE Computer Society, acceptance criteria, p. 4: "criteria that a system or component is required to satisfy to be accepted by a user, customer, or other authorized entity". Also: acceptance criterion.

appropriateness
: The expert judgment that the declared context (operational environment, requirement set and Domain-Specific Ontology) was the right frame for the judgment being made. Not whether the system passed, and not whether there was enough evidence. Source: Hawkins, Section 3.2 Asserted context, p. 7: "it is being asserted that the context is appropriate for the argument elements to which it applies". Ruling R-08.

attestation
: The recorded judgment of a named person that links one acceptance criterion to the evidence reviewed and records an outcome, together with the judgments of appropriateness of the declared context and sufficiency of the evidence. Source: ISO/IEC 17000:2020(en) Conformity assessment — Vocabulary and general principles, 7.3: "issue of a statement, based on a decision, that fulfilment of specified requirements has been demonstrated". Also: annotation.

conformance
: The record is correctly constructed: it satisfies every rule the Evaluation Process Ontology's shapes state about how an evaluation must be recorded. A mechanical yes or no, produced by machine. If the record conforms, the process was followed, its data is shaped, its required fields are filled, and coverage can be computed. A special case of conformity: fulfilment of the record-keeping requirements. Source: ISO 9000:2026(en) Quality management — Fundamentals and vocabulary, 3.5.9 conformity, Note 1: "The term "conformance" is synonymous but deprecated.". Also: correct construction, correctness by construction. Ruling R-16.

conformity
: Fulfilment of a requirement, in the ISO sense: the system under test conforms to an acceptance criterion when its response fulfils it, as a named person attests. For the machine-checked shape of the record itself, see conformance. Source: ISO 9000:2026(en) Quality management — Fundamentals and vocabulary, 3.5.9: "fulfilment of a requirement". Ruling R-16.

Contextual AI Evaluation
: The evaluation of a deployed AI system against the needs of a specific domain and deployment context, judged by people who know that domain. The class of evaluation this specification is for; OG-CAIE is the way it is performed here. Coined by the authors for this specification; it cites no source. Also: CAIE. Ruling R-29.

contract
: The binding agreement between the sponsor organization and the testing organization to perform OG-CAIE as a service. It is signed by the sponsor and by the testing organization's authorized representative, precedes the requirement set and follows the mission, the need and the proposal in the record. Source: ISO 9000:2026(en) Quality management — Fundamentals and vocabulary, 3.3.13: "binding agreement". Also: agreement, service agreement. Ruling R-21.

customer
: A person or organization that receives a product or a service. Two products change hands around an OG-CAIE evaluation, so there are two customers: the evaluation customer, the sponsor, receives the evaluation as a service; the test item customer receives the AI system under test, as the sponsor sometimes does and as the affected populations do when they use it. The two may be the same organization, and the record says whether they are. Source: ISO 9000:2026(en) Quality management — Fundamentals and vocabulary, 3.9.1: "person or organization that can or does receive a product or a service that is intended for or required by this person or organization". Ruling R-21.

determination
: The ruling, made on one or more evidence items, that a criterion's expected result was met, was not met, or cannot be told. It is the ruling made on evidence, recorded with an EARL outcome of passed, failed or cannot tell, made by machine or by a named person, and it is what an attestation aggregates for a criterion. Source: ISO 9000:2026(en) Quality management — Fundamentals and vocabulary, 3.11.1: "activity to find out one or more characteristics and their characteristic values". Also: judgment. Ruling R-20.

dialogue
: The ordered prompts to, and responses by, the system under test within one session. Its recorded form is the trajectory. Source: NIST AI 700-2, Appendix A, Dialogue, p. 16 (first sentence of the entry): "A set of prompts to, and responses by, an application.". Also: conversation. Ruling R-13.

Domain-Specific Ontology
: The vocabulary and relations of the problem domain, imported from an existing ontology or supplied by domain experts, that equip one evaluation with the concepts it needs. A domain expert supplies or approves the release used. It changes when the domain changes. Coined by the authors for this specification; it cites no source. Also: DSO. Ruling R-09.

evaluation
: Systematically determining how far something meets its specified criteria. An OG-CAIE evaluation determines, for a declared requirement set, which criteria the system under test met, and reports coverage and performance separately. Source: IEEE Computer Society, evaluation, p. 155: "systematic determination of the extent to which an entity meets its specified criteria". Also: AI evaluation.

evaluation operator
: The technical expert who operates the evaluation: declares the requirement set with the sponsor, writes the test plan, administers the probes to the test item, collects the responses and the evidence per the plan, and drafts the report and the recommendation. The operator makes determinations but does not attest; attestation belongs to the domain expert. An abstract actor category, filled by a named person in each evaluation. Source: IEEE Computer Society, operator, p. 283 (ISO/IEC/IEEE 12207:2026, 3.1.40): "entity that performs the operation of a system". Also: AI evaluation expert, operator, red teamer. Ruling R-23.

Evaluation Process Ontology
: The reusable, domain-independent description of how a rigorous evaluation is run: the standard operating procedure whose six steps, performed inside the contracting lifecycle, make a coverage claim checkable when followed. It assumes a Domain-Specific Ontology is in place and does not change across domains. Coined by the authors for this specification; it cites no source. Also: EPO. Ruling R-09, R-31.

evaluation record
: The record of one evaluation, bound by the Evaluation Process Ontology: the DSO release, the requirement set, the test plan, the probes, the sessions and their trajectories, the evidence, the attestations, the report and the recommendations, with who did what and when. The EPO determines what must be present for requirements traceability in both directions and for coverage, and makes all three checkable by machine; a conformant record therefore provides both traceability directions and coverage. Source: ISO 9000:2026(en) Quality management — Fundamentals and vocabulary, 3.8.12 record: "document stating results achieved or providing evidence of activities performed". Also: record (ISO 9000:2026 3.8.12, of one evaluation), test log. Ruling R-17.

expected results
: What the system under test should observably do if it meets an acceptance criterion under the probe's conditions. Stated on the criterion before testing, so the criterion is defined in terms of evidence a test can collect, and the attestation is a judgment that the actual result did or did not correspond. Source: IEEE Computer Society, expected results, p. 160: "observable predicted behavior of the test item under specified conditions based on its specification or another source". Also: expected result. Ruling R-12.

first-party conformity assessment activity
: Evaluation performed by the organization that provides or is accountable for the test item: the test item provider. In OG-CAIE the test item provider is a party to every evaluation, since it grants access to the test item, but it does not perform the evaluation unless it is also the sponsor and the testing organization, and the record says so. Source: ISO/IEC 17000:2020(en) Conformity assessment — Vocabulary and general principles, 4.3 first-party conformity assessment activity: "conformity assessment activity that is performed by the person or organization that provides or that is the object of conformity assessment". Also: first party. Ruling R-21.

guardrail
: A requirement on the system stating what may be shared with a user and what must be withheld. Recommendations at the end of an evaluation typically propose changes to guardrails. Source: NIST AI 700-2, Appendix A, Guardrail, p. 17 (first sentence of the entry): "An application requirement specifying both 1) permitted information that can be shared with a user, and 2) prohibited information that should be withheld from a user.".

measurement uncertainty
: A non-negative number that says how dispersed the values attributed to a measured quantity are. A probe pass rate estimated from replicate sessions carries one; coverage, counted exactly over the record, does not. Source: JCGM 200:2012 International vocabulary of metrology, 2.26 measurement uncertainty, p. 41: "non-negative parameter characterizing the dispersion of the quantity values being attributed to a measurand, based on the information used". Also: uncertainty. Ruling R-13.

mission
: The sponsor organization's purpose for existing, as its top management expresses it, and with it the obligations and duties it holds towards the affected populations. Recorded before the need is stated, it is the context the contract answers to: what the sponsor owes the people the test item will serve. Pinned at the contract. Source: ISO 9000:2026(en) Quality management — Fundamentals and vocabulary, 3.4.11: "organization's purpose for existing as expressed by top management". Also: mandate, obligations to the affected populations. Ruling R-37.

monitoring
: Determining the status of a system at different stages or times. After an evaluation, a sponsor may require the test item provider to change the system per the findings and then require new testing to certify that the flagged issues were addressed; in conformity assessment that repeat is called surveillance. Observed in practice; not a step of the contracting lifecycle. Source: ISO 9000:2026(en) Quality management — Fundamentals and vocabulary, 3.11.3: "determining the status of a system, a process or an activity". Also: re-evaluation, surveillance (ISO/IEC 17000 8.1). Ruling R-36.

non-deterministic system
: A system that, given the same inputs and starting state, will not always produce the same outputs. The system under test is one, which is why a single probe is weak evidence and why pass rates are estimated over replicate sessions. Source: IEEE Computer Society, non-deterministic system, p. 272 (ISO/IEC TR 29119-11:2020, testing of AI-based systems): "system which, given a particular set of inputs and starting state, will not always produce the same set of outputs and final state". Also: nondeterministic system. Ruling R-13.

objective evidence
: Data that supports the existence or truth of something. Here, what is collected as the basis for a determination: a response at one turn, a session's trajectory, or several of them rolled up over a test suite, as in a robustness battery. Each evidence item bears on one acceptance criterion's expected result and is bound to the test plan it was collected under. Evidence is the domain; the determination made on it, passed, failed or cannot tell, is the codomain. On its own evidence verifies nothing; a determination rules on it and an attestation judges it. Source: ISO 9000:2026(en) Quality management — Fundamentals and vocabulary, 3.8.6: "data supporting the existence or verity of something". Also: evidence. Ruling R-18, R-20.

OG-CAIE
: Contextual AI Evaluation performed with the method this specification sets out: the Evaluation Process Ontology, the same six steps for every domain inside a contracting lifecycle, applied with a Domain-Specific Ontology supplied or approved by the domain's experts, leaving a record anyone can check for conformance, traceability and coverage. Coined by the authors for this specification; it cites no source. Also: Ontology-Grounded Contextual AI Evaluation. Ruling R-09, R-29.

operational envelope
: The requirements this system under test must meet in this operational environment, with their acceptance criteria and weights, declared before any probe is run. It refines the idea of a requirement by adding specificity: the same system in a different environment, or a different system in the same environment, gets a different envelope. That is what makes the evaluation contextual, and what separates it from a benchmark; the nearest practice is that of safety-critical systems. Coverage is measured over the envelope and only over it. Source: ISO 9000:2026(en) Quality management — Fundamentals and vocabulary, 3.5.1 requirement: "need or expectation that is stated, generally implied or obligatory". Also: requirement set. Ruling R-03, R-14.

operational environment
: The conditions and assumptions about the deployment setting under which acceptable behavior is defined: who uses the system, for what, and what is out of scope. Source: IEEE Computer Society, operational environment, p. 282: "physical context, setting, and circumstances used to support the in-service operation of a system". Also: operating environment. Ruling R-02.

outcome
: The result recorded for a judgment: passed, failed or cannot tell, the three EARL values the record uses (EARL also allows inapplicable and untested). Not binary on purpose. Source: IEEE Computer Society, test result, p. 438: "indication of whether a specific test case has passed or failed, i.e. if the actual results correspond to the expected results or if deviations were observed".

performance
: A measurable result. Here: how the system did on what was exercised, reported as the pass, fail and cannot-tell fractions of the covered criteria. Never merged with coverage. Source: ISO 9000:2026(en) Quality management — Fundamentals and vocabulary, 3.7.3: "measurable result".

probe
: A scenario tied to the acceptance criteria it exercises, derived from the Domain-Specific Ontology and checked for consistency before use, applied at one turn of a session. Its run yields one prompt and response pair; the response collected is evidence bearing on those criteria. A test plan may list its probes or choose them by a test strategy as the trajectory unfolds. Source: IEEE Computer Society, test case, p. 432 (fragment of the entry): "set of test inputs, execution conditions, and expected results developed for a particular objective". Also: prompt, task, test case (SEVOCAB, tied to criteria).

provider
: An organization that provides a product or a service. Two products change hands around an OG-CAIE evaluation, so there are two providers: the evaluation service provider, the testing organization, provides the evaluation as a service; the test item provider provides, and is accountable for, the AI system under test. They are different organizations when the evaluation is independent, and the record states that fact rather than assuming it. Source: ISO 9000:2026(en) Quality management — Fundamentals and vocabulary, 3.1.9: "organization that provides a product or a service". Also: contractor, supplier. Ruling R-21.

record
: A document stating results achieved or giving evidence of activities performed: any document that records what was done or what was found, in the most general sense the standard gives the word. The evaluation record is its special case here, the record of one evaluation; the DSO release, the test plan and the report are records too, each in its own right. Source: ISO 9000:2026(en) Quality management — Fundamentals and vocabulary, 3.8.12: "document stating results achieved or providing evidence of activities performed". Ruling R-48.

red teaming
: A testing level in which human testers probe the system adversarially to see whether it stays within its guardrails. One way to run the probes in step four. Source: NIST AI 700-2, Appendix A, Red teaming, p. 17: "Testing level which evaluates whether applications adhere to guardrails in response to adversarial prompting or stress testing by human testers.".

repeatability
: How closely results agree when the same measurement is repeated under the same conditions: same system version, same procedure, same operator or policy, same session protocol, over a short period. Replicate sessions under repeatability conditions are what turn a probe into a pass rate. Source: JCGM 200:2012 International vocabulary of metrology, 2.21 measurement repeatability, p. 40: "measurement precision under a set of repeatability conditions of measurement". Ruling R-13.

reproducibility
: How closely results agree when the measurement is repeated under changed conditions: different operators, different sessions, a different evaluation team. Two evaluations that share a requirement set and a DSO release are comparable to the extent their results reproduce. Source: JCGM 200:2012 International vocabulary of metrology, 2.25 measurement reproducibility, p. 41: "measurement precision under reproducibility conditions of measurement". Ruling R-13.

requirement
: Something the system must do, or a condition it must meet, to be fit for its purpose. Broad requirements are decomposed into acceptance criteria that can be checked one at a time. Source: ISO 9000:2026(en) Quality management — Fundamentals and vocabulary, 3.5.1: "need or expectation that is stated, generally implied or obligatory".

requirements traceability
: The documented path linking what was required to how it was tested and what was found, so a coverage claim can be checked by anyone holding the record. Source: IEEE Computer Society, requirements traceability, p. 352: "identification and documentation of the derivation path (upward) and allocation/ flow-down path (downward) of requirements in the requirements set". Ruling R-15.

risk-based testing
: Testing in which what is tested, and how much, is chosen according to analyzed risk. Deployment sensitivity is the weight that makes coverage reflect consequence. Source: IEEE Computer Society, risk-based testing, p. 362: "testing in which the management, selection, prioritization, and use of testing activities and resources are consciously based on corresponding types and levels of analyzed risk".

scenario
: A step-by-step description of a situation the system is put through: the user, their circumstances, and what they ask. A scenario becomes a probe once it is tied to the criteria it exercises. Source: IEEE Computer Society, scenario, p. 369: "step-by-step description of a series of events that occur concurrently or sequentially".

second-party conformity assessment activity
: Evaluation performed by, or on behalf of, an organization with a user interest in the test item: a purchaser, a regulator, a deploying agency. A sponsor that is not the test item provider commissions the evaluation in this position. Source: ISO/IEC 17000:2020(en) Conformity assessment — Vocabulary and general principles, 4.4 second-party conformity assessment activity: "conformity assessment activity that is performed by a person or organization that has a user interest in the object of conformity assessment". Also: second party. Ruling R-21.

session
: One pairing of one tester with one system under test, in which a sequence of turns is run. Sessions are stateful: what the system says at a later turn depends on everything said before, so evidence belongs to its session, not only to its probe. Source: NIST AI 700-2, Appendix A, Session, p. 17 (first sentence of the entry): "A single unit of ARIA testing, consisting of a pairing of one tester and one application.". Ruling R-13.

stakeholder
: A person or organization that can affect, be affected by, or believe itself affected by a decision or activity. The parties (the sponsor, the testing organization, the test item provider), the people who act for them, and the affected populations are the stakeholders named in this specification; customers and providers are kinds of interested party in the standard's own examples. Source: ISO 9000:2026(en) Quality management — Fundamentals and vocabulary, 3.1.4: "person or organization that can affect, be affected by, or perceive itself to be affected by a decision or activity". Also: interested party.

statement of work
: The sponsor's decisions about the work to be performed under the contract; here, for each affected population, whether it is interviewed, with its stakeholder needs documented as input, or represented by the domain expert. A scope-of-work judgment: representation is the common case, interviews are reserved for underrepresented stakeholders or underdocumented needs because of the effort they cost. Decided with the agreement, pinned at the contract, consumed by the scope step, and traceable either way. Source: IEEE Computer Society, statement of work, p. 406: "statement of the expected outcomes and outline of the work required to achieve the outcomes". Also: SOW, scope of work. Ruling R-40.

sufficiency
: The expert judgment that the evidence gathered is enough to support the claim being made. A quantity judgment, distinct from appropriateness. A judgment with no evidence cannot record a pass or a fail. Source: Hawkins, Section 3.3 Asserted solution, p. 10: "it is being asserted that the evidence put forward is sufficient to support the claim". Ruling R-08.

technical expert
: A person who provides specific knowledge or expertise to the evaluation team. Two kinds sit on the team. The domain expert is expert in the Domain-Specific Ontology: they supply or approve its release, attest that it is appropriate for the case being evaluated (this system under test, these requirements, this operational environment), and may be consulted on interpreting evidence. The evaluation operator is expert in performing the tests the Evaluation Process Ontology specifies, conditioned on the DSO, and in assembling the evidence. Source: ISO 9000:2026(en) Quality management — Fundamentals and vocabulary, 3.12.9: "person who provides specific knowledge or expertise to the audit team". Also: domain expert, subject matter expert. Ruling R-10.

test coverage
: How much of the declared acceptance criteria the evaluation actually reached, as a share weighted by deployment sensitivity. It says how much was evaluated, not how well the system did. Source: IEEE Computer Society, test coverage, p. 433: "degree, expressed as a percentage, to which specified test coverage items have been exercised by a test case or test cases". Also: coverage. Ruling R-01.

test item
: The deployed AI system being evaluated, taken as a black box: only what it is given and what it produces are recorded. The prose calls it the system under test; the standard headword is test item. Source: IEEE Computer Society, test item, p. 435 (ISO/IEC/IEEE 29119-2:2021): "work product to be tested". Also: SUT, application, system of interest, system under test, test object. Ruling R-19.

test plan
: The statement, made before any test runs, of what the evaluation will test and how: which acceptance criteria are its objectives, which probes are its means, and what each probe is expected to show. Derived from the requirement set and the Domain-Specific Ontology in step three; every attestation is bound to the plan that produced its evidence. Source: IEEE Computer Society, test plan, p. 437: "detailed description of test objectives to be achieved and the means and schedule for achieving them, organized to coordinate testing activities for some test item or set of test items". Ruling R-12.

test strategy
: The part of a test plan that decides which probe comes next from the trajectory so far, grounded in the Domain-Specific Ontology, rather than listing probes in advance. It closes a loop: the system's outputs feed back into the choice of the next input. A human red teamer following their own judgment is one such strategy; a written policy is another. Source: IEEE Computer Society, test strategy, p. 439: "part of the test plan that describes the approach to testing for a specific project, test level, or test type". Also: semantic state feedback, state feedback policy, strategy. Ruling R-13.

test suite
: A set of sessions run together, for example replicate sessions of one strategy, or the varied sessions of a sensitivity test or robustness battery. Evidence rolled up over a suite is evidence at the third level, above probe and session. Source: IEEE Computer Society, test suite, p. 439: "set of test cases or test procedures". Also: battery, robustness battery. Ruling R-18.

third-party conformity assessment activity
: Evaluation performed by an organization independent of the provider of the test item and with no user interest in it, and not on behalf of anyone who has one. Independence of the testing organization from the test item provider is what makes an OG-CAIE result independent; the record states it as a fact about the parties rather than assuming it, and states separately whether the sponsor has a user interest. Source: ISO/IEC 17000:2020(en) Conformity assessment — Vocabulary and general principles, 4.5 third-party conformity assessment activity: "conformity assessment activity that is performed by a person or organization that is independent of the provider of the object of conformity assessment and has no user interest in the object". Also: independent testing, third party. Ruling R-21.

trajectory
: The recorded sequence of prompt and response pairs of a session, in order. The system's internal state is never observed; the trajectory is the observable realization, and plays the role a time series of measurements plays in system identification. A small change early in a trajectory can change everything after it. Source: IEC 60050-351:2013 International Electrotechnical Vocabulary, 351-41-10 trajectory: "representation of the solution x(t) of the state equation as connecting line of the ends of the vector x(t) in state space with time as parameter". Also: history, realization. Ruling R-13.

verification
: Confirming with objective evidence that specified requirements were fulfilled. Applied to the evaluation itself: did it exercise what it declared, and was its declared process followed. Both are mechanical checks over the record. Source: ISO 9000:2026(en) Quality management — Fundamentals and vocabulary, 3.11.12: "confirmation, through the provision of objective evidence, that specified requirements have been fulfilled".

```

SEVOCAB definitions: Copyright © 2021 IEEE. Used by permission.
