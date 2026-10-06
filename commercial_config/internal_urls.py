from django.urls import path

from .internal_api import (
    configuration_save,
    configuration_state,
    health,
    route_save,
    route_state,
)

from .internal_catalog_api import (
    cost_center_save,
    cost_center_state,
    delivery_site_save,
    delivery_site_state,
)


app_name = 'commercial_config_internal'


urlpatterns = [
    path(
        'health/',
        health,
        name='health',
    ),

    # ========================================================
    # SITIOS DE ENTREGA
    # ========================================================

    path(
        'delivery-site/save/',
        delivery_site_save,
        name='delivery_site_save',
    ),

    path(
        'delivery-site/state/',
        delivery_site_state,
        name='delivery_site_state',
    ),

    # ========================================================
    # CENTROS DE COSTO
    # ========================================================

    path(
        'cost-center/save/',
        cost_center_save,
        name='cost_center_save',
    ),

    path(
        'cost-center/state/',
        cost_center_state,
        name='cost_center_state',
    ),

    # ========================================================
    # CLIENTES + PROYECTOS
    # ========================================================

    path(
        'configuration/save/',
        configuration_save,
        name='configuration_save',
    ),

    path(
        'configuration/state/',
        configuration_state,
        name='configuration_state',
    ),

    # ========================================================
    # RUTAS
    # ========================================================

    path(
        'route/save/',
        route_save,
        name='route_save',
    ),

    path(
        'route/state/',
        route_state,
        name='route_state',
    ),
]