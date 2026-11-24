import { useState } from 'react'
import { Card, Badge, Button, Collapse, Alert, Spinner } from 'react-bootstrap'
import ConditionRow from './ConditionRow'
import FeedbackForm from './FeedbackForm'
import { explainResult } from '../api/client'

const OUTCOME = {
  appears_eligible: { bg: 'success', label: 'Appears Eligible' },
  appears_non_eligible: { bg: 'danger', label: 'Appears Non-Eligible' },
  more_information_needed: { bg: 'warning', label: 'Need More Info' },
}

function SchemeResult({ result, profile }) {
  const [open, setOpen] = useState(result.outcome === 'appears_eligible')
  const [showFeedback, setShowFeedback] = useState(false)
  const [explanation, setExplanation] = useState(null)
  const [explaining, setExplaining] = useState(false)
  const [explainError, setExplainError] = useState(null)
  const { bg, label } = OUTCOME[result.outcome] ?? OUTCOME.more_information_needed

  async function handleExplain() {
    setExplaining(true)
    setExplainError(null)
    try {
      const data = await explainResult({
        scheme_id: result.scheme_id,
        scheme_name: result.scheme_name,
        outcome: result.outcome,
        conditions: result.conditions.map(c => ({
          field: c.field,
          result: c.result,
          explanation: c.explanation,
        })),
        profile: profile ?? {},
      })
      setExplanation(data.explanation)
    } catch (e) {
      setExplainError(e.message)
    } finally {
      setExplaining(false)
    }
  }

  return (
    <Card className={`mb-3 border-${bg} border-opacity-50`}>
      <Card.Body>
        <div className="d-flex align-items-start justify-content-between gap-2 flex-wrap">
          <div>
            <Card.Title className="fs-6 mb-1">{result.scheme_name}</Card.Title>
            <Badge bg={bg}>{label}</Badge>
          </div>
          <Button
            variant="link"
            size="sm"
            className="text-muted p-0 text-decoration-none"
            onClick={() => setOpen(o => !o)}
          >
            {open ? 'Hide conditions ▲' : 'Show conditions ▼'}
          </Button>
        </div>

        {explanation && (
          <Alert variant="info" className="mt-3 mb-0 small">
            <strong>AI Explanation</strong>
            <p className="mb-0 mt-1">{explanation}</p>
          </Alert>
        )}

        <Collapse in={open}>
          <div className="mt-3">
            {result.conditions.length === 0 ? (
              <p className="text-muted small mb-0">No eligibility rules found for this scheme.</p>
            ) : (
              result.conditions.map(c => (
                <ConditionRow key={c.rule_id} condition={c} />
              ))
            )}

            <div className="mt-3 d-flex gap-2 flex-wrap align-items-center">
              {!explanation && (
                <Button
                  variant="outline-primary"
                  size="sm"
                  onClick={handleExplain}
                  disabled={explaining}
                >
                  {explaining ? (
                    <><Spinner size="sm" className="me-1" />Explaining…</>
                  ) : (
                    'Explain with AI ✨'
                  )}
                </Button>
              )}
              <Button
                variant="outline-secondary"
                size="sm"
                onClick={() => setShowFeedback(true)}
              >
                Report incorrect info
              </Button>
            </div>

            {explainError && (
              <Alert variant="warning" className="mt-2 mb-0 small py-2">
                {explainError}
              </Alert>
            )}
          </div>
        </Collapse>
      </Card.Body>

      {showFeedback && (
        <FeedbackForm
          schemeVersionId={result.scheme_version_id}
          schemeName={result.scheme_name}
          onClose={() => setShowFeedback(false)}
        />
      )}
    </Card>
  )
}

export default function MatchResults({ results, profile }) {
  if (!results.length) {
    return (
      <Card className="shadow-sm text-center py-5 text-muted">
        No published schemes found to match against.
      </Card>
    )
  }

  const eligible = results.filter(r => r.outcome === 'appears_eligible')
  const needsInfo = results.filter(r => r.outcome === 'more_information_needed')
  const nonEligible = results.filter(r => r.outcome === 'appears_non_eligible')
  const ordered = [...eligible, ...needsInfo, ...nonEligible]

  return (
    <div>
      <div className="d-flex gap-3 mb-4 flex-wrap">
        <span className="badge bg-success fs-6 px-3 py-2">{eligible.length} Eligible</span>
        <span className="badge bg-warning text-dark fs-6 px-3 py-2">{needsInfo.length} Need Info</span>
        <span className="badge bg-danger fs-6 px-3 py-2">{nonEligible.length} Non-Eligible</span>
      </div>
      {ordered.map(r => <SchemeResult key={r.scheme_id} result={r} profile={profile} />)}
    </div>
  )
}
