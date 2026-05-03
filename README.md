# Tech Trend Monitor

Tech Trend Monitor is a Flask-based web application that aggregates developer signals from GitHub, Dev.to, Hacker News, and Reddit into one interface.

**Live Demo:** [https://tech-trend-monitor.onrender.com/](https://tech-trend-monitor.onrender.com/)

## Features

- **Multi-source aggregation**: Combines repositories, articles, and community discussions from multiple platforms.
- **Trend analysis**: Detects common topics such as AI, Web Development, Python, Cloud, and Security.
- **Analytics dashboard**: Shows source distribution, topic distribution, and average engagement.
- **Event tracking**: Pulls likely launches, conferences, hackathons, and releases from trend data.
- **Email reporting**: Generates and sends summary reports through SMTP.
- **Secure backend fetching**: External APIs are called only from backend Python service functions.
- **Protected API route**: `/api/trends` supports same-origin frontend access and optional `x-api-key` access for external clients.

## Architecture

```text
Frontend (Flask templates)
        ->
Flask routes + security
        ->
Python service layer
        ->
External APIs
```

## Project Structure

```text
app.py                 Flask routes and security checks
trend_service.py       External API fetching, aggregation, email reports
config.py              Environment variable helpers and shared config
templates/             HTML templates
static/                CSS, JS, images
data/                  Local snapshot history
```

## Installation

1. Clone the repository:

```bash
git clone <https://github.com/Harshed-V/Tech_Trend_Monitor>
cd tech-trend-monitor
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy the environment template:

```bash
copy .env.example .env
```

5. Fill in your local `.env` file:

```ini
APP_ENV=development
SECRET_KEY=replace_with_a_long_random_secret_key
FRONTEND_ORIGIN=http://127.0.0.1:5000
API_ROUTE_KEY=replace_with_a_long_random_api_key
GITHUB_TOKEN=optional_github_token_for_higher_rate_limits
REDDIT_USER_AGENT=TechTrendMonitor/1.0 (contact@yourdomain.com)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
REPORT_FROM_EMAIL=your_email@gmail.com
```

## Environment Variables

- `APP_ENV`: Use `development` locally and `production` on Render.
- `SECRET_KEY`: Required in production for Flask session security.
- `FRONTEND_ORIGIN`: Allowed frontend origin for CORS and same-origin API protection. You can provide more than one origin separated by commas.
- `API_ROUTE_KEY`: Optional key for server-to-server calls to `/api/trends`.
- `GITHUB_TOKEN`: Optional, but recommended to avoid GitHub API rate limits.
- `REDDIT_USER_AGENT`: User-Agent for Reddit requests.
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`: Required for email reports.
- `REPORT_FROM_EMAIL`: Sender address for email reports.

## Running Locally

Start the development server:

```bash
python app.py
```

Open:

[http://127.0.0.1:5000](http://127.0.0.1:5000)

## Routes

### UI

- `/`
- `/analytics`
- `/explore`
- `/events`
- `/reports`

### API

- `/api/trends`
  - Query params: `type`, `page`, `q`, `search_pages`
  - Same-origin frontend requests are allowed
  - External clients can use `x-api-key: <API_ROUTE_KEY>`

## Security Notes

- Keep secrets only in `.env` or Render environment variables.
- Never put API keys, SMTP passwords, or `SECRET_KEY` in HTML, CSS, or JavaScript.
- Never commit `.env`.
- Rotate any secret immediately if it was pushed to GitHub or shared publicly.
- Keep external API requests in backend Python files only.

## Render Deployment

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
gunicorn app:app
```

### Add Environment Variables in Render

In Render:

`Dashboard -> Your Web Service -> Environment`

Add:

- `APP_ENV=production`
- `SECRET_KEY=your_long_random_secret`
- `FRONTEND_ORIGIN=https://your-app-name.onrender.com`
- `API_ROUTE_KEY=your_long_random_api_key` if you need external API access
- `GITHUB_TOKEN=...` if you use one
- `REDDIT_USER_AGENT=TechTrendMonitor/1.0 (you@yourdomain.com)`
- `SMTP_HOST=...`
- `SMTP_PORT=587`
- `SMTP_USERNAME=...`
- `SMTP_PASSWORD=...`
- `REPORT_FROM_EMAIL=...`

### Recommended Render Settings

- Environment: `Python`
- Auto-deploy: enabled
- Health check path: `/`

## License

This project is licensed under the MIT License.
