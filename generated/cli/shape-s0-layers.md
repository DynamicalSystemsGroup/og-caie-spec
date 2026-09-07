$ uv run -q ogc shape S0-Layers
# ogc shape S0-Layers @ <sha>
## S0-Layers  (shapes/epo.shapes.ttl)
target: epo:ServiceAgreement
counterexamples (executor mutations): requirements-before-agreement

property constraints (0):
(none)

sparql constraints (1):
  - S0 two layers (R-32): every item of the record pinned at the contract is generated no later
    than the requirement set, and every item pinned within the evaluation no earlier than the
    agreement.
      PREFIX epo: <https://w3id.org/og-caie/epo#>
      PREFIX ogc: <https://w3id.org/og-caie/>
      PREFIX prov: <http://www.w3.org/ns/prov#>
      SELECT $this ?value WHERE {
          $this prov:generatedAtTime ?ta ; ogc:inRecord ?rec . ?rs a epo:RequirementSet ;
              ogc:inRecord ?rec ; prov:generatedAtTime ?tr .
          ?value a ?cls ; ogc:inRecord ?rec ; prov:generatedAtTime ?t . ?cls ogc:pinnedAt ?layer
              .
          FILTER( (?layer = epo:contract && ?t > ?tr && NOT EXISTS { ?value a epo:Delivery } &&
              NOT EXISTS { ?value a epo:Acceptance })
               || (?layer = epo:evaluation && ?t < ?ta) )
      }
(exit 0)
