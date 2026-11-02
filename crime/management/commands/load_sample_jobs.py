
from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from crime.models import Skill, JobPosting, JobPostingSkill


SKILLS = {
    "Python": "Programming",
    "Django": "Backend",
    "SQL": "Database",
    "PostgreSQL": "Database",
    "REST API": "Backend",
    "Java": "Programming",
    "JavaScript": "Frontend",
    "React": "Frontend",
    "HTML": "Frontend",
    "CSS": "Frontend",
    "Machine Learning": "AI / ML",
    "Excel": "Analytics",
    "Git": "Tools",
}


JOBS = [
    {
        "title": "Python Backend Developer",
        "company": "DemoTech",
        "location": "Bengaluru",
        "date": date(2025, 1, 15),
        "type": "full_time",
        "skills": ["Python", "Django", "SQL", "REST API"],
    },
    {
        "title": "Django Developer",
        "company": "SampleWorks",
        "location": "Bengaluru",
        "date": date(2025, 3, 10),
        "type": "full_time",
        "skills": ["Python", "Django", "PostgreSQL", "REST API"],
    },
    {
        "title": "Java Backend Engineer",
        "company": "CodeDemo",
        "location": "Hyderabad",
        "date": date(2025, 4, 12),
        "type": "full_time",
        "skills": ["Java", "SQL", "PostgreSQL", "REST API"],
    },
    {
        "title": "Data Analyst",
        "company": "DataSample",
        "location": "Pune",
        "date": date(2025, 6, 20),
        "type": "full_time",
        "skills": ["Python", "SQL", "Excel"],
    },
    {
        "title": "Full Stack Developer",
        "company": "WebDemo",
        "location": "Bengaluru",
        "date": date(2025, 8, 5),
        "type": "full_time",
        "skills": ["Python", "JavaScript", "React", "HTML", "CSS"],
    },
    {
        "title": "Machine Learning Engineer",
        "company": "AI Sample",
        "location": "Hyderabad",
        "date": date(2025, 10, 14),
        "type": "full_time",
        "skills": ["Python", "Machine Learning", "SQL"],
    },
    {
        "title": "Python Developer",
        "company": "TechExample",
        "location": "Pune",
        "date": date(2026, 2, 10),
        "type": "full_time",
        "skills": ["Python", "Django", "PostgreSQL", "Git"],
    },
    {
        "title": "Software Engineer",
        "company": "BuildDemo",
        "location": "Bengaluru",
        "date": date(2026, 3, 18),
        "type": "full_time",
        "skills": ["Java", "SQL", "REST API", "Git"],
    },
    {
        "title": "Backend Development Intern",
        "company": "StartupDemo",
        "location": "Bengaluru",
        "date": date(2026, 4, 8),
        "type": "internship",
        "skills": ["Python", "Django", "SQL", "Git"],
    },
    {
        "title": "Data Engineer",
        "company": "CloudSample",
        "location": "Hyderabad",
        "date": date(2026, 5, 22),
        "type": "full_time",
        "skills": ["Python", "SQL", "PostgreSQL", "Git"],
    },
    {
        "title": "Frontend Developer",
        "company": "UI Demo",
        "location": "Pune",
        "date": date(2026, 7, 11),
        "type": "full_time",
        "skills": ["JavaScript", "React", "HTML", "CSS"],
    },
    {
        "title": "QA Automation Engineer",
        "company": "TestSample",
        "location": "Bengaluru",
        "date": date(2026, 8, 19),
        "type": "full_time",
        "skills": ["Python", "SQL", "Git"],
    },
]


class Command(BaseCommand):
    help = "Load synthetic sample jobs for TracBee development"

    @transaction.atomic
    def handle(self, *args, **options):

        skill_objects = {}

        for name, category in SKILLS.items():
            skill, _ = Skill.objects.get_or_create(
                name=name,
                defaults={"category": category},
            )
            skill_objects[name] = skill

        created_jobs = 0

        for item in JOBS:
            job, created = JobPosting.objects.update_or_create(
                title=item["title"],
                company=item["company"],
                location=item["location"],
                posted_at=item["date"],
                defaults={
                    "employment_type": item["type"],
                    "description": (
                        "Synthetic sample record for TracBee development. "
                        "This is not a real job vacancy."
                    ),
                    "source": "TracBee Demo Dataset",
                    "source_url": "",
                    "is_active": True,
                },
            )

            if created:
                created_jobs += 1

            for skill_name in item["skills"]:
                JobPostingSkill.objects.get_or_create(
                    job_posting=job,
                    skill=skill_objects[skill_name],
                    defaults={"is_required": True},
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Sample dataset loaded. New jobs created: {created_jobs}"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Total skills: {Skill.objects.count()}"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Total jobs: {JobPosting.objects.count()}"
            )
        )
