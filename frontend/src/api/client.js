const BASE = '/api/v1'

export async function fetchSchemes() {
  const res = await fetch(`${BASE}/schemes/`)
  if (!res.ok) throw new Error('Failed to fetch schemes')
  return res.json()
}

export async function checkEligibility(profile) {
  const res = await fetch(`${BASE}/matches`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ profile }),
  })
  if (!res.ok) throw new Error('Failed to check eligibility')
  return res.json()
}

export async function submitFeedback(data) {
  const res = await fetch(`${BASE}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error('Failed to submit feedback')
  return res.json()
}

export async function explainResult(data) {
  const res = await fetch(`${BASE}/assistant/explain`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  const json = await res.json()
  if (!res.ok) throw new Error(json.detail ?? 'AI explanation unavailable')
  return json
}
