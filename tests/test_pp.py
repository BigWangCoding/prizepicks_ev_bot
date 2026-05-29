import asyncio

from prizepicks_ev_bot.ingestion.prizepicks_client import PrizePicksClient


async def main() -> None:
    client = PrizePicksClient()
    lines = await client.get_live_lines()

    print(f"\nFetched {len(lines)} lines\n")
    for line in lines[:5]:
        print(f"{line.player_name:20} | {line.stat_type.value:15} | {line.line}")


asyncio.run(main())
