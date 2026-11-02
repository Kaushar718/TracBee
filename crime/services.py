from django.db.models import Count, Q

from .models import JobPosting, JobPostingSkill


def get_skill_demand(location=None, year=None):
    """
    Calculate skill demand from stored job postings.

    This currently uses synthetic development data,
    not real-world job market statistics.
    """

    active_jobs = JobPosting.objects.filter(is_active=True)

    external_jobs = active_jobs.exclude(
        source="TracBee Demo Dataset"
    )

    # Prefer external postings when available.
    # Otherwise retain the synthetic demo dataset.
    jobs = external_jobs if external_jobs.exists() else active_jobs

    # Filter by location
    if location:
        jobs = jobs.filter(location__icontains=location.strip())

    # Filter by posting year
    if year:
        jobs = jobs.filter(
            Q(posted_at__year=year)
            | Q(posted_at__isnull=True, source_updated_at__year=year)
        )

    total_jobs = jobs.count()

    # Count how many matching job postings require each skill
    demand_data = (
        JobPostingSkill.objects
        .filter(job_posting__in=jobs)
        .values(
            "skill_id",
            "skill__name",
            "skill__category",
        )
        .annotate(
            job_count=Count("job_posting_id", distinct=True)
        )
        .order_by("-job_count", "skill__name")
    )

    results = []

    for item in demand_data:
        job_count = item["job_count"]

        percentage = (
            round((job_count / total_jobs) * 100, 2)
            if total_jobs else 0
        )

        results.append({
            "skill_id": item["skill_id"],
            "skill": item["skill__name"],
            "category": item["skill__category"],
            "job_count": job_count,
            "demand_percentage": percentage,
        })

    return {
        "total_jobs": total_jobs,
        "location": location or "All locations",
        "year": year or "All years",
        "skills": results,
    }
