import { Card, Badge, Button } from 'react-bootstrap'
import { useNavigate } from 'react-router-dom'

export default function SchemeCard({ scheme }) {
  const navigate = useNavigate()
  const v = scheme.latest_version

  return (
    <Card className="h-100 shadow-sm">
      <Card.Body className="d-flex flex-column">
        <div className="mb-2">
          <Badge bg="secondary" className="me-1 text-capitalize">{scheme.jurisdiction}</Badge>
          {scheme.state && <Badge bg="light" text="dark">{scheme.state}</Badge>}
        </div>
        <Card.Title className="fs-6 fw-bold">{scheme.name}</Card.Title>
        <Card.Subtitle className="text-muted small mb-2">{scheme.department}</Card.Subtitle>
        {v && (
          <>
            <Card.Text className="small text-secondary flex-grow-1">
              {v.description?.slice(0, 120)}{v.description?.length > 120 ? '…' : ''}
            </Card.Text>
            {v.benefit_amount && (
              <div className="small fw-medium text-success mb-1">
                {v.benefit_amount}
              </div>
            )}
            <div className="small text-muted mb-3">
              Year: {v.applicable_year}
              {v.application_close && ` · Closes: ${v.application_close}`}
            </div>
          </>
        )}
        <div className="d-flex gap-2 mt-auto">
          <Button
            size="sm"
            variant="primary"
            onClick={() => navigate('/check')}
          >
            Check Eligibility
          </Button>
          {v?.official_url && (
            <Button
              size="sm"
              variant="outline-secondary"
              href={v.official_url}
              target="_blank"
              rel="noopener noreferrer"
              as="a"
            >
              Official Link ↗
            </Button>
          )}
        </div>
      </Card.Body>
    </Card>
  )
}
