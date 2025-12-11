# proposal/admin.py
from django.contrib import admin, messages
from .models import Proposal, ProposalHistory


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'status', 'created_at')
    list_filter  = ('status',)
    readonly_fields = ('created_at', 'updated_at')
    actions = ['verify_offline']

    @admin.action(description='Mark VERIFIED (offline procedure done)')
    def verify_offline(self, request, queryset):
        for prop in queryset.filter(status='A'):   # accepted
            # send final PDF / SMS here
            messages.success(request, f'Proposal {prop.id} verified and archived.')