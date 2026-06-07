# InstaSnoop 🕵️‍♂️

InstaSnoop is a premium, feature-rich command-line interface (CLI) tool designed for Open Source Intelligence (OSINT) username investigations. It aggregates profile details from Instagram, checks availability/presence on 30+ popular websites concurrently, runs search engine dorking queries, parses contact information from biographies, and generates gorgeous interactive reports.

## Features

- **Instagram Scraping**: Fetches public profile details (follower/following counts, biography, external link, privacy status, verification badge, and profile picture).
- **Session Support**: Supports `--cookie` session parameter to perform authenticated queries, avoiding login blocks.
- **Cross-Platform Username Scan**: Asynchronously audits 30+ platforms (GitHub, Twitter/X, Reddit, TikTok, YouTube, Medium, Dev.to, etc.) to discover accounts registered under the same handle.
- **Entity & Bio Intelligence**: Parses biographies using advanced regex to extract email addresses, phone numbers, and cross-platform mentions.
- **Search Engine Dorking**: Queries public search footprints to find web references.
- **Premium Glassmorphic Reports**: Compiles data into structured JSON and self-contained HTML dashboards using Outfit typography, FontAwesome icons, deep космических gradients, glassmorphism layouts, and interactive filter searches.

## Installation

Ensure you have Python 3.10+ and [uv](https://github.com/astral-sh/uv) or pip installed.

```bash
# Clone the repository
git clone https://github.com/Siwoo4985/instasnoop.git
cd instasnoop

# Create a virtual environment and install in editable mode
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Usage

```bash
# Display help banner
instasnoop --help

# Run a default OSINT username scan (Simulation fallback)
instasnoop scan victim_username

# Run an authenticated live scan using your Instagram session cookie
instasnoop scan victim_username --cookie "sessionid=YOUR_SESSION_ID; csrftoken=..."

# Specify a custom directory to save reports
instasnoop scan victim_username --output-dir custom_reports
```

### Retrieving Instagram Session Cookie

1. Log in to Instagram on your desktop browser.
2. Open Developer Tools (F12 or Right Click -> Inspect).
3. Navigate to **Application** (Chrome/Edge) or **Storage** (Firefox) tab.
4. Select **Cookies** -> `https://www.instagram.com`.
5. Copy the value of the `sessionid` and `ds_user_id` cookie, and supply them in `--cookie` parameter or store them in a `.env` file.

## Project Structure

```
instasnoop/
├── instasnoop/
│   ├── __init__.py      # Package version and metadata
│   ├── cli.py           # Typer CLI definition & rich formatting
│   ├── scanner.py       # Orchestration layer for modules
│   ├── instagram.py     # Instagram scraper & simulation engine
│   ├── crossplatform.py # 30+ platform checking engine
│   ├── dorker.py        # Search dork crawler
│   ├── parser.py        # Regex contact intelligence parser
│   └── reporter.py      # JSON and HTML dashboard generator
├── tests/
│   └── test_scanner.py  # Pytest suite
├── pyproject.toml       # Package dependencies
└── README.md            # Documentation
```

## Running Tests

Run pytest inside the virtual environment:

```bash
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
