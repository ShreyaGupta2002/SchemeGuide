# Contributing to SchemeGuide

SchemeGuide is an open-source project. There are three ways to contribute — choose the one that fits you.

| Type | What you do | Skills needed |
|---|---|---|
| **Code contributor** | Fix bugs, build features | Python, React, Docker |
| **Data contributor** | Add or correct scheme data | No code — just a browser and official government sources |
| **Maintainer** | Review PRs, publish schemes | Both of the above |

---

## Table of Contents

- [Local Setup (everyone)](#local-setup-everyone)
- [Code Contributors](#code-contributors)
- [Data Contributors](#data-contributors)
- [Maintainers](#maintainers)
- [Branch Naming](#branch-naming)
- [Commit Style](#commit-style)
- [Running Tests](#running-tests)

---

## Local Setup (everyone)

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) — running (whale icon in menu bar)
- Git

### Steps

```bash
# 1. Fork this repo on GitHub, then clone your fork
git clone https://github.com/<your-username>/SchemeGuide.git
cd SchemeGuide

# 2. Create your .env
cp .env.example .env
```

Open `.env` and fill in the generated secrets:

```bash
# Run each command and paste the output into .env
python3 -c "import secrets; print(secrets.token_urlsafe(50))"  # → CATALOG_SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"  # → POSTGRES_PASSWORD
```

Use the same `POSTGRES_PASSWORD` value in all three `DATABASE_URL` lines.

```bash
# 3. Start everything
docker compose -f infra/compose.yaml --env-file .env up --build
```

Wait until you see `Installed X object(s) from 1 fixture(s)` in the logs — that means sample data loaded.

Open `http://localhost` in your browser.

```bash
# 4. Create a Django admin user (required to publish schemes)
docker compose -f infra/compose.yaml --env-file .env exec catalog \
  python manage.py createsuperuser
```

Log in at `http://localhost/admin`.

---

## Code Contributors

### Workflow

```
1. Open or find an issue on GitHub
2. Comment "I'll take this" so others know it's claimed
3. Create a branch from main (see Branch Naming below)
4. Make your changes locally
5. Run tests (see Running Tests below)
6. Push and open a Pull Request
7. CI runs automatically — fix anything that fails
8. A maintainer reviews and merges
9. Vercel and Render auto-deploy within ~5 minutes
```

### Opening a Pull Request

Use the PR template. Fill in every checkbox before requesting review.

**A PR is ready for review when:**
- All CI checks are green
- You have tested it locally in the browser (for frontend changes)
- No secrets or `.env` values are in the diff

### What CI checks on every PR

- `pytest` — eligibility engine tests (35 tests)
- `ruff` — Python lint for all services
- Fixture JSON validation — `sample_schemes.json` must be valid JSON
- Docker build smoke test — each service builds without error

All four must pass before a maintainer will review.

### Services and what they own

| Service | Location | What to know |
|---|---|---|
| Catalog | `services/catalog/` | Django — scheme data, Django Admin, REST API |
| Eligibility | `services/eligibility/` | FastAPI — pure rule evaluation, no DB |
| AI Assistant | `services/assistant/` | FastAPI — calls Groq API, needs `GROQ_API_KEY` in `.env` |
| Feedback | `services/feedback/` | FastAPI + SQLAlchemy — user corrections |
| Frontend | `frontend/` | React + Vite — calls `/api/v1/*` (proxied by Vite in dev) |
| Gateway | `gateway/` | Nginx — routes traffic in Docker, replaced by Vercel rewrites in production |

### Adding or changing an API endpoint

1. Update the service code
2. Update `gateway/nginx.conf` if the path is new
3. Update `frontend/src/api/client.js` if the frontend needs to call it
4. Add or update tests

---

## Data Contributors

Data contributions do not require writing code. You use the Django Admin to add scheme data, then export it as a JSON fixture and open a PR.

### Rules

- **Official sources only** — `scholarships.gov.in`, ministry websites (`mha.gov.in`, `socialjustice.gov.in`, `education.gov.in`, etc.). Never use news articles or unofficial guides.
- **Every eligibility rule must cite a source passage** — an exact quote from the official document.
- **Income values must be in rupees as a plain number** — `250000`, not `2.5 lakh`.
- **Status must be `draft`** when you submit the PR. Maintainers publish to production.

### Workflow

```bash
# 1. Create a branch
git checkout -b data/scheme-name

# 2. Start the app
docker compose -f infra/compose.yaml --env-file .env up --build

# 3. Create a superuser if you haven't already
docker compose -f infra/compose.yaml --env-file .env exec catalog \
  python manage.py createsuperuser
```

**Step-by-step in Django Admin (`http://localhost/admin`):**

**Add a Scheme:**
- Name: full official name
- Department: the ministry running it
- Jurisdiction: `central` or `state`
- State: leave blank for central schemes

**Add a Scheme Version:**
- Scheme: the scheme you just created
- Version number: `1` (increment when rules change, never edit existing versions)
- Status: `draft` — always
- Official URL: direct link to the scheme's page on the official portal
- Fill in description, benefit amount, applicable year

**Add a Source Document** (inside the Scheme Version):
- Title: name of the PDF or page you read
- Official URL: direct link to that document
- Retrieval date: today's date

**Add Source Passages** (inside the Source Document):
- Text: exact quote from the document that justifies an eligibility rule
- Section reference: the heading it comes from (e.g. `Para 3 — Eligibility`)

**Add Eligibility Rules** (inside the Scheme Version):
- Field: one of `state`, `annual_income`, `education_level`, `caste_category`, `gender`, `age`, `parent_service`
- Operator: `equals`, `not_equals`, `in`, `not_in`, `gte`, `lte`, `gt`, `lt`
- Value: what the applicant's value must be
- Explanation: plain English reason
- Source passage: the passage you added above — **required**

**Add Required Documents** (inside the Scheme Version):
- Name: exact document name
- When required: leave blank if always required

**Export and submit:**

```bash
# Export the fixture
docker compose -f infra/compose.yaml --env-file .env exec catalog \
  python manage.py dumpdata schemes --indent 2 \
  > services/catalog/fixtures/sample_schemes.json

# Commit and push
git add services/catalog/fixtures/sample_schemes.json
git commit -m "data: add <scheme-name>"
git push origin data/scheme-name
```

Open a PR. Fill in the **Data PR Checklist** in the PR template completely.

### What reviewers check

- Every eligibility rule has a source passage
- Source URL is accessible and from an official government domain
- Rule accurately reflects what the passage says — no interpretation beyond what is written
- Income values are plain rupee numbers
- Status in the fixture is `draft`
- Retrieval date is recorded

---

## Maintainers

Maintainers review PRs and publish approved scheme data to production.

### Reviewing a Code PR

1. Check CI is green
2. Pull the branch locally and test it in the browser for any frontend/API changes
3. Approve and merge — Vercel and Render deploy automatically

### Reviewing a Data PR

1. Verify every item in the Data PR Checklist
2. Open the official source URL — confirm the passages are real and accurate
3. Confirm income values are in rupees (not lakhs)
4. Confirm status is `draft` in the fixture JSON
5. Approve and merge

### Publishing schemes in production

After a data PR merges, the scheme is in the fixture (available to all contributors locally) but **not published on the live app** — it's still `draft` in production.

To publish:

1. Log in to Django Admin on Render (the production URL)
2. Find the scheme version
3. Change status from `draft` to `published`
4. Save

This is intentional — a second person always verifies before anything reaches real users.

### Responding to feedback reports

Users can report incorrect scheme information via the app. To review reports:

```bash
# See all open feedback
curl https://<your-catalog-service>.onrender.com/api/v1/feedback

# Mark one as resolved after fixing
curl -X PATCH https://<your-catalog-service>.onrender.com/api/v1/feedback/<id>/resolve
```

---

## Branch Naming

| Type | Format | Example |
|---|---|---|
| New feature | `feat/short-description` | `feat/filter-by-state` |
| Bug fix | `fix/short-description` | `fix/income-comparison-boundary` |
| Documentation | `docs/short-description` | `docs/update-architecture` |
| New scheme data | `data/scheme-name` | `data/post-matric-obc` |
| Data correction | `data/scheme-name-update` | `data/central-sector-income-fix` |

---

## Commit Style

```
feat: add state filter to browse page
fix: handle missing income field in profile
docs: add deployment guide
test: add boundary tests for gte operator
data: add NSP merit-cum-means scholarship
chore: update dependencies
```

---

## Running Tests

### Eligibility engine (fastest — pure Python, no Docker needed)

```bash
cd services/eligibility
python3 -m venv .venv
.venv/bin/pip install pytest pydantic
.venv/bin/python -m pytest tests/ -v
```

### Catalog API (Django — uses SQLite in test mode)

```bash
cd services/catalog
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py test schemes.tests -v 2
```

### Feedback API (FastAPI — uses in-memory SQLite)

```bash
cd services/feedback
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt pytest httpx
.venv/bin/python -m pytest tests/ -v
```

### All tests via Docker (matches CI exactly)

```bash
# Eligibility
docker compose -f infra/compose.yaml --env-file .env exec eligibility \
  python -m pytest tests/ -v

# Catalog
docker compose -f infra/compose.yaml --env-file .env exec catalog \
  python manage.py test schemes.tests

# Feedback
docker compose -f infra/compose.yaml --env-file .env exec feedback \
  python -m pytest tests/ -v
```

---

## License

By contributing, you agree that your contributions will be licensed under the Apache-2.0 License.
