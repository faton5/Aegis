"""
Tests unitaires ciblés pour ReportService (création, doublons, rate limit, update).
"""
import pytest

from services.report_service import ReportService
from utils.rate_limiter import RateLimiter
from utils.anonymous_hasher import anonymous_hasher
from config.bot_config import bot_settings


@pytest.fixture(autouse=True)
def _ensure_hasher_configured():
    # Configurer un salt secret suffisant pour les tests
    bot_settings.reporter_salt_secret = "a" * 64
    # Forcer la ré-initialisation du hasher
    try:
        anonymous_hasher._initialized = False
    except Exception:
        pass
    assert anonymous_hasher.is_configured() is True


@pytest.mark.asyncio
async def test_create_report_success():
    rs = ReportService(db_client=None, rate_limiter=RateLimiter(max_actions=5, time_window=3600))
    report = await rs.create_report(
        user_id=123,
        guild_id=456,
        target_username="TargetUser",
        category="harassment",
        reason="Bad behavior",
        evidence=""
    )
    assert report is not None
    assert report.id in rs.active_reports


@pytest.mark.asyncio
async def test_duplicate_detection_prevents_second_report():
    rs = ReportService(db_client=None, rate_limiter=RateLimiter(max_actions=5, time_window=3600))
    r1 = await rs.create_report(123, 456, "TargetUser", "harassment", "Reason", "")
    assert r1 is not None
    # Même trio (reporter, guild, target) → doit être refusé
    r2 = await rs.create_report(123, 456, "TargetUser", "harassment", "Reason again", "")
    assert r2 is None


@pytest.mark.asyncio
async def test_rate_limit_blocks_second_report():
    rs = ReportService(db_client=None, rate_limiter=RateLimiter(max_actions=1, time_window=3600))
    r1 = await rs.create_report(999, 111, "UserA", "spam", "Reason", "")
    assert r1 is not None
    r2 = await rs.create_report(999, 111, "UserB", "spam", "Another reason", "")
    assert r2 is None  # bloqué par rate limit


class DummyDB:
    def __init__(self):
        self.called = False
        self.report = None

    async def update_report(self, report):
        self.called = True
        self.report = report
        return True


@pytest.mark.asyncio
async def test_update_report_status_calls_db():
    db = DummyDB()
    rs = ReportService(db_client=db, rate_limiter=RateLimiter())
    r = await rs.create_report(1, 2, "TUser", "other", "ok", "")
    assert r is not None
    ok = await rs.update_report_status(r.id, "validated", validator_id=42)
    assert ok is True
    assert db.called is True
    assert rs.active_reports[r.id].status == "validated"
