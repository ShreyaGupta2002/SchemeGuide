# SchemeGuide — Project Progress & Handoff Document

## What is SchemeGuide?

A microservices web application that helps students and citizens discover government scholarships and schemes, check their eligibility, and understand the results.

---

## Architecture Overview

```
[React Frontend :3000]
        |
   [Nginx Gateway :80]  ← single public entry point
        |
   ┌────┬────┬────┐
   │    │    │    │
Catalog  Eligibility  Feedback
(Django) (FastAPI)   (FastAPI)
 :8001    :8002       :8004
   │                    │
Postgres             Postgres
catalog_db           feedback_db
```

---

## What Has Been Built

### 1. Catalog Service — `services/catalog/` (Django + DRF)
**Status: Complete and working**

Owns all scheme data. Has a Django Admin UI for adding/managing schemes.

**Files:**
- `manage.py` — Django entry point
- `catalog_service/settings.py` — DB config (SQLite locally, PostgreSQL in Docker)
- `catalog_service/urls.py` — Root URL routing
- `catalog_service/wsgi.py` — WSGI entry point
- `schemes/models.py` — 7 database models
- `schemes/admin.py` — Admin UI with publish/review actions
- `schemes/serializers.py` — JSON response format
- `schemes/views.py` — API logic
- `schemes/urls.py` — URL routes
- `schemes/migrations/` — Database migration files
- `requirements.txt` — Python dependencies
- `Dockerfile` — Container config

**Database Models:**
```
Scheme              → name, department, jurisdiction, state
SchemeVersion       → description, benefit_amount, applicable_year,
                      application_open/close, official_url, status (draft/reviewed/published)
EligibilityRule     → field, operator, value, explanation
SourceDocument      → title, official_url, retrieval_date
SourcePassage       → text, section_reference
RequiredDocument    → name, when_required
ReviewRecord        → reviewer, decision, comments
```

**API Endpoints:**
```
GET  /api/v1/schemes/        → list all published schemes
GET  /api/v1/schemes/{id}/   → scheme detail with rules and sources
```

**How to run locally (without Docker):**
```bash
cd services/catalog
pip install -r requirements.txt
python manage.py migrate
python manage.py makemigrations schemes
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8001
```
Admin: `http://localhost:8001/admin/`
API: `http://localhost:8001/api/v1/schemes/`

---

### 2. Eligibility Service — `services/eligibility/` (FastAPI)
**Status: Complete and working**

Stateless service — fetches rules from Catalog, evaluates them against user profile, returns outcome.

**Files:**
- `main.py` — FastAPI app entry point
- `app/models.py` — Pydantic schemas (ProfileInput, MatchRequest, MatchResponse)
- `app/catalog_client.py` — HTTP client to fetch rules from Catalog service
- `app/engine.py` — Core eligibility logic (evaluate rules)
- `app/router.py` — POST /api/v1/matches endpoint
- `requirements.txt` — Python dependencies
- `Dockerfile` — Container config

**API Endpoint:**
```
POST /api/v1/matches
Body: {
  "profile": {
    "state": "UP",
    "annual_income": 150000,
    "education_level": "graduation",
    "caste_category": "SC",
    "gender": "female",
    "age": 20,
    "parent_service": "CAPF"
  }
}
Response: {
  "results": [
    {
      "scheme_id": 1,
      "scheme_name": "PM Scholarship...",
      "scheme_version_id": 1,
      "outcome": "appears_eligible",  // or "appears_ineligible" or "more_information_needed"
      "conditions": [...]
    }
  ]
}
```

**Engine logic (engine.py):**
- Supported operators: `equals`, `not_equals`, `in`, `not_in`, `gte`, `lte`, `gt`, `lt`
- Rule result: `pass`, `fail`, or `unknown` (if field not provided)
- Scheme outcome: if any rule fails → `appears_ineligible`, if any unknown → `more_information_needed`, all pass → `appears_eligible`

**How to run locally:**
```bash
cd services/eligibility
pip install -r requirements.txt
uvicorn main:app --reload --port 8002
```
Docs: `http://localhost:8002/docs`
Note: Catalog service must also be running.

---

### 3. Feedback Service — `services/feedback/` (FastAPI + SQLAlchemy)
**Status: Complete and working**

Lets users report incorrect scheme information. Stores feedback in PostgreSQL.

**Files:**
- `main.py` — FastAPI app entry point
- `app/database.py` — SQLAlchemy DB connection (SQLite locally, PostgreSQL in Docker)
- `app/models.py` — FeedbackRecord SQLAlchemy model + Pydantic schemas
- `app/router.py` — CRUD endpoints
- `requirements.txt` — Python dependencies
- `Dockerfile` — Container config

**API Endpoints:**
```
POST   /api/v1/feedback              → submit feedback
GET    /api/v1/feedback              → list all feedback
GET    /api/v1/feedback/{id}         → get one feedback
PATCH  /api/v1/feedback/{id}/resolve → mark as resolved
```

**How to run locally:**
```bash
cd services/feedback
pip install -r requirements.txt
uvicorn main:app --reload --port 8004
```
Docs: `http://localhost:8004/docs`

---

### 4. Docker Compose + Nginx Gateway — `infra/` and `gateway/`
**Status: Complete and working**

Runs all services together in containers with a single command.

**Files:**
- `infra/compose.yaml` — Docker Compose config
- `infra/init_db.sql` — Creates ai_db and feedback_db on first PostgreSQL start
- `gateway/nginx.conf` — Nginx routing rules
- `gateway/Dockerfile` — Nginx container

**How to run everything together:**
```bash
cd infra
docker compose up --build
```

**URL routing through Nginx:**
```
localhost/api/v1/schemes/*   → catalog:8001
localhost/api/v1/matches     → eligibility:8002
localhost/api/v1/feedback    → feedback:8004
localhost/admin/             → catalog:8001
localhost/static/            → catalog:8001
```

**Create superuser in Docker:**
```bash
cd infra
docker compose exec catalog python manage.py createsuperuser
```

---

### 5. React Frontend — `frontend/`
**Status: Partially complete — UI built, needs testing with live data**

**Files built:**
- `src/api/client.js` — API calls (fetchSchemes, checkEligibility, submitFeedback)
- `src/components/SchemeCard.jsx` — Scheme card for Browse page
- `src/components/ProfileForm.jsx` — User profile input form
- `src/components/MatchResults.jsx` — Eligibility results display
- `src/components/ConditionRow.jsx` — One row per eligibility rule result
- `src/components/FeedbackForm.jsx` — Report incorrect info form
- `src/pages/HomePage.jsx` — Landing page
- `src/pages/SchemesPage.jsx` — Browse all schemes
- `src/pages/MatchPage.jsx` — Check eligibility page
- `src/App.js` — Router + Navbar

**How to run:**
```bash
cd frontend
npm install
npm start
```
Opens at `http://localhost:3000`

**Pages:**
```
/          → Home page with hero section
/schemes   → Browse all published schemes
/check     → Check eligibility form
```

**Proxy config** (`package.json`):
```json
"proxy": "http://localhost:80"
```
This routes all `/api/*` calls through Nginx gateway.

---

## What is NOT Done Yet

```
❌ AI Assistant Service     → services/assistant/ (folder exists, no code)
❌ Tests                    → pytest for each service
❌ GitHub Actions CI        → .github/workflows/ (folders exist, no yml files)
❌ Docs                     → docs/ folder exists but empty
❌ Sample data fixture      → need to add schemes via admin or fixture file
```

---

## What Still Needs to Be Done

### Next Priority: AI Assistant Service — `services/assistant/`

This service:
1. Fetches source passages from Catalog
2. Calls Eligibility service for the evaluation result
3. Sends question + evidence to LLM (Claude/OpenAI)
4. Returns plain-language explanation + cited source passage IDs

**Files to create:**
```
services/assistant/
├── Dockerfile
├── requirements.txt          ← fastapi, uvicorn, httpx, anthropic or openai
├── main.py
└── app/
    ├── catalog_client.py     ← fetch source passages
    ├── eligibility_client.py ← fetch evaluation result
    ├── retrieval.py          ← search passages for a question
    ├── llm_adapter.py        ← call LLM, validate citations
    └── router.py             ← POST /api/v1/schemes/{id}/questions
```

**Needs:** An API key — either `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` in `.env`

### Then: Tests

```
services/catalog/tests/test_api.py        → GET /schemes returns only published
services/eligibility/tests/test_engine.py → boundary value tests for rules
services/feedback/tests/test_api.py       → submit and list feedback
```

### Then: GitHub Actions CI

```
.github/workflows/catalog.yml      → pytest on every PR
.github/workflows/eligibility.yml  → pytest on every PR
.github/workflows/integration.yml  → docker compose smoke test
```

### Then: Docs

```
docs/proposal.md         → problem statement, team, scope
docs/architecture.md     → architecture diagram, service responsibilities
docs/related-work.md     → comparison with existing tools
docs/data-maintenance.md → how to add a new scheme
docs/evaluation.md       → test dataset, results
```

---

## Repository Structure

```
SchemeGuide/
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── .env.example
├── .gitignore
├── services/
│   ├── catalog/          ✅ complete
│   ├── eligibility/      ✅ complete
│   ├── feedback/         ✅ complete
│   └── assistant/        ❌ not started
├── frontend/             ⚠️  UI built, needs testing
├── gateway/              ✅ complete
├── infra/                ✅ complete
├── docs/                 ❌ empty
├── contracts/openapi/    ❌ empty
└── .github/workflows/    ❌ empty
```

---

## GitHub Repository

```
https://github.com/ShuvechhaNandi/SchemeGuide
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Catalog | Django 5.1 + Django REST Framework |
| Eligibility | FastAPI + Pydantic |
| Feedback | FastAPI + SQLAlchemy |
| AI Assistant | FastAPI + anthropic/openai SDK (not built yet) |
| Frontend | React + React Bootstrap + React Router |
| Database | PostgreSQL (Docker) / SQLite (local dev) |
| Gateway | Nginx |
| Orchestration | Docker Compose |
| Python version | 3.13 |
| Node version | 24 |

---

## Important Notes for Handoff

1. **Database is fresh on every `docker compose down -v`** — schemes need to be re-added via admin
2. **Locally vs Docker** — local runs use SQLite, Docker uses PostgreSQL
3. **Admin credentials** — created via `docker compose exec catalog python manage.py createsuperuser`
4. **Frontend proxy** — `package.json` has `"proxy": "http://localhost:80"` so API calls go through Nginx
5. **Git config** — set `git config commit.gpgsign false` to avoid SAP GPG key popup
6. **Port map:**
   - `localhost:3000` → React dev server
   - `localhost:80` → Nginx (all API calls)
   - `localhost:8001` → Catalog (direct, local only)
   - `localhost:8002` → Eligibility (direct, local only)
   - `localhost:8004` → Feedback (direct, local only)
   - `localhost:5432` → PostgreSQL (direct, local only)
