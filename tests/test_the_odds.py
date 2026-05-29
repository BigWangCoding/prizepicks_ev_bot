import asyncio

from prizepicks_ev_bot.ingestion.the_odds_api_client import TheOddsAPIClient


async def main() -> None:
    client = TheOddsAPIClient()
    lines = await client.get_live_lines()

    print(f"\nFetched {len(lines)} lines\n")
    for line in lines:
        print(
            f"{line.player_name:20} | "
            f" {line.stat_type.value:15} | "
            f" {line.over_odds} | "
            f"{line.under_odds} | "
            f"{line.line} | "
            f"{line.source}"
        )


asyncio.run(main())
