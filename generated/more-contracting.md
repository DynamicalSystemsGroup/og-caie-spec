This page is a view. The model is the repository, and it holds more than the page shows: [Appendix B](appendix-explorer.md) opens the same model as a graph, and [Appendix E](appendix-toolchain.md) says how to run every check yourself.

:::{dropdown} For the shell: ask the graph, read the sources
- Rendered here: `generated/steps-contracting.md`, `generated/wiring-contracting.md`, `generated/wiring-table-contracting.md`, `generated/sci-contracting.md`, `generated/record-contracting.md`, regenerated from the graphs by the gate (`checks/run-checks.sh`, the one script that runs every check and prints PASS or FAIL) and diffed byte for byte.
- Ask the graph: `ogc view contracting`, `ogc views`, `ogc steps`, `ogc sci SCI-10`, `ogc term mission`, `ogc term customer`, `ogc term provider`, `ogc term contract`, `ogc verify iso-iec-17000-2020`, `ogc sparql`.
- Read the sources: `model/og-caie.sysml`, `model/og-caie.model.ttl`, `vocabulary/epo.ttl`, `shapes/epo.shapes.ttl (S0, S9)`, `shapes/model.shapes.ttl (M1, M5)`, `ogc/views.py`, `track/measles-evaluation.ttl`.
:::
