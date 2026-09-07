This page is a view. The model is the repository, and it holds more than the page shows: [Appendix A](appendix-explorer.md) opens the same model as a graph, and [Appendix D](appendix-toolchain.md) says how to run every check yourself.

:::{dropdown} For the shell: ask the graph, read the sources
- Rendered here: `generated/steps-evaluation.md`, `generated/wiring-evaluation.md`, `generated/wiring-table-evaluation.md`, `generated/sci-evaluation.md`, `generated/record-evaluation.md`, regenerated from the graphs by the gate (`checks/run-checks.sh`, the one script that runs every check and prints PASS or FAIL) and diffed byte for byte.
- Ask the graph: `ogc record`, `ogc record attestation-1`, `ogc view evaluation`, `ogc steps`, `ogc sci SCI-06`, `ogc term evidence`, `ogc term determination`, `ogc term attestation`, `ogc term trajectory`, `ogc rulings --term evidence`, `ogc sparql`.
- Read the sources: `model/og-caie.sysml`, `model/og-caie.model.ttl`, `vocabulary/epo.ttl`, `shapes/epo.shapes.ttl (S1 to S8)`, `shapes/model.shapes.ttl (M2 to M5)`, `track/measles-evaluation.ttl`, `counterexamples/`, `scripts/render_counterexamples.py`, `queries/coverage.rq`, `queries/traceback.rq`.
:::
