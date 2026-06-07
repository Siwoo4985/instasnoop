import pytest
from typer.testing import CliRunner
import httpx
import respx
import tempfile
import os
import json
import asyncio
from instasnoop.cli import app
from instasnoop.instagram import InstagramScanner
from instasnoop.crossplatform import CrossPlatformScanner
from instasnoop.dorker import DorkScanner
from instasnoop.parser import EntityParser
from instasnoop.reporter import ReportGenerator
from instasnoop.scanner import SnoopScanner

runner = CliRunner()

# 1. CLI Tests
def test_cli_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "InstaSnoop OSINT Tool" in result.output

def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "scan" in result.output
    assert "version" in result.output

# 2. Instagram Scanner Error Boundaries with mock network requests
@pytest.mark.asyncio
@respx.mock
async def test_instagram_scanner_404():
    # Mock Instagram 404 Not Found
    respx.get("https://www.instagram.com/api/v1/users/web_profile_info/?username=nonexistent").mock(
        return_value=httpx.Response(404)
    )
    
    scanner = InstagramScanner("nonexistent", session_cookie="fake_cookie")
    # Should raise ValueError for 404
    with pytest.raises(ValueError) as excinfo:
        await scanner.fetch_profile_with_cookie("fake_cookie")
    assert "not found on Instagram (404)" in str(excinfo.value)

@pytest.mark.asyncio
@respx.mock
async def test_instagram_scanner_403_rate_limit():
    # Mock Instagram 403 Forbidden or 429
    respx.get("https://www.instagram.com/api/v1/users/web_profile_info/?username=blocked_user").mock(
        return_value=httpx.Response(429)
    )
    
    scanner = InstagramScanner("blocked_user", session_cookie="fake_cookie")
    # Should raise HTTPStatusError
    with pytest.raises(httpx.HTTPStatusError):
        await scanner.fetch_profile_with_cookie("fake_cookie")

# 3. Cross-Platform Status Mappings with mock network requests
@pytest.mark.asyncio
@respx.mock
async def test_crossplatform_status_mappings():
    # Mock various platform responses
    # 200 OK (User found)
    respx.get("https://github.com/test_user").mock(return_value=httpx.Response(200, text="Profile page"))
    # 404 Not Found (User doesn't exist)
    respx.get("https://gitlab.com/test_user").mock(return_value=httpx.Response(404))
    # 403 Forbidden (Blocked)
    respx.get("https://x.com/test_user").mock(return_value=httpx.Response(403))
    # 429 Too Many Requests (Rate limited)
    respx.get("https://www.tiktok.com/@test_user").mock(return_value=httpx.Response(429))
    # 200 OK containing "not found" keywords (Should map to false)
    respx.get("https://medium.com/@test_user").mock(return_value=httpx.Response(200, text="Sorry, this user page is not found on Medium"))

    async with httpx.AsyncClient() as client:
        scanner = CrossPlatformScanner("test_user", client)
        
        # Test GitHub (Found)
        github_res = await scanner.check_site(client, asyncio.Semaphore(1), "GitHub", "https://github.com/{}")
        assert github_res["exists"] is True
        assert github_res["status_label"] == "FOUND"
        
        # Test GitLab (Not Found)
        gitlab_res = await scanner.check_site(client, asyncio.Semaphore(1), "GitLab", "https://gitlab.com/{}")
        assert gitlab_res["exists"] is False
        assert gitlab_res["status_label"] == "NOT_FOUND"
        
        # Test Twitter/X (Blocked)
        twitter_res = await scanner.check_site(client, asyncio.Semaphore(1), "Twitter/X", "https://x.com/{}")
        assert twitter_res["exists"] is False
        assert twitter_res["status_label"] == "BLOCKED/FORBIDDEN"
        
        # Test TikTok (Rate Limited)
        tiktok_res = await scanner.check_site(client, asyncio.Semaphore(1), "TikTok", "https://www.tiktok.com/@{}")
        assert tiktok_res["exists"] is False
        assert tiktok_res["status_label"] == "RATE_LIMITED"
        
        # Test Medium (200 with keyword -> Not Found)
        medium_res = await scanner.check_site(client, asyncio.Semaphore(1), "Medium", "https://medium.com/@{}")
        assert medium_res["exists"] is False
        assert medium_res["status_label"] == "NOT_FOUND"

# 4. HTML Stored XSS Autoescape Verification
def test_html_autoescape():
    with tempfile.TemporaryDirectory() as tmpdir:
        html_path = os.path.join(tmpdir, "xss_report.html")
        reporter = ReportGenerator("<script>alert('username_xss')</script>")
        
        # Inject malicious HTML script tags
        data = {
            "username": "<script>alert('username_xss')</script>",
            "profile": {
                "username": "xss_target",
                "full_name": "<img src=x onerror=alert('name_xss')>",
                "biography": "<iframe src='javascript:alert(1)'></iframe>",
                "follower_count": 0,
                "following_count": 0,
                "post_count": 0,
                "simulated": True
            },
            "parsed_intelligence": {
                "emails": [],
                "phones": [],
                "socials": []
            },
            "cross_platform_results": [],
            "search_footprints": [
                {"title": "<script>xss</script>", "link": "http://xss.com", "snippet": "snippet <script>xss</script>"}
            ]
        }
        
        reporter.generate_html_report(data, html_path)
        assert os.path.exists(html_path)
        
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            # Dynamic fields MUST be escaped and not present as raw script tags
            assert "<script>alert('username_xss')</script>" not in html_content
            assert "&lt;script&gt;alert(&#39;username_xss&#39;)&lt;/script&gt;" in html_content
            assert "<img src=x onerror=alert('name_xss')>" not in html_content
            assert "&lt;img src=x onerror=alert(&#39;name_xss&#39;)&gt;" in html_content
            assert "<iframe src='javascript:alert(1)'></iframe>" not in html_content
            assert "&lt;iframe src=&#39;javascript:alert(1)&#39;&gt;&lt;/iframe&gt;" in html_content
