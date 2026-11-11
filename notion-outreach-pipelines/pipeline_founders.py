#!/usr/bin/env python3
"""
Pipeline 1: Founders & Tech Leaders Pipeline.
Pulls targeted company founders, builds connection notes (<200 chars) & cold emails,
deduplicates locally, and syncs directly to Notion.
"""

import json
import os
import ssl
import sys
import urllib.request
import urllib.error

from config import (
    NOTION_TOKEN,
    NOTION_FOUNDERS_DB_ID,
    USER_NAME,
    USER_TITLE,
    USER_LINKEDIN
)

STATE_FILE = os.path.join(os.path.dirname(__file__), "processed_founders.json")

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

def generate_notes(name, role, company, category, pitch):
    first = name.split()[0] if name else "there"
    # LinkedIn note strictly < 200 chars
    li_note = f"Hi {first}, following your journey building {company} in {category}. Really inspired by your architecture and vision. Would love to connect!"
    if len(li_note) > 195:
        li_note = f"Hi {first}, following your work on {company} ({category}). Huge fan of what you're building. Let's connect!"

    email = (
        f"Subject: Quick question regarding {company} & {category}\n\n"
        f"Hi {first},\n\n"
        f"I've been closely following {company}'s momentum in the {category} space, especially {pitch}.\n\n"
        f"As a tech engineer working across modern architectures, I really appreciate your execution here.\n\n"
        f"Would love to stay connected on your journey. Feel free to connect on LinkedIn if you're open:\n"
        f"{USER_LINKEDIN}\n\n"
        f"Best regards,\n"
        f"{USER_NAME}\n"
        f"{USER_TITLE}"
    )
    return li_note, email

def push_lead(lead):
    if not NOTION_TOKEN or not NOTION_FOUNDERS_DB_ID:
        print("Error: Missing NOTION_TOKEN or NOTION_FOUNDERS_DB_ID in environment/.env", file=sys.stderr)
        return False

    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    li_note, email_body = generate_notes(
        lead["name"], lead["role"], lead["company"], lead["category"], lead.get("pitch", "your recent technical milestones")
    )
    payload = {
        "parent": {"database_id": NOTION_FOUNDERS_DB_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": lead["name"]}}]},
            "Company": {"rich_text": [{"text": {"content": lead["company"]}}]},
            "Category": {"select": {"name": lead["category"]}},
            "Role": {"select": {"name": lead["role"]}},
            "LinkedIn URL": {"url": lead.get("linkedin_url") or None},
            "Email": {"email": lead.get("email") or None},
            "Status": {"select": {"name": "Queued"}},
            "LinkedIn Note": {"rich_text": [{"text": {"content": li_note}}]},
            "Cold Email Draft": {"rich_text": [{"text": {"content": email_body}}]}
        }
    }
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as e:
        print(f"Error pushing {lead['name']}: {e.code} - {e.read().decode('utf-8')}", file=sys.stderr)
        return False

def run_batch(leads):
    seen = load_seen()
    added = 0
    for lead in leads:
        cid = f"{lead['company'].lower()}:{lead['name'].lower()}"
        if cid in seen:
            print(f"Skipping duplicate: {lead['company']} ({lead['name']})")
            continue
        success = push_lead(lead)
        if success:
            seen.add(cid)
            added += 1
            print(f"✓ Synced to Notion: {lead['name']} ({lead['company']} - {lead['role']})")
    save_seen(seen)
    print(f"\nPipeline finished. Added {added} new leads.")

if __name__ == "__main__":
    # Example test batch
    sample = [
        {
            "name": "Harrison Chase",
            "company": "LangChain",
            "category": "AI DevTools",
            "role": "CEO",
            "linkedin_url": "https://www.linkedin.com/in/harrison-chase-961287118/",
            "email": "harrison@langchain.dev",
            "pitch": "composable agent abstractions"
        }
    ]
    run_batch(sample)
