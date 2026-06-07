import asyncio
from typing import Dict, Any, List
import httpx
from .instagram import InstagramScanner
from .crossplatform import CrossPlatformScanner
from .dorker import DorkScanner
from .parser import EntityParser

class SnoopScanner:
    def __init__(self, username: str, session_cookie: str = None):
        self.username = username
        self.session_cookie = session_cookie

    async def scan(self, console_status_callback=None) -> Dict[str, Any]:
        """Runs all scanning modules concurrently using a shared HTTP client and aggregates findings."""
        
        if console_status_callback:
            console_status_callback("Launching concurrent OSINT scanners...")

        limits = httpx.Limits(max_keepalive_connections=15, max_connections=40)
        async with httpx.AsyncClient(limits=limits) as client:
            # Initialize scanners with the shared client session
            ig_scanner = InstagramScanner(self.username, self.session_cookie, client)
            cp_scanner = CrossPlatformScanner(self.username, client)
            dork_scanner = DorkScanner(self.username, client)

            # Start all scans concurrently
            ig_task = ig_scanner.fetch_profile()
            cp_task = cp_scanner.scan_all()
            dork_task = dork_scanner.search_dorks()

            if console_status_callback:
                console_status_callback("Querying Instagram, scanning cross-platform availability, and searching footprints...")

            # Run concurrently
            ig_profile, cp_results, dork_results = await asyncio.gather(
                ig_task, cp_task, dork_task, return_exceptions=True
            )

            # Handle exceptions from concurrently gathered tasks
            if isinstance(ig_profile, Exception):
                ig_profile = {
                    "username": self.username,
                    "full_name": "Error fetching profile",
                    "biography": f"An error occurred: {str(ig_profile)}",
                    "follower_count": 0,
                    "following_count": 0,
                    "post_count": 0,
                    "profile_pic_url": "",
                    "external_url": "",
                    "is_private": False,
                    "is_verified": False,
                    "simulated": True,
                    "error": str(ig_profile)
                }

            if isinstance(cp_results, Exception):
                cp_results = []

            if isinstance(dork_results, Exception):
                dork_results = []

            # Extract intelligence from the biography (synchronous post-processing)
            if console_status_callback:
                console_status_callback("Analyzing biography for contact intelligence...")
            
            parser = EntityParser()
            bio_text = ig_profile.get("biography", "") or ""
            parsed_entities = parser.extract_all(bio_text)

            scan_result = {
                "username": self.username,
                "profile": ig_profile,
                "parsed_intelligence": parsed_entities,
                "cross_platform_results": cp_results,
                "search_footprints": dork_results
            }
            return scan_result
