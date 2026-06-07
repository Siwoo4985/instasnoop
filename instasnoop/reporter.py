import os
import json
from datetime import datetime
from jinja2 import Environment, select_autoescape, FileSystemLoader

class ReportGenerator:
    def __init__(self, username: str):
        self.username = username

    def generate_json_report(self, data: dict, output_path: str) -> None:
        """Dumps all scan data to a formatted JSON file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def generate_html_report(self, data: dict, output_path: str) -> None:
        """Generates a self-contained, premium responsive HTML dashboard with security and print styling."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Calculate stats for the summary card
        profile = data.get("profile", {})
        parsed_intel = data.get("parsed_intelligence", {})
        cp_results = data.get("cross_platform_results", [])
        dorks = data.get("search_footprints", [])
        
        found_platforms = [r for r in cp_results if r.get("exists")]
        total_platforms = len(cp_results)
        
        # The Jinja2 HTML/CSS Template
        template_str = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InstaSnoop OSINT Report: @{{ username | e }}</title>
    <!-- Google Fonts Outfit & JetBrains Mono -->
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <!-- FontAwesome CDN for premium icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        :root {
            --bg-gradient: linear-gradient(135deg, #090514 0%, #030207 100%);
            --glass-bg: rgba(255, 255, 255, 0.02);
            --glass-border: rgba(255, 255, 255, 0.05);
            --glass-glow: rgba(139, 92, 246, 0.15);
            --accent-purple: #8b5cf6;
            --accent-cyan: #06b6d4;
            --accent-emerald: #10b981;
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --font-main: 'Outfit', sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background: var(--bg-gradient);
            color: var(--text-primary);
            font-family: var(--font-main);
            min-height: 100vh;
            padding: 2rem;
            line-height: 1.6;
            overflow-x: hidden;
        }

        /* Ambient neon blobs in the background */
        .ambient-glow-1 {
            position: absolute;
            top: -10%;
            left: -10%;
            width: 40%;
            height: 40%;
            background: radial-gradient(circle, rgba(139, 92, 246, 0.08) 0%, transparent 70%);
            z-index: -1;
            filter: blur(80px);
        }

        .ambient-glow-2 {
            position: absolute;
            bottom: -10%;
            right: -10%;
            width: 50%;
            height: 50%;
            background: radial-gradient(circle, rgba(6, 182, 212, 0.06) 0%, transparent 70%);
            z-index: -1;
            filter: blur(100px);
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            position: relative;
        }

        /* Top Header */
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--glass-border);
        }

        .logo {
            font-size: 1.8rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            background: linear-gradient(to right, var(--text-primary), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .logo i {
            color: var(--accent-purple);
            -webkit-text-fill-color: initial;
        }

        .meta-info {
            font-family: var(--font-mono);
            font-size: 0.85rem;
            color: var(--text-secondary);
            text-align: right;
        }

        /* Bento Grid Layout */
        .bento-grid {
            display: grid;
            grid-template-columns: repeat(12, 1fr);
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        /* Glass Cards */
        .glass-card {
            background: var(--glass-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 1.75rem;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }

        .glass-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.01) 0%, transparent 100%);
            pointer-events: none;
        }

        .glass-card:hover {
            border-color: rgba(139, 92, 246, 0.25);
            box-shadow: 0 12px 40px 0 rgba(139, 92, 246, 0.08);
            transform: translateY(-2px);
        }

        /* Individual Bento Cards */
        .card-profile {
            grid-column: span 5;
        }

        .card-stats {
            grid-column: span 7;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .card-intel {
            grid-column: span 4;
        }

        .card-crossplatform {
            grid-column: span 8;
        }

        .card-dorks {
            grid-column: span 12;
        }

        /* Component Details */
        .profile-header {
            display: flex;
            align-items: center;
            gap: 1.25rem;
            margin-bottom: 1.25rem;
        }

        .avatar {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid var(--accent-purple);
            background: #1e1e1e;
        }

        .profile-title h2 {
            font-size: 1.5rem;
            font-weight: 800;
            letter-spacing: -0.3px;
        }

        .badge-verified {
            color: #38bdf8;
            font-size: 1.1rem;
            margin-left: 0.25rem;
        }

        .profile-handle {
            font-family: var(--font-mono);
            font-size: 0.9rem;
            color: var(--accent-cyan);
        }

        .profile-bio {
            font-size: 0.95rem;
            color: var(--text-secondary);
            background: rgba(255, 255, 255, 0.01);
            border: 1px solid rgba(255, 255, 255, 0.02);
            border-radius: 12px;
            padding: 1rem;
            white-space: pre-line;
            margin-top: 1rem;
        }

        .profile-bio a {
            color: var(--accent-purple);
            text-decoration: none;
        }

        .profile-bio a:hover {
            text-decoration: underline;
        }

        /* Warning banner for simulations */
        .simulated-warning {
            background: rgba(234, 179, 8, 0.05);
            border: 1px solid rgba(234, 179, 8, 0.15);
            color: #fbbf24;
            border-radius: 12px;
            padding: 0.85rem;
            font-size: 0.85rem;
            margin-top: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .simulated-warning i {
            font-size: 1.1rem;
        }

        /* Stat Grid */
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .stat-box {
            background: rgba(255, 255, 255, 0.01);
            border: 1px solid rgba(255, 255, 255, 0.03);
            border-radius: 14px;
            padding: 1rem;
            text-align: center;
        }

        .stat-value {
            font-size: 1.8rem;
            font-weight: 800;
            color: var(--text-primary);
        }

        .stat-label {
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-secondary);
            margin-top: 0.25rem;
        }

        /* Intel lists */
        .section-title {
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 1.25rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--text-primary);
            border-bottom: 1px solid rgba(255, 255, 255, 0.03);
            padding-bottom: 0.5rem;
        }

        .intel-list {
            list-style: none;
        }

        .intel-item {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.75rem;
            background: rgba(255, 255, 255, 0.01);
            border: 1px solid rgba(255, 255, 255, 0.02);
            border-radius: 10px;
            margin-bottom: 0.75rem;
            font-size: 0.9rem;
            position: relative;
        }

        .intel-item i {
            font-size: 1.1rem;
            color: var(--accent-purple);
            width: 20px;
            text-align: center;
        }

        .intel-item .value {
            font-family: var(--font-mono);
            word-break: break-all;
            flex-grow: 1;
        }

        /* Copy Button styling */
        .copy-btn {
            background: none;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            padding: 0.2rem;
            margin-left: 0.5rem;
            font-size: 0.85rem;
            transition: color 0.2s;
        }

        .copy-btn:hover {
            color: var(--accent-cyan);
        }

        .empty-text {
            color: var(--text-secondary);
            font-style: italic;
            font-size: 0.9rem;
            text-align: center;
            padding: 1.5rem 0;
        }

        /* Cross-platform Search and Grid */
        .cp-controls {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            gap: 1rem;
            flex-wrap: wrap;
        }

        .search-bar {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--glass-border);
            border-radius: 10px;
            padding: 0.5rem 1rem;
            color: var(--text-primary);
            font-family: var(--font-main);
            outline: none;
            width: 100%;
            max-width: 250px;
            font-size: 0.85rem;
            transition: all 0.3s;
        }

        .search-bar:focus {
            border-color: var(--accent-purple);
            box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.15);
        }

        .cp-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
            gap: 0.75rem;
            max-height: 280px;
            overflow-y: auto;
            padding-right: 0.5rem;
        }

        /* Custom scrollbar */
        .cp-grid::-webkit-scrollbar, .dorks-list::-webkit-scrollbar {
            width: 4px;
        }
        .cp-grid::-webkit-scrollbar-thumb, .dorks-list::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
        }

        .cp-badge {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.6rem 0.85rem;
            background: rgba(255, 255, 255, 0.01);
            border: 1px solid rgba(255, 255, 255, 0.03);
            border-radius: 10px;
            font-size: 0.85rem;
            text-decoration: none;
            color: var(--text-secondary);
            transition: all 0.25s;
        }

        .cp-badge.found {
            color: var(--text-primary);
            background: rgba(16, 185, 129, 0.03);
            border-color: rgba(16, 185, 129, 0.2);
        }

        .cp-badge.found:hover {
            background: rgba(16, 185, 129, 0.08);
            border-color: var(--accent-emerald);
            transform: translateY(-1px);
        }

        .cp-badge.not-found {
            opacity: 0.45;
            cursor: not-allowed;
            pointer-events: none;
        }

        .badge-status {
            font-size: 0.55rem;
            padding: 0.15rem 0.35rem;
            border-radius: 4px;
            text-transform: uppercase;
            font-weight: 700;
        }

        .badge-status.found {
            background: rgba(16, 185, 129, 0.15);
            color: var(--accent-emerald);
        }

        /* Footprints/Dorks list */
        .dorks-list {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            max-height: 400px;
            overflow-y: auto;
        }

        .dork-item {
            background: rgba(255, 255, 255, 0.01);
            border: 1px solid rgba(255, 255, 255, 0.02);
            border-radius: 12px;
            padding: 1rem;
            transition: all 0.2s;
        }

        .dork-item:hover {
            border-color: rgba(255, 255, 255, 0.05);
            background: rgba(255, 255, 255, 0.02);
        }

        .dork-title {
            font-size: 1rem;
            font-weight: 600;
            color: var(--accent-cyan);
            text-decoration: none;
            display: inline-block;
            margin-bottom: 0.25rem;
        }

        .dork-title:hover {
            text-decoration: underline;
        }

        .dork-link {
            font-family: var(--font-mono);
            font-size: 0.75rem;
            color: var(--text-secondary);
            word-break: break-all;
            margin-bottom: 0.5rem;
        }

        .dork-snippet {
            font-size: 0.85rem;
            color: var(--text-secondary);
        }

        /* Print styling/PDF button */
        .print-btn {
            background: linear-gradient(135deg, var(--accent-purple) 0%, #7c3aed 100%);
            border: none;
            color: white;
            font-family: var(--font-main);
            font-weight: 600;
            font-size: 0.85rem;
            padding: 0.6rem 1.2rem;
            border-radius: 10px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            box-shadow: 0 4px 12px rgba(139, 92, 246, 0.2);
            transition: all 0.25s;
        }

        .print-btn:hover {
            box-shadow: 0 6px 16px rgba(139, 92, 246, 0.35);
            transform: translateY(-1px);
        }

        /* Custom toggle switch for found only */
        .toggle-container {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.85rem;
            color: var(--text-secondary);
            cursor: pointer;
        }

        .toggle-container input {
            cursor: pointer;
        }

        @media (max-width: 900px) {
            .card-profile, .card-stats, .card-intel, .card-crossplatform {
                grid-column: span 12;
            }
            body {
                padding: 1rem;
            }
        }

        /* Print Override Stylesheet */
        @media print {
            body {
                background: white !important;
                color: black !important;
                padding: 0 !important;
                font-size: 11pt;
            }
            
            .ambient-glow-1,
            .ambient-glow-2,
            .print-btn,
            .cp-controls,
            .copy-btn,
            .simulated-warning {
                display: none !important;
            }

            header {
                border-bottom: 2px solid #333 !important;
                margin-bottom: 2rem !important;
                padding-bottom: 0.5rem !important;
            }

            .logo {
                background: none !important;
                -webkit-text-fill-color: black !important;
                color: black !important;
            }

            .logo i {
                color: black !important;
            }

            .meta-info {
                color: #333 !important;
            }

            .bento-grid {
                display: block !important;
            }

            .glass-card {
                background: white !important;
                border: 1px solid #ddd !important;
                border-radius: 12px !important;
                padding: 1.5rem !important;
                box-shadow: none !important;
                color: black !important;
                margin-bottom: 1.5rem !important;
                page-break-inside: avoid;
                backdrop-filter: none !important;
                -webkit-backdrop-filter: none !important;
            }

            .profile-bio {
                background: #f9f9f9 !important;
                border: 1px solid #eee !important;
                color: #333 !important;
            }

            .stat-box {
                background: #f9f9f9 !important;
                border: 1px solid #eee !important;
            }

            .stat-value {
                color: black !important;
            }

            .stat-label {
                color: #555 !important;
            }

            .intel-item {
                background: #f9f9f9 !important;
                border: 1px solid #eee !important;
            }

            .intel-item i {
                color: #333 !important;
            }

            .cp-grid {
                display: flex !important;
                flex-wrap: wrap !important;
                gap: 0.5rem !important;
                max-height: none !important;
                overflow: visible !important;
            }

            .cp-badge {
                border: 1px solid #ccc !important;
                background: white !important;
                color: black !important;
                padding: 0.4rem 0.6rem !important;
            }

            .cp-badge.not-found {
                display: none !important; /* Hide non-existent platforms in print to save space */
            }

            .badge-status.found {
                background: none !important;
                color: #0f766e !important;
                font-weight: bold !important;
            }

            .dorks-list {
                max-height: none !important;
                overflow: visible !important;
            }

            .dork-item {
                border: 1px solid #eee !important;
                background: #f9f9f9 !important;
            }

            .dork-title {
                color: #0369a1 !important;
            }

            .dork-link {
                color: #555 !important;
            }

            .dork-snippet {
                color: #333 !important;
            }
        }
    </style>
</head>
<body>
    <div class="ambient-glow-1"></div>
    <div class="ambient-glow-2"></div>

    <div class="container">
        <!-- Top header -->
        <header>
            <div class="logo">
                <i class="fa-solid fa-user-secret"></i> InstaSnoop OSINT
            </div>
            <div style="display: flex; align-items: center; gap: 1rem;">
                <button class="print-btn" onclick="window.print()">
                    <i class="fa-solid fa-file-pdf"></i> Save / Print PDF
                </button>
                <div class="meta-info">
                    <div>Target: @{{ username | e }}</div>
                    <div>Generated: {{ date_str | e }}</div>
                </div>
            </div>
        </header>

        <!-- Bento Layout -->
        <div class="bento-grid">
            <!-- Profile Info Card -->
            <div class="glass-card card-profile">
                <div class="section-title">
                    <i class="fa-solid fa-address-card"></i> Instagram Profile
                </div>
                <div class="profile-header">
                    <img src="{{ profile.profile_pic_url | e or 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&q=80&w=200' }}" alt="avatar" class="avatar">
                    <div class="profile-title">
                        <h2>{{ profile.full_name | e or username | e }}
                            {% if profile.is_verified %}
                                <i class="fa-solid fa-circle-check badge-verified"></i>
                            {% endif %}
                        </h2>
                        <div class="profile-handle">@{{ username | e }}</div>
                    </div>
                </div>
                <div class="profile-bio">
                    {{ profile.biography | e or "No biography provided." }}
                </div>
                
                {% if profile.simulated %}
                <div class="simulated-warning">
                    <i class="fa-solid fa-triangle-exclamation"></i>
                    <span>Simulation Mode. Live Instagram profile scraping requires a session cookie.</span>
                </div>
                {% endif %}
            </div>

            <!-- Stats/Overview Card -->
            <div class="glass-card card-stats">
                <div class="section-title">
                    <i class="fa-solid fa-chart-simple"></i> Target Metrics
                </div>
                
                <div class="stat-grid">
                    <div class="stat-box">
                        <div class="stat-value">{{ "{:,}".format(profile.follower_count | default(0) | int) }}</div>
                        <div class="stat-label">Followers</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{{ "{:,}".format(profile.following_count | default(0) | int) }}</div>
                        <div class="stat-label">Following</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{{ "{:,}".format(profile.post_count | default(0) | int) }}</div>
                        <div class="stat-label">Posts</div>
                    </div>
                </div>

                <div class="intel-list">
                    <div class="intel-item">
                        <i class="fa-solid fa-lock"></i>
                        <span>Privacy State:</span>
                        <strong style="margin-left: auto; color: {% if profile.is_private %}#ef4444{% else %}var(--accent-emerald){% endif %};">
                            {{ "Private" if profile.is_private else "Public" }}
                        </strong>
                    </div>
                    {% if profile.external_url %}
                    <div class="intel-item">
                        <i class="fa-solid fa-link"></i>
                        <span>External Link:</span>
                        <a href="{{ profile.external_url | e }}" target="_blank" class="value" style="margin-left: auto; color: var(--accent-cyan);">{{ profile.external_url | e }}</a>
                        <button class="copy-btn" onclick="copyToClipboard('{{ profile.external_url | e }}')" title="Copy URL"><i class="fa-regular fa-copy"></i></button>
                    </div>
                    {% endif %}
                </div>
            </div>

            <!-- Parsed Bio Intel Card -->
            <div class="glass-card card-intel">
                <div class="section-title">
                    <i class="fa-solid fa-fingerprint"></i> Bio Intelligence
                </div>
                
                {% if not parsed_intel.emails and not parsed_intel.phones and not parsed_intel.socials %}
                    <div class="empty-text">No contacts or handles extracted from bio.</div>
                {% else %}
                    <ul class="intel-list">
                        {% for email in parsed_intel.emails %}
                        <li class="intel-item">
                            <i class="fa-solid fa-envelope"></i>
                            <span class="value">{{ email | e }}</span>
                            <button class="copy-btn" onclick="copyToClipboard('{{ email | e }}')" title="Copy Email"><i class="fa-regular fa-copy"></i></button>
                        </li>
                        {% endfor %}
                        
                        {% for phone in parsed_intel.phones %}
                        <li class="intel-item">
                            <i class="fa-solid fa-phone"></i>
                            <span class="value">{{ phone | e }}</span>
                            <button class="copy-btn" onclick="copyToClipboard('{{ phone | e }}')" title="Copy Phone"><i class="fa-regular fa-copy"></i></button>
                        </li>
                        {% endfor %}

                        {% for social in parsed_intel.socials %}
                        <li class="intel-item">
                            <i class="fa-solid fa-hashtag"></i>
                            <span>{{ social.platform | e }}:</span>
                            <span class="value" style="margin-left: auto; color: var(--accent-cyan);">@{{ social.handle | e }}</span>
                            <button class="copy-btn" onclick="copyToClipboard('@{{ social.handle | e }}')" title="Copy Handle"><i class="fa-regular fa-copy"></i></button>
                        </li>
                        {% endfor %}
                    </ul>
                {% endif %}
            </div>

            <!-- Cross-Platform Card -->
            <div class="glass-card card-crossplatform">
                <div class="section-title">
                    <i class="fa-solid fa-network-wired"></i> Cross-Platform Presence
                </div>
                <div class="cp-controls">
                    <div style="font-size: 0.9rem; color: var(--text-secondary);">
                        Matches Found: <strong style="color: var(--accent-emerald);" id="matchCounter">{{ found_platforms|length }}</strong> / {{ total_platforms }} platforms checked
                    </div>
                    <label class="toggle-container">
                        <input type="checkbox" id="showFoundOnly" onchange="filterPlatforms()"> Hide N/A Platforms
                    </label>
                    <input type="text" id="platformSearch" class="search-bar" placeholder="Filter platforms..." oninput="filterPlatforms()">
                </div>
                <div class="cp-grid" id="cpGrid">
                    {% for result in cp_results %}
                        <a href="{{ result.url | e }}" target="_blank" 
                           class="cp-badge {% if result.exists %}found{% else %}not-found{% endif %}" 
                           data-name="{{ result.site | lower | e }}"
                           data-exists="{{ 'true' if result.exists else 'false' }}">
                            <span>{{ result.site | e }}</span>
                            {% if result.exists %}
                                <span class="badge-status found">found</span>
                            {% else %}
                                <span class="badge-status not-found" style="background: rgba(255,255,255,0.02); color: rgba(255,255,255,0.1);">N/A</span>
                            {% endif %}
                        </a>
                    {% endfor %}
                </div>
            </div>

            <!-- Search Footprints / Dorks Card -->
            <div class="glass-card card-dorks">
                <div class="section-title">
                    <i class="fa-solid fa-globe"></i> Public Web Footprints & Mentions
                </div>
                <div class="dorks-list">
                    {% for dork in dorks %}
                    <div class="dork-item">
                        <a href="{{ dork.link | e }}" target="_blank" class="dork-title">{{ dork.title | e }}</a>
                        <div class="dork-link">{{ dork.link | e }}</div>
                        <div class="dork-snippet">{{ dork.snippet | e }}</div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>

    <script>
        function filterPlatforms() {
            const query = document.getElementById('platformSearch').value.toLowerCase();
            const showFoundOnly = document.getElementById('showFoundOnly').checked;
            const badges = document.querySelectorAll('.cp-badge');
            let visibleCount = 0;
            
            badges.forEach(badge => {
                const name = badge.getAttribute('data-name');
                const exists = badge.getAttribute('data-exists') === 'true';
                
                const matchesQuery = name.includes(query);
                const matchesToggle = !showFoundOnly || exists;
                
                if (matchesQuery && matchesToggle) {
                    badge.style.display = 'flex';
                    if (exists) visibleCount++;
                } else {
                    badge.style.display = 'none';
                }
            });
            
            document.getElementById('matchCounter').innerText = visibleCount;
        }

        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(function() {
                // Temporary feedback on icon
                const btn = event.currentTarget;
                const origHtml = btn.innerHTML;
                btn.innerHTML = '<i class="fa-solid fa-check" style="color: var(--accent-emerald);"></i>';
                setTimeout(() => {
                    btn.innerHTML = origHtml;
                }, 1500);
            }, function(err) {
                console.error('Could not copy text: ', err);
            });
        }
    </script>
</body>
</html>
"""
        
        # Compile and render using Jinja environment with autoescape enabled
        env = Environment(
            autoescape=select_autoescape(['html', 'xml'])
        )
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        template = env.from_string(template_str)
        html_content = template.render(
            username=self.username,
            profile=profile,
            parsed_intel=parsed_intel,
            cp_results=cp_results,
            dorks=dorks,
            found_platforms=found_platforms,
            total_platforms=total_platforms,
            date_str=date_str
        )
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
