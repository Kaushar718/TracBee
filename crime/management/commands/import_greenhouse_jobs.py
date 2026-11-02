
import re
from datetime import datetime, timezone as datetime_timezone
from html import unescape

import requests

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from crime.models import Skill, JobPosting, JobPostingSkill


def clean_html(value):
    """Convert HTML job descriptions into readable text."""

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

    value = re.sub(
        r"\bBangalore\b",
        "Bengaluru",
        value,
        flags=re.IGNORECASE
    )

    return value or "Not specified" 


def parse_source_updated(value):
    """Parse Greenhouse updated_at into a timezone-aware datetime."""

    if not value:
        return None

    try:
        parsed = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )

        if parsed.tzinfo is None:
            parsed = parsed.replace(
                tzinfo=datetime_timezone.utc
            )

        return parsed

    except (ValueError, AttributeError):
        return None


def parse_posted_date(value):
    """Convert first_published into a Python date."""

    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        ).date()

    except (ValueError, AttributeError):
        return None


class Command(BaseCommand):

    help = "Import public jobs from a Greenhouse job board"

    def add_arguments(self, parser):

        parser.add_argument(
            "--board-token",
            required=True,
            help="Greenhouse public board token",
        )

        parser.add_argument(
            "--company-name",
            required=True,
            help="Company display name",
        )

        parser.add_argument(
            "--max-jobs",
            type=int,
            default=25,
        )

        parser.add_argument(
            "--location-contains",
            default="",
            help="Optional location filter",
        )

    def handle(self, *args, **options):

        token = options["board_token"].strip()
        company = options["company_name"].strip()

        max_jobs = options["max_jobs"]
        location_filter = options["location_contains"].strip()

        # ================= VALIDATION =================

        if not re.fullmatch(r"[A-Za-z0-9_-]{1,60}", token):
            raise CommandError("Invalid Greenhouse board token.")

        if not company:
            raise CommandError("Company name cannot be empty.")

        if not 1 <= max_jobs <= 100:
            raise CommandError(
                "Maximum jobs must be between 1 and 100."
            )

        skill_catalog = list(Skill.objects.all())

        if not skill_catalog:
            raise CommandError(
                "No skills found. Add skills through Django Admin."
            )

        # ================= API CONFIGURATION =================

        url = (
            "https://boards-api.greenhouse.io/v1/"
            f"boards/{token}/jobs"
        )

        source_name = f"Greenhouse:{token}"

        created_count = 0
        updated_count = 0
        skill_links = 0
        skipped_count = 0

        session = requests.Session()

        session.headers.update({
            "Accept": "application/json",
            "User-Agent": "TracBeePortfolio/1.0",
        })

        self.stdout.write(
            self.style.NOTICE(
                f"Fetching jobs for {company}..."
            )
        )

        # ================= FETCH JOB LIST =================

        try:

            response = session.get(
                url,
                params={"content": "true"},
                timeout=20,
            )

            response.raise_for_status()

            payload = response.json()

        except (requests.RequestException, ValueError) as error:

            session.close()

            raise CommandError(
                f"Greenhouse API request failed: {error}"
            )

        finally:
            # Response fetching is completed before database writes.
            pass

        if not isinstance(payload, dict):
            session.close()
            raise CommandError("Invalid API response.")

        listings = payload.get("jobs")

        if not isinstance(listings, list):
            session.close()
            raise CommandError(
                "Greenhouse jobs list was not found."
            )

        # ================= LOCATION FILTER =================

        if location_filter:

            listings = [
                item for item in listings

                if isinstance(item, dict)

                and location_filter.casefold() in (
                    (
                        (item.get("location") or {}).get("name", "")
                        if isinstance(item.get("location"), dict)
                        else ""
                    ).casefold()
                )
            ]

        listings = listings[:max_jobs]

        if not listings:

            session.close()

            self.stdout.write(
                self.style.WARNING(
                    "No matching job postings found."
                )
            )

            return

        self.stdout.write(
            f"Found {len(listings)} matching job postings."
        )

        # ================= PROCESS JOBS =================

        try:

            for item in listings:

                if not isinstance(item, dict):
                    skipped_count += 1
                    continue

                job_id = item.get("id")
                title = str(item.get("title") or "").strip()
                job_url = str(item.get("absolute_url") or "").strip()

                if not job_id or not title or not job_url:
                    skipped_count += 1
                    continue

                # ================= LOCATION =================

                location_data = item.get("location")
                location = (
                    location_data.get("name", "")
                    if isinstance(location_data, dict)
                    else ""
                )
                location = normalize_location(location)

                # ================= JOB DETAILS =================

                detail = {}

                # The list endpoint provides content.
                # Retrieve individual details for publication
                # date when it is missing.

                needs_detail = (
                    not item.get("first_published")
                    or not item.get("content")
                )

                if needs_detail:

                    try:

                        detail_response = session.get(
                            f"{url}/{job_id}",
                            timeout=15,
                        )

                        detail_response.raise_for_status()

                        detail = detail_response.json()

                        if not isinstance(detail, dict):
                            detail = {}

                    except (requests.RequestException, ValueError):

                        self.stdout.write(
                            self.style.WARNING(
                                f"Details unavailable for job {job_id}."
                            )
                        )

                # ================= DESCRIPTION =================

                description_html = (
                    item.get("content")
                    or detail.get("content")
                    or ""
                )

                description = clean_html(description_html)

                # ================= DATES =================

                published_value = (
                    item.get("first_published")
                    or detail.get("first_published")
                )

                posted_at = parse_posted_date(
                    published_value
                )

                updated_value = (
                    item.get("updated_at")
                    or detail.get("updated_at")
                )

                source_updated_at = parse_source_updated(
                    updated_value
                )

                # ================= DATABASE SAVE =================

                defaults = {
                    "title": title,
                    "company": company,
                    "location": location,
                    "employment_type": "",
                    "is_active": True,
                }

                # Preserve existing values when the source
                # does not provide the corresponding information.

                if description:
                    defaults["description"] = description

                if posted_at is not None:
                    defaults["posted_at"] = posted_at

                if source_updated_at is not None:
                    defaults["source_updated_at"] = (
                        source_updated_at
                    )

                with transaction.atomic():

                    job, created = JobPosting.objects.update_or_create(
                        source=source_name,
                        source_url=job_url,
                        defaults=defaults,
                    )

                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

                    # ================= SKILL DETECTION =================

                    searchable_text = (
                        f"{title} {description}"
                    )

                    JobPostingSkill.objects.filter(
                        job_posting=job
                    ).delete()

                    for skill in skill_catalog:
                        terms = [skill.name] + (skill.aliases or [])

                        matched = any(
                            re.search(
                                rf"(?<!\w){re.escape(term)}(?!\w)",
                                searchable_text,
                                re.IGNORECASE,
                            )
                            for term in terms
                            if term.strip()
                        )

                        if matched:
                            JobPostingSkill.objects.create(
                                job_posting=job,
                                skill=skill,
                                is_required=False,
                            )

                            skill_links += 1

        finally:

            session.close()

        # ================= IMPORT SUMMARY =================

        total_imported = JobPosting.objects.filter(
            source=source_name
        ).count()

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS("IMPORT COMPLETED")
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"New jobs: {created_count}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated jobs: {updated_count}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Detected skill mentions: {skill_links}"
            )
        )

        self.stdout.write(
            self.style.WARNING(
                f"Skipped jobs: {skipped_count}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Total company jobs in database: {total_imported}"
            )
        )
