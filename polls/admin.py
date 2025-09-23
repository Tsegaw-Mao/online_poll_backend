from django.contrib import admin
from .models import Poll, Option, Vote

@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'created_by', 'expiry_date', 'created_at')
    list_filter = ('created_by', 'expiry_date')
    search_fields = ('title', 'description', 'created_by__username')
    ordering = ('-created_at',)


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'poll', 'vote_count')
    list_filter = ('poll',)
    search_fields = ('text',)
    ordering = ('poll',)


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'poll', 'option', 'created_at')
    list_filter = ('poll', 'option', 'user')
    search_fields = ('poll__title', 'option__text', 'user__username')
