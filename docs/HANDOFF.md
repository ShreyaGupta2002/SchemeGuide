# SchemeGuide — Handoff Document

Last updated: November 2026

---

## What is SchemeGuide?

An open-source web application that helps Indian students and citizens discover government scholarships, check eligibility against official published rules, and get plain-language explanations. Every eligibility rule is sourced from an official government document — no guessing, no AI deciding eligibility.

---

## Architecture

```
[React Frontend]
      |
 [Nginx :80]  ← single public entry point
      |
  ┌───┼──────┬──────┐
  │   │      │      │
Catalog  Eligibility  Assistant  Feedback
(Django)  (FastAPI)   (FastAPI)  (FastAPI)
 :8001     :8002       :8003      :8004
  │                               │
Postgres                       Postgres
catalog_db                     feedback_db
```

All services run in Docker. Nginx is the only port exposed publicly (port 80). Services talk to each other by container name on the Docker internal network.

---

## Repository

```
https://github.com/ShuvechhaNandi/SchemeGuide
```

---

## Current Status

| Component | Status | Notes |
|---|---|---|
| Catalog service | ✅ Working | Django + DRF, Django Admin with CSS |
| Eligibility service | ✅ Working | 8 operators, 35 unit tests passing |
| AI Assistant service | ✅ Working | Groq API (httpx), needs GROQ_API_KEY |
| Feedback service | ✅ Working | SQLAlchemy + PostgreSQL |
| React frontend | ✅ Working | Browse, eligibility check, AI explain button |
| Docker Compose | ✅ Working | All 6 services orchestrated |
| Sample data fixture | ✅ Working | 3 real Indian govt schemes auto-loaded on startup |
| Tests | ⚠️  Partial | 35 engine unit tests; no API or integration tests |
| GitHub Actions CI | ❌ Not started | No CI workflows |

---

## Services

### 1. Catalog — `services/catalog/` (Django + DRF)

Owns all scheme data. Exposes a REST API and Django Admin for data management.

**Models:**
```
Scheme              name, department, jurisdiction, state
SchemeVersion       description, benefit_amount, applicable_year,
                    application_open/close, official_url,
                    status (draft → reviewed → published)
EligibilityRule     field, operator, value, explanation, source_passage
SourceDocument      title, official_url, retrieval_date
SourcePassage       text, section_reference
RequiredDocument    name, when_required
ReviewRecord        reviewer, decision, comments
```

**API:**
```
GET  /api/v1/schemes/        list all published schemes (with latest_version)
GET  /api/v1/schemes/{id}/   scheme detail with rules and sources
```

**Key details:**
- WhiteNoise middleware serves Django static files (admin CSS/JS) through gunicorn — no separate static file server needed
- `collectstatic` runs automatically on container startup
- Fixtures at `fixtures/sample_schemes.json` are loaded automatically via `loaddata` on startup
- Status workflow: contributors add data as `draft`, admin promotes to `published` via Django Admin

**Run the startup command:**
```bash
python manage.py migrate
python manage.py loaddata fixtures/sample_schemes.json || true
python manage.py collectstatic --noinput
gunicorn catalog_service.wsgi:application --bind 0.0.0.0:8001
```

---

### 2. Eligibility — `services/eligibility/` (FastAPI)

Stateless service. Fetches published rules from Catalog, evaluates them against a user profile, returns structured results.

**API:**
```
POST /api/v1/matches
Body:  { "profile": { "caste_category": "SC", "annual_income": 200000, ... } }
Response: { "results": [ { "scheme_id": 1, "outcome": "appears_eligible", "conditions": [...] } ] }
```

**Outcomes:**
- `appears_eligible` — all rules pass
- `appears_non_eligible` — at least one rule fails
- `more_information_needed` — no failures but some fields were not provided

**Supported operators:** `equals`, `not_equals`, `in`, `not_in`, `gte`, `lte`, `gt`, `lt`

**Rule result per condition:** `pass`, `fail`, or `unknown` (when user didn't provide that field)

**Key rule:** a `fail` always beats `unknown` — a definite disqualifier wins even if other fields are missing.

**Tests (35 passing):**
```bash
cd services/eligibility
python3 -m venv .venv && .venv/bin/pip install pytest pydantic
.venv/bin/python -m pytest tests/ -v
```

---

### 3. AI Assistant — `services/assistant/` (FastAPI + Groq)

Takes a match result and explains it to the user in plain language.

**API:**
```
POST /api/v1/assistant/explain
Body: {
  "scheme_id": 1,
  "scheme_name": "...",
  "outcome": "appears_non_eligible",
  "conditions": [ { "field": "caste_category", "result": "fail", "explanation": "..." } ],
  "profile": { "caste_category": "OBC", ... }
}
Response: { "scheme_id": 1, "explanation": "You are not eligible because..." }
```

**How it works:**
1. Fetches the scheme description from Catalog
2. Builds a prompt with the scheme, the per-condition results, and the user profile
3. Calls the Groq API (`api.groq.com/openai/v1/chat/completions`) via `httpx`
4. Returns 2–3 plain-language sentences

**Configuration:**
```
GROQ_API_KEY=gsk_...                  # required — free Groq API key
GROQ_MODEL=openai/gpt-oss-20b         # optional override (default: llama-3.1-8b-instant)
```

**Get a free Groq key:** console.groq.com → API Keys → Create API Key (no credit card)

**Why Groq instead of HuggingFace Inference API:**
`api-inference.huggingface.co` is blocked on some corporate/institutional networks. Groq's `api.groq.com` is not. The integration uses `httpx` directly — no extra SDK dependency.

---

### 4. Feedback — `services/feedback/` (FastAPI + SQLAlchemy)

Lets users report incorrect or outdated scheme information.

**API:**
```
POST   /api/v1/feedback              submit feedback
GET    /api/v1/feedback              list all feedback
GET    /api/v1/feedback/{id}         get one entry
PATCH  /api/v1/feedback/{id}/resolve mark resolved
```

---

### 5. Frontend — `frontend/` (React + Vite)

**Pages:**
```
/          Home — hero, "how it works", transparency note
/schemes   Browse all published schemes (SchemeCard grid)
/check     Eligibility check — ProfileForm + MatchResults side by side
```

**Components:**
```
SchemeCard.jsx      scheme card with official link button
ProfileForm.jsx     7-field form (all optional)
MatchResults.jsx    ordered results (eligible first), summary badges
ConditionRow.jsx    one rule per row — pass/fail/unknown with colour
FeedbackForm.jsx    modal report form
```

**API calls** (`src/api/client.js`):
```
fetchSchemes()           GET  /api/v1/schemes/
checkEligibility(p)      POST /api/v1/matches
submitFeedback(d)        POST /api/v1/feedback
explainResult(d)         POST /api/v1/assistant/explain
```

**Local dev:** `npm run dev` — Vite proxies `/api` to `http://localhost:80` (Nginx)
**Docker:** multi-stage build — Node builds to `dist/`, Nginx serves static files

---

### 6. Infrastructure — `infra/` and `gateway/`

**compose.yaml services:**
```
db          postgres:16 — single server, 3 databases (catalog_db, feedback_db, ai_db)
catalog     Django — port 8001
eligibility FastAPI — port 8002
assistant   FastAPI — port 8003
feedback    FastAPI — port 8004
frontend    Nginx static — port 80 (internal)
gateway     Nginx reverse proxy — port 80 (public)
```

**init_db.sql** creates `feedback_db` and `ai_db` on first PostgreSQL startup (`catalog_db` is created by the POSTGRES_DB env var).

**Nginx routing:**
```
/api/v1/schemes    → catalog:8001
/api/v1/matches    → eligibility:8002
/api/v1/assistant  → assistant:8003
/api/v1/feedback   → feedback:8004
/admin/            → catalog:8001
/static/           → catalog:8001
/                  → frontend:80
```

---

## Environment Variables

All secrets live in `.env` (never committed). `.env.example` is the template.

| Variable | Used by | Notes |
|---|---|---|
| `CATALOG_SECRET_KEY` | catalog | Django secret key |
| `CATALOG_DEBUG` | catalog | `true` locally, `false` in production |
| `CATALOG_DATABASE_URL` | catalog | PostgreSQL connection string |
| `FEEDBACK_DATABASE_URL` | feedback | PostgreSQL connection string |
| `POSTGRES_USER` | db | Database username |
| `POSTGRES_PASSWORD` | db | Database password |
| `POSTGRES_DB` | db | Primary database name |
| `CATALOG_SERVICE_URL` | eligibility, assistant | `http://catalog:8001` |
| `ELIGIBILITY_SERVICE_URL` | (future) | `http://eligibility:8002` |
| `GROQ_API_KEY` | assistant | Free Groq API key — console.groq.com |
| `GROQ_MODEL` | assistant | Optional model override (default: `llama-3.1-8b-instant`) |

Generate secrets:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"  # CATALOG_SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"  # POSTGRES_PASSWORD
```

---

## Sample Data

`services/catalog/fixtures/sample_schemes.json` — 3 real Indian government schemes, auto-loaded on every container startup.

| Scheme | Ministry | Official URL |
|---|---|---|
| PM Scholarship for CAPF | Ministry of Home Affairs | mha.gov.in/en/MHA-Scholarships |
| Post Matric Scholarship for SC | Ministry of Social Justice | socialjustice.gov.in |
| Central Sector Scholarship | Ministry of Education | education.gov.in |

Each scheme has: eligibility rules with operator + value + explanation, source documents and passages (official quotes), required documents, and published status.

**To add more schemes:** see [data-maintenance.md](data-maintenance.md).

---

## Running Locally (Full Setup)

```bash
# 1. Start Docker Desktop

# 2. Clone and configure
git clone https://github.com/ShuvechhaNandi/SchemeGuide.git
cd SchemeGuide
cp .env.example .env
# edit .env — fill in generated secrets

# 3. Start everything
docker compose -f infra/compose.yaml --env-file .env up --build

# 4. Create admin user (in a new terminal)
docker compose -f infra/compose.yaml --env-file .env exec catalog \
  python manage.py createsuperuser

# 5. Open http://localhost
```

**Wipe and reset:**
```bash
docker compose -f infra/compose.yaml --env-file .env down -v
docker compose -f infra/compose.yaml --env-file .env up --build
# re-run createsuperuser
```

**Run eligibility tests:**
```bash
cd services/eligibility
python3 -m venv .venv && .venv/bin/pip install pytest pydantic
.venv/bin/python -m pytest tests/ -v
```

---

## Known Issues and Gotchas

| Issue | Cause | Fix |
|---|---|---|
| `--env-file .env` required (or use `make`) | compose.yaml is in `infra/`, not root — Docker reads `.env` relative to the compose file location | use `make up` from repo root, or pass `--env-file .env` explicitly |
| `db`, `eligibility`, `assistant` use `env_file` in compose; `catalog` and `feedback` still use `environment:` substitution | `catalog` maps `CATALOG_DATABASE_URL` → `DATABASE_URL` and `feedback` maps `FEEDBACK_DATABASE_URL` → `DATABASE_URL` — `env_file` can't rename vars | `make` / `--env-file .env` handles these; a future fix is to rename vars in `.env` to match what each service reads |
| Healthcheck `role "-d" does not exist` | `${POSTGRES_USER}` in healthcheck was empty at parse time | use `$$POSTGRES_USER` (double dollar = evaluated at runtime inside container) |
| Admin page has no CSS | gunicorn doesn't serve static files | WhiteNoise middleware added — must rebuild after any catalog change |
| `api-inference.huggingface.co` DNS blocked on some networks | corporate/institutional networks block this HuggingFace subdomain | switched assistant to Groq (`api.groq.com`), which is not blocked |
| Port 5432 conflict | Local PostgreSQL occupies the port | db exposed on `5433:5432` in compose.yaml |
| `npm ci` fails in Docker | No `package-lock.json` in the repo | Dockerfile uses `npm install` |

---

## What Still Needs to Be Done

### High priority
- **GitHub Actions CI** — pytest on every PR for eligibility and catalog; Docker Compose smoke test
- **API tests** — `GET /api/v1/schemes/` returns only published; `POST /api/v1/matches` with known fixture data returns expected outcomes
- **npm lock file** — run `npm install` locally once, commit `package-lock.json`, switch Dockerfile back to `npm ci`

### Medium priority
- **More sample schemes** — 5–10 schemes is a better demo; contributors can open data PRs
- **Scheme search/filter** — filter Browse page by state, caste category, education level
- **Assistant: source citations** — the explanation currently has no citations; link each sentence to the source passage it draws from

### Lower priority
- **Production hosting** — Oracle Always Free or Fly.io; needs HTTPS, non-debug mode, production secret key
- **Catalog API tests** — test that draft schemes do not appear in `/api/v1/schemes/`
- **Feedback admin view** — reviewers should be able to see and resolve feedback from Django Admin, not just the API

---

## Tech Stack

| Component | Technology | Version |
|---|---|---|
| Catalog | Django + DRF | 5.1.4 / 3.15.2 |
| Eligibility | FastAPI + Pydantic | 0.115.5 / 2.10.2 |
| AI Assistant | FastAPI + httpx (Groq) | 0.115.5 / 0.28.0 |
| Feedback | FastAPI + SQLAlchemy | 0.115.5 |
| Frontend | React + Vite + React Bootstrap | 18 / 6 / 2 |
| Database | PostgreSQL | 16 |
| Static files | WhiteNoise | 6.8.2 |
| Gateway | Nginx | alpine |
| Orchestration | Docker Compose | v2 |
| Python | 3.13 | |
| Node | 24 | |
