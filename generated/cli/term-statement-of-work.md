$ uv run -q ogc term 'statement of work'
# ogc term statement of work @ <sha>
## statement of work  (statement-of-work)

  The sponsor's decisions about the work to be performed under the contract; here, for each
  affected population, whether it is interviewed, with its stakeholder needs documented as
  input, or represented by the domain expert. A scope-of-work judgment: representation is the
  common case, interviews are reserved for underrepresented stakeholders or underdocumented
  needs because of the effort they cost. Decided with the agreement, pinned at the contract,
  consumed by the scope step, and traceable either way.

class: adopted
also: SOW; scope of work
canonical:
  sevocab (rank 2, heldLocally) statement of work, p. 406  [machine]
    "statement of the expected outcomes and outline of the work required to achieve the
    outcomes"
scope note:
  Ruling R-40: a boundary item between the contract and its fulfilment; the sponsor decides, per
  affected population, interview or representation; the record must show the decision and the
  evaluation must realize it.
binding: sysml item def StatementOfWork, port def StatementOfWorkWrite, seams
    statementOfWorkSeam and statementOfWorkToExecutiveSeam; epo:StatementOfWork with epo:decides
    engagement decisions
related: contract (contract); evaluation customer (evaluation-customer); mission (mission);
    stakeholder (stakeholder)
matches: exactMatch SEVOCAB statement of work, p. 406
EPO classes naming it: epo:EngagementDecision, epo:StatementOfWork
derives from rulings: R-40
concerns naming it: C-46 (ruled) the sponsor's decision to interview or represent each affected
    population had no item of its own
essentials stated in it: SCI-10
Popper crosswalk: auxiliary assumption, first layer (pinned at the contract)
(exit 0)
