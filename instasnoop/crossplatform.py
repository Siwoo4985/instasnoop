import asyncio
import httpx
from typing import List, Dict, Any, Optional

class CrossPlatformScanner:
    def __init__(self, username: str, client: Optional[httpx.AsyncClient] = None):
        self.username = username.strip().replace("@", "")
        self.client = client
        # Standard list of platforms and URL templates for checking existence
        self.platforms = {
            "GitHub": "https://github.com/{}",
            "GitLab": "https://gitlab.com/{}",
            "Twitter/X": "https://x.com/{}",
            "TikTok": "https://www.tiktok.com/@{}",
            "Reddit": "https://www.reddit.com/user/{}",
            "YouTube": "https://www.youtube.com/@{}",
            "Medium": "https://medium.com/@{}",
            "Dev.to": "https://dev.to/{}",
            "Pinterest": "https://www.pinterest.com/{}",
            "Twitch": "https://www.twitch.tv/{}",
            "Steam": "https://steamcommunity.com/id/{}",
            "SoundCloud": "https://soundcloud.com/{}",
            "Linktree": "https://linktr.ee/{}",
            "Patreon": "https://www.patreon.com/{}",
            "Vimeo": "https://vimeo.com/{}",
            "Flickr": "https://www.flickr.com/people/{}",
            "Dribbble": "https://dribbble.com/{}",
            "Behance": "https://www.behance.net/{}",
            "ProductHunt": "https://www.producthunt.com/@{}",
            "Keybase": "https://keybase.io/{}",
            "Spotify": "https://open.spotify.com/user/{}",
            "Quora": "https://www.quora.com/profile/{}",
            "Letterboxd": "https://letterboxd.com/{}",
            "Chess.com": "https://www.chess.com/member/{}",
            "Substack": "https://{}.substack.com",
            "DockerHub": "https://hub.docker.com/u/{}",
            "Instructables": "https://www.instructables.com/member/{}",
            "Bandcamp": "https://bandcamp.com/{}",
            "Kaggle": "https://www.kaggle.com/{}",
            "npm": "https://www.npmjs.com/~{}",
            "PyPI": "https://pypi.org/user/{}"
        }

    async def check_site(self, client: httpx.AsyncClient, semaphore: asyncio.Semaphore, site: str, url_template: str) -> Dict[str, Any]:
        """Checks if a user profile exists on a specific site under a semaphore lock."""
        url = url_template.format(self.username)
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }
        
        async with semaphore:
            try:
                # Add a micro delay to jitter/stagger requests slightly
                await asyncio.sleep(0.05)
                response = await client.get(url, headers=headers, follow_redirects=True, timeout=5.0)
                
                exists = False
                status_code = response.status_code
                status_label = "NOT_FOUND"
                
                if status_code == 200:
                    exists = True
                    status_label = "FOUND"
                    content = response.text.lower()
                    
                    # Check for common "not found" indicators in HTML content
                    not_found_keywords = [
                        "page not found", "user not found", "profile not found",
                        "isn't available", "doesn't exist", "cannot find", 
                        "error-404", "404 not found", "404 - page not found"
                    ]
                    
                    if any(kw in content for kw in not_found_keywords):
                        exists = False
                        status_label = "NOT_FOUND"
                
                elif status_code == 404:
                    exists = False
                    status_label = "NOT_FOUND"
                elif status_code in (403, 401):
                    exists = False
                    status_label = "BLOCKED/FORBIDDEN"
                elif status_code == 429:
                    exists = False
                    status_label = "RATE_LIMITED"
                else:
                    exists = False
                    status_label = f"HTTP_{status_code}"
                    
                return {
                    "site": site,
                    "url": url,
                    "exists": exists,
                    "status_code": status_code,
                    "status_label": status_label
                }
            except httpx.HTTPError as e:
                return {
                    "site": site,
                    "url": url,
                    "exists": False,
                    "status_code": 0,
                    "status_label": "ERROR",
                    "error": str(e)
                }

    async def scan_all(self) -> List[Dict[str, Any]]:
        """Scans all platforms concurrently with throttled concurrency."""
        semaphore = asyncio.Semaphore(10)
        
        if self.client:
            tasks = [
                self.check_site(self.client, semaphore, site, template)
                for site, template in self.platforms.items()
            ]
            results = await asyncio.gather(*tasks)
        else:
            limits = httpx.Limits(max_keepalive_connections=10, max_connections=30)
            async with httpx.AsyncClient(limits=limits) as client:
                tasks = [
                    self.check_site(client, semaphore, site, template)
                    for site, template in self.platforms.items()
                ]
                results = await asyncio.gather(*tasks)
                
        return sorted(results, key=lambda x: x["site"])
