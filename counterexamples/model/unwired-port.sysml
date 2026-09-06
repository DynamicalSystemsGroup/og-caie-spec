package UnwiredPort {
    doc /* Model counterexample: the recorder has a port no seam reaches.
       M2-Part must reject the graph of this package. Everything
       else is a minimal, correctly wired assembly. */
    item def Dso { attribute id : ScalarValues::String; }
    item def Probe { attribute id : ScalarValues::String; }
    item def Rec { attribute id : ScalarValues::String; }
    port def DsoWrite { out item i : Dso; }
    port def ProbeWrite { out item i : Probe; }
    port def RecordWrite { out item i : Rec; }
    interface def DsoSeam { end supplier : DsoWrite; end consumer : ~DsoWrite; }
    interface def ProbeSeam { end supplier : ProbeWrite; end consumer : ~ProbeWrite; }
    interface def RecordSeam { end supplier : RecordWrite; end consumer : ~RecordWrite; }
    action def EvaluationProcess {
        out record : Rec;
        action scope { out dso : Dso; } action declareRequirements; action plan { out probes : Probe[1..*]; }
        action execute; action determineAndAttest; action report;
        succession first scope then declareRequirements;
        succession first declareRequirements then plan; succession first plan then execute;
        succession first execute then determineAndAttest; succession first determineAndAttest then report;
    }
    abstract part def Party { attribute name : ScalarValues::String; }
    part def Organization :> Party;
    part def Person :> Party;
    part def Machine :> Party;
    part def SponsorOrganization :> Organization;
    part def AccountExecutive :> Person { port recordIn : ~RecordWrite; }
    part def EvaluationOperator :> Person { port probesIn : ~ProbeWrite; port probesToItem : ProbeWrite; }
    part def TestItem :> Machine { port probesIn : ~ProbeWrite; }
    part def AccountableOrganization :> Organization { part testItem : TestItem; }
    part def AffectedPopulation :> Party;
    part def DomainExpert :> Person { port dsoOut : DsoWrite; }
    part def EvaluationTeam { part domainExpert : DomainExpert[1..*]; part operator : EvaluationOperator[1..*]; }
    part def ProbeDeriver :> Machine { port probesOut : ProbeWrite; }
    part def Recorder :> Machine { port dsoIn : ~DsoWrite; port orphanIn : ~DsoWrite; port recordToExecutive : RecordWrite; }
    part def TestingOrganization :> Organization { part accountExecutive : AccountExecutive; part team : EvaluationTeam; part probeDeriver : ProbeDeriver; part recorder : Recorder; }
    part def OgCaieEvaluation {
        interface dsoSeam : DsoSeam connect testingOrg.team.domainExpert.dsoOut to testingOrg.recorder.dsoIn;
        interface derivedProbeSeam : ProbeSeam connect testingOrg.probeDeriver.probesOut to testingOrg.team.operator.probesIn;
        interface probeRunSeam : ProbeSeam connect testingOrg.team.operator.probesToItem to accountable.testItem.probesIn;
        interface recordToExecutiveSeam : RecordSeam connect testingOrg.recorder.recordToExecutive to testingOrg.accountExecutive.recordIn;
        part sponsor : SponsorOrganization;
        part testingOrg : TestingOrganization;
        part accountable : AccountableOrganization;
        part affected : AffectedPopulation[0..*];
        perform action process : EvaluationProcess;
    }
}
