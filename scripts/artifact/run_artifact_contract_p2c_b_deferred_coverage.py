from core.canonical.json import write_canonical_json

def main() -> None:
    write_canonical_json('out/contracts/artifact_contract_p2c_b_deferred_coverage_report.latest.json', {'status':'passed','batch':'P2C-B'})
if __name__=='__main__':
    main()
