# Notion Outreach & Career Automation Pipelines

A dual automated pipeline that finds, categorizes, enriches, and syncs tech leads directly into Notion databases. Built with pure Python standard library (zero external pip packages required).

---

## Architecture Overview

```
notion-outreach-pipelines/
├── .env                  # Local secret keys (ignored by git - NEVER COMMIT)
├── .env.example          # Template for public repo
├── .gitignore            # Protects keys, tokens, and logs
├── config.py             # Pure stdlib environment variable loader
├── pipeline_founders.py  # Pipeline 1: Tech Founders & Leadership outreach
├── pipeline_careers_takeme.py # Pipeline 2: 'Take Me' Job Application outreach
└── README.md
```

---

## Security & Privacy (Zero-Leak Guarantee)

All tokens and database IDs are loaded through `.env` via `config.py`.
The included `.gitignore` strictly prevents:
- Secret tokens (`NOTION_TOKEN`, API keys)
- Notion Database IDs
- Personal state logs and deduplication cache (`processed_*.json`)

When uploading this folder to GitHub, `.env` stays on your local machine.

---

## Setup & Usage

### 1. Configure Credentials
Copy `.env.example` to `.env` (already done on your local setup):
```bash
cp .env.example .env
```
Fill in:
- `NOTION_TOKEN`
- `NOTION_FOUNDERS_DB_ID`
- `NOTION_CAREERS_DB_ID`
- Your public portfolio links

### 2. Run Founders Pipeline
Finds company leaders, drafts a 200-char LinkedIn note and a concise cold email, and syncs to Notion:
```bash
python3 pipeline_founders.py
```

### 3. Run 'Take Me' Career Pipeline
Finds company career emails and application pages, drafts anti-AI humanized application emails + structured visual cards with icons, and syncs to Notion:
```bash
python3 pipeline_careers_takeme.py
```

---

## Features
* **Zero Dependencies**: Pure Python 3 standard library (`urllib.request`, `json`, `os`).
* **Automated Deduplication**: Keeps track of processed companies so no duplicate entries are pushed.
* **Safe from Bans**: Zero scraping bots touching your personal LinkedIn account.
