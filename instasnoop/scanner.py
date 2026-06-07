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
        """Runs all scanning modules asynchronously and aggregates findings."""
        
        # 1. Instagram Profile scan (needed first to get bio for parsing)
        if console_status_callback:
            console_status_callback("Fetching Instagram profile...")
        
        ig_scanner = InstagramScanner(self.username, self.session_cookie)
        try:
            ig_profile = await ig_scanner.fetch_profile()
        except Exception as e:
            ig_profile = {
                "username": self.username,
                "full_name": "Error fetching profile",
                "biography": f"An error occurred: {str(e)}",
                "follower_count": 0,
                "following_count": 0,
                "post_count": 0,
                "profile_pic_url": "",
                "external_url": "",
                "is_private": False,
                "is_verified": False,
                "simulated": True,
                "error": str(e)
            }

        # 2. Extract intelligence from the biography
        if console_status_callback:
            console_status_callback("Extracting contact info from bio...")
        parser = EntityParser()
        bio_text = ig_profile.get("biography", "") or ""
        parsed_entities = parser.extract_all(bio_text)

        # 3. Cross-platform username check and Search engine dorking run concurrently
        if console_status_callback:
            console_status_callback("Checking cross-platform accounts & crawling search engines...")

        cp_scanner = CrossPlatformScanner(self.username)
        dork_scanner = DorkScanner(self.username)

        cp_task = cp_scanner.scan_all()
        dork_task = dork_scanner.search_dorks()

        cp_results, dork_results = await asyncio.gather(cp_task, dork_task, return_exceptions=True)

        if isinstance(cp_results, Exception):
            cp_results = []
        if isinstance(dork_results, Exception):
            dork_results = []

        # 4. Compile everything into a structured scan result
        scan_result = {
            "username": self.username,
            "profile": ig_profile,
            "parsed_intelligence": parsed_entities,
            "cross_platform_results": cp_results,
            "search_footprints": dork_results
        }
        return scan_result
