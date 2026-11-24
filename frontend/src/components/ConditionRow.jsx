const BADGE = {
  pass: { bg: 'success', label: '✓ Pass' },
  fail: { bg: 'danger', label: '✗ Fail' },
  unknown: { bg: 'secondary', label: '? Unknown' },
}

export default function ConditionRow({ condition }) {
  const { bg, label } = BADGE[condition.result] ?? BADGE.unknown

  return (
    <div className="d-flex align-items-start gap-3 py-2 border-bottom">
      <span className={`badge bg-${bg} mt-1 text-nowrap`}>{label}</span>
      <div className="flex-grow-1">
        <div className="fw-medium">{condition.explanation}</div>
        {condition.actual_value !== null ? (
          <small className="text-muted">
            Your value: <strong>{condition.actual_value}</strong>
            {' · '}Required: {condition.operator} <strong>{condition.expected_value}</strong>
          </small>
        ) : (
          <small className="text-muted">Not provided in your profile</small>
        )}
      </div>
    </div>
  )
}
