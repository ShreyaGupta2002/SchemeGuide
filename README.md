# SchemeGuide

An open-source web application that helps students and citizens discover government scholarships and schemes, check eligibility against official published rules, and get plain-language explanations backed by official source citations.

## Problem

Students struggle to find relevant government scholarships and interpret eligibility conditions spread across multiple official sources. Important schemes are missed because the information is dense, scattered, and hard to understand.

## Solution

SchemeGuide lets a user enter basic profile details (state, education level, income range), then:
- Checks eligibility against structured, reviewed rules from official sources
- Shows which conditions pass, fail, or need more information
- Explains results in plain language using AI — with every claim linked to an official source passage
- Provides document checklists and official application links

## Key Features

- Profile-based scheme matching with transparent condition-level results
- Rule-based eligibility engine (deterministic — no AI decides eligibility)
- AI-assisted plain-language explanations with source citations
- Source-backed Q&A about any scheme
- Django Admin for contributor and reviewer data workflow
- Feedback system for reporting outdated information

## Architecture

Microservices: React frontend → Nginx gateway → 4 Python backend services → PostgreSQL

| Service | Technology | Responsibility |
|---|---|---|
| Catalog | Django + DRF | Scheme data, rules, sources, review workflow |
| Eligibility | FastAPI | Deterministic rule evaluation |
| AI Assistant | FastAPI | Retrieval-augmented explanations and Q&A |
| Feedback | FastAPI | User-submitted corrections |

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Git

### Run Locally

```bash
git clone https://github.com/ShuvechhaNandi/SchemeGuide.git
cd SchemeGuide
cp .env.example .env
# Add your AI_API_KEY to .env
docker compose -f infra/compose.yaml up --build
```

Open `http://localhost` in your browser.
Django Admin is at `http://localhost/admin`.

## Project Structure

```
schemeguide/
├── services/
│   ├── catalog/       Django REST Framework + Admin
│   ├── eligibility/   FastAPI — rule evaluation
│   ├── assistant/     FastAPI — AI explanations
│   └── feedback/      FastAPI — user corrections
├── frontend/          React
├── gateway/           Nginx
├── infra/             Docker Compose
├── contracts/openapi/ API specifications
└── docs/              Architecture, proposal, evaluation
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to contribute code or scheme data.

## License

Apache-2.0 — see [LICENSE](LICENSE).
