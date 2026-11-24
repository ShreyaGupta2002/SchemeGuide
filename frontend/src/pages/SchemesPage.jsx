import { useEffect, useState } from 'react'
import { Container, Row, Col, Spinner, Alert } from 'react-bootstrap'
import { fetchSchemes } from '../api/client'
import SchemeCard from '../components/SchemeCard'

export default function SchemesPage() {
  const [schemes, setSchemes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchSchemes()
      .then(setSchemes)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <Container className="py-5">
      <div className="mb-4">
        <h2 className="fw-bold mb-1">Government Schemes</h2>
        {!loading && !error && (
          <p className="text-muted">{schemes.length} published scheme{schemes.length !== 1 ? 's' : ''}</p>
        )}
      </div>

      {loading && (
        <div className="text-center py-5">
          <Spinner animation="border" variant="primary" />
          <p className="text-muted mt-2">Loading schemes…</p>
        </div>
      )}

      {error && (
        <Alert variant="danger">
          Could not load schemes: {error}
        </Alert>
      )}

      {!loading && !error && schemes.length === 0 && (
        <Alert variant="info">
          No published schemes yet. Check back soon.
        </Alert>
      )}

      <Row className="g-4">
        {schemes.map(scheme => (
          <Col key={scheme.id} md={6} lg={4}>
            <SchemeCard scheme={scheme} />
          </Col>
        ))}
      </Row>
    </Container>
  )
}
