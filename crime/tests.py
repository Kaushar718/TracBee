
from datetime import date

from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APITestCase

from .models import Skill, JobPosting, JobPostingSkill


class SkillDemandAPITests(APITestCase):

    def setUp(self):
        self.python = Skill.objects.create(
            name="Python",
            category="Programming",
        )

        self.django = Skill.objects.create(
            name="Django",
            category="Backend",
        )

        self.job1 = JobPosting.objects.create(
            title="Python Developer",
            company="DemoTech",
            location="Bengaluru",
            posted_at=date(2025, 1, 15),
        )

        self.job2 = JobPosting.objects.create(
            title="Django Developer",
            company="SampleWorks",
            location="Bengaluru",
            posted_at=date(2025, 3, 10),
        )

        self.job3 = JobPosting.objects.create(
            title="Python Engineer",
            company="CodeDemo",
            location="Pune",
            posted_at=date(2026, 2, 10),
        )

        JobPostingSkill.objects.create(
            job_posting=self.job1,
            skill=self.python,
        )

        JobPostingSkill.objects.create(
            job_posting=self.job1,
            skill=self.django,
        )

        JobPostingSkill.objects.create(
            job_posting=self.job2,
            skill=self.django,
        )

        JobPostingSkill.objects.create(
            job_posting=self.job3,
            skill=self.python,
        )

        self.url = reverse("skill-demand-api")

    def test_all_jobs_demand(self):
        response = self.client.get(self.url, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total_jobs"], 3)

    def test_location_filter(self):
        response = self.client.get(
            self.url,
            {"location": "Bengaluru"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total_jobs"], 2)

    def test_year_filter(self):
        response = self.client.get(
            self.url,
            {"year": 2025},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total_jobs"], 2)

    def test_combined_filter(self):
        response = self.client.get(
            self.url,
            {"location": "Bengaluru", "year": 2025},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total_jobs"], 2)

    def test_invalid_year(self):
        response = self.client.get(
            self.url,
            {"year": "invalid"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
