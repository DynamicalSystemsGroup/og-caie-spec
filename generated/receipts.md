## Receipts

### Strict validation of the authoring view

```text
$ sysml model/og-caie.sysml -validate -strict
✓ package OGCAIE
✓ model/og-caie.sysml: no errors
(exit 0)
```
### The canonical model graph

`sysml -convert ttl` renders 11240 triples; the term map keeps 3166 (174 of them resolved ends computed by `scripts/prune_model.py`), within a budget of 3600. Conformance of the graph to the 10 wiring shapes M1 to M5: **conforms**.
