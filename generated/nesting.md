```{mermaid}
flowchart TB
  subgraph OUTER["Contracting lifecycle"]
    direction LR
    o_need[need] --> o_propose[propose] --> o_agree[agree] --> o_access[access] --> o_fulfil[["fulfil : EvaluationProcess"]] --> o_deliver[deliver] --> o_acceptDelivery[acceptDelivery]
  end
  subgraph INNER["fulfil, opened: the evaluation"]
    direction LR
    i_scope[scope] --> i_declareRequirements[declareRequirements] --> i_plan[plan] --> i_execute[execute] --> i_determineAndAttest[determineAndAttest] --> i_report[report]
  end
  i_report -- "Recommendation (from the evaluation operator), ReportApproval (from the domain expert), Report (from the report assembler)" --> o_deliver
  o_access -- "TestItemAccess (from the accountable organization)" --> i_execute
  o_agree -- "ServiceAgreement (from the account executive)" --> i_declareRequirements
  o_agree -- "StatementOfWork (from the sponsor organization)" --> i_scope
  classDef step fill:#37474f,stroke:#cfd8dc,stroke-width:1.5px,color:#ffffff;
  classDef black fill:#000000,stroke:#ffb300,stroke-width:3px,color:#ffffff;
  class o_need,o_propose,o_agree,o_access,o_deliver,o_acceptDelivery,i_scope,i_declareRequirements,i_plan,i_execute,i_determineAndAttest,i_report step;
  linkStyle default stroke:#90a4ae,stroke-width:1.5px;
  class o_fulfil black;
```

**View `nesting`: the nested lifecycle.** In focus: the two cycles as chains of steps, the fulfil step as a black box in the outer chain and opened as the inner chain, and the only wires that cross the boundary: what the contract hands in and what the evaluation hands back, bundled by item kind. Left out: the flows inside each chain, the parties, the parts and ports, the DSO as a parameter, and who performs which step (the two chapters before this one have them).
