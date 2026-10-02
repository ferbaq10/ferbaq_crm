from django.contrib import admin

from .models import (
    ClientProjectConfiguration,
    CostCenter,
    DeliverySite,
)


@admin.register(DeliverySite)
class DeliverySiteAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'name',
        'city',
        'is_active',
        'modified',
    )

    list_filter = (
        'is_active',
        'city',
    )

    search_fields = (
        'code',
        'name',
        'address',
    )

    ordering = (
        'name',
    )


@admin.register(CostCenter)
class CostCenterAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'name',
        'delivery_site',
        'default_credit_days',
        'collection_contact',
        'is_active',
        'modified',
    )

    list_filter = (
        'is_active',
        'delivery_site',
    )

    search_fields = (
        'code',
        'name',
        'delivery_site__name',
        'collection_contact__name',
    )

    list_select_related = (
        'delivery_site',
        'collection_contact',
    )

    ordering = (
        'code',
    )


@admin.register(ClientProjectConfiguration)
class ClientProjectConfigurationAdmin(
    admin.ModelAdmin
):
    list_display = (
        'client',
        'project',
        'udn',
        'cost_center',
        'client_cost_center',
        'validation_status',
        'is_active',
        'modified',
    )

    list_filter = (
        'validation_status',
        'is_active',
        'udn',
        'cost_center',
    )

    search_fields = (
        'client__company',
        'client__rfc',
        'project__name',
        'cost_center__code',
        'client_cost_center',
    )

    list_select_related = (
        'client',
        'project',
        'udn',
        'cost_center',
        'work_cell',
    )

    readonly_fields = (
        'validated_at',
        'validated_by_username',
    )

    ordering = (
        'client__company',
        'project__name',
    )