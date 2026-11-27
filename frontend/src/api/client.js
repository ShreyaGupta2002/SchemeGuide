const CATALOG_BASE = import.meta.env.VITE_CATALOG_URL || '/api/v1'
const ELIGIBILITY_BASE = import.meta.env.VITE_ELIGIBILITY_URL || '/api/v1'
const FEEDBACK_BASE = import.meta.env.VITE_FEEDBACK_URL || '/api/v1'
const ASSISTANT_BASE = import.meta.env.VITE_ASSISTANT_URL || '/api/v1'

export async function fetchSchemes() {
  const res = await fetch(`${CATALOG_BASE}/schemes/`)
  if (!res.ok) throw new Error('Failed to fetch schemes')
  return res.json()
}

export async function checkEligibility(profile) {
  const res = await fetch(`${ELIGIBILITY_BASE}/matches`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ profile }),
  })
  if (!res.ok) throw new Error('Failed to check eligibility')
  return res.json()
}

export async function submitFeedback(data) {
  const res = await fetch(`${FEEDBACK_BASE}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error('Failed to submit feedback')
  return res.json()
}

export async function explainResult(data) {
  const res = await fetch(`${ASSISTANT_BASE}/assistant/explain`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  const json = await res.json()
  if (!res.ok) throw new Error(json.detail ?? 'AI explanation unavailable')
  return json
}
