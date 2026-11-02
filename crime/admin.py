from django.contrib import admin
from .models import (
    Skill,
    JobPosting,
    JobPostingSkill,
    LoginActivity,
    SearchLog,
)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "created_at")
    search_fields = ("name", "category")
    list_filter = ("category",)


class JobPostingSkillInline(admin.TabularInline):
    model = JobPostingSkill
    extra = 1


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "company",
        "location",
        "posted_at",
        "is_active",
    )
    search_fields = ("title", "company", "location")
    list_filter = ("location", "is_active", "employment_type")
    inlines = [JobPostingSkillInline]


admin.site.register(LoginActivity)
admin.site.register(SearchLog)