import logging
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional

logger = logging.getLogger("instasnoop.dorker")

class DorkScanner:
    def __init__(self, username: str, client: Optional[httpx.AsyncClient] = None):
        self.username = username.strip().replace("@", "")
        self.client = client

    async def search_dorks(self) -> List[Dict[str, Any]]:
        """Queries DuckDuckGo HTML search for public traces of the username."""
        query = f'"{self.username}"'
        url = f"https://html.duckduckgo.com/html/?q={query}"
        
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }
        
        results = []
        try:
            if self.client:
                response = await self.client.get(url, headers=headers, timeout=8.0)
            else:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, headers=headers, timeout=8.0)
                
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                result_divs = soup.find_all("div", class_="result")
                
                for div in result_divs[:10]:  # Limit to top 10 results
                    # Main title element and link
                    title_el = div.find("a", class_="result__a")
                    if not title_el:
                        continue
                    
                    title = title_el.text.strip()
                    link = title_el["href"].strip()
                    
                    # Main snippet element
                    snippet = ""
                    desc_el_actual = div.find("td", class_="result-snippet")
                    if desc_el_actual:
                        snippet = desc_el_actual.text.strip()
                    else:
                        snippet_el = div.find("a", class_="result__snippet")
                        if snippet_el:
                            snippet = snippet_el.text.strip()
                        
                    # Clean links if they are redirected DDG links
                    if link.startswith("//duckduckgo.com/y.js"):
                        from urllib.parse import urlparse, parse_qs
                        parsed = urlparse("https:" + link)
                        q_params = parse_qs(parsed.query)
                        if "u" in q_params:
                            link = q_params["u"][0]

                    if title and link:
                        results.append({
                            "title": title,
                            "link": link,
                            "snippet": snippet
                        })
            else:
                logger.warning(f"DuckDuckGo search returned status code {response.status_code}")
        except Exception as e:
            logger.error(f"Error during DuckDuckGo search: {e}", exc_info=True)

        # If no results found (due to rate-limit/network), generate some basic suggested manual footprint links
        if not results:
            results = [
                {
                    "title": f"Google Search: {self.username}",
                    "link": f"https://www.google.com/search?q=%22{self.username}%22",
                    "snippet": f"Suggested: Click to search directly on Google for exact matches of '{self.username}'."
                },
                {
                    "title": f"Bing Search: {self.username}",
                    "link": f"https://www.bing.com/search?q=%22{self.username}%22",
                    "snippet": f"Suggested: Click to search directly on Bing for exact matches of '{self.username}'."
                },
                {
                    "title": f"Instagram Profile: {self.username}",
                    "link": f"https://www.instagram.com/{self.username}/",
                    "snippet": f"Suggested: Click to view the Instagram profile for '{self.username}' directly."
                }
            ]
            
        return results
