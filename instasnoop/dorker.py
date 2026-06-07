import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any

class DorkScanner:
    def __init__(self, username: str):
        self.username = username.strip().replace("@", "")

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
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=8.0)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    # DuckDuckGo HTML search results are typically in divs with class "result"
                    result_divs = soup.find_all("div", class_="result")
                    
                    for div in result_divs[:10]:  # Limit to top 10 results
                        title_el = div.find("a", class_="result__snippet")
                        title = title_el.text.strip() if title_el else ""
                        
                        link_el = div.find("a", class_="result__url")
                        link = link_el["href"].strip() if link_el else ""
                        
                        desc_el = div.find("a", class_="result__snippet")
                        # The snippet is often inside a different structure or the same one. Let's find result__snippet
                        snippet_el = div.find("a", class_="result__snippet")
                        snippet = snippet_el.text.strip() if snippet_el else ""
                        
                        # Fix up description if title and description are same element
                        desc_el_actual = div.find("td", class_="result-snippet")
                        if desc_el_actual:
                            snippet = desc_el_actual.text.strip()
                        
                        # Get title from result__a if it exists (which is usually the real title link)
                        real_title_el = div.find("a", class_="result__a")
                        if real_title_el:
                            title = real_title_el.text.strip()
                            link = real_title_el["href"].strip()
                            
                        # Clean links if they are redirected DDG links
                        if link.startswith("//duckduckgo.com/y.js"):
                            # The URL contains a u query param with the real URL
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
                    # DDG might have rate-limited us. We'll return empty list and let reporter show a message.
                    pass
        except Exception:
            # Silence exceptions in network scanner to prevent crashing CLI
            pass

        # If no results found (due to rate-limit/network), generate some basic simulated footprint links
        # that are standard search URLs for that username, so the user can easily click and view manually.
        if not results:
            results = [
                {
                    "title": f"Google Search: {self.username}",
                    "link": f"https://www.google.com/search?q=%22{self.username}%22",
                    "snippet": f"Search directly on Google for exact matches of '{self.username}'."
                },
                {
                    "title": f"Bing Search: {self.username}",
                    "link": f"https://www.bing.com/search?q=%22{self.username}%22",
                    "snippet": f"Search directly on Bing for exact matches of '{self.username}'."
                },
                {
                    "title": f"Instagram profile search: {self.username}",
                    "link": f"https://www.instagram.com/{self.username}/",
                    "snippet": f"Direct link to Instagram profile for '{self.username}'."
                }
            ]
            
        return results
