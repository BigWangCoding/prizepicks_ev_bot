"""
prizepicks_ev_bot/models.py

Shared Pydantic data models used across every module.
These are the data contracts — define them once, import everywhere.
No logic lives here, only structure and validation.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


# ─────────────────────────────────────────────────────────────────
# ENUMS
# ─────────────────────────────────────────────────────────────────

class StatType(str, Enum):
    """Canonical stat types. All sources are normalized to these values."""
    POINTS = "points"
    REBOUNDS = "rebounds"
    ASSISTS = "assists"
    THREE_PM = "three_pointers_made"
    STEALS = "steals"
    BLOCKS = "blocks"
    TURNOVERS = "turnovers"
    PRA = "pts_reb_ast"
    PR = "pts_reb"
    PA = "pts_ast"
    RA = "reb_ast"
    FANTASY_SCORE = "fantasy_score"


class Side(str, Enum):
    OVER = "over"
    UNDER = "under"


class Confidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EntryType(str, Enum):
    POWER = "power"
    FLEX = "flex"


# ─────────────────────────────────────────────────────────────────
# RAW INGESTION MODELS
# ─────────────────────────────────────────────────────────────────

class OddsLine(BaseModel):
    """
    A single prop line from a sharp sportsbook.
    Both over AND under odds are required — we need both sides to remove vig.
    """
    id: UUID = Field(default_factory=uuid4)
    player_name: str
    team: str
    stat_type: StatType
    line: float
    over_odds: int                    # American odds e.g. -115
    under_odds: int                   # American odds e.g. -108
    source: str                       # "fanduel", "draftkings", "betmgm", "caesars"
    market_width: float = Field(default=0.0)
    fetched_at: datetime = Field(default_factory=datetime.utcnow)

    def model_post_init(self, __context: object) -> None:
        object.__setattr__(self, "market_width", abs(self.over_odds - self.under_odds))

    @field_validator("over_odds", "under_odds")
    @classmethod
    def validate_american_odds(cls, v: int) -> int:
        # Valid American odds are >= +100 or <= -100.
        # Values between -99 and +99 indicate a parsing error.
        if -100 < v < 100:
            raise ValueError(
                f"Invalid American odds value: {v}. "
                "Odds must be >= +100 or <= -100. Check ingestion source."
            )
        return v


class PrizePicksLine(BaseModel):
    """
    A single player projection from PrizePicks.
    PrizePicks uses fixed multipliers, not American odds —
    implied odds are reverse-engineered in the analytics layer.
    """
    id: UUID = Field(default_factory=uuid4)
    player_name: str
    team: str
    stat_type: StatType
    line: float
    entry_type: EntryType
    num_legs: int = Field(ge=2, le=6)
    is_active: bool = True
    fetched_at: datetime = Field(default_factory=datetime.utcnow)


# ─────────────────────────────────────────────────────────────────
# NORMALIZED / MATCHED MODELS
# ─────────────────────────────────────────────────────────────────

class MatchedMarket(BaseModel):
    """
    A PrizePicks line successfully matched to one or more sharp book lines.
    This is the input to the analytics engine.
    """
    id: UUID = Field(default_factory=uuid4)
    canonical_player: str
    stat_type: StatType
    pp_line: PrizePicksLine
    sharp_lines: list[OddsLine]
    match_confidence: float = Field(ge=0.0, le=1.0)
    matched_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def num_books(self) -> int:
        return len(self.sharp_lines)


# ─────────────────────────────────────────────────────────────────
# ANALYTICS OUTPUT MODELS
# ─────────────────────────────────────────────────────────────────

class EVResult(BaseModel):
    """
    The fully computed +EV result for a single matched market.
    All CLI output columns come from this model.
    """
    id: UUID = Field(default_factory=uuid4)
    matched_market_id: UUID

    # Player / Market info
    canonical_player: str
    team: str
    stat_type: StatType
    pp_line: float

    # Core OddsJam-style columns
    recommended_side: Side
    pp_implied_odds: int              # what PP is effectively offering (American)
    no_vig_fair_odds: int             # sharp consensus fair odds after vig removal
    sharp_consensus_prob: float       # no-vig win probability (0.0 – 1.0)

    # EV & sizing
    ev_pct: float                     # profit margin per $100
    kelly_fraction: float
    rec_bet_size: float               # half-Kelly dollar recommendation

    # Confidence signals
    market_width: float
    num_books_agreeing: int
    confidence: Confidence

    computed_at: datetime = Field(default_factory=datetime.utcnow)


class LineMovement(BaseModel):
    """Tracks when a sharp book's odds move between pipeline runs."""
    player_name: str
    stat_type: StatType
    source: str
    prev_over_odds: int
    curr_over_odds: int
    cents_moved: float
    moved_toward: Side | Literal["none"]
    is_sharp_move: bool
    detected_at: datetime = Field(default_factory=datetime.utcnow)


# ─────────────────────────────────────────────────────────────────
# BACKTESTING MODELS
# ─────────────────────────────────────────────────────────────────

class OutcomeResult(BaseModel):
    """Actual box score result for a previously surfaced EV pick."""
    ev_result_id: UUID
    canonical_player: str
    stat_type: StatType
    pp_line: float
    actual_value: float
    recommended_side: Side
    hit: bool
    game_date: datetime


class CLVRecord(BaseModel):
    """Closing Line Value: did our pick beat the closing sharp odds?"""
    ev_result_id: UUID
    open_sharp_fair_odds: int
    close_sharp_fair_odds: int
    clv: float
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
