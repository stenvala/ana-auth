"""Tests for backup_db.py retention policy logic."""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from backup_db import (
    cleanup_backups,
    is_last_day_of_month,
    parse_backup_date,
    should_keep,
)


class TestIsLastDayOfMonth:
    def test_january_31(self) -> None:
        assert is_last_day_of_month(date(2026, 1, 31)) is True

    def test_january_30(self) -> None:
        assert is_last_day_of_month(date(2026, 1, 30)) is False

    def test_february_28_non_leap(self) -> None:
        assert is_last_day_of_month(date(2026, 2, 28)) is True

    def test_february_29_leap(self) -> None:
        assert is_last_day_of_month(date(2024, 2, 29)) is True

    def test_february_28_leap(self) -> None:
        assert is_last_day_of_month(date(2024, 2, 28)) is False

    def test_april_30(self) -> None:
        assert is_last_day_of_month(date(2026, 4, 30)) is True

    def test_all_12_months(self) -> None:
        last_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        for month, last_day in enumerate(last_days, 1):
            assert is_last_day_of_month(date(2026, month, last_day)) is True


class TestParseBackupDate:
    def test_valid_filename(self) -> None:
        assert parse_backup_date("2026-03-21-main.gz") == date(2026, 3, 21)

    def test_different_suffix(self) -> None:
        assert parse_backup_date("2026-01-15-dev.gz") == date(2026, 1, 15)

    def test_invalid_filename(self) -> None:
        assert parse_backup_date("backup.gz") is None

    def test_invalid_date(self) -> None:
        assert parse_backup_date("2026-13-01-main.gz") is None


class TestShouldKeep:
    def test_recent_file_kept(self) -> None:
        today = date(2026, 3, 22)
        assert should_keep(date(2026, 3, 21), today) is True

    def test_exactly_30_days_kept(self) -> None:
        today = date(2026, 3, 22)
        assert should_keep(date(2026, 2, 20), today) is True

    def test_31_days_non_monthly_deleted(self) -> None:
        today = date(2026, 3, 22)
        assert should_keep(date(2026, 2, 19), today) is False

    def test_old_last_day_of_month_kept(self) -> None:
        today = date(2026, 3, 22)
        # Jan 31 is 50 days old but is last day of month
        assert should_keep(date(2026, 1, 31), today) is True

    def test_monthly_older_than_365_deleted(self) -> None:
        today = date(2026, 3, 22)
        # Dec 31 2024 is >365 days old
        assert should_keep(date(2024, 12, 31), today) is False

    def test_monthly_within_365_kept(self) -> None:
        today = date(2026, 3, 22)
        # Jun 30 2025 is ~265 days old, last day of month
        assert should_keep(date(2025, 6, 30), today) is True


class TestCleanupBackups:
    def test_deletes_expired_files(self, tmp_path: Path) -> None:
        today = date(2026, 3, 22)
        # Create files: recent (keep), old non-monthly (delete), old monthly (keep)
        (tmp_path / "2026-03-21-main.gz").touch()  # 1 day old - keep
        (tmp_path / "2026-02-01-main.gz").touch()  # 49 days old, not last day - delete
        (tmp_path / "2026-01-31-main.gz").touch()  # 50 days old, last day of Jan - keep

        deleted = cleanup_backups(tmp_path, today)

        assert len(deleted) == 1
        assert deleted[0].name == "2026-02-01-main.gz"
        assert (tmp_path / "2026-03-21-main.gz").exists()
        assert not (tmp_path / "2026-02-01-main.gz").exists()
        assert (tmp_path / "2026-01-31-main.gz").exists()

    def test_ignores_non_matching_files(self, tmp_path: Path) -> None:
        today = date(2026, 3, 22)
        (tmp_path / "readme.txt").touch()
        (tmp_path / "other.gz").touch()

        deleted = cleanup_backups(tmp_path, today)
        assert len(deleted) == 0
