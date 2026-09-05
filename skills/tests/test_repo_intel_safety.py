import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('repo_intel', ROOT / 'skills/abraxas-repo-intel/scripts/build_repo_intel.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


def test_heuristic_edges_are_not_observed_or_authorized():
    files = [{'path':'out/fixture.json','category':'artifact'}, {'path':'validator.py','category':'validator'}]
    edges = m.build_governance_graph(files)['edges'] + m.build_artifact_lineage(files)['edges']
    assert edges
    assert all(e.get('observed') is not True for e in edges)
    assert all(e['evidence_status'] == 'INFERRED' for e in edges)


def test_tiny_checkout_manifest_reads_only_supplied_root(tmp_path, monkeypatch):
    (tmp_path / 'module.py').write_text('value = 1\n')
    monkeypatch.setattr(m, 'REPO_ROOT', tmp_path)
    files = m.discover_files()
    assert [f['path'] for f in files] == ['module.py']
    assert files[0]['content_hash'] == m.get_file_hash(tmp_path / 'module.py')
