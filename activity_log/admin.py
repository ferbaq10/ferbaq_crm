from django.contrib import admin
from .models import ActivityLog
from .forms import ActivityLogForm

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    form = ActivityLogForm
