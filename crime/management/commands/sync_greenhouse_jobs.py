
import re
from datetime import datetime, timezone as dt_timezone
from html import unescape

import requests

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from crime.models import Skill, JobPosting, JobPostingSkill


def clean_html(value):
    value = unescape(unescape(value or ""))

    value = re.sub(
        r"<(script|style)\b[^>]*>.*?</\1>",
        " ",
        value,
        flags=re.IGNORECASE | re.DOTALL,
    )

    value = re.sub(r"<[^>]+>", " ", value)

    return re.sub(r"\s+", " ", value).strip()


def normalize_location(value):
    value = (value or "").strip()

    return re.sub(
        r"\bBangalore\b",
        "Bengaluru",
        value,
        flags=re.IGNORECASE,
    ) or "Not specified"


def parse_source_updated(value):
    if not value:
        return None

    try:
        result = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )

        if result.tzinfo is None:
            result = result.replace(tzinfo=dt_timezone.utc)

        return result

    except (ValueError, AttributeError):
        return None


def parse_posted_date(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        ).date()

    except (ValueError, AttributeError):
        return None


class Command(BaseCommand):

    help = "Synchronize all published jobs from a Greenhouse board"

    def add_arguments(self, parser):

        parser.add_argument(
            "--board-token",
            required=True,
        )

        parser.add_argument(
            "--company-name",
            required=True,
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
        )

        parser.add_argument(
            "--deactivate-missing",
            action="store_true",
        )

    def handle(self, *args, **options):

        token = options["board_token"].strip()
        company = options["company_name"].strip()

        dry_run = options["dry_run"]
        deactivate_missing = options["deactivate_missing"]

        if not re.fullmatch(r"[A-Za-z0-9_-]{1,60}", token):
            raise CommandError("Invalid board token.")

        if not company:
            raise CommandError("Company name is required.")

        skills = list(Skill.objects.all())

        if not skills:
            raise CommandError("No skills found in database.")

        source_name = f"Greenhouse:{token}"

        url = (
            "https://boards-api.greenhouse.io/v1/"
            f"boards/{token}/jobs"
        )

        # ================= FETCH COMPLETE BOARD =================

        session = requests.Session()

        session.headers.update({
            "Accept": "application/json",
            "User-Agent": "TracBeePortfolio/1.0",
        })

        self.stdout.write("Fetching complete company job board...")

        try:

            response = session.get(
                url,
                params={"content": "true"},
                timeout=30,
            )

            response.raise_for_status()
            payload = response.json()

        except (requests.RequestException, ValueError) as error:

            session.close()

            raise CommandError(f"API request failed: {error}")

        finally:
            session.close()

        if not isinstance(payload, dict):
            raise CommandError("Invalid Greenhouse response.")

        listings = payload.get("jobs")
        meta = payload.get("meta") or {}

        if not isinstance(listings, list):
            raise CommandError("Complete job list was not returned.")

        reported_total = meta.get("total")

        if reported_total is not None:
            try:
                if int(reported_total) != len(listings):
                    raise CommandError(
                        "Incomplete board response. "
                        "Synchronization cancelled."
                    )
            except (TypeError, ValueError):
                raise CommandError("Invalid board total.")

        # Never deactivate all records based on an empty response.
        if not listings:
            raise CommandError(
                "Board returned zero jobs. No records were changed."
            )

        # ================= VALIDATE SNAPSHOT =================

        prepared_jobs = []
        seen_urls = set()

        for item in listings:

            if not isinstance(item, dict):
                raise CommandError("Invalid job record in board response.")

            job_id = item.get("id")
            title = str(item.get("title") or "").strip()
            job_url = str(item.get("absolute_url") or "").strip()

            if not job_id or not title or not job_url:
                raise CommandError(
                    "A job record is missing its ID, title or URL. "
                    "Synchronization cancelled."
                )

            if job_url in seen_urls:
                raise CommandError(
                    "Duplicate job URLs in board response. "
                    "Synchronization cancelled."
                )

            seen_urls.add(job_url)

            location_data = item.get("location") or {}

            location = normalize_location(
                location_data.get("name", "")
                if isinstance(location_data, dict)
                else ""
            )

            description = clean_html(item.get("content", ""))

            posted_at = parse_posted_date(
                item.get("first_published")
            )

            source_updated_at = parse_source_updated(
                item.get("updated_at")
            )

            searchable_text = f"{title} {description}"

            matched_skills = []

            for skill in skills:

                terms = [skill.name] + (skill.aliases or [])

                matched = any(
                    re.search(
                        rf"(?<!\w){re.escape(term)}(?!\w)",
                        searchable_text,
                        re.IGNORECASE,
                    )
                    for term in terms
                    if isinstance(term, str) and term.strip()
                )

                if matched:
                    matched_skills.append(skill)

            prepared_jobs.append({
                "title": title,
                "url": job_url,
                "location": location,
                "description": description,
                "posted_at": posted_at,
                "source_updated_at": source_updated_at,
                "skills": matched_skills,
            })

        # ================= DRY RUN =================

        existing = JobPosting.objects.filter(
            source=source_name
        )

        seen_list = list(seen_urls)

        stale_query = existing.filter(
            is_active=True
        ).exclude(
            source_url__in=seen_list
        ).exclude(
            source_url=""
        )

        stale_count = stale_query.count()

        existing_urls = set(
            existing.values_list("source_url", flat=True)
        )

        new_count = sum(
            1 for job in prepared_jobs
            if job["url"] not in existing_urls
        )

        self.stdout.write(f"Company: {company}")
        self.stdout.write(f"Board jobs: {len(prepared_jobs)}")
        self.stdout.write(f"New jobs: {new_count}")
        self.stdout.write(
            f"Existing jobs: {len(prepared_jobs) - new_count}"
        )
        self.stdout.write(f"Potential inactive jobs: {stale_count}")

        if dry_run:

            self.stdout.write(
                self.style.SUCCESS(
                    "DRY RUN COMPLETE. Database unchanged."
                )
            )

            return

        # ================= DATABASE SYNCHRONIZATION =================

        created_count = 0
        updated_count = 0
        association_count = 0
        inactive_count = 0

        with transaction.atomic():

            for item in prepared_jobs:

                defaults = {
                    "title": item["title"],
                    "company": company,
                    "location": item["location"],
                    "is_active": True,
                }

                if item["description"]:
                    defaults["description"] = item["description"]

                if item["posted_at"] is not None:
                    defaults["posted_at"] = item["posted_at"]

                if item["source_updated_at"] is not None:
                    defaults["source_updated_at"] = (
                        item["source_updated_at"]
                    )

                job, created = JobPosting.objects.update_or_create(
                    source=source_name,
                    source_url=item["url"],
                    defaults=defaults,
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

                JobPostingSkill.objects.filter(
                    job_posting=job
                ).delete()

                links = [
                    JobPostingSkill(
                        job_posting=job,
                        skill=skill,
                        is_required=False,
                    )
                    for skill in item["skills"]
                ]

                JobPostingSkill.objects.bulk_create(links)

                association_count += len(links)

            # Deactivate only after a complete successful import.
            if deactivate_missing:

                inactive_count = existing.filter(
                    is_active=True
                ).exclude(
                    source_url__in=seen_list
                ).exclude(
                    source_url=""
                ).update(
                    is_active=False
                )

        # ================= SUMMARY =================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS("SYNCHRONIZATION COMPLETED")
        )

        self.stdout.write(f"New jobs: {created_count}")
        self.stdout.write(f"Updated jobs: {updated_count}")
        self.stdout.write(f"Skill associations: {association_count}")
        self.stdout.write(f"Deactivated jobs: {inactive_count}")

        self.stdout.write(
            f"Current company records: "
            f"{JobPosting.objects.filter(source=source_name).count()}"
        )
