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
