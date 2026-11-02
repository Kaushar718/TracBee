
from django.core.paginator import Paginator
from django.db.models import Q

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import JobPosting

from .services import get_skill_demand

from .serializers import (
    SkillDemandQuerySerializer,
    JobPostingQuerySerializer,
    JobPostingSerializer,
)


@api_view(["GET"])
@permission_classes([AllowAny])
def skill_demand_api(request):

    serializer = SkillDemandQuerySerializer(
        data=request.query_params
    )

    if not serializer.is_valid():
        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    filters = serializer.validated_data

    try:
        result = get_skill_demand(
            location=filters.get("location"),
            year=filters.get("year")
        )

        return Response(
            result,
            status=status.HTTP_200_OK
        )

    except ValueError as error:
        return Response(
            {"error": str(error)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def job_list_api(request):

    # Validate incoming query parameters.
    serializer = JobPostingQuerySerializer(
        data=request.query_params
    )

    if not serializer.is_valid():
        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    filters = serializer.validated_data

    # Start with active job postings.
    jobs = (
        JobPosting.objects
        .filter(is_active=True)
        .prefetch_related("skills")
    )

    # Search across title, company, location,
    # description and skill names.
    search = filters.get("search", "").strip()

    if search:
        jobs = jobs.filter(
            Q(title__icontains=search)
            | Q(company__icontains=search)
            | Q(location__icontains=search)
            | Q(description__icontains=search)
            | Q(skills__name__icontains=search)
        ).distinct()

    # Filter by exact skill name.
    skill = filters.get("skill", "").strip()

    if skill:
        jobs = jobs.filter(
            skills__name__iexact=skill
        )

    # Filter by company.
    company = filters.get("company", "").strip()

    if company:
        jobs = jobs.filter(
            company__icontains=company
        )

    # Filter by location.
    location = filters.get("location", "").strip()

    if location:
        jobs = jobs.filter(
            location__icontains=location
        )

    # Filter by posting year.
    year = filters.get("year")

    if year:
        jobs = jobs.filter(
            posted_at__year=year
        )

    # Filter by employment type.
    employment_type = filters.get("employment_type")

    if employment_type:
        jobs = jobs.filter(
            employment_type=employment_type
        )

    # Consistent ordering for pagination.
    jobs = jobs.order_by(
        "-posted_at",
        "-created_at",
        "-id"
    )

    # Pagination.
    page_size = filters.get("page_size", 10)
    page_number = filters.get("page", 1)

    paginator = Paginator(jobs, page_size)

    page_obj = paginator.get_page(page_number)

    # Serialize selected page.
    job_serializer = JobPostingSerializer(
        page_obj.object_list,
        many=True
    )

    return Response(
        {
            "total_count": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page_obj.number,
            "page_size": page_size,
            "results": job_serializer.data,
        },
        status=status.HTTP_200_OK
    )
