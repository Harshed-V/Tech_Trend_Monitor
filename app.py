import os
import secrets
from datetime import datetime

from flask import Flask, jsonify, redirect, render_template, request, url_for

from config import (
    get_allowed_frontend_origins,
    get_api_route_key,
    get_debug_mode,
    get_secret_key,
    get_smtp_settings,
    is_production,
)
from trend_service import (
    build_trend_snapshot,
    generate_insights,
    generate_summary,
    get_average_score_by_platform,
    get_distribution,
    get_event_items,
    get_trending_items,
    load_snapshots,
    search_items_across_pages,
    send_report_email,
)


ALLOWED_TRENDING_TYPES = {"daily", "weekly"}
DEFAULT_TRENDING_TYPE = "weekly"

app = Flask(__name__)
app.config.update(
    SECRET_KEY=get_secret_key(),
    DEBUG=get_debug_mode(),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=is_production(),
    PREFERRED_URL_SCHEME="https" if is_production() else "http",
)

if is_production() and app.config["SECRET_KEY"] == "dev-only-change-me":
    raise RuntimeError("SECRET_KEY must be set before running in production.")


def normalize_origin(value):
    return (value or "").strip().rstrip("/")


def get_selected_trending_type():
    trending_type = request.args.get("type", default=DEFAULT_TRENDING_TYPE)
    if trending_type not in ALLOWED_TRENDING_TYPES:
        return DEFAULT_TRENDING_TYPE

    return trending_type


def origin_matches_allowed_frontend(origin):
    normalized_origin = normalize_origin(origin)
    return normalized_origin in get_allowed_frontend_origins()


def request_from_allowed_frontend():
    allowed_origins = get_allowed_frontend_origins()
    if not allowed_origins:
        return True

    origin = normalize_origin(request.headers.get("Origin"))
    if origin and origin_matches_allowed_frontend(origin):
        return True

    referer = request.headers.get("Referer", "").strip()
    for allowed_origin in allowed_origins:
        if referer == allowed_origin or referer.startswith(f"{allowed_origin}/"):
            return True

    return False


def request_has_valid_api_key():
    expected_api_key = get_api_route_key()
    provided_api_key = request.headers.get("x-api-key", "")

    if not expected_api_key or not provided_api_key:
        return False

    return secrets.compare_digest(provided_api_key, expected_api_key)


def api_request_is_authorized():
    return request_from_allowed_frontend() or request_has_valid_api_key()


def json_error(message, status_code, error="Request failed"):
    response = jsonify({
        "error": error,
        "message": message,
    })
    response.status_code = status_code
    return response


@app.after_request
def apply_response_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")

    if request.path.startswith("/api/"):
        origin = normalize_origin(request.headers.get("Origin"))
        if origin and origin_matches_allowed_frontend(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-API-Key"
            response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response.headers["Vary"] = "Origin"

    return response


@app.route("/")
def home():
    trending_type = get_selected_trending_type()
    items = get_trending_items(trending_type=trending_type, page=1)
    summary = generate_summary(items)
    insights = generate_insights(items)
    top_items = items[:3]
    snapshot = build_trend_snapshot(items, trending_type)
    current_time = datetime.now().strftime("%d %b %Y, %I:%M %p")

    return render_template(
        "index.html",
        items=items,
        top_items=top_items,
        summary=summary,
        insights=insights,
        snapshot=snapshot,
        selected_type=trending_type,
        current_time=current_time,
    )


@app.route("/analytics")
def analytics():
    trending_type = get_selected_trending_type()
    items = get_trending_items(trending_type=trending_type)
    return render_template(
        "analytics.html",
        selected_type=trending_type,
        platform_distribution=get_distribution(items, "source"),
        topic_distribution=get_distribution(items, "topic"),
        average_scores=get_average_score_by_platform(items),
        total_items=len(items),
    )


@app.route("/explore")
def explore():
    trending_type = get_selected_trending_type()
    items = get_trending_items(trending_type=trending_type)
    return render_template(
        "explore.html",
        items=items,
        selected_type=trending_type,
    )


@app.route("/events")
def events():
    trending_type = get_selected_trending_type()
    items = get_event_items(get_trending_items(trending_type=trending_type))
    return render_template(
        "events.html",
        items=items,
        selected_type=trending_type,
    )


@app.route("/reports")
def reports():
    smtp_settings = get_smtp_settings()
    smtp_configured = all([
        smtp_settings["host"],
        smtp_settings["port"],
        smtp_settings["username"],
        smtp_settings["password"],
        smtp_settings["from_email"],
    ])

    return render_template(
        "reports.html",
        snapshots=load_snapshots(),
        message=request.args.get("message", ""),
        error=request.args.get("error", ""),
        smtp_configured=smtp_configured,
        report_from_email=smtp_settings["from_email"],
    )


@app.route("/send-report", methods=["POST"])
def send_report():
    to_email = request.form.get("to_email", "").strip()
    trending_type = request.form.get("type", DEFAULT_TRENDING_TYPE)

    if trending_type not in ALLOWED_TRENDING_TYPES:
        trending_type = DEFAULT_TRENDING_TYPE

    if not to_email:
        return redirect(url_for("reports", error="Enter a recipient email address."))

    success, message = send_report_email(to_email, trending_type)
    if success:
        return redirect(url_for("reports", message=message))

    return redirect(url_for("reports", error=message))


@app.route("/api/trends", methods=["GET", "OPTIONS"])
def api_trends():
    if request.method == "OPTIONS":
        origin = request.headers.get("Origin")
        if origin and not origin_matches_allowed_frontend(origin):
            return json_error("Origin is not allowed for this API route.", 403, error="Origin not allowed")

        return ("", 204)

    if not api_request_is_authorized():
        return json_error(
            "This endpoint accepts same-origin frontend requests or a valid x-api-key header.",
            401,
            error="Unauthorized",
        )

    page = request.args.get("page", default=1, type=int)
    if page < 1:
        page = 1

    query = request.args.get("q", default="")
    trending_type = get_selected_trending_type()

    if (query or "").strip():
        search_pages = request.args.get("search_pages", default=6, type=int)
        if search_pages < 1:
            search_pages = 1
        if search_pages > 20:
            search_pages = 20

        items = search_items_across_pages(
            trending_type=trending_type,
            query=query,
            max_pages=search_pages,
            limit=200,
        )
        has_more = False
    else:
        items = get_trending_items(trending_type=trending_type, page=page)
        has_more = len(items) > 0

    return jsonify({
        "items": items,
        "has_more": has_more,
        "page": page,
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=app.config["DEBUG"],
    )
