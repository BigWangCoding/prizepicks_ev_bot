"""
prizepicks_ev_bot/settings.py

Loads all configuration from config.yaml and .env into typed Python objects.

Usage:
    from prizepicks_ev_bot.settings import settings, config
    print(settings.odds_api_key)
    print(config.analytics.min_ev_pct)
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# ─────────────────────────────────────────────────────────────────
# .ENV SETTINGS
# ─────────────────────────────────────────────────────────────────


class Settings(BaseSettings):  # type: ignore[misc]
    """Loads secrets from .env or real environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    odds_api_key: SecretStr = Field(default=SecretStr("dev_placeholder"))
    database_url: str = Field(
        default="postgresql+asyncpg://ppev:password@localhost:5432/prizepicks_ev_bot"
    )
    redis_url: str = Field(default="redis://localhost:6379/0")
    discord_webhook_url: str = Field(default="")
    environment: str = Field(default="development")
    log_level: str = Field(default="INFO")
    bankroll: float = Field(default=1000.00)


# ─────────────────────────────────────────────────────────────────
# CONFIG.YAML MODELS
# ─────────────────────────────────────────────────────────────────

# yaml.safe_load returns an untyped dict; using Any here is correct and idiomatic —
# it lets the value lookups propagate cleanly without per-line suppressions.


class SchedulerConfig:
    def __init__(self, data: dict[str, Any]) -> None:
        self.game_day_interval_minutes: int = data["game_day_interval_minutes"]
        self.off_peak_interval_minutes: int = data["off_peak_interval_minutes"]
        self.pregame_interval_seconds: int = data["pregame_interval_seconds"]
        self.active_hours_et: str = data["active_hours_et"]


class AnalyticsConfig:
    def __init__(self, data: dict[str, Any]) -> None:
        self.min_ev_pct: float = data["min_ev_pct"]
        self.half_kelly: bool = data["half_kelly"]
        self.default_bankroll: float = data["default_bankroll"]
        self.min_match_confidence: float = data["min_match_confidence"]
        self.min_books_for_high_confidence: int = data["min_books_for_high_confidence"]


class BooksConfig:
    def __init__(self, data: dict[str, Any]) -> None:
        self.weights: dict[str, float] = data["weights"]


class PrizePicksConfig:
    def __init__(self, data: dict[str, Any]) -> None:
        self.payouts: dict[str, float] = data["payouts"]
        self.default_entry_type: str = data["default_entry_type"]


class MarketWidthConfig:
    def __init__(self, data: dict[str, Any]) -> None:
        self.tight_threshold: int = data["tight_threshold"]
        self.wide_threshold: int = data["wide_threshold"]


class AlertsConfig:
    def __init__(self, data: dict[str, Any]) -> None:
        self.discord_webhook_url: str = data["discord_webhook_url"]
        self.min_ev_pct_for_alert: float = data["min_ev_pct_for_alert"]
        self.min_confidence_for_alert: str = data["min_confidence_for_alert"]
        self.dedup_window_minutes: int = data["dedup_window_minutes"]


class AppConfig:
    """Parsed config.yaml — all tunable, non-secret parameters."""

    def __init__(self, data: dict[str, Any]) -> None:
        self.scheduler = SchedulerConfig(data["scheduler"])
        self.analytics = AnalyticsConfig(data["analytics"])
        self.books = BooksConfig(data["books"])
        self.prizepicks = PrizePicksConfig(data["prizepicks"])
        self.market_width = MarketWidthConfig(data["market_width"])
        self.alerts = AlertsConfig(data["alerts"])


# ─────────────────────────────────────────────────────────────────
# LOADERS
# ─────────────────────────────────────────────────────────────────


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, encoding="utf-8") as f:
        raw: dict[str, Any] = yaml.safe_load(f)
    return AppConfig(raw)


settings = get_settings()
config = get_config()
