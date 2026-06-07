import asyncio
import httpx
from typing import List, Dict, Any

class CrossPlatformScanner:
    def __init__(self, username: str):
        self.username = username.strip().replace("@", "")
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

    async def check_site(self, client: httpx.AsyncClient, site: str, url_template: str) -> Dict[str, Any]:
        """Checks if a user profile exists on a specific site."""
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
        
        try:
            # Most sites return 404 if user doesn't exist.
            # Some sites (like TikTok) are heavily protected, but a 200 or 404 is still standard.
            # Using HEAD request is faster, but some sites require GET or block HEAD.
            # We'll use GET but limit the response read size to save bandwidth/time.
            response = await client.get(url, headers=headers, follow_redirects=True, timeout=5.0)
            
            # Custom logic for specific sites that return 200 but might not contain the user
            exists = False
            status_code = response.status_code
            
            if status_code == 200:
                exists = True
                content = response.text.lower()
                
                # Check for common "not found" indicators in HTML content
                not_found_keywords = [
                    "page not found", "user not found", "profile not found",
                    "isn't available", "doesn't exist", "cannot find", 
                    "error-404", "404 not found", "404 - page not found"
                ]
                
                if any(kw in content for kw in not_found_keywords):
                    exists = False
            
            elif status_code == 404:
                exists = False
            else:
                # Other status codes (like 403, 429) might mean protected or rate-limited.
                # In OSINT, we usually treat these as inconclusive or false.
                exists = False
                
            return {
                "site": site,
                "url": url,
                "exists": exists,
                "status_code": status_code
            }
        except httpx.HTTPError:
            # Connection errors, timeouts, etc.
            return {
                "site": site,
                "url": url,
                "exists": False,
                "status_code": 0,
                "error": "Connection Timeout/Error"
            }

    async def scan_all(self) -> List[Dict[str, Any]]:
        """Scans all platforms concurrently."""
        limits = httpx.Limits(max_keepalive_connections=10, max_connections=30)
        async with httpx.AsyncClient(limits=limits) as client:
            tasks = [
                self.check_site(client, site, template)
                for site, template in self.platforms.items()
            ]
            results = await asyncio.gather(*tasks)
            # Sort results alphabetically by site name
            return sorted(results, key=lambda x: x["site"])
