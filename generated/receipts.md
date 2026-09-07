## Receipts

### Strict validation of the authoring view

```text
$ sysml model/og-caie.sysml -validate -strict
✓ package OGCAIE
✓ model/og-caie.sysml: no errors
(exit 0)
```
### The canonical model graph

`sysml -convert ttl` renders 18976 triples; the term map keeps 5712 (385 of them resolved ends computed by `scripts/prune_model.py`), within a budget of 6600. Conformance of the graph to the 12 wiring shapes M1 to M5: **conforms**.
