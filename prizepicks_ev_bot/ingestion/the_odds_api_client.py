from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime, timedelta
from typing import Any, Final, cast

from prizepicks_ev_bot.ingestion.base_client import BaseClient
from prizepicks_ev_bot.ingestion.stats_map import normalize_stat_type
from prizepicks_ev_bot.models import OddsLine
from prizepicks_ev_bot.settings import settings

logger = logging.getLogger(__name__)

ODDS_API_BASE_URL: Final = "https://api.the-odds-api.com"
EVENTS_PATH: Final = "/v4/sports/basketball_nba/events"
EVENT_ODDS_PATH: Final = "/v4/sports/basketball_nba/events/{event_id}/odds"
now = datetime.now(UTC)
later = now + timedelta(hours=36)
EVENTS_PARAMS: Final[dict[str, Any]] = {
    "apiKey": settings.odds_api_key.get_secret_value(),  # your key from .env
    "commenceTimeFrom": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
    "commenceTimeTo": later.strftime("%Y-%m-%dT%H:%M:%SZ"),
}


EVENT_ODDS_PARAMS: Final[dict[str, Any]] = {
    "apiKey": settings.odds_api_key.get_secret_value(),
    "regions": "us",  # us sportsbooks only
    "markets": ",".join(
        [  # which prop markets to fetch
            "player_points",
            "player_rebounds",
            "player_assists",
            "player_threes",
            "player_steals",
            "player_blocks",
            "player_points_rebounds_assists",
            "player_points_rebounds",
            "player_points_assists",
            "player_rebounds_assists",
            "player_fantasy_points",
            "player_blocks_steals",
        ]
    ),
    "oddsFormat": "american",  # gives us -115, +110 style odds
}
ODDS_API_EXTRA_HEADERS: Final[dict[str, Any]] = {}


class TheOddsAPIClient(BaseClient):
    def __init__(self) -> None:
        super().__init__(
            base_url=ODDS_API_BASE_URL,
            timeout_seconds=15,
            max_retries=3,
            extra_headers=ODDS_API_EXTRA_HEADERS,
        )

    async def get_live_lines(self) -> list[OddsLine]:
        logger.info("Fetching TheOddsAPI NBA projections...")

        raw = await self.get(EVENTS_PATH, EVENTS_PARAMS)
        raw = cast(list[dict[str, Any]], raw)
        lines: list[OddsLine] = []

        for event in raw:
            event_id = event.get("id", "")
            path = EVENT_ODDS_PATH.format(event_id=event_id)
            request = cast(dict[str, Any], await self.get(path, EVENT_ODDS_PARAMS))
            player_info = self._get_players_info(request)

            if player_info is None:
                continue

            for key, value in player_info.items():
                obj = self._convert_player_info(key, value)
                if obj is None:
                    continue
                lines.append(obj)

        return lines

    def _convert_player_info(self, key: str, value: dict[str, Any]) -> OddsLine | None:
        player_name, stat_type, book, point = key.split("|")
        stat_type_n = normalize_stat_type(stat_type)
        if stat_type_n is None:
            return None

        if not point or point == "None":
            return None
        over_line = value.get("Over_line")
        under_line = value.get("Under_line")

        if over_line is None or under_line is None:
            return None
        if not book:
            return None

        return OddsLine(
            player_name=player_name,
            stat_type=stat_type_n,
            line=float(point),
            team="",
            over_odds=over_line,
            under_odds=under_line,
            source=book,
        )

    def _get_players_info(self, event: dict[str, Any]) -> dict[str, dict[str, Any]]:
        player_map: dict[str, Any] = dict()
        bookmakers = event.get("bookmakers", [])

        for book in bookmakers:
            markets = book.get("markets", [])

            for market in markets:
                market_type = market.get("key", "")
                outcomes = market.get("outcomes", [])
                for outcome in outcomes:
                    player_name = outcome.get("description", "")
                    point = outcome.get("point")
                    book_key = book.get("key" or "").strip()
                    name = f"{player_name}|{market_type}|{book_key}|{point}"
                    if name not in player_map:
                        player_map[name] = dict()

                    stat_type = outcome.get("name", "")
                    merge_dict = {
                        f"{stat_type}_line": outcome.get("price", None),
                    }
                    player_map[name] = player_map[name] | merge_dict
        return player_map


async def main() -> None:
    client = TheOddsAPIClient()
    await client.get_live_lines()


if __name__ == "__main__":
    asyncio.run(main())
