import { useState } from 'react'
import { Form, Button, Card, Row, Col } from 'react-bootstrap'

const EDUCATION_OPTIONS = [
  { value: '', label: 'Select…' },
  { value: 'class12', label: 'Class 12 / Intermediate' },
  { value: 'diploma', label: 'Diploma' },
  { value: 'graduation', label: 'Graduation (UG)' },
  { value: 'postgraduation', label: 'Post Graduation (PG)' },
]

const CASTE_OPTIONS = [
  { value: '', label: 'Select…' },
  { value: 'general', label: 'General' },
  { value: 'OBC', label: 'OBC' },
  { value: 'SC', label: 'SC' },
  { value: 'ST', label: 'ST' },
]

const GENDER_OPTIONS = [
  { value: '', label: 'Select…' },
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
  { value: 'other', label: 'Other' },
]

export default function ProfileForm({ onSubmit, loading }) {
  const [form, setForm] = useState({
    state: '',
    annual_income: '',
    education_level: '',
    caste_category: '',
    gender: '',
    age: '',
    parent_service: '',
  })

  function handleChange(e) {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }))
  }

  function handleSubmit(e) {
    e.preventDefault()
    const profile = {}
    if (form.state.trim()) profile.state = form.state.trim()
    if (form.annual_income) profile.annual_income = parseFloat(form.annual_income)
    if (form.education_level) profile.education_level = form.education_level
    if (form.caste_category) profile.caste_category = form.caste_category
    if (form.gender) profile.gender = form.gender
    if (form.age) profile.age = parseInt(form.age, 10)
    if (form.parent_service.trim()) profile.parent_service = form.parent_service.trim()
    onSubmit(profile)
  }

  return (
    <Card className="shadow-sm">
      <Card.Body>
        <Card.Title className="mb-1">Your Profile</Card.Title>
        <p className="text-muted small mb-4">
          Fill in what applies to you. Leave blank to skip a field — we'll mark those conditions as unknown.
        </p>
        <Form onSubmit={handleSubmit}>
          <Row className="g-3">
            <Col sm={6}>
              <Form.Group>
                <Form.Label className="small fw-medium">State</Form.Label>
                <Form.Control
                  size="sm"
                  name="state"
                  value={form.state}
                  onChange={handleChange}
                  placeholder="e.g. Maharashtra"
                />
              </Form.Group>
            </Col>
            <Col sm={6}>
              <Form.Group>
                <Form.Label className="small fw-medium">Age</Form.Label>
                <Form.Control
                  size="sm"
                  type="number"
                  name="age"
                  value={form.age}
                  onChange={handleChange}
                  placeholder="e.g. 21"
                  min={1}
                  max={100}
                />
              </Form.Group>
            </Col>
            <Col sm={12}>
              <Form.Group>
                <Form.Label className="small fw-medium">Annual Family Income (₹)</Form.Label>
                <Form.Control
                  size="sm"
                  type="number"
                  name="annual_income"
                  value={form.annual_income}
                  onChange={handleChange}
                  placeholder="e.g. 250000"
                  min={0}
                />
                <Form.Text className="text-muted">Enter in rupees (e.g. 2.5 lakh = 250000)</Form.Text>
              </Form.Group>
            </Col>
            <Col sm={6}>
              <Form.Group>
                <Form.Label className="small fw-medium">Education Level</Form.Label>
                <Form.Select size="sm" name="education_level" value={form.education_level} onChange={handleChange}>
                  {EDUCATION_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                </Form.Select>
              </Form.Group>
            </Col>
            <Col sm={6}>
              <Form.Group>
                <Form.Label className="small fw-medium">Caste Category</Form.Label>
                <Form.Select size="sm" name="caste_category" value={form.caste_category} onChange={handleChange}>
                  {CASTE_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                </Form.Select>
              </Form.Group>
            </Col>
            <Col sm={6}>
              <Form.Group>
                <Form.Label className="small fw-medium">Gender</Form.Label>
                <Form.Select size="sm" name="gender" value={form.gender} onChange={handleChange}>
                  {GENDER_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                </Form.Select>
              </Form.Group>
            </Col>
            <Col sm={6}>
              <Form.Group>
                <Form.Label className="small fw-medium">Parent's Service</Form.Label>
                <Form.Control
                  size="sm"
                  name="parent_service"
                  value={form.parent_service}
                  onChange={handleChange}
                  placeholder="e.g. CAPF"
                />
                <Form.Text className="text-muted">For CAPF / RPF scholarships</Form.Text>
              </Form.Group>
            </Col>
          </Row>
          <Button type="submit" className="mt-4 w-100" disabled={loading}>
            {loading ? 'Checking…' : 'Check Eligibility'}
          </Button>
        </Form>
      </Card.Body>
    </Card>
  )
}
