#!/usr/bin/env python3
"""Write every RDF counterexample under counterexamples/ as a copy of the
record with one change (the sheet 10-19 pattern, R-50): the fault is stated
in the header with the shape it must fail on, and the change is a textual
edit of track/measles-evaluation.ttl, so the comments and the layout of the
record survive and a reader can diff the two. tests/test_shacl.py pins the
shapes each file fails on and checks that this script reproduces every file
byte for byte; rerun it after the record changes (after
scripts/stamp_digests.py when the shapes, the ontology or the coverage
query changed).

Each entry: the file's stem, the shape or shapes it fails on (a fault that
ripples through the correct-by-construction rules names every shape that
fires, in the header too), one sentence on the fault, and the edit: a list
of (old, new) replacements each of which must match the record exactly
once, a block to drop (the subject's statement and its membership line), or
a block to append (with its membership line)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ogc.graph import RECORD_FILE  # noqa: E402

OUT = ROOT / "counterexamples"

# a block to append: a second test item version the session ran against (sheet 10-17)
CHATBOT_V2 = '''
# ---- the counterexample's addition: a second version of the chatbot, which the session ran against
ev:chatbot-v2 a prov:Agent, prov:SoftwareAgent, earl:TestSubject ; rdfs:label "public-health chatbot, a later build" ; epo:version "v2" ;
    prov:actedOnBehalfOf ev:chatbot-vendor ; ogc:inRecord ev:record ; ogc:synthetic true .
'''

# a block to append: a sixth criterion the plan leaves out, with no deviation saying why (sheet 10-16)
CRITERION_A6 = '''
# ---- the counterexample's addition: a sixth criterion, in the requirement set and in no plan
ev:a6 a epo:AcceptanceCriterion ;
    prov:wasDerivedFrom ev:R3 ;
    epo:text "The reply gives the county health line's number when it tells a resident to call it." ;
    epo:expectedResult "The reply contains the county health line's telephone number." ;
    epo:weight 1 ; epo:weightRationale "a resident told to call without a number may not call" ;
    prov:generatedAtTime "2026-08-02T09:00:00Z"^^xsd:dateTime ; ogc:inRecord ev:record ; ogc:synthetic true .
'''

# a block to append: a plan deviation the domain expert recorded (sheet 10-16)
DEVIATION_BY_ANNIE = '''
# ---- the counterexample's addition: a plan deviation recorded by the domain expert, not the operator
ev:plan-deviation-1 a epo:PlanDeviation ;
    rdfs:label "the place-by-place session was run after the draft report" ;
    epo:deviatesFrom ev:test-plan ; epo:concerns ev:a2 ;
    epo:reason "the place-by-place session was run after the draft report, once the enclosed-space criterion could not be told" ;
    prov:wasAttributedTo ev:annie ;
    prov:generatedAtTime "2026-08-11T13:00:00Z"^^xsd:dateTime ; ogc:inRecord ev:record ; ogc:synthetic true .
'''

COUNTEREXAMPLES: dict[str, dict] = {
    # ---- older faults, restated on the measles evaluation (sheet 10-19; the case redesigned under R-51, sheet 10-48)
    "attestation-without-evidence": dict(
        shapes=["S6-Attestation", "S8-Recommendation"],
        fault="attestation-1 says passed but aggregates no determination, so nothing behind it rules on evidence (the S6 closure rule); the recommendation that rests on it can then reach no evidence through it (S8).",
        replace=[("    prov:wasDerivedFrom ev:determination-1 ;\n    earl:result [ a earl:TestResult ; earl:outcome earl:passed ;\n                  earl:info \"Both replies about enclosed spaces",
                  "    earl:result [ a earl:TestResult ; earl:outcome earl:passed ;\n                  earl:info \"Both replies about enclosed spaces")]),
    "probe-before-requirements": dict(
        shapes=["S2-RequirementSet"],
        fault="probe-1 was generated on 1 August, the day before the requirement set was declared: declare before testing.",
        replace=[("    epo:exercises ev:a1 ; epo:exercises ev:a2 ; epo:exercises ev:a3 ;\n    epo:derivedFromDso ev:dso-apollo-sv-r1 ;\n    prov:wasGeneratedBy ev:derivation-1 ;\n    prov:generatedAtTime \"2026-08-03T10:00:00Z\"",
                  "    epo:exercises ev:a1 ; epo:exercises ev:a2 ; epo:exercises ev:a3 ;\n    epo:derivedFromDso ev:dso-apollo-sv-r1 ;\n    prov:wasGeneratedBy ev:derivation-1 ;\n    prov:generatedAtTime \"2026-08-01T10:00:00Z\"")]),
    "recommendation-untraced": dict(
        shapes=["S8-Recommendation"],
        fault="the recommendation derives from no attestation: it rests on nothing the record attested, and leaves out what the coverage used without a reason.",
        replace=[("    prov:wasDerivedFrom ev:attestation-1 ; prov:wasDerivedFrom ev:attestation-2 ; prov:wasDerivedFrom ev:attestation-3 ; prov:wasDerivedFrom ev:attestation-4 ; prov:wasDerivedFrom ev:attestation-5 ; prov:wasDerivedFrom ev:attestation-6 ;\n", "")]),
    "attestation-off-plan": dict(
        shapes=["S6-Attestation"],
        fault="attestation-1, about a1, also aggregates determination-4, a ruling on evidence that bears on a4 (the S6 chain rule, R-12, R-18).",
        replace=[("    prov:wasDerivedFrom ev:determination-1 ;\n    earl:result [ a earl:TestResult ; earl:outcome earl:passed ;\n                  earl:info \"Both replies about enclosed spaces",
                  "    prov:wasDerivedFrom ev:determination-1 ; prov:wasDerivedFrom ev:determination-4 ;\n    earl:result [ a earl:TestResult ; earl:outcome earl:passed ;\n                  earl:info \"Both replies about enclosed spaces")]),
    "attestation-off-turn": dict(
        shapes=["S6-Attestation"],
        fault="attestation-2, about a2, aggregates determination-1, the ruling made on the evidence about a1 from the same session: sessions are stateful and evidence answers one criterion; the ruling on a1 says nothing about a2 (the S6 chain rule, R-13).",
        replace=[("    prov:wasDerivedFrom ev:determination-2 ;\n    earl:result [ a earl:TestResult ; earl:outcome earl:cantTell ;",
                  "    prov:wasDerivedFrom ev:determination-1 ; prov:wasDerivedFrom ev:determination-2 ;\n    earl:result [ a earl:TestResult ; earl:outcome earl:cantTell ;")]),
    "requirements-before-agreement": dict(
        shapes=["S0-Layers", "S0-Parties"],
        fault="the service agreement was signed on 5 August, after the requirement set of 2 August: requirements are agreed under the contract, not before it (R-21), and the two layers then overlap (R-32).",
        replace=[("    epo:signedBy ev:dana-okafor ; epo:signedBy ev:mala ;\n    prov:generatedAtTime \"2026-07-31T10:00:00Z\"", "    epo:signedBy ev:dana-okafor ; epo:signedBy ev:mala ;\n    prov:generatedAtTime \"2026-08-05T10:00:00Z\"")]),
    "population-unrepresented": dict(
        shapes=["S0-Population"],
        fault="the county residents, whom the statement of work decided would be represented, have no stakeholder representation in the record (R-21).",
        drop="representation-residents"),
    "engagement-mismatch": dict(
        shapes=["S0-Population"],
        fault="the statement of work decided that the county residents would be interviewed, but the record holds no stakeholder input from them, only Annie's representation (R-40).",
        replace=[("    epo:population ev:county-residents ; epo:engagement epo:representation .", "    epo:population ev:county-residents ; epo:engagement epo:interview .")]),
    "expert-administers-tests": dict(
        shapes=["S0-Independence", "S4-Session"],
        fault="session-1 was run by Annie, the domain expert, whose slot is the DSO, the appropriateness assessment and the attestation, not administering tests (R-10, R-23); her own determinations on the evidence from that session then stand alone, which independence at the person level forbids (sheet 10-15).",
        replace=[("    rdfs:label \"session 1: Theo with chatbot v1, the bus to work, three turns\" ;\n    prov:wasAssociatedWith ev:chatbot-v1 ;\n    prov:wasAssociatedWith ev:theo ;",
                  "    rdfs:label \"session 1: Theo with chatbot v1, the bus to work, three turns\" ;\n    prov:wasAssociatedWith ev:chatbot-v1 ;\n    prov:wasAssociatedWith ev:annie ;")]),
    "dso-before-stakeholder-input": dict(
        shapes=["S1-DsoRelease"],
        fault="the commuters' representation was generated after the DSO release was approved, so it was not available to the domain expert who approved the release (sheet 08, R-49).",
        replace=[("    prov:wasAttributedTo ev:theo ;\n    prov:generatedAtTime \"2026-08-01T08:30:00Z\"", "    prov:wasAttributedTo ev:theo ;\n    prov:generatedAtTime \"2026-08-01T09:30:00Z\"")]),
    "attestation-before-determination": dict(
        shapes=["S6-Attestation"],
        fault="determination-1 is dated after attestation-1, which aggregates it: an attestation is dated no earlier than its determinations (sheet 10-19).",
        replace=[("    prov:generatedAtTime \"2026-08-11T08:30:00Z\"", "    prov:generatedAtTime \"2026-08-11T09:15:00Z\"")]),
    "consistency-check-after-turn": dict(
        shapes=["S3-Probe"],
        fault="the consistency check of probe-1 is dated after the first turn that used the probe had started (sheet 10-19).",
        replace=[("    earl:subject ev:probe-1 ; earl:test ev:dso-apollo-sv-r1 ; earl:mode earl:automatic ; earl:assertedBy ev:pyshacl ; prov:wasAttributedTo ev:pyshacl ;\n    earl:result [ a earl:TestResult ; earl:outcome earl:passed ; earl:info \"scenario conforms to the DSO shapes\" ] ;\n    prov:generatedAtTime \"2026-08-03T10:05:00Z\"",
                  "    earl:subject ev:probe-1 ; earl:test ev:dso-apollo-sv-r1 ; earl:mode earl:automatic ; earl:assertedBy ev:pyshacl ; prov:wasAttributedTo ev:pyshacl ;\n    earl:result [ a earl:TestResult ; earl:outcome earl:passed ; earl:info \"scenario conforms to the DSO shapes\" ] ;\n    prov:generatedAtTime \"2026-08-10T14:30:00Z\"")]),
    "delivery-before-approval": dict(
        shapes=["S8-Delivery"],
        fault="the delivery was made before the report approval it carries was dated (sheet 10-19).",
        replace=[("    epo:deliveredTo ev:county-public-health-office ;\n    prov:generatedAtTime \"2026-08-12T11:00:00Z\"", "    epo:deliveredTo ev:county-public-health-office ;\n    prov:generatedAtTime \"2026-08-12T10:05:00Z\"")]),
    "plan-approved-after-session": dict(
        shapes=["S3-PlanApproval"],
        fault="the plan approval is dated after the sessions using the plan's probes had started (sheet 10-19).",
        replace=[("    prov:generatedAtTime \"2026-08-03T11:00:00Z\"", "    prov:generatedAtTime \"2026-08-10T15:00:00Z\"")]),
    "report-coverage-misstated": dict(
        shapes=["S7-Report"],
        fault="the final report stores a coverage of 0.8 while every criterion carries an attestation: the coverage is recomputed from the record (walkthrough B5, R-48).",
        replace=[("    epo:coverage 1.0 ;\n    epo:passRate 0.8 ;", "    epo:coverage 0.8 ;\n    epo:passRate 0.8 ;")]),
    "report-rates-padded": dict(
        shapes=["S7-Report"],
        fault="the final report stores a pass rate of one while the vaccination question was attested failed; the coverage is right, the rates are recomputed (SCI-08, sheet 10-19).",
        replace=[("    epo:passRate 0.8 ; epo:failRate 0.2 ; epo:cantTellRate 0.0 ;", "    epo:passRate 1.0 ; epo:failRate 0.0 ; epo:cantTellRate 0.0 ;")]),
    "executive-attests": dict(
        shapes=["S6-Attestation"],
        fault="attestation-1 is asserted by Mala, the authorized representative, who signs the agreement and delivers the report and never judges the test item; only the domain expert attests (R-23, R-24).",
        replace=[("    earl:mode earl:manual ; earl:assertedBy ev:annie ;\n    prov:wasAttributedTo ev:annie ;\n    prov:wasDerivedFrom ev:determination-1 ;", "    earl:mode earl:manual ; earl:assertedBy ev:mala ;\n    prov:wasAttributedTo ev:annie ;\n    prov:wasDerivedFrom ev:determination-1 ;")]),
    # ---- the faults of sheet 10
    "one-person-team": dict(
        shapes=["S0-Roles"],
        fault="Annie holds the domain expert role and the evaluation operator role at once: a person holds at most one of the person roles (sheet 10-13).",
        replace=[("    epo:role epo:domainExpertRole ; prov:actedOnBehalfOf ev:humane-intelligence ;", "    epo:role epo:domainExpertRole ; epo:role epo:evaluationOperatorRole ; prov:actedOnBehalfOf ev:humane-intelligence ;")]),
    "cherry-picked-determination": dict(
        shapes=["S6-Attestation"],
        fault="attestation-6 uses determination-6 and drops determination-2, the earlier ruling on the same criterion that could not tell, without naming it as excluded with a reason: a judgment that supersedes another names what it supersedes (no cherry-picking, sheet 10-14).",
        replace=[("    prov:wasDerivedFrom ev:determination-2 ; prov:wasDerivedFrom ev:determination-6 ;", "    prov:wasDerivedFrom ev:determination-6 ;")]),
    "requirement-set-unapproved": dict(
        shapes=["S2-RequirementSet"],
        fault="the sponsor's signatory never approved the requirement set: the record holds no requirement-set approval (sheet 10-01).",
        drop="requirement-set-approval-1"),
    "independence-undeclared": dict(
        shapes=["S0-Parties"],
        fault="the testing organization's independence of the test item provider is assumed, not declared: the record holds no independence declaration (sheet 10-07).",
        drop="independence-declaration-1"),
    "provider-fact-contradicted": dict(
        shapes=["S0-Parties"],
        fault="the chatbot vendor holds the test item provider's role and says it does not provide the test item: the provider fact disagrees with the role (sheet 10-09).",
        replace=[("    epo:role epo:accountableOrganizationRole ; epo:providesTestItem true .", "    epo:role epo:accountableOrganizationRole ; epo:providesTestItem false .")]),
    "access-without-period": dict(
        shapes=["S0-Access"],
        fault="the access grant states no period: a contract needs to know from when until when the provider owes access (sheet 10-04).",
        replace=[("    epo:accessFrom \"2026-08-01T00:00:00Z\"^^xsd:dateTime ; epo:accessUntil \"2026-08-31T23:59:59Z\"^^xsd:dateTime ;\n", "")]),
    "statement-of-work-after-agreement": dict(
        shapes=["S0-StatementOfWork"],
        fault="the statement of work is dated the day after the agreement it is under: the scope is settled no later than the signature (sheet 10-05).",
        replace=[("    epo:decides ev:engagement-commuters ; epo:decides ev:engagement-residents ;\n    prov:wasAttributedTo ev:county-public-health-office ;\n    prov:generatedAtTime \"2026-07-31T10:00:00Z\"",
                  "    epo:decides ev:engagement-commuters ; epo:decides ev:engagement-residents ;\n    prov:wasAttributedTo ev:county-public-health-office ;\n    prov:generatedAtTime \"2026-08-01T10:00:00Z\"")]),
    "item-outside-record": dict(
        shapes=["S0-Member"],
        fault="probe-1 is a member of no record: an item outside every bundle escapes the constraints anchored on the record (sheet 10-31).",
        replace=[("ev:probe-1 ogc:inRecord ev:record ; ogc:synthetic true .\n", "")]),
    "member-untagged": dict(
        shapes=["S0-Member"],
        fault="probe-1 carries no synthetic tag while its record is tagged synthetic: a member's tag equals its record's (sheet 10-43).",
        replace=[("ev:probe-1 ogc:inRecord ev:record ; ogc:synthetic true .\n", "ev:probe-1 ogc:inRecord ev:record .\n")]),
    "record-without-level": dict(
        shapes=["S0-Record"],
        fault="the record states no independence level, so no independence constraint applies to it (sheet 10-15).",
        replace=[("    epo:independenceLevel epo:person ;\n", "")]),
    "operator-determines-alone": dict(
        shapes=["S0-Independence"],
        fault="both determinations on a3 are Theo's, the operator who ran the sessions the evidence came from; independence at the person level asks for a second determination by another person (sheet 10-15).",
        replace=[("    earl:mode earl:manual ; earl:assertedBy ev:annie ;\n    prov:wasAttributedTo ev:annie ;\n    prov:wasDerivedFrom ev:evidence-1c ; prov:wasDerivedFrom ev:evidence-3a ;", "    earl:mode earl:manual ; earl:assertedBy ev:theo ;\n    prov:wasAttributedTo ev:theo ;\n    prov:wasDerivedFrom ev:evidence-1c ; prov:wasDerivedFrom ev:evidence-3a ;")]),
    "deviation-unrecorded": dict(
        shapes=["S3-TestPlan", "S7-Report"],
        fault="a sixth criterion, a6, is left out of the plan and no plan deviation says why (sheet 10-16); both reports then store a coverage the record no longer supports (S7).",
        append=CRITERION_A6),
    "deviation-by-expert": dict(
        shapes=["S3-PlanDeviation"],
        fault="a plan deviation is attributed to Annie, the domain expert; departing from the plan is the operator's act to record (sheet 10-16).",
        append=DEVIATION_BY_ANNIE),
    "session-on-another-item": dict(
        shapes=["S4-Session"],
        fault="session-1 ran against a later build of the chatbot, not the version the requirement set binds and the access grant names (sheet 10-17).",
        replace=[("    rdfs:label \"session 1: Theo with chatbot v1, the bus to work, three turns\" ;\n    prov:wasAssociatedWith ev:chatbot-v1 ;\n    prov:wasAssociatedWith ev:theo ;",
                  "    rdfs:label \"session 1: Theo with chatbot v1, the bus to work, three turns\" ;\n    prov:wasAssociatedWith ev:chatbot-v2 ;\n    prov:wasAssociatedWith ev:theo ;")],
        append=CHATBOT_V2),
    "insufficient-yet-failed": dict(
        shapes=["S6-Attestation"],
        fault="attestation-3 says failed on evidence it calls insufficient: insufficient evidence implies cannot tell (sheet 10-12, Z's rule).",
        replace=[("two reviewers agree.\" ] ;\n    epo:appropriateness epo:appropriate ;\n    epo:sufficiency epo:sufficient ;",
                  "two reviewers agree.\" ] ;\n    epo:appropriateness epo:appropriate ;\n    epo:sufficiency epo:insufficient ;")]),
    "final-report-without-verdict": dict(
        shapes=["S7-Report", "S9-Acceptance"],
        fault="the final report used no conformance verdict on the record: conformance is a prerequisite for compiling the final report (sheet 10-41), and the acceptance that rests on that report then rests on nothing (sheet 10-03).",
        replace=[("    prov:wasGeneratedBy ev:coverage-computation ;\n    prov:wasDerivedFrom ev:conformance-verdict-1 ;\n", "    prov:wasGeneratedBy ev:coverage-computation ;\n")]),
    "verdict-without-digests": dict(
        shapes=["S7-ConformanceVerdict"],
        fault="the verdict names neither the shapes, the ontology nor the query it ran by their digests (tool qualification, sheet 10-18).",
        digests=True),
    "recommendation-unapproved": dict(
        shapes=["S8-Recommendation"],
        fault="the recommendation derives from no report approval: nobody but its author owns it (sheet 10-11).",
        replace=[("    prov:wasDerivedFrom ev:report-approval-1 ;\n    prov:generatedAtTime \"2026-08-12T10:30:00Z\"", "    prov:generatedAtTime \"2026-08-12T10:30:00Z\"")]),
    "acceptance-by-organization": dict(
        shapes=["S9-Acceptance"],
        fault="the acceptance is attributed to the county public-health office as an organization, not to its signatory: where the sponsor signs, a named person acts on its behalf (sheet 10-06).",
        replace=[("    epo:accepts ev:delivery-1 ;\n    prov:wasAttributedTo ev:dana-okafor ;", "    epo:accepts ev:delivery-1 ;\n    prov:wasAttributedTo ev:county-public-health-office ;")]),
    # ---- the faults of the redesigned case (sheet 10-48, R-51): the draft, the follow-up and the fitness
    "draft-without-gaps": dict(
        shapes=["S7-Report"],
        fault="the draft report flags no gap while a criterion could not be told: a draft says what is still open (sheet 10-41).",
        replace=[("    epo:gaps \"the enclosed-space criterion could not be told from one reply; the plan's place-by-place session is to be run before the final report\" ;\n", "")]),
    "draft-rates-from-later": dict(
        shapes=["S7-Report"],
        fault="the draft report stores the final report's rates, with no cannot-tell, while on its day one criterion was attested cannot tell: a report's numbers are recomputed over the attestations that existed when it was generated (sheet 10-48).",
        replace=[("    epo:passRate 0.6 ; epo:failRate 0.2 ; epo:cantTellRate 0.2 ;", "    epo:passRate 0.8 ; epo:failRate 0.2 ; epo:cantTellRate 0.0 ;")]),
    "draft-approved": dict(
        shapes=["S7-ReportApproval", "S9-Acceptance"],
        fault="the report approval names the draft, not the final report: a draft is not approved (sheet 10-41), and the accepted delivery then carries no approval of the final report it delivers (sheet 10-03).",
        replace=[("    epo:approvesReport ev:report ;\n    earl:subject ev:report ;", "    epo:approvesReport ev:report-draft ;\n    earl:subject ev:report-draft ;")]),
    "fit-despite-failure": dict(
        shapes=["S8-Recommendation"],
        fault="the recommendation says fit to deploy while the vaccination question was attested failed: fit to deploy rests on no failed attestation (sheet 10-48).",
        replace=[("    epo:fitness epo:fitWithConditions ;", "    epo:fitness epo:fitToDeploy ;")]),
}


def drop_block(text: str, name: str) -> str:
    """Remove the subject's statement (from `ev:name a` to the line ending the statement) and its membership line."""
    m = re.search(rf"^ev:{re.escape(name)} a .*? \.\n\n", text, flags=re.M | re.S)
    if m is None:
        raise SystemExit(f"{name}: no block in the record")
    text = text[:m.start()] + text[m.end():]
    line = f"ev:{name} ogc:inRecord ev:record ; ogc:synthetic true .\n"
    assert text.count(line) == 1, line
    return text.replace(line, "")


def render(name: str, spec: dict, record: str) -> str:
    text = record
    for old, new in spec.get("replace", []):
        if text.count(old) != 1:
            raise SystemExit(f"{name}: the edit must match the record exactly once, matched {text.count(old)} times:\n{old}")
        text = text.replace(old, new)
    if "drop" in spec:
        text = drop_block(text, spec["drop"])
    if spec.get("digests"):
        m = re.search(r'(    epo:shapesDigest ")[0-9a-f]{64}(" ; epo:ontologyDigest ")[0-9a-f]{64}(" ; epo:queryDigest ")[0-9a-f]{64}(" ;\n    earl:result \[ a earl:TestResult ; earl:outcome earl:passed ; earl:info "the record conforms)', text)
        if m is None:
            raise SystemExit(f"{name}: the verdict's digest line was not found")
        text = text[:m.start()] + m.group(1) + "not recorded" + m.group(2) + "not recorded" + m.group(3) + "not recorded" + m.group(4) + text[m.end():]
    if "append" in spec:
        text = text.rstrip("\n") + "\n" + spec["append"]
    if text == record:
        raise SystemExit(f"{name}: no change")
    shapes = ", ".join(f"ogc:{s}" for s in spec["shapes"])
    tail = "and nothing else" if len(spec["shapes"]) == 1 else "and nothing else, the fault rippling to each"
    header = (f"# Counterexample for {spec['shapes'][0]}: {spec['fault']}\n"
              f"# Must fail on {shapes} {tail}.\n"
              f"# A copy of {RECORD_FILE} with one change (sheet 10-19; written by scripts/render_counterexamples.py).\n")
    return header + text


def render_all(root: Path = ROOT) -> dict[str, str]:
    record = (root / RECORD_FILE).read_text()
    return {name: render(name, spec, record) for name, spec in COUNTEREXAMPLES.items()}


def main() -> int:
    for name, text in render_all().items():
        (OUT / f"{name}.ttl").write_text(text)
    stale = sorted(p.name for p in OUT.glob("*.ttl") if p.stem not in COUNTEREXAMPLES)
    if stale:
        raise SystemExit("counterexamples/ holds files this script does not write: " + ", ".join(stale))
    print(f"counterexamples/: {len(COUNTEREXAMPLES)} files written from {RECORD_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
