# Data Maintenance Guide

This guide explains how to add a new scheme or correct existing scheme data.

---

## Where Scheme Data Comes From

All scheme data must come from official government sources only:

- [scholarships.gov.in](https://scholarships.gov.in) — National Scholarship Portal
- Ministry websites (mha.gov.in, socialjustice.gov.in, education.gov.in, etc.)
- State government portals for state-level schemes

Never copy from news articles, unofficial guides, or third-party aggregators. If you cannot find an official source URL, do not add the scheme.

---

## Adding a New Scheme Locally

### Step 1 — Set up

```bash
git checkout -b data/scheme-name
docker compose -f infra/compose.yaml up --build
docker compose -f infra/compose.yaml exec catalog python manage.py createsuperuser
```

Open `http://localhost/admin/`

---

### Step 2 — Add a Scheme

Go to **Schemes → Add Scheme**

| Field | What to enter |
|---|---|
| Name | Full official name of the scheme |
| Department | Ministry or department that runs it |
| Jurisdiction | `central` for central govt, `state` for state govt |
| State | Leave blank for central schemes, fill for state schemes |

---

### Step 3 — Add a Scheme Version

Go to **Scheme Versions → Add Scheme Version**

| Field | What to enter |
|---|---|
| Scheme | Pick the scheme you just created |
| Version number | Start at 1, increment when rules change |
| Description | 2–3 sentences: who it's for, what it provides |
| Benefit amount | Exact amount from the official document |
| Applicable year | e.g. `2024-25` |
| Application open/close | From the official notification, or leave blank if unknown |
| Official URL | Direct link to the scheme page on the official portal |
| Status | Leave as `draft` — do not publish locally |

---

### Step 4 — Add Source Documents and Passages

Inside the Scheme Version, go to **Source Documents → Add**

| Field | What to enter |
|---|---|
| Title | Name of the PDF or page you read |
| Official URL | Direct URL to that document |
| Retrieval date | Today's date |

Then add **Source Passages** for that document. A passage is an exact quote from the document that justifies an eligibility rule.

- Copy the exact sentence from the official document
- Note the section heading it comes from (e.g. "Para 3 — Eligibility")

---

### Step 5 — Add Eligibility Rules

Each rule is one condition the applicant must meet. Add rules inside the Scheme Version.

| Field | What to enter |
|---|---|
| Field | One of the profile fields listed below |
| Operator | How to compare the value |
| Value | What the applicant's value must be |
| Explanation | Plain language: why this rule exists |
| Source passage | The passage you added in Step 4 that justifies this rule |

**Linking every rule to a source passage is required.** If you cannot find an official passage for a rule, do not add the rule.

#### Profile Fields

| Field name | Meaning | Example values |
|---|---|---|
| `state` | Applicant's state | `Maharashtra`, `UP`, `Bihar` |
| `annual_income` | Family income in rupees (number) | `150000`, `450000` |
| `education_level` | Current level of study | `graduation`, `postgraduation`, `diploma`, `class12` |
| `caste_category` | Caste certificate category | `SC`, `ST`, `OBC`, `general` |
| `gender` | Gender | `male`, `female` |
| `age` | Age in years (number) | `20`, `25` |
| `parent_service` | Parent's service (for CAPF schemes) | `CAPF` |

#### Operators

| Operator | Means | Example |
|---|---|---|
| `equals` | Exact match (case-insensitive) | `caste_category equals SC` |
| `not_equals` | Must not equal | `gender not_equals male` |
| `in` | Must be one of a comma-separated list | `education_level in graduation,postgraduation` |
| `not_in` | Must not be in list | `state not_in Jammu and Kashmir,Ladakh` |
| `lte` | Less than or equal (numbers only) | `annual_income lte 450000` |
| `gte` | Greater than or equal (numbers only) | `age gte 18` |
| `lt` | Less than (numbers only) | `age lt 30` |
| `gt` | Greater than (numbers only) | `annual_income gt 0` |

---

### Step 6 — Add Required Documents

Inside the Scheme Version, add each document an applicant needs:

| Field | What to enter |
|---|---|
| Name | Exact name of the document |
| When required | Leave blank if always required, otherwise note conditions |

---

### Step 7 — Export and Submit

Export the fixture:

```bash
docker compose -f infra/compose.yaml exec catalog \
  python manage.py dumpdata schemes --indent 2 \
  > services/catalog/fixtures/sample_schemes.json
```

Commit and open a PR:

```bash
git add services/catalog/fixtures/sample_schemes.json
git commit -m "data: add <scheme-name>"
git push origin data/scheme-name
```

In the PR description, include:
- Official source URL
- Date you retrieved it
- Which rules map to which source passages

---

## Correcting Existing Scheme Data

If you find that a rule is wrong or outdated:

1. Check the current official source first — confirm what changed
2. Update the scheme via local admin
3. If the rules changed, increment the version number (create a new SchemeVersion, do not edit the old one)
4. Export the fixture and open a PR with the new official source URL as proof

---

## What Reviewers Check

Before approving a data PR, reviewers verify:

- Every eligibility rule has a source passage linked to it
- The source passage URL is accessible and from an official domain
- The rule accurately reflects what the passage says — no interpretation beyond what is written
- Income values are in rupees (not lakhs — `450000` not `4.5`)
- Scheme status in the fixture is `draft`, not `published`
- Retrieval date is recorded

---

## Who Publishes Schemes in Production

Contributors submit as `draft`. The core team reviews and publishes on the production server via Django Admin. This ensures a second person verifies every scheme before it reaches real users.
