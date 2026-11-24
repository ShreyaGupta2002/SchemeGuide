# SchemeGuide

**Find Indian government scholarships you actually qualify for.**

SchemeGuide checks your profile against official eligibility rules, shows you exactly which conditions pass or fail, and explains the results in plain language. Every rule is sourced from an official government document.

---

## How to Use SchemeGuide

### Browse Schemes

Go to **Browse Schemes** to see all available government scholarships. Each card shows:
- The ministry running the scheme
- Benefit amount and application year
- A direct link to the official government page

### Check Your Eligibility

Go to **Check Eligibility** and fill in your profile:

| Field | What to enter |
|---|---|
| State | Your state of residence |
| Age | Your age in years |
| Annual Family Income | Total family income in rupees (e.g. `200000` for 2 lakh) |
| Education Level | Your current level — Class 12, Graduation, Post-Graduation, Diploma |
| Caste Category | SC, ST, OBC, or General (as on your certificate) |
| Gender | Male, Female, or Other |
| Parent's Service | Enter `CAPF` if your parent served in a Central Armed Police Force |

You do not need to fill every field. Fields you leave blank show as "Need More Info" — the engine will not incorrectly disqualify you for missing data.

Click **Check Eligibility**. Results appear immediately.

### Reading Your Results

Results are grouped:

- **Appears Eligible** — all checked rules pass for this scheme
- **Need More Info** — some rules could not be checked because you left those fields blank
- **Appears Non-Eligible** — at least one rule failed

Click **Show conditions** on any result to see the full breakdown — each rule shows pass (green), fail (red), or unknown (grey), with the official reason.

> These results are informational only. SchemeGuide checks published rules but cannot guarantee final eligibility. Always confirm with the official scheme portal before applying.

### AI Explanation

Click **Explain with AI ✨** on any result to get a plain-language explanation of why you are or are not eligible, and what you would need to qualify. Requires a free Groq API key (see setup below).

### Reporting Incorrect Information

If you believe an eligibility rule is wrong or outdated, click **Report incorrect info** on that result. The core team reviews all reports and updates the data with a verified source.

---

## Run It Locally

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (make sure it is running)
- Git

### 1. Clone

```bash
git clone https://github.com/ShuvechhaNandi/SchemeGuide.git
cd SchemeGuide
```

### 2. Create `.env`

```bash
cp .env.example .env
```

Generate secrets and fill in `.env`:

```bash
# CATALOG_SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(50))"

# POSTGRES_PASSWORD — use the same value in all three DATABASE_URLs
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

For AI explanations, add a free Groq API key:
1. Create a free account at [console.groq.com](https://console.groq.com)
2. Go to **API Keys** → **Create API Key**
3. Add `GROQ_API_KEY=gsk_...` to your `.env`

### 3. Start

```bash
make up --build
```

Or without make:

```bash
docker compose -f infra/compose.yaml --env-file .env up --build
```

Wait until you see `Installed X object(s) from 1 fixture(s)` — that means sample data loaded. Open `http://localhost`.

### 4. Create a superuser (for Django Admin)

```bash
docker compose -f infra/compose.yaml --env-file .env exec catalog \
  python manage.py createsuperuser
```

Log in at `http://localhost/admin` to manage scheme data.

### Reset sample data

```bash
docker compose -f infra/compose.yaml --env-file .env down -v
docker compose -f infra/compose.yaml --env-file .env up --build
# then re-create superuser (step 4)
```

---

## Architecture

```
React Frontend → Nginx Gateway → 4 Python services → PostgreSQL
```

| Service | Technology | Port | Responsibility |
|---|---|---|---|
| Catalog | Django + DRF | 8001 | Scheme data, rules, sources, admin |
| Eligibility | FastAPI | 8002 | Deterministic rule evaluation |
| AI Assistant | FastAPI + Groq | 8003 | Plain-language explanations |
| Feedback | FastAPI | 8004 | User-submitted corrections |

## Project Structure

```
SchemeGuide/
├── services/
│   ├── catalog/       Django REST Framework + Admin
│   ├── eligibility/   FastAPI — rule evaluation
│   ├── assistant/     FastAPI — AI explanations (Groq)
│   └── feedback/      FastAPI — user corrections
├── frontend/          React + Vite + React Bootstrap
├── gateway/           Nginx reverse proxy
├── infra/             Docker Compose + DB init SQL
└── docs/              Architecture, data maintenance, handoff
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for code contributions.
See [docs/data-maintenance.md](docs/data-maintenance.md) to add or correct scheme data.
See [docs/HANDOFF.md](docs/HANDOFF.md) for the full project state and what still needs building.

## License

Apache-2.0 — see [LICENSE](LICENSE).
