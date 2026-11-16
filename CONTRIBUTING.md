# Contributing to SchemeGuide

## Getting Started

1. Fork the repository and clone it locally.
2. Create a branch from `main`: `git checkout -b feature/your-feature-name`
3. Make your changes, add tests, and commit.
4. Open a Pull Request linked to the relevant GitHub Issue.
5. Request a review from another team member.

## Branch Naming

| Type | Format | Example |
|---|---|---|
| New feature | `feature/short-description` | `feature/eligibility-engine` |
| Bug fix | `fix/short-description` | `fix/rule-evaluation-boundary` |
| Documentation | `docs/short-description` | `docs/architecture-diagram` |
| Data correction | `data/scheme-name` | `data/pm-scholarship-update` |

## Commit Style

Use short, imperative commit messages:
- `feat: add eligibility rule evaluation`
- `fix: handle missing income field in profile`
- `docs: update architecture diagram`
- `test: add boundary value tests for engine`
- `data: add NSP scholarship scheme`

## Pull Request Checklist

- [ ] Linked to a GitHub Issue
- [ ] Tests added or updated
- [ ] Documentation updated if needed
- [ ] For scheme data changes: official source URL included in the PR description
- [ ] No secrets or API keys committed

## Adding Scheme Data

Scheme data must come from official government sources only.
For each scheme, record the official URL, the retrieval date, and the applicable year.
A second team member must review scheme data before it is published.
See `docs/data-maintenance.md` for the full data workflow.

## Running Locally

```bash
cp .env.example .env
# Fill in your AI_API_KEY in .env
docker compose -f infra/compose.yaml up --build
```

## Running Tests

```bash
# Catalog
docker compose exec catalog python manage.py test

# Eligibility
docker compose exec eligibility pytest

# Assistant
docker compose exec assistant pytest
```

## License

By contributing, you agree that your contributions will be licensed under the Apache-2.0 License.
