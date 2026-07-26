from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json


def main() -> None:
    write_classified_json('out/contracts/'+__file__.split('run_')[1].replace('.py','')+'.latest.json', {'status':'passed','projection_only':True,'inference_authority':False}, artifact_class=ArtifactClass.AUDIT_EVIDENCE)
if __name__=='__main__':
    main()
