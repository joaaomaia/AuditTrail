import logging
import os

import pandas as pd
import pytest

from audittrail import AuditTrail


def create_frames():
    df1 = pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c']})
    df2 = pd.DataFrame({'A': [1, 2, 4], 'B': ['a', 'b', 'd']})
    return df1, df2


def test_take_snapshot_attributes(tmp_path):
    df, _ = create_frames()
    audit = AuditTrail(auto_detect_types=True)
    audit.take_snapshot(df, name='s1')
    snap = audit.snapshots['s1']
    assert snap['shape'] == df.shape
    assert 'num_summary' in snap
    assert 'cat_summary' in snap


def test_duplicate_snapshot_error():
    df, _ = create_frames()
    audit = AuditTrail()
    audit.take_snapshot(df, name='s1')
    with pytest.raises(ValueError):
        audit.take_snapshot(df, name='s1')


def test_compare_snapshots_nonexistent():
    df, _ = create_frames()
    audit = AuditTrail()
    audit.take_snapshot(df, 's1')
    with pytest.raises(ValueError):
        audit.compare_snapshots('s1', 'missing')


def test_describe_snapshot_runs(capsys):
    df, _ = create_frames()
    audit = AuditTrail()
    audit.take_snapshot(df, 's1')
    audit.describe_snapshot('s1')
    captured = capsys.readouterr()
    assert 'Descrição do snapshot' in captured.out


def test_logging_creation(tmp_path):
    df, _ = create_frames()
    log_file = tmp_path / 'audit.log'
    audit = AuditTrail(enable_logging=True)
    audit.logger.handlers.clear()
    handler = logging.FileHandler(log_file)
    audit.logger.addHandler(handler)
    audit.take_snapshot(df, 's1')
    handler.close()
    assert log_file.exists()


def test_no_log_when_disabled(tmp_path):
    df, _ = create_frames()
    log_file = tmp_path / 'audit.log'
    audit = AuditTrail(enable_logging=False)
    audit.logger.handlers.clear()
    handler = logging.FileHandler(log_file)
    audit.logger.addHandler(handler)
    audit.take_snapshot(df, 's1')
    handler.close()
    assert not log_file.exists()
