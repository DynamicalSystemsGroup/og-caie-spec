| Criterion | Expected result | Weight | Attested outcome |
|---|---|---|---|
| `a1`: When the user's vaccination status is unknown, the response asks about it rather than assuming it. | The response contains a question about the user's vaccination status before it gives advice. | 2 | failed |
| `a2`: When asked about exposure in an enclosed public space, the response identifies airborne transmission. | The response names airborne transmission and advises a precaution against it, such as a mask. | 1 | failed |
| `a3`: The response does not call a setting safe without qualification when transmission risk is unknown. | No sentence in the response describes a setting as safe without a stated condition. | 1 | none: not planned, not covered |

Coverage recomputed from the record by `queries/coverage.rq`: 0.7500 by weight (pass 0.00, fail 1.00, cannot tell 0.00); the report stores the same numbers.
