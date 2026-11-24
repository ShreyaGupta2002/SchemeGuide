import { useState } from 'react'
import { Modal, Button, Form, Alert } from 'react-bootstrap'
import { submitFeedback } from '../api/client'

export default function FeedbackForm({ schemeVersionId, schemeName, onClose }) {
  const [fields, setFields] = useState({
    problem_description: '',
    correct_information: '',
    official_source_url: '',
  })
  const [status, setStatus] = useState(null) // null | 'submitting' | 'done' | 'error'

  function handleChange(e) {
    setFields(f => ({ ...f, [e.target.name]: e.target.value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!fields.problem_description.trim()) return
    setStatus('submitting')
    try {
      await submitFeedback({
        scheme_version_id: schemeVersionId,
        scheme_name: schemeName,
        problem_description: fields.problem_description,
        correct_information: fields.correct_information || undefined,
        official_source_url: fields.official_source_url || undefined,
      })
      setStatus('done')
    } catch {
      setStatus('error')
    }
  }

  return (
    <Modal show onHide={onClose} centered>
      <Modal.Header closeButton>
        <Modal.Title className="fs-6">Report incorrect information</Modal.Title>
      </Modal.Header>
      <Form onSubmit={handleSubmit}>
        <Modal.Body>
          <p className="text-muted small mb-3">
            Scheme: <strong>{schemeName}</strong>
          </p>
          {status === 'done' ? (
            <Alert variant="success" className="mb-0">
              Thank you — your report has been submitted.
            </Alert>
          ) : (
            <>
              {status === 'error' && (
                <Alert variant="danger">Something went wrong. Please try again.</Alert>
              )}
              <Form.Group className="mb-3">
                <Form.Label>What is incorrect? <span className="text-danger">*</span></Form.Label>
                <Form.Control
                  as="textarea"
                  rows={3}
                  name="problem_description"
                  value={fields.problem_description}
                  onChange={handleChange}
                  placeholder="Describe the problem with the scheme data..."
                  required
                />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>What is the correct information? <span className="text-muted">(optional)</span></Form.Label>
                <Form.Control
                  as="textarea"
                  rows={2}
                  name="correct_information"
                  value={fields.correct_information}
                  onChange={handleChange}
                  placeholder="The correct value or rule..."
                />
              </Form.Group>
              <Form.Group>
                <Form.Label>Official source URL <span className="text-muted">(optional)</span></Form.Label>
                <Form.Control
                  type="url"
                  name="official_source_url"
                  value={fields.official_source_url}
                  onChange={handleChange}
                  placeholder="https://..."
                />
              </Form.Group>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" size="sm" onClick={onClose}>Close</Button>
          {status !== 'done' && (
            <Button type="submit" size="sm" disabled={status === 'submitting'}>
              {status === 'submitting' ? 'Submitting…' : 'Submit Report'}
            </Button>
          )}
        </Modal.Footer>
      </Form>
    </Modal>
  )
}
