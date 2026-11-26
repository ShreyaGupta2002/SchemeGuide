from django.contrib import admin
from .models import (
    Scheme, SchemeVersion, EligibilityRule,
    SourceDocument, SourcePassage, RequiredDocument, ReviewRecord
)


class EligibilityRuleInline(admin.TabularInline):
    model = EligibilityRule
    extra = 3
    fields = ['field', 'operator', 'value', 'explanation', 'source_passage']


class RequiredDocumentInline(admin.TabularInline):
    model = RequiredDocument
    extra = 1
    fields = ['name', 'when_required']


class SourcePassageInline(admin.TabularInline):
    model = SourcePassage
    extra = 1
    fields = ['text', 'section_reference']


class SourceDocumentInline(admin.TabularInline):
    model = SourceDocument
    extra = 1
    fields = ['title', 'official_url', 'retrieval_date', 'verified_date']


@admin.register(SchemeVersion)
class SchemeVersionAdmin(admin.ModelAdmin):
    list_display = ['scheme', 'version_number', 'status', 'applicable_year', 'application_close']
    list_filter = ['status', 'applicable_year']
    search_fields = ['scheme__name', 'description']
    inlines = [EligibilityRuleInline, RequiredDocumentInline, SourceDocumentInline]
    actions = ['publish_versions', 'mark_reviewed']

    @admin.action(description='Publish selected versions')
    def publish_versions(self, request, queryset):
        queryset.update(status='published')

    @admin.action(description='Mark selected versions as reviewed')
    def mark_reviewed(self, request, queryset):
        queryset.update(status='reviewed')


@admin.register(Scheme)
class SchemeAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'jurisdiction', 'state']
    list_filter = ['jurisdiction']
    search_fields = ['name', 'department']


@admin.register(SourceDocument)
class SourceDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'scheme_version', 'retrieval_date', 'verified_date']
    inlines = [SourcePassageInline]


admin.site.register(ReviewRecord)
