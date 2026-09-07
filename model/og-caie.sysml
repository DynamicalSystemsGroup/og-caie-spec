package OGCAIE {
    doc /* Ontology-Grounded Contextual AI Evaluation (OG-CAIE) as an
       executable specification. Scope: Concept Definition plus System
       Requirements Definition (SEBoK v2.14, ISO/IEC/IEEE 15288:2023),
       including the assessment of interactions across interfaces. No
       logical or physical architecture is modeled (ruling R-07).

       This file holds structure only (ruling R-22): the parties, the
       items that cross seams, the ports and interfaces, the six-step contracting lifecycle and the six-step
       Evaluation Process Ontology as an action def, and one assemblage
       that wires them. It is the authoring view. The canonical structure
       is its pruned RDF rendering, model/og-caie.model.ttl, produced by
       the pinned OpenSysML converter (designed for Flexo MMS) and checked
       by SHACL wiring shapes (shapes/model.shapes.ttl, M1 to M5). Value
       and provenance rules live in shapes over the evaluation record
       (shapes/epo.shapes.ttl, S0 to S8). The twelve essentials SCI-01 to
       SCI-12 and the shapes that check each are in model/trace.ttl.

       Vocabulary: terms are used, not owned. Canonical definitions are
       cited in vocabulary/og-caie.ttl in this precedence: ISO 9000:2026,
       SEVOCAB (IEEE CS), NIST AI 700-2, then W3C/OMG for binding only.
       Coinage is exactly three: DSO, EPO, OG-CAIE. Rulings are recorded
       verbatim in rulings/adjudications.ttl. */

    // ------------------------------------------------------------
    // Enumerations (bound to W3C EARL and Hawkins et al. 2011)
    // ------------------------------------------------------------

    enum def Outcome {
        doc /* W3C EARL 1.0 outcome values; NIST AI 700-2 section 3.1's
           Yes / No / Unable to Determine / N/A map onto passed / failed /
           cantTell / inapplicable; untested is a criterion with no
           attestation yet. */
        passed; failed; cantTell; inapplicable; untested;
    }

    enum def Mode {
        doc /* W3C EARL 1.0 test modes: who produced the assertion. */
        manual; semiAuto; automatic;
    }

    enum def Appropriateness {
        doc /* Hawkins, Kelly, Knight and Graydon 2011, section 3.2: the
           asserted context is appropriate for the elements it applies
           to. Ruling R-08 replaces the earlier label. */
        appropriate; inappropriate;
    }

    enum def Engagement {
        doc /* How an affected population is engaged, as the statement of work
           decides (ruling R-40). */
        interview; representation;
    }
    enum def Sufficiency {
        doc /* Hawkins et al. 2011, section 3.3; ISA 500 paragraph 5(f):
           the measure of the quantity of evidence. */
        sufficient; insufficient;
    }

    enum def EvidenceLevel {
        doc /* Ruling R-18: evidence at the probe, session or suite level. */
        probe; session; suite;
    }

    enum def EpoStep {
        doc /* The six steps of the Evaluation Process Ontology (ruling
           R-21 split the paper's five; R-32 moved agree out to the
           contracting lifecycle, ContractingStep). Every attestation and
           every recommendation names its step. */
        scope; declareRequirements; plan; execute; determineAndAttest; report;
    }

    enum def ContractingStep {
        doc /* The six steps of the contracting lifecycle (ruling R-32):
           contracting through delivery and acceptance. */
        need; propose; agree; access; deliver; acceptDelivery;
    }

    // ------------------------------------------------------------
    // Items: what crosses the seams. Identity and typing only; the
    // values of a run live in the evaluation record (ruling R-22).
    // ------------------------------------------------------------

    item def Mission {
        doc /* The sponsor's purpose for existing as its top management
           expresses it (ISO 9000:2026 3.4.11), and with it its obligations
           towards the affected populations: the context the contract
           answers to (ruling R-37). Pinned at the contract. It regards one or
           more of the affected populations (ruling R-38). */
        attribute id : ScalarValues::String;
        ref part regards : AffectedPopulation[1..*];
    }
    item def StatementOfWork {
        doc /* The sponsor's scope-of-work decisions under the contract (SEVOCAB
           statement of work): for each affected population, interview or
           representation. A boundary item between the contract and its
           fulfilment (ruling R-40): decided with the agreement, consumed by
           the scope step. Pinned at the contract. */
        attribute id : ScalarValues::String;
        ref part regards : AffectedPopulation[1..*];
        attribute engagement : Engagement[1..*];
    }
    item def Need {
        doc /* The sponsor's stated mission problem and measures of success
           (ISO 9000:2026 requirement: need or expectation that is stated;
           SEBoK business or mission analysis). Pinned at the contract
           (ruling R-32). */
        attribute id : ScalarValues::String;
    }
    item def Proposal {
        doc /* The testing organization's response to the need, offering the
           service (SEBoK: the supplier enters into an agreement with the
           acquirer). Pinned at the contract. */
        attribute id : ScalarValues::String;
    }
    item def Acceptance {
        doc /* The sponsor's acceptance of the delivery as performance of the
           agreement (ISO/IEC/IEEE 24748-5 acceptance; ISO/IEC 17000 9.6).
           Pinned at the contract. */
        attribute id : ScalarValues::String;
    }
    item def ServiceAgreement {
        doc /* The contract (ISO 9000:2026 3.3.13) between the sponsor
           organization and the testing organization to perform OG-CAIE
           as a service, signed by the sponsor and by the testing
           organization's account executive (rulings R-21, R-23). */
        attribute id : ScalarValues::String;
    }
    item def TestItemAccess {
        doc /* The accountable organization's grant of access to the test
           item, with the version to be tested. */
        attribute id : ScalarValues::String;
    }
    item def StakeholderInput {
        doc /* What an interviewed affected population said. Optional:
           populations not interviewed are represented by the domain
           expert, and the record names who represents them (R-21). */
        attribute id : ScalarValues::String;
    }
    item def DsoRelease {
        doc /* A versioned release of the Domain-Specific Ontology,
           approved by a named domain expert before any probe is derived. */
        attribute version : ScalarValues::String;
    }
    item def RequirementSet {
        doc /* The operational envelope (rulings R-03, R-14): the
           requirements THIS test item must meet in THIS operational
           environment, agreed under the service agreement. */
        attribute id : ScalarValues::String;
    }
    item def AcceptanceCriterion {
        doc /* Derived from a requirement; states its expected result
           (SEVOCAB) and its weight, the deployment sensitivity (R-05,
           which specializes risk-based testing). The coverage item (R-01). */
        attribute id : ScalarValues::String;
    }
    item def AppropriatenessAssessment {
        doc /* The domain expert's assessment that the requirement set is
           appropriate for the affected populations and the environment
           (R-08, R-21). */
        attribute id : ScalarValues::String;
    }
    item def TestPlan {
        doc /* SEVOCAB test plan: objectives (criteria) and means (probes
           or a test strategy), fixed before any session (R-12, R-13). */
        attribute id : ScalarValues::String;
    }
    item def PlanApproval {
        doc /* The domain expert's approval of a test plan (R-21). */
        attribute id : ScalarValues::String;
    }
    item def Strategy {
        doc /* A test strategy: a state feedback policy choosing the next
           probe from the trajectory so far (R-13). Optional. */
        attribute id : ScalarValues::String;
    }
    item def Probe {
        doc /* A scenario tied to the criteria it exercises, derived from
           the DSO release and checked for consistency (R-12). */
        attribute id : ScalarValues::String;
    }
    item def Session {
        doc /* One operator paired with the test item; its ordered turns
           form a trajectory (NIST AI 700-2; IEC 60050-351; R-13). */
        attribute id : ScalarValues::String;
    }
    item def Response {
        doc /* What the test item produced at one turn of a session. */
        attribute id : ScalarValues::String;
    }
    item def Evidence {
        doc /* Collected material bearing on one criterion's expected
           result under the plan; the domain (R-18, R-20). */
        attribute id : ScalarValues::String;
    }
    item def Determination {
        doc /* The ruling on evidence: passed, failed or cantTell; the
           codomain (ISO 9000:2026 3.11.1; R-20). */
        attribute id : ScalarValues::String;
    }
    item def Attestation {
        doc /* ISO/IEC 17000 7.3: a named domain expert's statement for one
           criterion, aggregating its determinations, with outcome,
           appropriateness and sufficiency (R-08, R-20, R-21). */
        attribute id : ScalarValues::String;
    }
    item def Report {
        doc /* Coverage and performance, computed by machine over a
           conformant record and reported together, never merged. */
        attribute id : ScalarValues::String;
    }
    item def Recommendation {
        doc /* A named person's proposal, typically to change a guardrail,
           traceable to the attestations it rests on. */
        attribute id : ScalarValues::String;
    }
    item def Delivery {
        doc /* The report and the recommendation handed to the sponsor by
           the account executive: the output of the delivery activity,
           distinct from recommending (ruling R-24). */
        attribute id : ScalarValues::String;
    }
    item def EvaluationRecord {
        doc /* The record itself (ISO 9000:2026 3.8.12, refined): the hub
           every fact passes through, read by every machine and every
           member of the testing organization. */
        attribute id : ScalarValues::String;
    }

    // ------------------------------------------------------------
    // Ports: one typed item each, directional. A conjugate (~) port
    // consumes what the plain port supplies.
    // ------------------------------------------------------------

    port def MissionWrite { out item i : Mission; }
    port def StatementOfWorkWrite { out item i : StatementOfWork; }
    port def NeedWrite { out item i : Need; }
    port def ProposalWrite { out item i : Proposal; }
    port def AcceptanceWrite { out item i : Acceptance; }
    port def AgreementWrite { out item i : ServiceAgreement; }
    port def AccessWrite { out item i : TestItemAccess; }
    port def StakeholderInputWrite { out item i : StakeholderInput; }
    port def DsoWrite { out item i : DsoRelease; }
    port def RequirementSetWrite { out item i : RequirementSet; }
    port def AssessmentWrite { out item i : AppropriatenessAssessment; }
    port def PlanWrite { out item i : TestPlan; }
    port def PlanApprovalWrite { out item i : PlanApproval; }
    port def ProbeWrite { out item i : Probe; }
    port def ResponseWrite { out item i : Response; }
    port def EvidenceWrite { out item i : Evidence; }
    port def DeterminationWrite { out item i : Determination; }
    port def AttestationWrite { out item i : Attestation; }
    port def ReportWrite { out item i : Report; }
    port def RecommendationWrite { out item i : Recommendation; }
    port def DeliveryWrite { out item i : Delivery; }
    port def RecordWrite { out item i : EvaluationRecord; }

    // ------------------------------------------------------------
    // Interfaces: the seams assessed (15288 System Requirements
    // Definition). Supplier end plain, consumer end conjugated.
    // ------------------------------------------------------------

    interface def MissionSeam { end supplier : MissionWrite; end consumer : ~MissionWrite; }
    interface def StatementOfWorkSeam { end supplier : StatementOfWorkWrite; end consumer : ~StatementOfWorkWrite; }
    interface def NeedSeam { end supplier : NeedWrite; end consumer : ~NeedWrite; }
    interface def ProposalSeam { end supplier : ProposalWrite; end consumer : ~ProposalWrite; }
    interface def AcceptanceSeam { end supplier : AcceptanceWrite; end consumer : ~AcceptanceWrite; }
    interface def AgreementSeam { end supplier : AgreementWrite; end consumer : ~AgreementWrite; }
    interface def AccessSeam { end supplier : AccessWrite; end consumer : ~AccessWrite; }
    interface def StakeholderInputSeam { end supplier : StakeholderInputWrite; end consumer : ~StakeholderInputWrite; }
    interface def DsoSeam { end supplier : DsoWrite; end consumer : ~DsoWrite; }
    interface def RequirementSeam { end supplier : RequirementSetWrite; end consumer : ~RequirementSetWrite; }
    interface def AssessmentSeam { end supplier : AssessmentWrite; end consumer : ~AssessmentWrite; }
    interface def PlanSeam { end supplier : PlanWrite; end consumer : ~PlanWrite; }
    interface def PlanApprovalSeam { end supplier : PlanApprovalWrite; end consumer : ~PlanApprovalWrite; }
    interface def ProbeSeam { end supplier : ProbeWrite; end consumer : ~ProbeWrite; }
    interface def ResponseSeam { end supplier : ResponseWrite; end consumer : ~ResponseWrite; }
    interface def EvidenceSeam { end supplier : EvidenceWrite; end consumer : ~EvidenceWrite; }
    interface def DeterminationSeam { end supplier : DeterminationWrite; end consumer : ~DeterminationWrite; }
    interface def AttestationSeam { end supplier : AttestationWrite; end consumer : ~AttestationWrite; }
    interface def ReportSeam { end supplier : ReportWrite; end consumer : ~ReportWrite; }
    interface def RecommendationSeam { end supplier : RecommendationWrite; end consumer : ~RecommendationWrite; }
    interface def DeliverySeam { end supplier : DeliveryWrite; end consumer : ~DeliveryWrite; }
    interface def RecordSeam { end supplier : RecordWrite; end consumer : ~RecordWrite; }

    // ------------------------------------------------------------
    // Two cycles (rulings R-21, R-24, R-32). The contracting lifecycle
    // is the outer cycle, contracting through delivery, whose actors are
    // the parties; it pins the first layer of assumptions. The EPO is the
    // inner cycle, performed between access and delivery; it pins the
    // second. Each step is an activity with precise typed inputs and
    // outputs; actors perform activities; an activity's outputs are what
    // its performer's ports carry. Every item kind is produced by some
    // step or is the record itself (M4).
    // ------------------------------------------------------------

    action def ContractingProcess {
        doc /* The contracting lifecycle: the ISO/IEC/IEEE 15288 agreement
           processes as SEBoK describes them, ISO/IEC 17000's access,
           scheme and acceptance, ISO 9000's contract (ruling R-32). One
           nested model (ruling R-33): the fulfil step is a black box typed
           by the EvaluationProcess, whose inputs are what the contract
           pinned and whose outputs are what the delivery carries; its
           definition below is the drill-down, and it conforms to that
           interface by typing. The flows say which item goes where. */
        action need { out mission : Mission; out statedNeed : Need; }
        action propose { in mission : Mission; in statedNeed : Need; out proposal : Proposal; }
        action agree { in mission : Mission; in proposal : Proposal; out agreement : ServiceAgreement; out statementOfWork : StatementOfWork; }
        action access { in agreement : ServiceAgreement; out testItemAccess : TestItemAccess; }
        action fulfil : EvaluationProcess;
        action deliver { in reportIn : Report; in recommendation : Recommendation; out delivery : Delivery; }
        action acceptDelivery { in delivery : Delivery; out acceptance : Acceptance; }
        succession first need then propose;
        succession first propose then agree;
        succession first agree then access;
        succession first access then fulfil;
        succession first fulfil then deliver;
        succession first deliver then acceptDelivery;
        flow need.statedNeed to propose.statedNeed;
        flow need.mission to propose.mission;
        flow need.mission to agree.mission;
        flow propose.proposal to agree.proposal;
        flow agree.agreement to access.agreement;
        flow agree.agreement to fulfil.agreement;
        flow agree.statementOfWork to fulfil.statementOfWork;
        flow access.testItemAccess to fulfil.testItemAccess;
        flow fulfil.reportOut to deliver.reportIn;
        flow fulfil.recommendation to deliver.recommendation;
        flow deliver.delivery to acceptDelivery.delivery;
    }

    action def EvaluationProcess {
        doc /* The Evaluation Process Ontology. Domain-independent; the
           agreement and the access enter from the contracting lifecycle;
           the DSO enters as a parameter at the scope step; the record
           leaves as the result. */
        in agreement : ServiceAgreement;
        in statementOfWork : StatementOfWork;
        in testItemAccess : TestItemAccess;
        out reportOut : Report;
        out recommendation : Recommendation;
        out record : EvaluationRecord;
        action scope { in agreement : ServiceAgreement; in statementOfWork : StatementOfWork; out input : StakeholderInput[0..*]; out dso : DsoRelease; }
        action declareRequirements { in agreement : ServiceAgreement; in dso : DsoRelease; in input : StakeholderInput[0..*];
            out requirements : RequirementSet; out criteria : AcceptanceCriterion[1..*]; out assessment : AppropriatenessAssessment; }
        action plan { in requirements : RequirementSet; in criteria : AcceptanceCriterion[1..*]; in dso : DsoRelease;
            out testPlan : TestPlan; out approval : PlanApproval; out strategy : Strategy[0..1]; out probes : Probe[1..*]; }
        action execute { in testPlan : TestPlan; in probes : Probe[1..*]; in testItemAccess : TestItemAccess;
            out sessions : Session[1..*]; out responses : Response[1..*]; out evidence : Evidence[1..*]; }
        action determineAndAttest { in evidence : Evidence[1..*]; in criteria : AcceptanceCriterion[1..*];
            out determinations : Determination[1..*]; out attestations : Attestation[1..*]; }
        action report { in attestations : Attestation[1..*]; in determinations : Determination[1..*]; in criteria : AcceptanceCriterion[1..*];
            out reportOut : Report; out recommendation : Recommendation; }
        succession first scope then declareRequirements;
        succession first declareRequirements then plan;
        succession first plan then execute;
        succession first execute then determineAndAttest;
        succession first determineAndAttest then report;
        bind scope.agreement = agreement;
        bind scope.statementOfWork = statementOfWork;
        bind declareRequirements.agreement = agreement;
        bind execute.testItemAccess = testItemAccess;
        bind reportOut = report.reportOut;
        bind recommendation = report.recommendation;
        flow scope.dso to declareRequirements.dso;
        flow scope.input to declareRequirements.input;
        flow scope.dso to plan.dso;
        flow declareRequirements.requirements to plan.requirements;
        flow declareRequirements.criteria to plan.criteria;
        flow plan.testPlan to execute.testPlan;
        flow plan.probes to execute.probes;
        flow execute.evidence to determineAndAttest.evidence;
        flow declareRequirements.criteria to determineAndAttest.criteria;
        flow determineAndAttest.attestations to report.attestations;
        flow determineAndAttest.determinations to report.determinations;
        flow declareRequirements.criteria to report.criteria;
    }

    // ------------------------------------------------------------
    // Parties (ruling R-21): organizations are concrete single
    // entities, affected populations are many, persons fill abstract
    // actor categories (ruling R-23), machines are versioned software.
    // ------------------------------------------------------------

    abstract part def Party {
        doc /* Anyone or anything named in the record (prov:Agent). */
        attribute name : ScalarValues::String;
    }
    part def Organization :> Party {
        doc /* ISO 9000:2026 3.1.1 (prov:Organization). */
    }
    part def Person :> Party {
        doc /* A named person (prov:Person). Judgment-bearing decisions
           are theirs and are recorded with their name. */
    }
    part def Machine :> Party {
        doc /* Versioned software (prov:SoftwareAgent). It derives, checks,
           records and computes; it never judges. */
        attribute version : ScalarValues::String;
    }

    part def SponsorOrganization :> Organization {
        doc /* The customer (ISO 9000:2026 3.9.1): states its mission and
           obligations towards the affected populations (R-37), states the need,
           receives the proposal, commissions the evaluation under the
           service agreement, receives the delivery through the account
           executive and accepts it (R-32). May or may not be the
           accountable organization; the record says. */
        attribute isAccountable : ScalarValues::Boolean;
        port missionOut : MissionWrite;
        port statementOfWorkOut : StatementOfWorkWrite;
        port needOut : NeedWrite;
        port proposalIn : ~ProposalWrite;
        port agreementOut : AgreementWrite;
        port deliveryIn : ~DeliveryWrite;
        port acceptanceOut : AcceptanceWrite;
    }

    part def AccountExecutive :> Person {
        doc /* Signatory of the service agreement and legal representative
           of the testing organization (ruling R-23). Countersigns the
           agreement into the record, reads the record, and delivers the
           report and the recommendation to the sponsor as one delivery
           (an activity of its own, R-24); answers the sponsor's need with
           the proposal and receives the acceptance (R-32). No evidence, determination or
           attestation port: the account executive never judges the test
           item. The worked example's Mala. */
        port missionIn : ~MissionWrite;
        port statementOfWorkIn : ~StatementOfWorkWrite;
        port needIn : ~NeedWrite;
        port proposalOut : ProposalWrite;
        port agreementIn : ~AgreementWrite;
        port agreementOut : AgreementWrite;
        port recordIn : ~RecordWrite;
        port deliveryOut : DeliveryWrite;
        port acceptanceIn : ~AcceptanceWrite;
    }

    part def DomainExpert :> Person {
        doc /* The technical expert (ISO 9000:2026 3.12.9) in the domain
           (rulings R-10, R-21): supplies or approves the DSO release,
           assesses the appropriateness of the requirement set for the
           affected populations, approves test plans, may make
           determinations on evidence (an activity either expert may
           perform, R-24), and attests. Represents the
           populations that are not interviewed. The worked example's
           Annie. */
        port recordIn : ~RecordWrite;
        port dsoOut : DsoWrite;
        port assessmentOut : AssessmentWrite;
        port planApprovalOut : PlanApprovalWrite;
        port determinationOut : DeterminationWrite;
        port attestationOut : AttestationWrite;
    }

    part def EvaluationOperator :> Person {
        doc /* The technical expert who operates the evaluation (SEVOCAB
           operator, refined; rulings R-10, R-23): declares the
           requirement set, writes the test plan, applies the probes to
           the test item, collects the evidence, makes determinations,
           and writes the recommendation. No attestation port: attestation
           belongs to the domain expert. The worked example's Theo. */
        port recordIn : ~RecordWrite;
        port requirementsOut : RequirementSetWrite;
        port planOut : PlanWrite;
        port probesIn : ~ProbeWrite;
        port accessIn : ~AccessWrite;
        port probesToItem : ProbeWrite;
        port evidenceOut : EvidenceWrite;
        port determinationOut : DeterminationWrite;
        port recommendationOut : RecommendationWrite;
    }

    part def EvaluationTeam {
        doc /* The evaluation team (refined from ISO 9000:2026 3.12.7 audit
           team): at least one domain expert and at least one evaluation
           operator, distinct actor categories (rulings R-10, R-23). */
        part domainExpert : DomainExpert[1..*];
        part operator : EvaluationOperator[1..*];
    }

    part def TestItem :> Machine {
        doc /* The test item (SEVOCAB; the prose says system under test,
           ruling R-19): a black box that is given probes and produces
           responses. Provided by the accountable organization, inside
           the record, outside the testing organization's responsibility. */
        port probesIn : ~ProbeWrite;
        port responseOut : ResponseWrite;
    }

    part def AccountableOrganization :> Organization {
        doc /* The organization that provides or is accountable for the
           test item: the first party in ISO/IEC 17000's sense (4.3). It
           grants access to the test item and is named in the record. */
        part testItem : TestItem;
        port accessOut : AccessWrite;
    }

    part def AffectedPopulation :> Party {
        doc /* A population of actors affected by the test item (ISO
           9000:2026 3.1.4 interested party, ruling R-21): interviewed,
           in which case its input enters the record, or represented by a
           domain expert, in which case the record names who. */
        port inputOut : StakeholderInputWrite;
    }

    part def ProbeDeriver :> Machine {
        doc /* Derives probes from the DSO release and the requirement set
           in the record; one output read by the operator and the recorder
           (an output wire may be shared, R-25). */
        port recordIn : ~RecordWrite;
        port probesOut : ProbeWrite;
    }

    part def ConformanceChecker :> Machine {
        doc /* Machine verification, called conformance (ruling R-16): the
           record is correctly constructed to the EPO shapes. */
        port recordIn : ~RecordWrite;
    }

    part def CoverageCalculator :> Machine {
        doc /* Computes coverage and the outcome distribution over the
           record; anyone holding the record recomputes the same numbers
           (queries/coverage.rq). */
        port recordIn : ~RecordWrite;
        port reportOut : ReportWrite;
    }

    part def Recorder :> Machine {
        doc /* Keeps the evaluation record: the hub every item kind passes
           through (M3), with who did what and when. One conjugate port
           per item kind in, each wired once (input wires are unique);
           one record port out, read by six (output wires are shared when
           what flows is information, R-25). */
        port missionIn : ~MissionWrite;
        port statementOfWorkIn : ~StatementOfWorkWrite;
        port needIn : ~NeedWrite;
        port proposalIn : ~ProposalWrite;
        port agreementIn : ~AgreementWrite;
        port accessIn : ~AccessWrite;
        port acceptanceIn : ~AcceptanceWrite;
        port inputIn : ~StakeholderInputWrite;
        port dsoIn : ~DsoWrite;
        port requirementsIn : ~RequirementSetWrite;
        port assessmentIn : ~AssessmentWrite;
        port planIn : ~PlanWrite;
        port planApprovalIn : ~PlanApprovalWrite;
        port probeIn : ~ProbeWrite;
        port responseIn : ~ResponseWrite;
        port evidenceIn : ~EvidenceWrite;
        port operatorDeterminationIn : ~DeterminationWrite;
        port expertDeterminationIn : ~DeterminationWrite;
        port attestationIn : ~AttestationWrite;
        port reportIn : ~ReportWrite;
        port recommendationIn : ~RecommendationWrite;
        port deliveryIn : ~DeliveryWrite;
        port recordOut : RecordWrite;
    }

    part def TestingOrganization :> Organization {
        doc /* The provider (ISO 9000:2026 3.1.9): performs the evaluation
           as a service. Holds exactly one account executive, one team of
           one or more domain experts and one or more operators (all three
           are roles within it, ruling R-23), and the four machines. Independent of the accountable
           organization, with no user interest in the test item, it is a
           third party (ISO/IEC 17000 4.5); the record states which. */
        attribute independentOfAccountable : ScalarValues::Boolean;
        part accountExecutive : AccountExecutive[1];
        part team : EvaluationTeam[1];
        part probeDeriver : ProbeDeriver;
        part conformanceChecker : ConformanceChecker;
        part coverageCalculator : CoverageCalculator;
        part recorder : Recorder;
    }

    // ------------------------------------------------------------
    // The assemblage: one evaluation. Interface usages are declared
    // before the parts they connect (v0.4.3 materializes in declaration
    // order). Every input port is the end of exactly one seam and every
    // output port of at least one (M2, R-25); every item kind reaches the
    // recorder (M3).
    // ------------------------------------------------------------

    connection def Obligation {
        doc /* The sponsor organization's obligation towards an affected
           population: a relation between two parties, not a flow of any
           item. It is what the mission expresses, and the context the
           contract answers to (ruling R-38). */
        end sponsor : SponsorOrganization;
        end population : AffectedPopulation;
    }
    part def OgCaieEvaluation {
        doc /* Four parties wired along typed seams, performing the
           contracting lifecycle, whose fulfil step is the EPO (R-33). */

        connection obligation : Obligation connect sponsor to affected;
        interface missionSeam : MissionSeam connect sponsor.missionOut to testingOrg.recorder.missionIn;
        interface missionToExecutiveSeam : MissionSeam connect sponsor.missionOut to testingOrg.accountExecutive.missionIn;
        interface statementOfWorkSeam : StatementOfWorkSeam connect sponsor.statementOfWorkOut to testingOrg.recorder.statementOfWorkIn;
        interface statementOfWorkToExecutiveSeam : StatementOfWorkSeam connect sponsor.statementOfWorkOut to testingOrg.accountExecutive.statementOfWorkIn;
        interface needSeam : NeedSeam connect sponsor.needOut to testingOrg.recorder.needIn;
        interface needToExecutiveSeam : NeedSeam connect sponsor.needOut to testingOrg.accountExecutive.needIn;
        interface proposalSeam : ProposalSeam connect testingOrg.accountExecutive.proposalOut to testingOrg.recorder.proposalIn;
        interface proposalToSponsorSeam : ProposalSeam connect testingOrg.accountExecutive.proposalOut to sponsor.proposalIn;
        interface agreementSeam : AgreementSeam connect sponsor.agreementOut to testingOrg.accountExecutive.agreementIn;
        interface countersignSeam : AgreementSeam connect testingOrg.accountExecutive.agreementOut to testingOrg.recorder.agreementIn;
        interface accessSeam : AccessSeam connect accountable.accessOut to testingOrg.recorder.accessIn;
        interface accessToOperatorSeam : AccessSeam connect accountable.accessOut to testingOrg.team.operator.accessIn;
        interface stakeholderInputSeam : StakeholderInputSeam connect affected.inputOut to testingOrg.recorder.inputIn;
        interface dsoSeam : DsoSeam connect testingOrg.team.domainExpert.dsoOut to testingOrg.recorder.dsoIn;
        interface requirementSeam : RequirementSeam connect testingOrg.team.operator.requirementsOut to testingOrg.recorder.requirementsIn;
        interface assessmentSeam : AssessmentSeam connect testingOrg.team.domainExpert.assessmentOut to testingOrg.recorder.assessmentIn;
        interface planSeam : PlanSeam connect testingOrg.team.operator.planOut to testingOrg.recorder.planIn;
        interface planApprovalSeam : PlanApprovalSeam connect testingOrg.team.domainExpert.planApprovalOut to testingOrg.recorder.planApprovalIn;
        interface derivedProbeSeam : ProbeSeam connect testingOrg.probeDeriver.probesOut to testingOrg.team.operator.probesIn;
        interface probeRecordSeam : ProbeSeam connect testingOrg.probeDeriver.probesOut to testingOrg.recorder.probeIn;
        interface probeRunSeam : ProbeSeam connect testingOrg.team.operator.probesToItem to accountable.testItem.probesIn;
        interface responseSeam : ResponseSeam connect accountable.testItem.responseOut to testingOrg.recorder.responseIn;
        interface evidenceSeam : EvidenceSeam connect testingOrg.team.operator.evidenceOut to testingOrg.recorder.evidenceIn;
        interface operatorDeterminationSeam : DeterminationSeam connect testingOrg.team.operator.determinationOut to testingOrg.recorder.operatorDeterminationIn;
        interface expertDeterminationSeam : DeterminationSeam connect testingOrg.team.domainExpert.determinationOut to testingOrg.recorder.expertDeterminationIn;
        interface attestationSeam : AttestationSeam connect testingOrg.team.domainExpert.attestationOut to testingOrg.recorder.attestationIn;
        interface reportSeam : ReportSeam connect testingOrg.coverageCalculator.reportOut to testingOrg.recorder.reportIn;
        interface recommendationSeam : RecommendationSeam connect testingOrg.team.operator.recommendationOut to testingOrg.recorder.recommendationIn;
        interface recordToDeriverSeam : RecordSeam connect testingOrg.recorder.recordOut to testingOrg.probeDeriver.recordIn;
        interface recordToCheckerSeam : RecordSeam connect testingOrg.recorder.recordOut to testingOrg.conformanceChecker.recordIn;
        interface recordToCalculatorSeam : RecordSeam connect testingOrg.recorder.recordOut to testingOrg.coverageCalculator.recordIn;
        interface recordToOperatorSeam : RecordSeam connect testingOrg.recorder.recordOut to testingOrg.team.operator.recordIn;
        interface recordToExpertSeam : RecordSeam connect testingOrg.recorder.recordOut to testingOrg.team.domainExpert.recordIn;
        interface recordToExecutiveSeam : RecordSeam connect testingOrg.recorder.recordOut to testingOrg.accountExecutive.recordIn;
        interface deliverySeam : DeliverySeam connect testingOrg.accountExecutive.deliveryOut to sponsor.deliveryIn;
        interface deliveryRecordSeam : DeliverySeam connect testingOrg.accountExecutive.deliveryOut to testingOrg.recorder.deliveryIn;
        interface acceptanceSeam : AcceptanceSeam connect sponsor.acceptanceOut to testingOrg.recorder.acceptanceIn;
        interface acceptanceToExecutiveSeam : AcceptanceSeam connect sponsor.acceptanceOut to testingOrg.accountExecutive.acceptanceIn;

        part sponsor : SponsorOrganization;
        part testingOrg : TestingOrganization;
        part accountable : AccountableOrganization;
        part affected : AffectedPopulation[0..*];

        perform action contracting : ContractingProcess;
    }

    // ------------------------------------------------------------
    // The worked example, bound by name only (ruling R-22): the values
    // of the run live in track/measles-run.ttl. Synthetic case; the
    // names recognise the roles of real people who made no attestation
    // here (ruling R-23).
    // ------------------------------------------------------------

    package Runs {
        part def MeaslesRun :> OgCaieEvaluation {
            doc /* A public-health chatbot during a measles outbreak: a
               county public-health office sponsors the evaluation, the
               chatbot's vendor is accountable for it, Humane Intelligence
               performs it with Mala, Annie and Theo, and two populations
               are affected. */
            part :>> sponsor { attribute :>> name = "county public-health office"; attribute :>> isAccountable = false; }
            part :>> accountable {
                attribute :>> name = "chatbot vendor";
                part :>> testItem { attribute :>> name = "measles-chatbot"; attribute :>> version = "v1"; }
            }
            part :>> testingOrg {
                attribute :>> name = "Humane Intelligence"; attribute :>> independentOfAccountable = true;
                part :>> accountExecutive { attribute :>> name = "Mala"; }
                part :>> team {
                    part annie :> domainExpert { attribute :>> name = "Annie"; }
                    part theo :> operator { attribute :>> name = "Theo"; }
                }
                part :>> probeDeriver { attribute :>> name = "probe-deriver"; attribute :>> version = "0.1"; }
                part :>> conformanceChecker { attribute :>> name = "pyshacl"; attribute :>> version = "0.27"; }
                part :>> coverageCalculator { attribute :>> name = "coverage-calculator"; attribute :>> version = "0.1"; }
                part :>> recorder { attribute :>> name = "recorder"; attribute :>> version = "0.1"; }
            }
            part residents :> affected { attribute :>> name = "county residents"; }
            part commuters :> affected { attribute :>> name = "commuters through the county"; }
        }
        part measlesRun : MeaslesRun;
    }
}
