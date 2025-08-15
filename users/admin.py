from django.contrib import admin
from .models import RolePolicy

@admin.register(RolePolicy)
class RolePolicyAdmin(admin.ModelAdmin):
    list_display = ('group', 'scope', 'priority')
    list_editable = ('scope', 'priority')
    search_fields = ('group__name',)
    ordering = ('priority', 'group__name')
