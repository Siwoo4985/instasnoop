import re
from typing import Dict, Any, List

class EntityParser:
    def __init__(self):
        # Email regex
        self.email_pattern = re.compile(
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        )
        
        # Phone number regex (covers international, US, Korean, and simple digital formats)
        self.phone_pattern = re.compile(
            r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{4}'
        )
        
        # Social media handles & links (e.g. @username, telegram/line links)
        self.social_patterns = {
            "Telegram": re.compile(r'(?:t\.me|telegram\.me)/([a-zA-Z0-9_]{5,})', re.IGNORECASE),
            "Twitter/X": re.compile(r'(?:twitter\.com|x\.com)/([a-zA-Z0-9_]{1,15})', re.IGNORECASE),
            "YouTube": re.compile(r'(?:youtube\.com/@|youtube\.com/c/)([a-zA-Z0-9_-]+)', re.IGNORECASE),
            "Facebook": re.compile(r'(?:facebook\.com|fb\.com)/([a-zA-Z0-9.]+)', re.IGNORECASE),
            "Snapchat": re.compile(r'(?:snapchat\.add|snapchat\.com/add)/([a-zA-Z0-9._-]+)', re.IGNORECASE),
            "Kakao": re.compile(r'(?:kakao|open\.kakao\.com/o/)([a-zA-Z0-9_-]+)', re.IGNORECASE),
            "Line": re.compile(r'(?:line\.me/ti/p/|line\.me/R/ti/g/)([a-zA-Z0-9_-]+)', re.IGNORECASE),
            "Mention": re.compile(r'@([a-zA-Z0-9_.]+)')
        }

    def extract_emails(self, text: str) -> List[str]:
        """Extracts email addresses from text."""
        return list(set(self.email_pattern.findall(text)))

    def extract_phones(self, text: str) -> List[str]:
        """Extracts phone numbers from text."""
        # Clean up some false positives (like long version numbers or simple date strings)
        raw_matches = self.phone_pattern.findall(text)
        cleaned_matches = []
        for m in raw_matches:
            # Must contain at least 7 digits to be a phone number
            digits = re.sub(r'\D', '', m)
            if len(digits) >= 7 and len(digits) <= 15:
                cleaned_matches.append(m.strip())
        return list(set(cleaned_matches))

    def extract_socials(self, text: str) -> List[Dict[str, str]]:
        """Extracts social media links and mentions from text."""
        socials = []
        # Check explicit links
        for platform, pattern in self.social_patterns.items():
            matches = pattern.findall(text)
            for match in matches:
                # Clean up any trailing punctuation like dots or commas from handle
                handle = match.rstrip(".,!?;:")
                
                # If it's a mention, we exclude if it was already caught in a platform link
                if platform == "Mention" and any(m in handle for m in ["twitter", "youtube", "facebook", "snapchat", "telegram"]):
                    continue
                
                socials.append({
                    "platform": platform,
                    "handle": handle
                })
        
        # De-duplicate list of dicts
        seen = set()
        deduped = []
        for s in socials:
            key = (s["platform"], s["handle"])
            if key not in seen:
                seen.add(key)
                deduped.append(s)
                
        return deduped

    def extract_all(self, text: str) -> Dict[str, Any]:
        """Runs all extractions and returns the aggregated data."""
        return {
            "emails": self.extract_emails(text),
            "phones": self.extract_phones(text),
            "socials": self.extract_socials(text)
        }
