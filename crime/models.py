
from django.db import models
from django.contrib.auth.models import User


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    aliases = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class JobPosting(models.Model):

    EMPLOYMENT_TYPES = [
        ("full_time", "Full-time"),
        ("part_time", "Part-time"),
        ("internship", "Internship"),
        ("contract", "Contract"),
    ]

    title = models.CharField(max_length=200)
    company = models.CharField(max_length=150)
    location = models.CharField(max_length=150, db_index=True)

    employment_type = models.CharField(
        max_length=30,
        choices=EMPLOYMENT_TYPES,
        blank=True
    )

    description = models.TextField(blank=True)

    salary_min = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    salary_max = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    currency = models.CharField(max_length=3, default="INR")

    source = models.CharField(max_length=80, blank=True)
    source_url = models.URLField(max_length=500, blank=True)

    source_updated_at = models.DateTimeField(
    null=True,
    blank=True
)

    posted_at = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    skills = models.ManyToManyField(
        Skill,
        through="JobPostingSkill",
        related_name="job_postings"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-posted_at", "-created_at"]

        indexes = [
            models.Index(fields=["posted_at"]),
            models.Index(fields=["is_active"]),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["source", "source_url"],
                condition=~models.Q(source_url=""),
                name="unique_job_source_url",
            )
        ]

    def __str__(self):
        return f"{self.title} - {self.company}"


class JobPostingSkill(models.Model):
    job_posting = models.ForeignKey(
        JobPosting,
        on_delete=models.CASCADE,
        related_name="job_skill_links"
    )

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="job_skill_links"
    )

    is_required = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["job_posting", "skill"],
                name="unique_job_posting_skill"
            )
        ]

    def __str__(self):
        return f"{self.job_posting.title} - {self.skill.name}"


class LoginActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    login_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} logged in from {self.ip_address}"


class SearchLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    skill = models.CharField(max_length=100, blank=True)
    year = models.CharField(max_length=10, blank=True)
    location = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        username = self.user.username if self.user else "Guest"
        return f"{username} searched {self.skill} in {self.location} ({self.year})"
