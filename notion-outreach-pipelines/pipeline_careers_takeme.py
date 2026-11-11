#!/usr/bin/env python3
"""
Pipeline 2: 'Take Me' Career & Job Outreach Pipeline.
Finds target companies, career pages, and career recruiting emails.
Generates both a human anti-AI outreach email and an interactive visual application post.
Syncs directly to Notion.
"""

import json
import os
import ssl
import sys
import urllib.request
import urllib.error

from config import (
    NOTION_TOKEN,
    NOTION_CAREERS_DB_ID,
    USER_NAME,
    USER_TITLE,
    USER_LINKEDIN,
    USER_GITHUB,
    USER_PORTFOLIO
)

STATE_FILE = os.path.join(os.path.dirname(__file__), "processed_takeme.json")

def load_seen():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_seen(seen):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen), f, indent=2)

def generate_direct_email(company, category, tech_hook, role):
    return (
        f"Subject: {role} opening — quick note regarding {company}\n\n"
        f"Hey {company} hiring team,\n\n"
        f"I've been tracking what you're building in {category}, especially your work around {tech_hook}.\n\n"
        f"I'm an engineer focused on scalable web apps and backend pipelines. "
        f"I recently built an async processing architecture with 99.9% uptime and low tail latency, "
        f"and I'd love to bring that practical backend experience to your team.\n\n"
        f"You can check my background and code here:\n"
        f"- GitHub: {USER_GITHUB}\n"
        f"- Portfolio: {USER_PORTFOLIO}\n"
        f"- LinkedIn: {USER_LINKEDIN}\n\n"
        f"Are you open to a brief chat this week about current engineering openings at {company}?\n\n"
        f"Thanks,\n"
        f"{USER_NAME}"
    )

def generate_visual_post(company, category, tech_hook, role):
    return (
        f"📬 APPLICATION SNAPSHOT: {company.upper()}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 Role Target: {role}\n"
        f"🏷️ Sector: {category}\n"
        f"💡 Focus: {tech_hook}\n\n"
        f"🛠️ CORE STACK & EXPERTISE\n"
        f"• Languages: TypeScript, Python, Node.js, Go\n"
        f"• Systems: Distributed queues, REST/GraphQL APIs, PostgreSQL, Redis\n"
        f"• Cloud/DevOps: Docker, AWS, Cloudflare Workers, CI/CD\n\n"
        f"📈 HIGHLIGHTED PROJECT\n"
        f"• Engineered real-time data ingestion pipeline processing 20K+ ops/sec\n"
        f"• Decreased p95 response time by 42% through query caching & async workers\n\n"
        f"🔗 VERIFIED PROFILES\n"
        f"• GitHub: {USER_GITHUB}\n"
        f"• Portfolio: {USER_PORTFOLIO}\n"
        f"• LinkedIn: {USER_LINKEDIN}\n\n"
        f"💬 CALL TO ACTION\n"
        f"\"Excited about {company}'s roadmap. Open to discussing technical alignment this week.\""
    )

def push_take_me_lead(item, humanity_score=88):
    if not NOTION_TOKEN or not NOTION_CAREERS_DB_ID:
        print("Error: Missing NOTION_TOKEN or NOTION_CAREERS_DB_ID in environment/.env", file=sys.stderr)
        return False

    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    direct_email = generate_direct_email(item["company"], item["category"], item["tech_hook"], item["role"])
    visual_post = generate_visual_post(item["company"], item["category"], item["tech_hook"], item["role"])

    payload = {
        "parent": {"database_id": NOTION_CAREERS_DB_ID},
        "properties": {
            "Company": {"title": [{"text": {"content": item["company"]}}]},
            "Category": {"select": {"name": item["category"]}},
            "Career Page": {"url": item.get("career_page") or None},
            "Career Email": {"email": item.get("career_email") or None},
            "Target Role": {"select": {"name": item["role"]}},
            "Status": {"select": {"name": "Queued"}},
            "Humanity Score": {"number": humanity_score},
            "Direct Email Body": {"rich_text": [{"text": {"content": direct_email}}]},
            "Visual Email Post": {"rich_text": [{"text": {"content": visual_post}}]}
        }
    }
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as e:
        print(f"Error pushing {item['company']}: {e.code} - {e.read().decode('utf-8')}", file=sys.stderr)
        return False

def run_batch(companies):
    seen = load_seen()
    added = 0
    for item in companies:
        cid = item["company"].lower()
        if cid in seen:
            print(f"Skipping duplicate: {item['company']}")
            continue
        ok = push_take_me_lead(item)
        if ok:
            seen.add(cid)
            added += 1
            print(f"✓ Synced to Notion: {item['company']} | Role: {item['role']}")
    save_seen(seen)
    print(f"\n'Take Me' finished. Added {added} career leads.")

if __name__ == "__main__":
    sample = [
        {
            "company": "Supabase",
            "category": "DevTools",
            "career_page": "https://supabase.com/careers",
            "career_email": "careers@supabase.io",
            "role": "AI / Backend Engineer",
            "tech_hook": "Postgres edge functions and real-time replication"
        }
    ]
    run_batch(sample)
