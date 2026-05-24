"""
prizepicks_ev_bot/cli/main.py

Entry point for the CLI. Invoked via the `ppev` command after install.

Commands:
  ppev live       — show live +EV feed (Phase 5)
  ppev history    — historical picks by date (Phase 5)
  ppev stats      — overall hit rate & ROI (Phase 6)
  ppev backtest   — run backtest over date range (Phase 6)
  ppev bankroll   — set bankroll for Kelly sizing (Phase 5)
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

app = typer.Typer(
    name="ppev",
    help="OddsJam-style +EV basketball analyzer for PrizePicks.",
    add_completion=False,
)
console = Console()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        banner = Text()
        banner.append("PrizePicks EV Bot\n", style="bold green")
        banner.append("OddsJam-style +EV Analyzer for NBA Player Props\n\n", style="white")
        banner.append("Run ", style="white")
        banner.append("ppev --help", style="bold cyan")
        banner.append(" to see available commands.", style="white")
        console.print(Panel(banner, border_style="green"))


@app.command()
def live(
    min_ev: float = typer.Option(2.0, "--min-ev", help="Minimum EV% to display"),
    stat: list[str] = typer.Option([], "--stat", help="Filter by stat type"),
    confidence: str = typer.Option("low", "--confidence", help="low | medium | high"),
    max_width: int = typer.Option(9999, "--max-width", help="Max market width in cents"),
    sort: str = typer.Option("ev", "--sort", help="Sort by: ev | kelly | width"),
) -> None:
    """[Phase 5] Show the live +EV feed."""
    console.print("[yellow]Live feed coming in Phase 5.[/yellow]")
    console.print(f"Filters → min_ev={min_ev}, stat={stat}, confidence={confidence}")


@app.command()
def history(
    date: str = typer.Argument(..., help="Date in YYYY-MM-DD format"),
) -> None:
    """[Phase 5] Show all picks surfaced on a specific date."""
    console.print("[yellow]History coming in Phase 5.[/yellow]")
    console.print(f"Date: {date}")


@app.command()
def stats() -> None:
    """[Phase 6] Show overall hit rate and ROI."""
    console.print("[yellow]Stats coming in Phase 6.[/yellow]")


@app.command()
def backtest(
    date_range: str = typer.Argument(..., help="YYYY-MM-DD:YYYY-MM-DD"),
) -> None:
    """[Phase 6] Run a backtest over a historical date range."""
    console.print("[yellow]Backtest coming in Phase 6.[/yellow]")
    console.print(f"Range: {date_range}")


@app.command()
def bankroll(
    amount: float = typer.Argument(..., help="Your bankroll in USD"),
) -> None:
    """[Phase 5] Set your bankroll for Kelly Criterion bet sizing."""
    console.print(f"[green]Bankroll set to ${amount:,.2f}[/green]")
    console.print("[dim](Persistence coming in Phase 4)[/dim]")


if __name__ == "__main__":
    app()
