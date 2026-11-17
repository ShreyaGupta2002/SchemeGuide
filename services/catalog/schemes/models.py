from django.db import models
from django.contrib.auth.models import User


class Scheme(models.Model):
    name = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    jurisdiction = models.CharField(
        max_length=50,
        choices=[('central', 'Central'), ('state', 'State')],
        default='central'
    )
    state = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class SchemeVersion(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('reviewed', 'Reviewed'),
        ('published', 'Published'),
    ]

    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField(default=1)
    description = models.TextField()
    benefit_amount = models.CharField(max_length=255, blank=True)
    applicable_year = models.CharField(max_length=20)
    application_open = models.DateField(null=True, blank=True)
    application_close = models.DateField(null=True, blank=True)
    official_url = models.URLField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.scheme.name} v{self.version_number} ({self.status})"

    class Meta:
        ordering = ['-version_number']
        unique_together = ['scheme', 'version_number']


class SourceDocument(models.Model):
    scheme_version = models.ForeignKey(SchemeVersion, on_delete=models.CASCADE, related_name='source_documents')
    title = models.CharField(max_length=255)
    official_url = models.URLField()
    retrieval_date = models.DateField()
    verified_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title


class SourcePassage(models.Model):
    source_document = models.ForeignKey(SourceDocument, on_delete=models.CASCADE, related_name='passages')
    text = models.TextField()
    section_reference = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.source_document.title} — {self.section_reference or 'passage'}"


class EligibilityRule(models.Model):
    OPERATOR_CHOICES = [
        ('equals', 'Equals'),
        ('not_equals', 'Not Equals'),
        ('in', 'In (list)'),
        ('not_in', 'Not In (list)'),
        ('gte', 'Greater than or equal'),
        ('lte', 'Less than or equal'),
        ('gt', 'Greater than'),
        ('lt', 'Less than'),
    ]

    scheme_version = models.ForeignKey(SchemeVersion, on_delete=models.CASCADE, related_name='eligibility_rules')
    field = models.CharField(max_length=100)
    operator = models.CharField(max_length=20, choices=OPERATOR_CHOICES)
    value = models.CharField(max_length=500)
    explanation = models.CharField(max_length=500)
    source_passage = models.ForeignKey(
        SourcePassage, on_delete=models.SET_NULL, null=True, blank=True, related_name='rules'
    )

    def __str__(self):
        return f"{self.field} {self.operator} {self.value}"


class RequiredDocument(models.Model):
    scheme_version = models.ForeignKey(SchemeVersion, on_delete=models.CASCADE, related_name='required_documents')
    name = models.CharField(max_length=255)
    when_required = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class ReviewRecord(models.Model):
    DECISION_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('flagged', 'Flagged for revision'),
    ]

    scheme_version = models.ForeignKey(SchemeVersion, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    decision = models.CharField(max_length=20, choices=DECISION_CHOICES)
    comments = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.scheme_version} — {self.decision}"
