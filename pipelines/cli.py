#!/usr/bin/env python3
"""
SPYGLASS CLI - Main entry point
"""
import click
import asyncio
import webbrowser
import sys
from rich.console import Console
from rich.panel import Panel

console = Console()

@click.group()
def cli():
    """ SPYGLASS - SEO Intelligence Platform -by https://github.com/ssecgroup"""
    pass

@cli.command()
@click.argument('url')
@click.option('--auto-pdf', is_flag=True, help='Auto-download PDF')
def scan(url, auto_pdf):
    """Scan a website for SEO issues"""
    console.print(Panel.fit(
        "[bold cyan] SPYGLASS[/bold cyan] - Starting scan...",
        border_style="cyan"
    ))
    console.print(f"[bold]Target:[/bold] {url}")
    console.print("[yellow]Scan feature coming soon![/yellow]")

@cli.command()
def version():
    """Show version information"""
    try:
        from spyglass import __version__
        console.print(f"[cyan]SPYGLASS[/cyan] version [bold]{__version__}[/bold]")
    except ImportError:
        console.print("[cyan]SPYGLASS[/cyan] version [bold]0.1.0[/bold]")

@cli.command()
@click.argument('url')
def quick(url):
    """Quick scan - just basic info"""
    import requests
    from bs4 import BeautifulSoup
    
    console.print(f"[bold]Quick scan:[/bold] {url}")
    
    try:
        response = requests.get(url, timeout=10, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        console.print(f"[green]✓[/green] Status: {response.status_code}")
        console.print(f"[green]✓[/green] Title: {soup.title.string if soup.title else 'N/A'}")
        console.print(f"[green]✓[/green] Size: {len(response.text):,} bytes")
        console.print(f"[green]✓[/green] Time: {response.elapsed.total_seconds():.2f}s")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")

def main():
    """Main entry point"""
    cli()

if __name__ == '__main__':
    main()
