# og-caie-spec

**Ontology-Grounded Contextual AI Evaluation (OG-CAIE) as an executable
specification.** Site: <https://dynamicalsystemsgroup.github.io/og-caie-spec/>

The process Humane Intelligence and Dynamical Systems Group use to evaluate a
deployed AI system against the needs of a specific domain, written down as:

- a **glossary** whose every term cites one canonical definition (ISO 9000:2026,
  SEVOCAB, NIST AI 700-2, W3C), with exactly three coined terms;
- a **SysML v2 model** (OpenSysML v0.4.3) of the Evaluation Process Ontology
  as a standard operating procedure and of the human and machine assemblage
  that runs it, with nine requirements each tagged machine-verified or
  human-validated;
- one **evaluation record** (PROV-O + EARL) of the measles chatbot example,
  checked by SHACL shapes, with counterexamples that must fail;
- a **rulings register** holding every interpretive choice verbatim.

## Run the gate

```bash
uv sync && bash checks/run-checks.sh
```

The only verdict is the `CHECKS: PASS|FAIL` line; details in `checks/out/`.

## IRIs

Ontology and record IRIs are authored under `https://w3id.org/og-caie/`.
Until the w3id redirect is merged they resolve nowhere and are used purely
as identifiers; the site above is the fallback.

## Licence

CC BY-SA 4.0 for the whole work. The licence does not extend to the quoted
source materials, which remain their publishers' property. This is an open
standards activity under development with a computational implementation
pathway. See `LICENSE.md`.
