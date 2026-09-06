## Receipts

### Strict validation

```text
$ sysml model/og-caie.sysml -validate -strict
✓ package OGCAIE
✓ model/og-caie.sysml: no errors
(exit 0)
```
### Every requirement holds on the measles run

```text
$ sysml model/og-caie.sysml -satisfy=OGCAIE::Runs
✓ package OGCAIE
✓ satisfy sci01 holds
✓ satisfy sci02 holds
✓ satisfy sci03 holds
✓ satisfy sci04 holds
✓ satisfy sci05 holds
✓ satisfy sci06 holds
✓ satisfy sci07 holds
✓ satisfy sci08 holds
✓ satisfy sci09 holds
(exit 0)
```
### The counterexample fails, as it must

```text
$ sysml model/og-caie.sysml counterexamples/untested-counted-covered.sysml -satisfy=UntestedCountedCovered
✓ package OGCAIE
✓ package UntestedCountedCovered
✗ satisfy sci07 fails
  Required condition evaluated to false: ev.recorder.a3.covered implies ev.recorder.a3.attestationCount >= 1
(exit 1)
```
