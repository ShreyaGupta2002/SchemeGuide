import { Link } from 'react-router-dom'
import { Container, Button, Row, Col, Card } from 'react-bootstrap'

const FEATURES = [
  {
    icon: '🔍',
    title: 'Enter Your Profile',
    text: 'Tell us your state, income, education level, and category. All fields are optional.',
  },
  {
    icon: '✅',
    title: 'See Your Eligibility',
    text: 'Each scheme condition is checked against your profile — pass, fail, or unknown.',
  },
  {
    icon: '📋',
    title: 'Apply with Confidence',
    text: 'Every result links to the official government source it was drawn from.',
  },
]

export default function HomePage() {
  return (
    <>
      <div className="bg-dark text-white py-5">
        <Container className="py-4 text-center">
          <h1 className="display-5 fw-bold mb-3">
            Find Government Scholarships<br className="d-none d-md-block" /> That Apply to You
          </h1>
          <p className="lead text-secondary mb-4 mx-auto" style={{ maxWidth: 560 }}>
            SchemeGuide helps students and citizens discover government schemes,
            check eligibility against official rules, and understand results in plain language.
          </p>
          <div className="d-flex gap-3 justify-content-center flex-wrap">
            <Button as={Link} to="/check" size="lg" variant="primary">
              Check My Eligibility
            </Button>
            <Button as={Link} to="/schemes" size="lg" variant="outline-light">
              Browse All Schemes
            </Button>
          </div>
        </Container>
      </div>

      <Container className="py-5">
        <h2 className="text-center fw-semibold mb-5">How It Works</h2>
        <Row className="g-4 justify-content-center">
          {FEATURES.map((f, i) => (
            <Col key={i} md={4}>
              <Card className="h-100 text-center border-0 shadow-sm p-3">
                <div className="fs-1 mb-3">{f.icon}</div>
                <Card.Title className="fw-semibold">{f.title}</Card.Title>
                <Card.Text className="text-muted small">{f.text}</Card.Text>
              </Card>
            </Col>
          ))}
        </Row>

        <div className="text-center mt-5 p-4 bg-white rounded shadow-sm">
          <h5 className="fw-semibold mb-2">Transparent by design</h5>
          <p className="text-muted small mb-0">
            Eligibility is decided by rules, not AI. Every rule links to the official government
            passage it came from. If anything looks wrong, you can report it directly.
          </p>
        </div>
      </Container>
    </>
  )
}
