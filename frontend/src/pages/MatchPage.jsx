import { useState } from 'react'
import { Container, Row, Col, Alert } from 'react-bootstrap'
import { checkEligibility } from '../api/client'
import ProfileForm from '../components/ProfileForm'
import MatchResults from '../components/MatchResults'

export default function MatchPage() {
  const [results, setResults] = useState(null)
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(submittedProfile) {
    setLoading(true)
    setError(null)
    setResults(null)
    setProfile(submittedProfile)
    try {
      const data = await checkEligibility(submittedProfile)
      setResults(data.results)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container className="py-5">
      <div className="mb-4">
        <h2 className="fw-bold mb-1">Check Your Eligibility</h2>
        <p className="text-muted">
          Enter your details and we'll check them against every published scheme instantly.
        </p>
      </div>

      <Row className="g-4">
        <Col md={5} lg={4}>
          <ProfileForm onSubmit={handleSubmit} loading={loading} />
        </Col>

        <Col md={7} lg={8}>
          {error && (
            <Alert variant="danger">Could not check eligibility: {error}</Alert>
          )}

          {!results && !loading && !error && (
            <div className="text-center text-muted py-5 border rounded bg-white">
              <div className="fs-1 mb-3">📋</div>
              <p className="mb-0">Fill in your profile and click <strong>Check Eligibility</strong> to see results.</p>
            </div>
          )}

          {loading && (
            <div className="text-center text-muted py-5 border rounded bg-white">
              <div className="spinner-border text-primary mb-3" role="status" />
              <p className="mb-0">Checking against all schemes…</p>
            </div>
          )}

          {results && <MatchResults results={results} profile={profile} />}
        </Col>
      </Row>
    </Container>
  )
}
