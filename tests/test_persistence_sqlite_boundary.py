"""Real temporary SQLite transactions, synthetic data, no live One Mind adapter.

The schedules are explicit and deterministic. WAL permits a committed writer
while an existing reader retains its snapshot. These tests do not establish
cross-database, multi-process or production-service correctness.
"""

import sqlite3
from contextlib import closing

import pytest

from core.canonical.json import canonical_hash
from core.evaluation.persistence_shadow import compaction_admission, recall_boundary

ROLES = ("claim", "enrichment", "materialized_source")


@pytest.fixture
def database(tmp_path):
    path = tmp_path / "synthetic-memory.sqlite"
    with closing(sqlite3.connect(path, isolation_level=None)) as db:
        assert db.execute("PRAGMA journal_mode=WAL").fetchone()[0] == "wal"
        db.executescript(
            "CREATE TABLE meta (epoch INTEGER, publication TEXT);"
            "INSERT INTO meta VALUES (2, 'CLEAN');"
            "CREATE TABLE evidence (role TEXT PRIMARY KEY, revision TEXT);"
            "CREATE TABLE projection (epoch INTEGER, policy TEXT, state_hash TEXT, summary_hash TEXT);"
        )
        db.executemany("INSERT INTO evidence VALUES (?, 'r1')", [(r,) for r in ROLES])
        db.execute(
            "INSERT INTO projection VALUES (2, 'p1', ?, NULL)",
            (canonical_hash(state()),),
        )
    return path


def state():
    return {"decision": {"value": "old", "source_ref": "source:r1"}}


def record(reader, role):
    revision = reader.execute(
        "SELECT revision FROM evidence WHERE role=?", (role,)
    ).fetchone()[0]
    return {"source_ref": "source:a", "role": role, "revision": revision}


def publish(writer):
    writer.execute("BEGIN IMMEDIATE")
    writer.execute("UPDATE meta SET epoch=3, publication='DIRTY'")
    writer.execute("UPDATE evidence SET revision='r2'")
    writer.execute("UPDATE meta SET epoch=4, publication='CLEAN'")
    writer.commit()


@pytest.mark.parametrize("pause_after", [1, 2])
def test_actual_autocommit_read_skew_is_detected(database, pause_after):
    with (
        closing(sqlite3.connect(database, isolation_level=None)) as reader,
        closing(sqlite3.connect(database, isolation_level=None)) as writer,
    ):
        begin = reader.execute("SELECT epoch FROM meta").fetchone()[0]
        records = [record(reader, role) for role in ROLES[:pause_after]]
        publish(writer)
        records.extend(record(reader, role) for role in ROLES[pause_after:])
        end, publication = reader.execute(
            "SELECT epoch, publication FROM meta"
        ).fetchone()
        # Negative control: the unguarded path really assembled mixed revisions.
        assert {r["revision"] for r in records} == {"r1", "r2"}
        assert (
            recall_boundary(
                begin, end, publication, {"source:a": "r1"}, records, set(ROLES)
            )
            == "RETRY"
        )
        retry = [record(reader, role) for role in ROLES]
        assert (
            recall_boundary(4, 4, "CLEAN", {"source:a": "r2"}, retry, set(ROLES))
            == "READY"
        )


def test_one_transaction_keeps_complete_old_snapshot_after_new_commit(database):
    with (
        closing(sqlite3.connect(database, isolation_level=None)) as reader,
        closing(sqlite3.connect(database, isolation_level=None)) as writer,
    ):
        reader.execute("BEGIN")
        begin = reader.execute("SELECT epoch FROM meta").fetchone()[0]
        records = [record(reader, ROLES[0])]
        publish(writer)
        records.extend(record(reader, role) for role in ROLES[1:])
        end, publication = reader.execute(
            "SELECT epoch, publication FROM meta"
        ).fetchone()
        assert begin == end == 2
        assert (
            recall_boundary(
                begin, end, publication, {"source:a": "r1"}, records, set(ROLES)
            )
            == "READY"
        )
        reader.commit()
        assert reader.execute("SELECT epoch FROM meta").fetchone()[0] == 4
        # READY describes the bound old snapshot, not latest-at-consumption.


def test_separate_reader_connections_do_not_share_snapshot_automatically(database):
    with (
        closing(sqlite3.connect(database, isolation_level=None)) as old_reader,
        closing(sqlite3.connect(database, isolation_level=None)) as fresh_reader,
        closing(sqlite3.connect(database, isolation_level=None)) as writer,
    ):
        old_reader.execute("BEGIN")
        records = [record(old_reader, ROLES[0])]
        publish(writer)
        records.extend(record(fresh_reader, role) for role in ROLES[1:])
        # Sampling epoch only on the old connection would conceal the write.
        assert old_reader.execute("SELECT epoch FROM meta").fetchone()[0] == 2
        assert (
            recall_boundary(2, 2, "CLEAN", {"source:a": "r1"}, records, set(ROLES))
            == "NOT_COMPUTABLE"
        )
        old_reader.rollback()


def test_failed_atomic_publication_rolls_back_all_evidence(database):
    with closing(sqlite3.connect(database, isolation_level=None)) as db:
        with pytest.raises(RuntimeError, match="injected"):
            try:
                db.execute("BEGIN IMMEDIATE")
                db.execute("UPDATE meta SET epoch=3, publication='DIRTY'")
                db.execute("UPDATE evidence SET revision='r2' WHERE role='claim'")
                raise RuntimeError("injected publication failure")
            except RuntimeError:
                db.rollback()
                raise
        epoch, publication = db.execute(
            "SELECT epoch, publication FROM meta"
        ).fetchone()
        records = [record(db, role) for role in ROLES]
        assert epoch == 2
        assert {r["revision"] for r in records} == {"r1"}
        assert (
            recall_boundary(
                epoch, epoch, publication, {"source:a": "r1"}, records, set(ROLES)
            )
            == "READY"
        )
        # Single atomic database rollback only, not cross-store recovery.


@pytest.mark.parametrize("intervention", ["none", "correction", "deletion", "policy"])
def test_compare_and_swap_closes_check_then_publish_race(database, intervention):
    frozen = state()
    digest = canonical_hash(frozen)
    assert (
        compaction_admission(
            frozen,
            frozen,
            frozen,
            frozen_epoch=2,
            current_epoch=2,
            frozen_policy="p1",
            current_policy="p1",
        )
        == "READY"
    )
    with (
        closing(sqlite3.connect(database, isolation_level=None)) as reader,
        closing(sqlite3.connect(database, isolation_level=None)) as writer,
    ):
        # A real committed change occurs AFTER the pure check above.
        if intervention == "correction":
            writer.execute(
                "UPDATE projection SET epoch=4, state_hash=?",
                (canonical_hash({"decision": "new"}),),
            )
        elif intervention == "deletion":
            writer.execute("DELETE FROM projection")
        elif intervention == "policy":
            writer.execute("UPDATE projection SET policy='p2'")
        result = reader.execute(
            "UPDATE projection SET summary_hash=? WHERE epoch=? AND policy=? AND state_hash=?",
            (digest, 2, "p1", digest),
        )
        assert result.rowcount == (1 if intervention == "none" else 0)
        summaries = reader.execute("SELECT summary_hash FROM projection").fetchall()
        if intervention == "none":
            assert summaries == [(digest,)]
        else:
            assert all(row[0] is None for row in summaries)
