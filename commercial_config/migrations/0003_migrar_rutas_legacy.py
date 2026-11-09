from django.db import migrations


def migrar_rutas_legacy(
    apps,
    schema_editor,
):
    Configuration = apps.get_model(
        'commercial_config',
        'ClientProjectConfiguration',
    )

    Route = apps.get_model(
        'commercial_config',
        'ClientProjectRoute',
    )

    RouteWorkCell = apps.get_model(
        'commercial_config',
        'ClientProjectRouteWorkCell',
    )

    configuraciones = (
        Configuration.objects
        .filter(
            is_removed=False,
        )
        .iterator()
    )

    for configuration in configuraciones:

        # Configuraciones antiguas siempre tenían UDN.
        # A partir de ahora puede ser NULL porque la UDN vive
        # en ClientProjectRoute.

        if not configuration.udn_id:
            continue

        route, _ = (
            Route.objects
            .get_or_create(
                configuration_id=configuration.pk,
                udn_id=configuration.udn_id,
                defaults={
                    'is_active': (
                        configuration.is_active
                    ),
                    'is_removed': False,
                },
            )
        )

        # Si la configuración antigua tenía una célula,
        # se convierte automáticamente en una célula
        # autorizada para la ruta.

        if configuration.work_cell_id:

            RouteWorkCell.objects.get_or_create(
                route_id=route.pk,
                work_cell_id=(
                    configuration.work_cell_id
                ),
                defaults={
                    'is_active': True,
                    'is_removed': False,
                },
            )


class Migration(migrations.Migration):

    dependencies = [
        (
            'commercial_config',
            '0002_rutas_operativas',
        ),
    ]

    operations = [
        migrations.RunPython(
            migrar_rutas_legacy,
            migrations.RunPython.noop,
        ),
    ]