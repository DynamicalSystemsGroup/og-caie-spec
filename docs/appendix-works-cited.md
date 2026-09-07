# Appendix F: works cited

Every chapter closes with the sources it cites, and each of those lists is
derived from the graph rather than typed: the term references on the page
resolve to glossary terms, whose canonical and neighbouring citations name
a registered source with a locator; the steps tables name the canon each
step matches; the essentials tables name what each essential rests on; and
the bridge tables on the front page and the conclusion name the session
and the book behind it. This appendix aggregates those lists for the whole
work. The table below has one row per source in the register
(`sources/sources.ttl`, shown with its posture and licence note in the
Sources section of the standards chapter), in citation precedence, with
the pages that cite it; a source cited by no page says so. The
bibliography beneath it is rendered by MyST from `references.bib`, which
`scripts/render_bib.py` regenerates from the register: one entry per
source, keyed by the source's own BibTeX key (`ogc:bibkey`), with no
field the register does not state. The entries the hand-written file carried before
the renderer existed are kept and merged.

```{include} ../generated/cited-all.md
```

## Cited through the compilations

```{include} ../generated/cited-through.md
```

## The bibliography

```{bibliography}
```
