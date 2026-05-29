"""
prizepicks_ev_bot/ingestion/stat_map.py

Translates raw stat type strings from any data source into our
canonical StatType enum. Every source uses different terminology
for the same stat — this is the single place that resolves them.

When you see "UNMAPPED STAT TYPE" in your logs, add the new string here.
"""

from __future__ import annotations

import logging

from prizepicks_ev_bot.models import StatType

logger = logging.getLogger(__name__)

STAT_ALIAS_MAP: dict[str, StatType] = {
    # POINTS
    "points": StatType.POINTS,
    "pts": StatType.POINTS,
    "player_points": StatType.POINTS,
    "player points": StatType.POINTS,
    # REBOUNDS
    "rebounds": StatType.REBOUNDS,
    "reb": StatType.REBOUNDS,
    "player_rebounds": StatType.REBOUNDS,
    "player rebounds": StatType.REBOUNDS,
    "total rebounds": StatType.REBOUNDS,
    # ASSISTS
    "assists": StatType.ASSISTS,
    "ast": StatType.ASSISTS,
    "player_assists": StatType.ASSISTS,
    "player assists": StatType.ASSISTS,
    # 3-POINTERS MADE
    "3-pointers made": StatType.THREE_PM,
    "3pt made": StatType.THREE_PM,
    "3-pt made": StatType.THREE_PM,
    "3pm": StatType.THREE_PM,
    "3 pointers made": StatType.THREE_PM,
    "threes": StatType.THREE_PM,
    "three pointers made": StatType.THREE_PM,
    "player_threes": StatType.THREE_PM,
    "player threes": StatType.THREE_PM,
    "player_three_pointers_made": StatType.THREE_PM,
    # 3-POINTERS ATTEMPTED
    "3-pt attempted": StatType.THREE_PA,
    # STEALS
    "steals": StatType.STEALS,
    "stl": StatType.STEALS,
    "player_steals": StatType.STEALS,
    "player steals": StatType.STEALS,
    # BLOCKS
    "blocks": StatType.BLOCKS,
    "blk": StatType.BLOCKS,
    "blocked shots": StatType.BLOCKS,
    "player_blocks": StatType.BLOCKS,
    "player blocks": StatType.BLOCKS,
    # BLOCKS + STEALS
    "blks+stls": StatType.BA,
    "player_blocks_steals": StatType.BA,
    # TURNOVERS
    "turnovers": StatType.TURNOVERS,
    "tov": StatType.TURNOVERS,
    "player_turnovers": StatType.TURNOVERS,
    "player turnovers": StatType.TURNOVERS,
    # COMBOS — Points + Rebounds + Assists
    "pts+reb+ast": StatType.PRA,
    "pts+rebs+asts": StatType.PRA,
    "p+r+a": StatType.PRA,
    "points+rebounds+assists": StatType.PRA,
    "pts_reb_ast": StatType.PRA,
    "player_points_rebounds_assists": StatType.PRA,
    # COMBOS — Points + Rebounds
    "pts+reb": StatType.PR,
    "pts+rebs": StatType.PR,
    "points+rebounds": StatType.PR,
    "pts_reb": StatType.PR,
    "player_points_rebounds": StatType.PR,
    # COMBOS — Points + Assists
    "pts+ast": StatType.PA,
    "pts+asts": StatType.PA,
    "points+assists": StatType.PA,
    "pts_ast": StatType.PA,
    "player_points_assists": StatType.PA,
    # COMBOS — Rebounds + Assists
    "reb+ast": StatType.RA,
    "rebs+asts": StatType.RA,
    "rebounds+assists": StatType.RA,
    "reb_ast": StatType.RA,
    "player_rebounds_assists": StatType.RA,
    # FANTASY SCORE
    "fantasy score": StatType.FANTASY_SCORE,
    "fantasy_score": StatType.FANTASY_SCORE,
    "fantasy points": StatType.FANTASY_SCORE,
    # Field Goals Made
    "fg made": StatType.FGM,
    # Two Pointers Attempted
    "two pointers attempted": StatType.FG2A,
    "fg attempted": StatType.FG2A,
    # Two Pointers Made
    "two pointers made": StatType.FG2M,
    # Free Throws Attempted
    "free throws attempted": StatType.FTA,
    # Free Throws Made
    "free throws made": StatType.FTM,
    # Two Pointers Made
    # Offensive Rebounds
    "offensive rebounds": StatType.OFFENSIVE_REBOUNDS,
    # Defensive Rebounds
    "defensive rebounds": StatType.DEFENSIVE_REBOUNDS,
    # Dunks
    "dunks": StatType.DUNKS,
    # Double-Doubles
    "double-double": StatType.DD,
    # Triple-Doubles
    "triple-double": StatType.TD,
    # Personal Fouls
    "personal fouls": StatType.PF,
    # 1st quarter 3 minutes
    "points - 1st 3 minutes": StatType.POINTS1Q3M,
    "assists - 1st 3 minutes": StatType.ASSISTS1Q3M,
    "rebounds - 1st 3 minutes": StatType.REBOUNDS1Q3M,
}


def normalize_stat_type(raw: str) -> StatType | None:
    """
    Convert a raw stat string from any source into our canonical StatType.

    Returns None if unrecognized — callers should log and skip those props
    rather than crashing.

    Example:
        normalize_stat_type("player_threes")  →  StatType.THREE_PM
        normalize_stat_type("gibberish")      →  None
    """
    key = raw.strip().lower()
    stat_type = STAT_ALIAS_MAP.get(key)

    if stat_type is None:
        logger.warning("UNMAPPED STAT TYPE: '%s' — add it to stat_map.py if valid.", raw)

    return stat_type
