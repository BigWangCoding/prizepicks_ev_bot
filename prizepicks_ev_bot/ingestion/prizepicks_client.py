"""
prizepicks_ev_bot/ingestion/prizepicks_client.py

Fetches live NBA player projections from PrizePicks.
PrizePicks doesn't have a public API, so we use their
internal API endpoint discovered via browser DevTools.
"""

from __future__ import annotations

import logging
from typing import Any, Final, cast

from prizepicks_ev_bot.ingestion.base_client import BaseClient
from prizepicks_ev_bot.ingestion.stats_map import normalize_stat_type
from prizepicks_ev_bot.models import EntryType, PrizePicksLine

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────

PP_BASE_URL: Final[str] = "https://api.prizepicks.com"

# Query parameters to send with every request.
# Find these by watching the Network tab in Chrome DevTools.
PP_PARAMS: Final[dict[str, Any]] = {
    "league_id": 7,  # 7 = NBA
    "per_page": 250,  # max projections per response
    "single_stat": "true",  # only single-stat props, not combos
    "in_play": "false",  # exclude in-game props
}

# PrizePicks needs these extra headers or they block the request.
# Found by inspecting the Request Headers in Chrome DevTools.
PP_HEADERS: Final[dict[str, Any]] = {
    "Referer": "https://app.prizepicks.com/",
    "Origin": "https://app.prizepicks.com",
}


class PrizePicksClient(BaseClient):
    """
    Client for fetching NBA player projections from PrizePicks.
    Inherits retry logic, timeouts, and logging from BaseClient.
    """

    def __init__(self) -> None:
        super().__init__(
            base_url=PP_BASE_URL,
            timeout_seconds=15.0,  # PP can be slow, give it extra time
            max_retries=3,
            extra_headers=PP_HEADERS,
        )

    async def get_live_lines(self, standard_lines: bool = True) -> list[PrizePicksLine]:
        """
        Fetch all active NBA projections from PrizePicks.

        Returns:
            List of PrizePicksLine objects ready for matching
            against sharp book odds. Empty list if no lines found.
        """
        logger.info("Fetching PrizePicks NBA projections...")

        # Step 1: Make the HTTP request
        # FILL IN: call self.get() with the right path and params
        raw = cast(dict[str, Any], await self.get("/projections", PP_PARAMS))

        # Step 2: Pull out the two lists from the response
        # FILL IN: get "data" and "included" from the raw dict
        # Use .get() with a default of [] so it never crashes on missing keys

        data = raw.get("data", [])

        included = raw.get("included", [])

        # Step 3: Build the player lookup dictionary
        # FILL IN: loop through included, find items where type == "new_player",
        # and build a dict mapping id -> attributes
        player_lookup = _build_player_lookup(included)

        # Step 4: Parse each projection
        lines: list[PrizePicksLine] = []

        for projection in data:
            line = self._parse_projection(projection, player_lookup, standard_lines)

            if line is None:
                continue

            lines.append(line)
            # FILL IN: call _parse_projection() and append to lines if not None
            ...

        logger.info("PrizePicks: fetched %d active NBA lines.", len(lines))
        return lines

    def _parse_projection(
        self,
        projection: dict[str, Any],
        player_lookup: dict[str, dict[str, Any]],
        standard_lines: bool = True,
    ) -> PrizePicksLine | None:
        """
        Convert one raw projection dict into a PrizePicksLine.
        Returns None if the projection should be skipped.
        """
        attributes = projection.get("attributes", {})
        player_id = projection["relationships"]["new_player"]["data"]["id"]
        player = player_lookup.get(player_id, None)
        if player is None:
            return None
        if player.get("combo", False):
            return None

        odds_type = attributes.get("odds_type")

        if standard_lines and odds_type != "standard":
            return None

        stat_type = normalize_stat_type(attributes["stat_type"])
        line_score = attributes.get("line_score")

        if player is None:
            logger.warning("Player %s doesn't exist!", player_id)
            return None
        if stat_type is None:
            return None
        return PrizePicksLine(
            player_name=player.get("display_name", ""),
            team=player.get("team", ""),
            stat_type=stat_type,
            line=line_score,
            entry_type=EntryType.POWER,
            num_legs=2,
        )


def _build_player_lookup(included: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """
    Build a dictionary mapping player ID -> player attributes.
    This lets us look up a player's name and team by their ID
    in O(1) time instead of searching the list every time.

    Args:
        included: The "included" list from the PrizePicks response.

    Returns:
        Dict like {"player_99": {"name": "LeBron James", "team": "LAL"}}
    """
    # FILL IN: loop through included, only keep items where type == "new_player"
    # return a dict mapping item["id"] -> item["attributes"]
    player_map = dict()
    for player in included:
        if player["type"] == "new_player":
            player_map[player["id"]] = player["attributes"]
    return player_map
