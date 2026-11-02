
from rest_framework import serializers

from .models import JobPosting


class SkillDemandQuerySerializer(serializers.Serializer):
    location = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=120
    )

    year = serializers.IntegerField(
        required=False,
        min_value=1900,
        max_value=2100
    )


class JobPostingQuerySerializer(serializers.Serializer):

    search = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=150
    )

    skill = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100
    )

    company = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=150
    )

    location = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=120
    )

    year = serializers.IntegerField(
        required=False,
        min_value=1900,
        max_value=2100
    )

    employment_type = serializers.ChoiceField(
        choices=[
            "full_time",
            "part_time",
            "internship",
            "contract",
        ],
        required=False
    )

    page = serializers.IntegerField(
        required=False,
        min_value=1,
        default=1
    )

    page_size = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=50,
        default=10
    )


class JobPostingSerializer(serializers.ModelSerializer):

    skills = serializers.StringRelatedField(
        many=True,
        read_only=True
    )

    class Meta:
        model = JobPosting

        fields = [
            "id",
            "title",
            "company",
            "location",
            "employment_type",
            "description",
            "salary_min",
            "salary_max",
            "currency",
            "source",
            "source_url",
            "posted_at",
            "source_updated_at",
            "skills",
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields
