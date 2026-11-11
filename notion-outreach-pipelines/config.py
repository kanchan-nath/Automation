import os

def load_env(env_path=".env"):
    """Load key-value pairs from .env into os.environ using pure Python stdlib."""
    if not os.path.exists(env_path):
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip("'").strip('"')
            if k not in os.environ:
                os.environ[k] = v

load_env(os.path.join(os.path.dirname(__file__), ".env"))

NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
NOTION_FOUNDERS_DB_ID = os.getenv("NOTION_FOUNDERS_DB_ID", "")
NOTION_CAREERS_DB_ID = os.getenv("NOTION_CAREERS_DB_ID", "")

USER_NAME = os.getenv("USER_NAME", "[YOUR_NAME]")
USER_TITLE = os.getenv("USER_TITLE", "[YOUR_TITLE]")
USER_LINKEDIN = os.getenv("USER_LINKEDIN_URL", "https://linkedin.com/in/[YOUR_PROFILE]")
USER_GITHUB = os.getenv("USER_GITHUB_URL", "https://github.com/[YOUR_GITHUB]")
USER_PORTFOLIO = os.getenv("USER_PORTFOLIO_URL", "https://[YOUR_PORTFOLIO_LINK]")
