from __future__ import annotations
"""CLI entry point for Tutorial Genesys."""

import asyncio
import logging
import webbrowser
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

app = typer.Typer(name="genesys", help="Generate publication-ready AI tutorials for The Pulse")
console = Console()


def _setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


@app.command()
def pipeline(
    max_tutorials: int = typer.Option(3, help="Max tutorials to generate"),
    deploy: bool = typer.Option(False, help="Deploy to ai-evolution.com.au"),
    log_level: str = typer.Option("INFO", help="Log level"),
) -> None:
    """Run the full pipeline: select topics from Hunter -> generate tutorials."""
    _setup_logging(log_level)

    from tutorial_genesys.agents.orchestrator import Orchestrator

    async def _run():
        orch = Orchestrator()
        return await orch.run(max_tutorials=max_tutorials, deploy=deploy)

    result = asyncio.run(_run())

    console.print()
    console.print(Panel(
        f"[green]{len(result.successful)}[/green] tutorials generated, "
        f"[red]{len(result.failed)}[/red] failed",
        title="Pipeline Complete",
        border_style="green",
    ))

    if result.successful:
        table = Table(title="Generated Tutorials")
        table.add_column("Title", style="green")
        table.add_column("Score", justify="right")
        table.add_column("Words", justify="right")
        table.add_column("Status")
        for r in result.successful:
            table.add_row(
                r.tutorial.title[:50] if r.tutorial else "?",
                f"{r.review.overall_score:.0f}" if r.review else "?",
                str(r.tutorial.word_count) if r.tutorial else "?",
                r.manifest.deploy_status if r.manifest else "?",
            )
        console.print(table)

    if result.failed:
        console.print("\n[red]Failed:[/red]")
        for r in result.failed:
            console.print(f"  • {r.topic}: {r.error}")


@app.command()
def generate(
    topic: str = typer.Argument(help="Topic to generate a tutorial for"),
    deploy: bool = typer.Option(False, help="Deploy to ai-evolution.com.au"),
    log_level: str = typer.Option("INFO", help="Log level"),
) -> None:
    """Generate a single tutorial for a specific topic."""
    _setup_logging(log_level)

    from tutorial_genesys.agents.orchestrator import Orchestrator

    async def _run():
        orch = Orchestrator()
        return await orch.generate_single(topic=topic, deploy=deploy)

    result = asyncio.run(_run())

    if result.success and result.tutorial:
        console.print(Panel(
            f"[green]'{result.tutorial.title}'[/green]\n"
            f"Words: {result.tutorial.word_count} | "
            f"Score: {result.review.overall_score:.0f}" if result.review else "",
            title="Tutorial Generated",
            border_style="green",
        ))
        if result.manifest:
            console.print(f"Saved to: {result.manifest.html_file}")
    else:
        console.print(f"[red]Failed:[/red] {result.error}")


@app.command()
def preview(
    tutorial_id: str = typer.Argument(default="", help="Tutorial ID or slug"),
    log_level: str = typer.Option("INFO", help="Log level"),
) -> None:
    """Preview a generated tutorial in the browser."""
    _setup_logging(log_level)
    from tutorial_genesys.config.settings import get_settings

    output_dir = Path(get_settings().output_dir)
    if not output_dir.exists():
        console.print("[yellow]No output directory found. Generate a tutorial first.[/yellow]")
        return

    # Find the tutorial
    candidates = sorted(output_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
    target = None

    if tutorial_id:
        for d in candidates:
            if tutorial_id in d.name:
                target = d
                break
    else:
        # Default to most recent
        for d in candidates:
            if (d / "index.html").exists():
                target = d
                break

    if target and (target / "index.html").exists():
        html_path = target / "index.html"
        console.print(f"Opening: {html_path}")
        webbrowser.open(f"file://{html_path.resolve()}")
    else:
        console.print("[yellow]No tutorial found. Generate one first.[/yellow]")
        if candidates:
            console.print("Available:")
            for d in candidates[:10]:
                if d.is_dir():
                    console.print(f"  • {d.name}")


@app.command("list")
def list_tutorials(
    log_level: str = typer.Option("INFO", help="Log level"),
) -> None:
    """List all generated tutorials."""
    _setup_logging(log_level)
    from tutorial_genesys.config.settings import get_settings
    import json

    output_dir = Path(get_settings().output_dir)
    if not output_dir.exists():
        console.print("[yellow]No tutorials generated yet.[/yellow]")
        return

    table = Table(title="Generated Tutorials")
    table.add_column("#", justify="right", style="dim")
    table.add_column("Title", style="green")
    table.add_column("Slug")
    table.add_column("Difficulty")
    table.add_column("Words", justify="right")

    count = 0
    for d in sorted(output_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        meta_file = d / "meta.json"
        if meta_file.exists():
            count += 1
            meta = json.loads(meta_file.read_text())
            table.add_row(
                str(count),
                meta.get("title", "?")[:50],
                d.name,
                meta.get("difficulty", "?"),
                str(meta.get("word_count", "?")),
            )

    if count:
        console.print(table)
    else:
        console.print("[yellow]No tutorials found in output directory.[/yellow]")


@app.command()
def topics(
    limit: int = typer.Option(10, help="Max topics to show"),
    log_level: str = typer.Option("INFO", help="Log level"),
) -> None:
    """Show top topics from Tutorial Hunter ready for tutorial generation."""
    _setup_logging(log_level)

    from tutorial_genesys.integration.topic_selector import TopicSelector

    async def _run():
        selector = TopicSelector()
        return await selector.select_topics(max_topics=limit)

    candidates = asyncio.run(_run())

    if not candidates:
        console.print("[yellow]No topics available. Run tutorial-hunter first.[/yellow]")
        return

    table = Table(title="Top Topics for Tutorial Generation")
    table.add_column("#", justify="right", style="dim")
    table.add_column("Topic", style="green")
    table.add_column("Potential", justify="right")
    table.add_column("Sources", justify="right")
    table.add_column("Avg Quality", justify="right")
    for i, c in enumerate(candidates, 1):
        table.add_row(
            str(i), c.topic[:50],
            f"{c.tutorial_potential:.1f}",
            str(len(c.source_tutorials)),
            f"{c.avg_quality:.0f}",
        )
    console.print(table)


if __name__ == "__main__":
    app()
