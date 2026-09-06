package UntestedCountedCovered {
    doc /* Counterexample: a run that reports the third criterion as covered
       although no attestation exists for it. SCI-07 must reject it, so
       `sysml model/og-caie.sysml counterexamples/untested-counted-covered.sysml
       -satisfy=UntestedCountedCovered` exits non-zero. Everything else is
       the MeaslesRun. Coverage is reported as 1.0, the number an honest
       recomputation would not give. */

    part def PaddedRun :> OGCAIE::Runs::MeaslesRun {
        part :>> recorder {
            item :>> a3 { attribute :>> attestationCount = 0; attribute :>> covered = true; attribute :>> coveredWeight = 1.0; }
        }
        part :>> coverageCalculator {
            item :>> report { attribute :>> coverage = 1.0; }
        }
    }

    part paddedRun : PaddedRun;

    requirement sci07 : OGCAIE::CoverageRecomputable { subject ev = paddedRun; }

    verification def PaddedRunCase {
        objective { verify sci07; }
    }
}
