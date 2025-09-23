from django.core.management.base import BaseCommand
from polls.models import Poll, Option, User

class Command(BaseCommand):
    help = "Seed initial users, polls, and options"

    def handle(self, *args, **kwargs):
        user, created = User.objects.get_or_create(username='seeduser', email='seed@example.com')
        if created:
            user.set_password('password123')
            user.save()

        poll_data = [
            {
                "title": "Favorite programming language?",
                "description": "Choose your top language",
                "options": ["Python", "JavaScript", "Go", "Rust"]
            },
            {
                "title": "Best frontend framework?",
                "description": "",
                "options": ["React", "Vue", "Angular", "Svelte"]
            }
        ]

        for pdata in poll_data:
            poll = Poll.objects.create(title=pdata['title'], description=pdata['description'], created_by=user)
            for opt in pdata['options']:
                Option.objects.create(poll=poll, text=opt)

        self.stdout.write(self.style.SUCCESS("Seeded users, polls, and options successfully!"))
