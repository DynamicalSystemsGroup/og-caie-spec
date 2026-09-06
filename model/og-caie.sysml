package OGCAIE {
    doc /* Ontology-Grounded Contextual AI Evaluation (OG-CAIE) as an
       executable specification. Scope: Concept Definition plus System
       Requirements Definition (SEBoK v2.14, ISO/IEC/IEEE 15288:2023),
       including the assessment of interactions across interfaces. No
       logical or physical architecture is modeled (ruling R-07).

       Three layers: the Evaluation Process Ontology (EPO) is the
       domain-independent standard operating procedure, modeled as an
       action def; the Domain-Specific Ontology (DSO) is the expert-
       supplied parameter that makes the procedure implementable in one
       domain; the evaluation itself is an assemblage of human and
       machine parts wired along typed ports. Nine requirements
       (SCI-01..09) state what is essential for the result to count as
       science; each is tagged as verified by machine (a SHACL shape
       over the evaluation record) or validated by a named human (an
       attestation in the record).

       Vocabulary: terms are used, not owned. Canonical definitions are
       cited in vocabulary/og-caie.ttl in this precedence: ISO 9000:2026,
       SEVOCAB (IEEE CS), NIST AI 700-2, then W3C/OMG for binding only.
       Coinage is exactly three: DSO, EPO, OG-CAIE. Rulings are recorded
       verbatim in rulings/adjudications.ttl. */

    // ------------------------------------------------------------
    // Enumerations (bound to W3C EARL and Hawkins et al. 2011)
    // ------------------------------------------------------------

    enum def Outcome {
        doc /* W3C EARL 1.0 outcome values. NIST AI 700-2 section 3.1
           annotates dialogues with Yes / No / Unable to Determine / N/A,
           which map onto passed / failed / cantTell / inapplicable;
           untested is the value a criterion carries before any
           attestation exists. */
        passed;
        failed;
        cantTell;
        inapplicable;
        untested;
    }

    enum def Mode {
        doc /* W3C EARL 1.0 test modes: who produced the assertion. */
        manual;
        semiAuto;
        automatic;
    }

    enum def Appropriateness {
        doc /* Hawkins, Kelly, Knight and Graydon 2011, section 3.2:
           asserted context is asserted to be appropriate for the
           argument elements to which it applies. Here: was the declared
           context (operational environment, requirement set, DSO
           release) the right frame for the judgment. Ruling R-08
           replaces the earlier label "adequacy". */
        appropriate;
        inappropriate;
    }

    enum def Sufficiency {
        doc /* Hawkins, Kelly, Knight and Graydon 2011, section 3.3:
           asserted solution is asserted to be sufficient to support the
           claim. ISA 500 paragraph 5(f): sufficiency is the measure of
           the quantity of evidence. */
        sufficient;
        insufficient;
    }
}
