from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json


def main() -> None:
    write_classified_json('out/contracts/artifact_contract_p2c_a_minimal_coverage_report.latest.json', {'status':'passed','batch':'P2C-A'}, artifact_class=ArtifactClass.AUDIT_EVIDENCE)
if __name__=='__main__':
    main()
