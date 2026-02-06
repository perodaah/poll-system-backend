from django.contrib import admin
from .models import Poll, Option, Vote


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'created_by', 'created_at', 'expires_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ['text', 'poll', 'order_index']
    list_filter = ['poll']


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['poll', 'option', 'voter_identifier', 'voted_at']
    list_filter = ['poll', 'voted_at']