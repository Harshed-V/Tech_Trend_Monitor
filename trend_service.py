import json
import logging
import smtplib
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

import requests

from config import (
    CACHE_TTL_SECONDS,
    DATA_DIR,
    DEVTO_ARTICLES_URL,
    GITHUB_SEARCH_URL,
    HACKER_NEWS_ITEM_URL,
    HACKER_NEWS_TOP_STORIES_URL,
    REDDIT_PROGRAMMING_TOP_URL,
    SNAPSHOT_FILE,
    get_github_headers,
    get_reddit_headers,
    get_smtp_settings,
)


logger = logging.getLogger(__name__)
TREND_CACHE = {}


def get_trending_items(trending_type="weekly", page=1):
    cache_key = (trending_type, page)
    cached = TREND_CACHE.get(cache_key)
    if cached and time.time() - cached["created_at"] < CACHE_TTL_SECONDS:
        return cached["items"]

    with ThreadPoolExecutor(max_workers=4) as executor:
        github_future = executor.submit(get_trending_repos, trending_type, page)
        devto_future = executor.submit(get_devto_articles, trending_type, page)
        hacker_news_future = executor.submit(get_hacker_news_stories, page)
        reddit_future = executor.submit(get_reddit_posts, trending_type, page)

        github_data = github_future.result()
        devto_data = devto_future.result()
        hacker_news_data = hacker_news_future.result()
        reddit_data = reddit_future.result()

    all_data = github_data + devto_data + hacker_news_data + reddit_data

    items = sorted(all_data, key=lambda item: item["score"], reverse=True)
    TREND_CACHE[cache_key] = {
        "created_at": time.time(),
        "items": items,
    }

    return items


def filter_items_by_query(items, query):
    cleaned_query = (query or "").strip().lower()
    if not cleaned_query:
        return items

    tokens = [token for token in cleaned_query.split() if token]
    if not tokens:
        return items

    def normalize(value):
        if value is None:
            return ""
        return str(value)

    filtered = []
    for item in items:
        haystack = " ".join([
            normalize(item.get("title", "")),
            normalize(item.get("description", "")),
            normalize(item.get("topic", "")),
            normalize(item.get("name", "")),
            normalize(item.get("source", "")),
        ]).lower()

        if cleaned_query in haystack or all(token in haystack for token in tokens):
            filtered.append(item)

    return filtered


def search_items_across_pages(trending_type, query, max_pages=6, limit=200):
    cleaned_query = (query or "").strip()
    if not cleaned_query:
        return []

    seen = set()
    results = []

    for page_num in range(1, max_pages + 1):
        page_items = get_trending_items(trending_type=trending_type, page=page_num)
        if not page_items:
            break

        matched = filter_items_by_query(page_items, cleaned_query)
        for item in matched:
            unique_key = item.get("link") or item.get("title")
            if unique_key in seen:
                continue

            seen.add(unique_key)
            results.append(item)

            if len(results) >= limit:
                break

        if len(results) >= limit:
            break

    results.sort(key=lambda item: item.get("score", 0), reverse=True)
    return results


def get_trending_repos(trending_type="weekly", page=1):
    query_parts = []

    if trending_type == "daily":
        created_after = datetime.now(timezone.utc) - timedelta(days=1)
        query_parts.append(f"created:>{created_after:%Y-%m-%d}")
    elif trending_type == "weekly":
        created_after = datetime.now(timezone.utc) - timedelta(days=7)
        query_parts.append(f"created:>{created_after:%Y-%m-%d}")

    query = "+".join(query_parts)
    url = f"{GITHUB_SEARCH_URL}?q={query}&sort=stars&per_page=10&page={page}"

    try:
        response = requests.get(url, headers=get_github_headers(), timeout=8)
        response.raise_for_status()
        data = response.json()

        if "items" not in data:
            return []

        repos = []
        for item in data["items"]:
            topic = detect_topic(item["name"], item.get("description"), item["language"])
            stars = item["stargazers_count"]

            repos.append({
                "title": item["name"],
                "name": item["name"],
                "score": stars,
                "score_label": "stars",
                "description": item.get("description") or "No description available.",
                "link": item["html_url"],
                "topic": topic,
                "source": "GitHub",
                "why_trending": get_trending_reason(stars, topic),
            })

        return repos

    except Exception as error:
        logger.warning("GitHub fetch failed: %s", error)
        return []


def get_hacker_news_stories(page=1):
    try:
        story_ids_response = requests.get(HACKER_NEWS_TOP_STORIES_URL, timeout=8)
        story_ids_response.raise_for_status()
        story_ids = story_ids_response.json()

        if not isinstance(story_ids, list):
            return []

        stories = []
        start = (page - 1) * 10
        end = start + 10
        story_ids = story_ids[start:end]

        def fetch_story(story_id):
            item_response = requests.get(
                HACKER_NEWS_ITEM_URL.format(story_id=story_id),
                timeout=6,
            )
            item_response.raise_for_status()
            item = item_response.json()

            if not isinstance(item, dict) or item.get("type") != "story":
                return None

            title = item.get("title", "Untitled story")
            score = item.get("score", 0)
            topic = detect_topic(title)

            return {
                "title": title,
                "name": title,
                "score": score,
                "score_label": "upvotes",
                "description": "Industry discussion trending on Hacker News.",
                "link": item.get("url") or f"https://news.ycombinator.com/item?id={story_id}",
                "topic": topic,
                "source": "Hacker News",
                "why_trending": get_community_trending_reason(score, topic, "Hacker News"),
            }

        with ThreadPoolExecutor(max_workers=10) as executor:
            for story in executor.map(fetch_story, story_ids):
                if story:
                    stories.append(story)

        return stories

    except Exception as error:
        logger.warning("Hacker News fetch failed: %s", error)
        return []


def get_devto_articles(trending_type="weekly", page=1):
    top_days = 1 if trending_type == "daily" else 7
    url = f"{DEVTO_ARTICLES_URL}?top={top_days}&per_page=10&page={page}"

    try:
        response = requests.get(url, timeout=8)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            return []

        articles = []
        for item in data:
            reactions = item.get("public_reactions_count", 0)
            tags = item.get("tag_list") or []
            topic = detect_topic(item.get("title"), item.get("description"), " ".join(tags))

            articles.append({
                "title": item.get("title", "Untitled article"),
                "name": item.get("title", "Untitled article"),
                "score": reactions,
                "score_label": "reactions",
                "description": item.get("description") or "No description available.",
                "link": item.get("url", "#"),
                "topic": topic,
                "source": "Dev.to",
                "why_trending": get_article_trending_reason(reactions, topic),
            })

        return articles[:10]

    except Exception as error:
        logger.warning("Dev.to fetch failed: %s", error)
        return []


def get_reddit_posts(trending_type="weekly", page=1):
    time_window = "day" if trending_type == "daily" else "week"
    limit = page * 10
    url = f"{REDDIT_PROGRAMMING_TOP_URL}?t={time_window}&limit={limit}"

    try:
        response = requests.get(url, headers=get_reddit_headers(), timeout=8)
        response.raise_for_status()
        data = response.json()
        posts = data.get("data", {}).get("children", [])

        if not isinstance(posts, list):
            return []

        reddit_items = []
        start = (page - 1) * 10
        end = start + 10
        for post in posts[start:end]:
            item = post.get("data", {})
            title = item.get("title", "Untitled Reddit post")
            score = item.get("ups", 0)
            topic = detect_topic(title, item.get("selftext", ""))

            reddit_items.append({
                "title": title,
                "name": title,
                "score": score,
                "score_label": "upvotes",
                "description": item.get("selftext") or "Community discussion trending on r/programming.",
                "link": item.get("url") or f"https://www.reddit.com{item.get('permalink', '')}",
                "topic": topic,
                "source": "Reddit",
                "why_trending": get_community_trending_reason(score, topic, "Reddit"),
            })

        return reddit_items

    except Exception as error:
        logger.warning("Reddit fetch failed: %s", error)
        return []


def detect_topic(name, description="", language=""):
    text = f"{name or ''} {description or ''} {language or ''}".lower()

    topic_keywords = {
        "AI": ["ai", "agent", "llm", "machine learning", "openai", "model"],
        "Web Development": ["web", "react", "next", "javascript", "css", "frontend"],
        "Python": ["python", "django", "flask", "fastapi"],
        "Cloud": ["cloud", "aws", "azure", "gcp", "docker", "kubernetes"],
        "Security": ["security", "auth", "vulnerability", "privacy"],
        "Developer Tools": ["cli", "tool", "framework", "library", "api"],
    }

    for topic, keywords in topic_keywords.items():
        if any(keyword in text for keyword in keywords):
            return topic

    return language or "General Tech"


def get_trending_reason(stars, topic):
    if stars >= 100000:
        return f"Trending due to very high GitHub stars and strong community adoption in {topic}."

    if stars >= 10000:
        return f"Trending due to strong developer interest and high engagement around {topic}."

    return f"Trending due to fresh community activity and growing interest in {topic}."


def get_article_trending_reason(reactions, topic):
    if reactions >= 100:
        return f"Trending due to high Dev.to reactions and active discussion around {topic}."

    if reactions >= 25:
        return f"Trending due to steady reader engagement from the developer community around {topic}."

    return f"Trending due to early reader interest in {topic}."


def get_community_trending_reason(score, topic, source):
    if score >= 500:
        return f"Trending due to high community upvotes and active discussion on {source} around {topic}."

    if score >= 100:
        return f"Trending due to strong community attention on {source} around {topic}."

    return f"Trending due to fresh community discussion on {source} around {topic}."


def generate_summary(repos):
    if not repos:
        return "No trend data available right now."

    return f"Monitoring {len(repos)} tech signals merged from GitHub, Dev.to, Hacker News, and Reddit."


def generate_insights(repos):
    if not repos:
        return {
            "most_active_platform": "N/A",
            "top_topic": "N/A",
            "highest_engagement": "0",
            "top_item": "N/A",
        }

    platform_count = {}
    topic_count = {}

    for item in repos:
        platform_count[item["source"]] = platform_count.get(item["source"], 0) + 1
        topic_count[item["topic"]] = topic_count.get(item["topic"], 0) + 1

    most_active_platform = max(platform_count, key=platform_count.get)
    top_topic = max(topic_count, key=topic_count.get)
    highest_engagement = max(item["score"] for item in repos)

    return {
        "most_active_platform": most_active_platform,
        "top_topic": top_topic,
        "highest_engagement": f"{highest_engagement:,}",
        "top_item": repos[0]["name"],
    }


def get_distribution(items, key):
    distribution = {}
    for item in items:
        value = item.get(key, "Unknown")
        distribution[value] = distribution.get(value, 0) + 1

    return sorted(distribution.items(), key=lambda row: row[1], reverse=True)


def get_average_score_by_platform(items):
    totals = {}
    counts = {}

    for item in items:
        source = item["source"]
        totals[source] = totals.get(source, 0) + item["score"]
        counts[source] = counts.get(source, 0) + 1

    return [
        (source, totals[source] // counts[source])
        for source in sorted(totals)
    ]


def get_event_items(items):
    event_keywords = [
        "event", "conference", "hackathon", "launch", "release",
        "summit", "webinar", "challenge", "meetup",
    ]
    events = []

    for item in items:
        text = f"{item['title']} {item['description']}".lower()
        if any(keyword in text for keyword in event_keywords):
            events.append(item)

    return events


def load_snapshots():
    if not SNAPSHOT_FILE.exists():
        return []

    try:
        return json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))[-20:]
    except json.JSONDecodeError:
        return []


def build_email_report(trending_type="weekly"):
    items = get_trending_items(trending_type=trending_type, page=1)
    insights = generate_insights(items)
    lines = [
        "Tech Trend Monitor Report",
        "",
        f"Report type: {trending_type.title()}",
        f"Generated: {datetime.now().strftime('%d %b %Y, %I:%M %p')}",
        "",
        "Insights",
        f"- Most active platform: {insights['most_active_platform']}",
        f"- Top topic: {insights['top_topic']}",
        f"- Highest engagement: {insights['highest_engagement']}",
        "",
        "Top Trends",
    ]

    for index, item in enumerate(items[:10], start=1):
        lines.extend([
            "",
            f"{index}. {item['title']}",
            f"Source: {item['source']}",
            f"Topic: {item['topic']}",
            f"Score: {item['score']} {item['score_label']}",
            f"Why trending: {item['why_trending']}",
            f"Link: {item['link']}",
        ])

    return "\n".join(lines), items


def send_report_email(to_email, trending_type="weekly"):
    smtp_settings = get_smtp_settings()
    smtp_host = smtp_settings["host"]
    smtp_port = smtp_settings["port"]
    smtp_username = smtp_settings["username"]
    smtp_password = smtp_settings["password"]
    from_email = smtp_settings["from_email"]

    if not smtp_host or not smtp_username or not smtp_password or not from_email:
        return False, "Email is not configured. Set SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, and REPORT_FROM_EMAIL."

    report_body, items = build_email_report(trending_type)

    message = EmailMessage()
    message["Subject"] = f"Tech Trend Monitor {trending_type.title()} Report"
    message["From"] = from_email
    message["To"] = to_email
    message.set_content(report_body)

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(message)

        save_trend_snapshot(items, trending_type)
        return True, f"Report sent to {to_email}."
    except Exception as error:
        logger.warning("Email delivery failed: %s", error)
        return False, f"Could not send report: {error}"


def save_trend_snapshot(repos, trending_type):
    DATA_DIR.mkdir(exist_ok=True)

    snapshots = []
    if SNAPSHOT_FILE.exists():
        try:
            snapshots = json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            snapshots = []

    snapshot = build_trend_snapshot(repos, trending_type)

    snapshots.append(snapshot)
    SNAPSHOT_FILE.write_text(json.dumps(snapshots[-30:], indent=2), encoding="utf-8")

    return snapshot


def build_trend_snapshot(repos, trending_type):
    now = datetime.now(timezone.utc)
    top_repo = repos[0] if repos else None

    return {
        "checked_at": now.isoformat(timespec="seconds"),
        "date": now.strftime("%Y-%m-%d"),
        "source": "merged",
        "type": trending_type,
        "repo_count": len(repos),
        "top_repo": top_repo["name"] if top_repo else "N/A",
        "highest_score": top_repo["score"] if top_repo else 0,
    }
