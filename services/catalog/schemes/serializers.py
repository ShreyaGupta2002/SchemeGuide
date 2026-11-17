from rest_framework import serializers
from .models import Scheme, SchemeVersion, EligibilityRule, SourcePassage, SourceDocument, RequiredDocument


class SourcePassageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourcePassage
        fields = ['id', 'text', 'section_reference']


class SourceDocumentSerializer(serializers.ModelSerializer):
    passages = SourcePassageSerializer(many=True, read_only=True)

    class Meta:
        model = SourceDocument
        fields = ['id', 'title', 'official_url', 'retrieval_date', 'verified_date', 'passages']


class EligibilityRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EligibilityRule
        fields = ['id', 'field', 'operator', 'value', 'explanation', 'source_passage']


class RequiredDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequiredDocument
        fields = ['id', 'name', 'when_required']


class SchemeVersionDetailSerializer(serializers.ModelSerializer):
    eligibility_rules = EligibilityRuleSerializer(many=True, read_only=True)
    required_documents = RequiredDocumentSerializer(many=True, read_only=True)
    source_documents = SourceDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = SchemeVersion
        fields = [
            'id', 'version_number', 'description', 'benefit_amount',
            'applicable_year', 'application_open', 'application_close',
            'official_url', 'status',
            'eligibility_rules', 'required_documents', 'source_documents',
        ]


class SchemeListSerializer(serializers.ModelSerializer):
    latest_version = serializers.SerializerMethodField()

    class Meta:
        model = Scheme
        fields = ['id', 'name', 'department', 'jurisdiction', 'state', 'latest_version']

    def get_latest_version(self, obj):
        version = obj.versions.filter(status='published').order_by('-version_number').first()
        if version:
            return {
                'id': version.id,
                'description': version.description,
                'benefit_amount': version.benefit_amount,
                'applicable_year': version.applicable_year,
                'application_open': version.application_open,
                'application_close': version.application_close,
                'official_url': version.official_url,
            }
        return None


class SchemeDetailSerializer(serializers.ModelSerializer):
    versions = serializers.SerializerMethodField()

    class Meta:
        model = Scheme
        fields = ['id', 'name', 'department', 'jurisdiction', 'state', 'versions']

    def get_versions(self, obj):
        versions = obj.versions.filter(status='published').order_by('-version_number')
        return SchemeVersionDetailSerializer(versions, many=True).data
