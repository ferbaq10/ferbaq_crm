from django.urls import path

from .internal_api import (
    configuration_save,
    configuration_state,
    health,
    route_save,
    route_state,
)


app_name = 'commercial_config_internal'


urlpatterns = [
    path(
        'health/',
        health,
        name='health',
    ),

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