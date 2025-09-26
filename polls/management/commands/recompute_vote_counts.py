# polls/management/commands/recompute_vote_counts.py
from django.core.management.base import BaseCommand
from django.db.models import Count
from polls.models import Option

class Command(BaseCommand):
    help = "Recompute Option.vote_count from real Vote rows (fix drift)."

    def handle(self, *args, **options):
        qs = Option.objects.annotate(real_count=Count('votes')).values('id', 'real_count')
        updated = 0
        for row in qs:
            Option.objects.filter(pk=row['id']).update(vote_count=row['real_count'])
            updated += 1
        self.stdout.write(self.style.SUCCESS(f"Recomputed vote_count for {updated} options."))
