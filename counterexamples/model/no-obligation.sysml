package NoObligation {
    doc /* Model counterexample: the assembly names a sponsor and affected
       populations but nothing relates them; the mission regards no
       population. M1-Obligation must reject the graph of this package. */
    item def Mission { attribute id : ScalarValues::String; }
    abstract part def Party;
    part def Organization :> Party;
    part def SponsorOrganization :> Organization;
    part def TestingOrganization :> Organization;
    part def AccountableOrganization :> Organization;
    part def AffectedPopulation :> Party;
    connection def Obligation { end sponsor : SponsorOrganization; end population : AffectedPopulation; }
    part def OgCaieEvaluation {
        part sponsor : SponsorOrganization;
        part testingOrg : TestingOrganization;
        part accountable : AccountableOrganization;
        part affected : AffectedPopulation[0..*];
    }
}
