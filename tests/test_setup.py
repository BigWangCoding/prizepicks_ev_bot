"""
tests/test_setup.py

Smoke tests — verify the project setup is correct.
Run with: uv run pytest tests/test_setup.py -v
All 6 should pass immediately after setup.
"""

import importlib


def test_models_import() -> None:
    """All core models should import without errors."""
    from prizepicks_ev_bot.models import (
        CLVRecord,
        Confidence,
        EntryType,
        EVResult,
        LineMovement,
        MatchedMarket,
        OddsLine,
        OutcomeResult,
        PrizePicksLine,
        Side,
        StatType,
    )
    assert StatType.POINTS == "points"
    assert Side.OVER == "over"
    assert Confidence.HIGH == "high"


def test_stat_type_enum_values() -> None:
    """Verify all expected stat types exist."""
    from prizepicks_ev_bot.models import StatType
    expected = ["points", "rebounds", "assists", "three_pointers_made", "steals", "blocks"]
    for val in expected:
        assert any(s.value == val for s in StatType), f"Missing StatType: {val}"


def test_odds_line_market_width_computed() -> None:
    """OddsLine should auto-compute market_width on creation."""
    from prizepicks_ev_bot.models import OddsLine, StatType
    line = OddsLine(
        player_name="LeBron James",
        team="LAL",
        stat_type=StatType.POINTS,
        line=24.5,
        over_odds=-115,
        under_odds=-108,
        source="fanduel",
    )
    assert line.market_width == abs(-115 - (-108))  # == 7


def test_config_loads() -> None:
    """config.yaml should load and expose expected values."""
    from prizepicks_ev_bot.settings import get_config
    cfg = get_config()
    assert cfg.analytics.min_ev_pct == 2.0
    assert cfg.books.weights["fanduel"] == 0.40
    assert abs(sum(cfg.books.weights.values()) - 1.0) < 0.001, "Book weights must sum to 1.0"


def test_logging_setup() -> None:
    """Logging setup should not raise."""
    from prizepicks_ev_bot.logging_config import get_logger, setup_logging
    setup_logging(level="DEBUG", fmt="text")
    logger = get_logger("test")
    logger.info("Logging is working")


def test_all_modules_importable() -> None:
    """Every package should be importable (catches syntax errors early)."""
    modules = [
        "prizepicks_ev_bot",
        "prizepicks_ev_bot.models",
        "prizepicks_ev_bot.settings",
        "prizepicks_ev_bot.logging_config",
        "prizepicks_ev_bot.ingestion",
        "prizepicks_ev_bot.normalization",
        "prizepicks_ev_bot.analytics",
        "prizepicks_ev_bot.storage",
        "prizepicks_ev_bot.scheduler",
        "prizepicks_ev_bot.alerts",
        "prizepicks_ev_bot.cli",
        "prizepicks_ev_bot.backtesting",
    ]
    for module in modules:
        imported = importlib.import_module(module)
        assert imported is not None, f"Failed to import: {module}"
