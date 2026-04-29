import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
SNAPSHOT_FILE = DATA_DIR / "trend_snapshots.json"
ENV_FILE = PROJECT_ROOT / ".env"
CACHE_TTL_SECONDS = 300

GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"
DEVTO_ARTICLES_URL = "https://dev.to/api/articles"
HACKER_NEWS_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HACKER_NEWS_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
REDDIT_PROGRAMMING_TOP_URL = "https://www.reddit.com/r/programming/top.json"


def load_local_env():
    if not ENV_FILE.exists():
        return

    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_local_env()


def getenv_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_app_env():
    return os.getenv("APP_ENV", "development").strip().lower()


def is_production():
    return get_app_env() == "production"


def get_debug_mode():
    return getenv_bool("FLASK_DEBUG", default=False)


def get_secret_key():
    return os.getenv("SECRET_KEY") or "dev-only-change-me"


def get_api_route_key():
    return os.getenv("API_ROUTE_KEY")


def get_allowed_frontend_origins():
    raw_value = os.getenv("FRONTEND_ORIGIN", "")
    origins = []
    for part in raw_value.split(","):
        candidate = part.strip().rstrip("/")
        if candidate:
            origins.append(candidate)

    return tuple(origins)


def get_github_headers():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return {}

    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }


def get_reddit_headers():
    return {
        "User-Agent": os.getenv("REDDIT_USER_AGENT", "TechTrendMonitor/1.0")
    }


def get_smtp_settings():
    return {
        "host": os.getenv("SMTP_HOST"),
        "port": int(os.getenv("SMTP_PORT", "587")),
        "username": os.getenv("SMTP_USERNAME"),
        "password": os.getenv("SMTP_PASSWORD"),
        "from_email": os.getenv("REPORT_FROM_EMAIL") or os.getenv("SMTP_USERNAME")
    }
