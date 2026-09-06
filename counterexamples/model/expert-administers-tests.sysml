package ExpertAdministersTests {
    doc /* Model counterexample: the domain expert applies probes to the test
       item, which is the evaluation operator's slot (rulings R-10, R-23).
       M5-PortsBelongToRoles must reject the graph of this package. */
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
        action agree; action scope { out dso : Dso; } action declareRequirements; action plan { out probes : Probe[1..*]; }
        action execute; action determineAndAttest; action report;
        succession first agree then scope; succession first scope then declareRequirements;
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
    part def DomainExpert :> Person { port dsoOut : DsoWrite; port probesToItem : ProbeWrite; }
    part def EvaluationTeam { part domainExpert : DomainExpert[1..*]; part operator : EvaluationOperator[1..*]; }
    part def ProbeDeriver :> Machine { port probesOut : ProbeWrite; port probesToOperator : ProbeWrite; }
    part def Recorder :> Machine { port dsoIn : ~DsoWrite; port probeIn : ~ProbeWrite; port recordToExecutive : RecordWrite; }
    part def TestingOrganization :> Organization { part accountExecutive : AccountExecutive; part team : EvaluationTeam; part probeDeriver : ProbeDeriver; part recorder : Recorder; }
    part def OgCaieEvaluation {
        interface dsoSeam : DsoSeam connect testingOrg.team.domainExpert.dsoOut to testingOrg.recorder.dsoIn;
        interface derivedProbeSeam : ProbeSeam connect testingOrg.probeDeriver.probesToOperator to testingOrg.team.operator.probesIn;
        interface probeRecordSeam : ProbeSeam connect testingOrg.probeDeriver.probesOut to testingOrg.recorder.probeIn;
        interface expertProbeRunSeam : ProbeSeam connect testingOrg.team.domainExpert.probesToItem to accountable.testItem.probesIn;
        interface operatorProbeRunSeam : ProbeSeam connect testingOrg.team.operator.probesToItem to accountable.testItem.probesIn;
        interface recordToExecutiveSeam : RecordSeam connect testingOrg.recorder.recordToExecutive to testingOrg.accountExecutive.recordIn;
        part sponsor : SponsorOrganization;
        part testingOrg : TestingOrganization;
        part accountable : AccountableOrganization;
        part affected : AffectedPopulation[0..*];
        perform action process : EvaluationProcess;
    }
}
