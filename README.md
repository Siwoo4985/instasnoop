# InstaSnoop

[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Testing](https://img.shields.io/badge/tests-7%20passed-emerald.svg)](tests/test_scanner.py)

InstaSnoop is a high-performance, command-line interface (CLI) tool designed for Open Source Intelligence (OSINT) username investigations. It aggregates profile metadata, extracts contact intelligence from biographies, checks availability across 30+ sites concurrently, and generates premium interactive HTML report dashboards.

---

## Why InstaSnoop? (Differentiators & Advantages)

Compared to traditional OSINT tools (like Osintgram, Sherlock, or Maigret), InstaSnoop is engineered to solve common pain points in modern social media reconnaissance:

*   **Zero API Keys Required (100% Free):** You do not need expensive official Meta APIs, Google Custom Search APIs, or paid scraping subscriptions. InstaSnoop runs entirely on open-source, login-free web scraping and search dorking.
*   **Fully Concurrent Processing:** While other tools scan platforms sequentially (taking minutes), InstaSnoop queries Instagram, crawls search engine footprints, and audits 30+ platforms *simultaneously* using asynchronous client pooling, delivering results in seconds.
*   **No-Login Safety Sandbox:** Instagram heavily blocks unauthenticated requests. InstaSnoop automatically detects blocks and falls back to a sandbox simulation mode. This ensures your investigation flow never crashes and keeps your IP address safe from aggressive bans.
*   **Self-Contained Glassmorphic Dashboard:** Instead of raw text logs or complex dashboard setups, InstaSnoop generates a single-file, zero-dependency HTML report. It features a premium dark cosmic theme, click-to-copy buttons, real-time grid filtering, and print-to-PDF optimization.
*   **Precision Intelligence Parsing:** Traditional scrapers often mistake email domains (e.g., `@example.com` inside `user@example.com`) as social media handles. InstaSnoop's parser uses negative lookbehinds to prevent handle leakage, assuring high data accuracy.
*   **Built-in Rate Limit Protection:** Integrates socket semaphores and request jitter to stagger outbound checks, preventing target servers from flagging your IP.

---

## Key Features

*   **Asynchronous Scan Engine:** Audits username availability across 30+ major platforms concurrently.
*   **Cookie Session Support:** Supports an optional browser session cookie (`sessionid`) to bypass login walls for real-time Instagram queries.
*   **Simulation Fallback:** Generates detailed profile and footprint simulations when blocked, keeping workflows active.
*   **Regex Entity Extractor:** Captures email addresses, phone numbers, and cross-platform handles from bio descriptions.
*   **Interactive HTML Reports:** Generates responsive glassmorphic HTML files optimized for browser viewing and paper printing.

---

## Terminal Preview

```text
 ██████╗███╗   ██╗ ██████╗  ██████╗ ██████╗ 
██╔════╝████╗  ██║██╔═══██╗██╔═══██╗██╔══██╗
██║     ██╔██╗ ██║██║   ██║██║   ██║██████╔╝
██║     ██║╚██╗██║██║   ██║██║   ██║██╔═══╝ 
╚██████╗██║ ╚████║╚██████╔╝╚██████╔╝██║     
 ╚═════╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚═╝     

[ InstaSnoop OSINT Tool v0.1.0 ]
Investigate Instagram targets and discover digital footprints across 30+ sites.

Scan complete!

╭─── Instagram Profile Details (Simulation Fallback) ───╮
│   Full Name    Siwoo Park                             │
│   Username     @siwoo                                 │
│   Bio          Tech Enthusiast | OSINT Researcher     │
│                email: siwoo.park@example.com          │
│                phone: +82 10-1234-5678                │
│   Followers    1,240                                  │
│   Following    450                                    │
│   Privacy      Public                                 │
╰───────────────────────────────────────────────────────╯
╭─────────────────── Intelligence Extracted ────────────────────╮
│   Email Extracted     siwoo.park@example.com                  │
│   Phone Extracted     +82 10-1234-5678                        │
╰───────────────────────────────────────────────────────────────╯
               Cross-Platform Username Detection (Matches)
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Site 1        ┃ Link 1                ┃ Site 2      ┃ Link 2                 ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩
│ GitHub        │ https://github.com/s… │ Twitter/X   │ https://x.com/siwoo    │
│ GitLab        │ https://gitlab.com/si…│ Reddit      │ https://www.reddit.co… │
└───────────────┴───────────────────────┴─────────────┴────────────────────────┘

✓ JSON Report Saved: reports/siwoo_report.json
✓ HTML Interactive Report Saved: reports/siwoo_report.html
```

---

## Install

Ensure you have Python 3.10+ and the uv package manager installed.

```bash
# Clone the repository
git clone https://github.com/Siwoo4985/instasnoop.git
cd instasnoop

# Create a virtual environment and sync dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

---

## Usage

### Command Syntax
```bash
instasnoop [COMMAND] [ARGS] [OPTIONS]
```

### Options & Arguments
| Argument/Option | Alias | Description | Default |
| :--- | :--- | :--- | :--- |
| `username` | (Argument) | The target Instagram handle to scan | (Required) |
| `--cookie` | `-c` | Instagram login cookie string (`sessionid=...`) | `None` |
| `--output-dir`| `-o` | Directory to save JSON and HTML reports | `reports` |

### Quick Examples
```bash
# Run a simulated default scan
instasnoop scan victim_username

# Run an authenticated live scan using a browser session cookie
instasnoop scan victim_username --cookie "sessionid=YOUR_COOKIE_VALUE; ds_user_id=..."

# Run a scan and output reports to a custom directory
instasnoop scan victim_username --output-dir audit_results

# Check version
instasnoop version
```

---

## Session Cookie Retrieval

Instagram restricts anonymous public profile queries. To get real-time info, supply an active session cookie:

1. Log in to Instagram on your desktop browser.
2. Press `F12` to open the Developer Tools, and navigate to **Application** (Chrome/Edge) or **Storage** (Firefox).
3. Under **Cookies**, click `https://www.instagram.com`.
4. Copy the value of the `sessionid` cookie.
5. Execute the scan command passing the cookie inside quotes:
   ```bash
   instasnoop scan target_user --cookie "sessionid=XXXXXX"
   ```

---

## Project Architecture

```
instasnoop/
├── instasnoop/
│   ├── __init__.py      # Package versioning
│   ├── cli.py           # Typer CLI definition and Rich output panels
│   ├── scanner.py       # Orchestration layer with shared httpx client pooling
│   ├── instagram.py     # Instagram scraper with simulation fallback
│   ├── crossplatform.py # 30+ platform checker with asyncio.Semaphore limits
│   ├── dorker.py        # Web search crawler querying DuckDuckGo
│   ├── parser.py        # Regex analyzer for emails, phone numbers, and socials
│   └── reporter.py      # JSON and XSS-protected glassmorphic HTML report renderer
├── tests/
│   └── test_scanner.py  # Pytest suite covering regex edge cases and mocks
├── pyproject.toml       # Project metadata and dependencies
└── README.md            # Documentation
```

---

## Tests

To run the test suite, execute `pytest` in your virtual environment:

```bash
pytest
```

---

## License & Disclaimers

This project is licensed under the MIT License - see LICENSE for details.

> [!WARNING]
> This tool is developed strictly for educational, cybersecurity research, and authorized investigative purposes. Automated scraping of Instagram profiles without prior consent violates Meta's Terms of Service. Use responsibly.
