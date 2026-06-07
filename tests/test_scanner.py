import pytest
from instasnoop.parser import EntityParser
from instasnoop.instagram import InstagramScanner
from instasnoop.reporter import ReportGenerator
import tempfile
import os
import json

def test_entity_parser_emails():
    parser = EntityParser()
    text = "Hello! Contact me at test.user@example.com or user_name+123@domain.co.kr."
    emails = parser.extract_emails(text)
    assert "test.user@example.com" in emails
    assert "user_name+123@domain.co.kr" in emails
    assert len(emails) == 2

def test_entity_parser_phones():
    parser = EntityParser()
    text = "Call us at +82 10-1234-5678 or +1 (555) 019-9000 for details."
    phones = parser.extract_phones(text)
    assert any("10-1234-5678" in p for p in phones)
    assert any("019-9000" in p for p in phones)

def test_entity_parser_socials():
    parser = EntityParser()
    text = "Find me on t.me/siwoo_test or twitter.com/test_user or send to @some_mention."
    socials = parser.extract_socials(text)
    platforms = [s["platform"] for s in socials]
    handles = [s["handle"] for s in socials]
    
    assert "Telegram" in platforms
    assert "siwoo_test" in handles
    assert "Twitter/X" in platforms
    assert "test_user" in handles
    assert "Mention" in platforms
    assert "some_mention" in handles

@pytest.mark.asyncio
async def test_instagram_scanner_simulation():
    scanner = InstagramScanner("siwoo")
    profile = await scanner.fetch_profile()
    assert profile["username"] == "siwoo"
    assert profile["simulated"] is True
    assert "Siwoo Park" in profile["full_name"]
    assert "siwoo.park@example.com" in profile["biography"]

def test_report_generation():
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = os.path.join(tmpdir, "report.json")
        html_path = os.path.join(tmpdir, "report.html")
        
        reporter = ReportGenerator("siwoo")
        data = {
            "username": "siwoo",
            "profile": {
                "username": "siwoo",
                "full_name": "Siwoo Park",
                "biography": "Tech Geek\nemail: siwoo@example.com",
                "follower_count": 100,
                "following_count": 50,
                "post_count": 10,
                "simulated": True
            },
            "parsed_intelligence": {
                "emails": ["siwoo@example.com"],
                "phones": [],
                "socials": []
            },
            "cross_platform_results": [
                {"site": "GitHub", "url": "https://github.com/siwoo", "exists": True, "status_code": 200}
            ],
            "search_footprints": [
                {"title": "Search Footprint", "link": "https://google.com", "snippet": "Found something"}
            ]
        }
        
        reporter.generate_json_report(data, json_path)
        reporter.generate_html_report(data, html_path)
        
        assert os.path.exists(json_path)
        assert os.path.exists(html_path)
        
        with open(json_path, "r", encoding="utf-8") as f:
            saved_data = json.load(f)
            assert saved_data["username"] == "siwoo"

def test_entity_parser_mention_edge_case():
    parser = EntityParser()
    # If the text has email address like user@domain.com, the domain should not be matched as @domain.com Mention
    text = "Email: siwoo@example.com, also see @siwoo_real on Twitter."
    socials = parser.extract_socials(text)
    handles = [s["handle"] for s in socials]
    
    assert "siwoo_real" in handles
    assert "example.com" not in handles
    assert "example" not in handles

def test_entity_parser_phone_date_exclusion():
    parser = EntityParser()
    # Dates like 2026-06-07 shouldn't match as a phone number
    text = "Born on 1995-12-05, contact +82 10-5555-4444 or +1-555-555-5555"
    phones = parser.extract_phones(text)
    
    assert "1995-12-05" not in phones
    assert any("5555-4444" in p for p in phones)
    assert any("555-5555" in p for p in phones)
