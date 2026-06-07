import asyncio
import os
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from .scanner import SnoopScanner
from .reporter import ReportGenerator
from . import __version__

app = typer.Typer(help="InstaSnoop: A powerful Instagram OSINT CLI & Report Tool")
console = Console()

BANNER = """
 ██████╗███╗   ██╗ ██████╗  ██████╗ ██████╗ 
██╔════╝████╗  ██║██╔═══██╗██╔═══██╗██╔══██╗
██║     ██╔██╗ ██║██║   ██║██║   ██║██████╔╝
██║     ██║╚██╗██║██║   ██║██║   ██║██╔═══╝ 
╚██████╗██║ ╚████║╚██████╔╝╚██████╔╝██║     
 ╚═════╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚═╝     
"""

def show_banner():
    console.print(Text(BANNER, style="bold purple"))
    console.print(Panel(
        f"[bold white]InstaSnoop OSINT Tool v{__version__}[/bold white]\n"
        "[dim]Investigate Instagram targets and discover digital footprints across 30+ sites.[/dim]",
        border_style="purple",
        expand=False
    ))

@app.command()
def scan(
    username: str = typer.Argument(..., help="The target Instagram username to scan"),
    cookie: str = typer.Option(None, "--cookie", "-c", help="Optional Instagram login session cookie for live profile scraping"),
    output_dir: str = typer.Option("reports", "--output-dir", "-o", help="Directory where scan reports will be saved")
):
    """Scan a target username across Instagram, search engine dorks, and 30+ platforms."""
    show_banner()
    
    clean_username = username.strip().replace("@", "")
    scanner = SnoopScanner(clean_username, cookie)
    
    # Run async scan in sync context
    async def run_scan():
        scan_data = None
        with Progress(
            SpinnerColumn(spinner_name="dots12", style="purple"),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(description="Initializing OSINT engines...", total=None)
            
            def update_status(msg: str):
                progress.update(task, description=f"[bold cyan]{msg}[/bold cyan]")
                
            scan_data = await scanner.scan(console_status_callback=update_status)
            progress.update(task, description="[bold green]Scan complete![/bold green]")
        return scan_data

    try:
        scan_result = asyncio.run(run_scan())
    except Exception as e:
        console.print(Panel(
            f"[bold red]Scan Failed:[/bold red] {str(e)}\n\n"
            "[dim]Please check your network connection, username syntax, or session cookie validity.[/dim]",
            title="[bold red]Error[/bold red]",
            border_style="red"
        ))
        raise typer.Exit(code=1)
        
    profile = scan_result.get("profile", {})
    parsed_intel = scan_result.get("parsed_intelligence", {})
    cp_results = scan_result.get("cross_platform_results", [])
    
    # 1. Print Profile Panel
    console.print()
    profile_table = Table(show_header=False, box=None, padding=(0, 2))
    profile_table.add_column("Key", style="bold cyan")
    profile_table.add_column("Value")
    
    profile_table.add_row("Full Name", profile.get("full_name", ""))
    profile_table.add_row("Username", f"@{profile.get('username', '')}")
    profile_table.add_row("Bio", profile.get("biography", ""))
    profile_table.add_row("Followers", f"{profile.get('follower_count', 0):,}")
    profile_table.add_row("Following", f"{profile.get('following_count', 0):,}")
    profile_table.add_row("Posts", f"{profile.get('post_count', 0):,}")
    profile_table.add_row("Privacy", "[bold red]Private[/bold red]" if profile.get("is_private") else "[bold green]Public[/bold green]")
    profile_table.add_row("Verified", "[bold blue]Yes[/bold blue]" if profile.get("is_verified") else "No")
    
    state_msg = " [yellow](Simulation Fallback - Cookie not provided)[/yellow]" if profile.get("simulated") else ""
    console.print(Panel(
        profile_table,
        title=f"[bold purple]Instagram Profile Details{state_msg}[/bold purple]",
        border_style="purple"
    ))

    # 2. Print Parsed Intel Panel
    if parsed_intel.get("emails") or parsed_intel.get("phones") or parsed_intel.get("socials"):
        intel_table = Table(show_header=False, box=None, padding=(0, 2))
        intel_table.add_column("Type", style="bold green")
        intel_table.add_column("Value")
        
        for email in parsed_intel.get("emails", []):
            intel_table.add_row("Email Extracted", email)
        for phone in parsed_intel.get("phones", []):
            intel_table.add_row("Phone Extracted", phone)
        for social in parsed_intel.get("socials", []):
            intel_table.add_row(f"Handle ({social['platform']})", f"@{social['handle']}")
            
        console.print(Panel(
            intel_table,
            title="[bold green]Intelligence Extracted from Biography[/bold green]",
            border_style="green"
        ))

    # 3. Print Cross-Platform Results in a dense 3-column table
    found_profiles = [r for r in cp_results if r.get("exists")]
    
    if found_profiles:
        cp_table = Table(title="[bold white]Cross-Platform Username Detection (Matches Found)[/bold white]", show_header=True, border_style="cyan")
        cp_table.add_column("Site 1", style="bold cyan")
        cp_table.add_column("Link 1", style="underline dim")
        cp_table.add_column("Site 2", style="bold cyan")
        cp_table.add_column("Link 2", style="underline dim")
        
        # Chunk found profiles into pairs to make a dense 2-column wide table (reducing vertical space by half)
        for i in range(0, len(found_profiles), 2):
            p1 = found_profiles[i]
            p2 = found_profiles[i+1] if i+1 < len(found_profiles) else {"site": "", "url": ""}
            
            cp_table.add_row(
                p1["site"], p1["url"],
                p2["site"], p2["url"]
            )
        console.print(cp_table)
    else:
        console.print("[dim italic]No matching usernames found on the checked platforms.[/dim italic]\n")

    # 4. Generate Reports
    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, f"{clean_username}_report.json")
    html_path = os.path.join(output_dir, f"{clean_username}_report.html")
    
    reporter = ReportGenerator(clean_username)
    reporter.generate_json_report(scan_result, json_path)
    reporter.generate_html_report(scan_result, html_path)
    
    console.print()
    console.print(f"[bold green]✓[/bold green] JSON Report Saved: [underline green]file://{os.path.abspath(json_path)}[/underline green]")
    console.print(f"[bold green]✓[/bold green] HTML Interactive Report Saved: [underline green]file://{os.path.abspath(html_path)}[/underline green]")
    console.print()

@app.command()
def version():
    """Display the version of InstaSnoop."""
    show_banner()

if __name__ == "__main__":
    app()
