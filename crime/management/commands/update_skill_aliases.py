
from django.core.management.base import BaseCommand
from crime.models import Skill


SKILL_ALIASES = {
    "Python": ["python3", "cpython"],
    "Django": ["django framework", "django rest framework", "drf"],
    "SQL": ["structured query language"],
    "PostgreSQL": ["postgres", "postgres sql"],
    "REST API": [
        "rest apis",
        "restful api",
        "restful apis",
        "restful services",
        "drf",
    ],
    "JavaScript": ["ecmascript"],
    "React": ["react.js", "reactjs"],
    "HTML": ["html5"],
    "CSS": ["css3", "cascading style sheets"],
    "Machine Learning": ["machine-learning"],
    "Excel": ["microsoft excel"],
    "Git": ["git version control"],
    "Java": ["java programming"],
}


class Command(BaseCommand):
    help = "Update aliases for existing TracBee skills"

    def handle(self, *args, **options):

        updated = 0
        missing = []

        for skill_name, aliases in SKILL_ALIASES.items():

            count = Skill.objects.filter(
                name__iexact=skill_name
            ).update(aliases=aliases)

            if count:
                updated += count
            else:
                missing.append(skill_name)

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated skill aliases: {updated}"
            )
        )

        if missing:
            self.stdout.write(
                self.style.WARNING(
                    f"Skills not found: {', '.join(missing)}"
                )
            )
