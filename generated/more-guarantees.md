This page is a view. The model is the repository, and it holds more than the page shows: [Appendix A](appendix-explorer.md) opens the same model as a graph, and [Appendix D](appendix-toolchain.md) says how to run every check yourself.

:::{dropdown} For the shell: ask the graph, read the sources
- Rendered here: `generated/sci-guarantees.md`, `generated/executor.md`, regenerated from the graphs by the gate (`checks/run-checks.sh`, the one script that runs every check and prints PASS or FAIL) and diffed byte for byte.
- Ask the graph: `ogc execute`, `ogc execute --mutate skip-access`, `ogc sci SCI-11`, `ogc term "test coverage"`, `ogc term "requirements traceability"`, `ogc sparql`.
- Read the sources: `ogc/executor.py`, `queries/coverage.rq`, `queries/traceback.rq`, `shapes/epo.shapes.ttl`, `model/og-caie.model.ttl`, `tests/test_executor.py`.
:::
